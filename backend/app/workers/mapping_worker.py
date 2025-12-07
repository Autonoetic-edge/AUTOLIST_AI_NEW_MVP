"""
Mapping Worker

Orchestrates the mapping process:
1. Loads product and schema data
2. Runs rule-based mapping
3. Calls Claude AI for missing/low-confidence fields
4. Merges results and saves mapping job
"""
import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum

import anthropic

from ..config import settings
from ..services.mapping_service import (
    map_to_schema,
    get_unmapped_fields,
    get_required_unmapped,
)
from ..services.claude_prompts import (
    build_extraction_prompt,
    build_focused_extraction_prompt,
    get_system_message,
)
from ..workers.normalizer import normalize_product


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MappingJobStatus(str, Enum):
    """Status values for mapping jobs."""
    PENDING = "pending"
    PROCESSING = "processing"
    NEEDS_USER_INPUT = "needs_user_input"
    READY = "ready"
    COMPLETED = "completed"
    ERROR = "error"


class MappingWorker:
    """Worker class for processing product mappings."""

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        confidence_threshold: float = 0.8,
        required_threshold: float = 0.5,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize the mapping worker.

        Args:
            anthropic_api_key: Claude API key (defaults to settings)
            confidence_threshold: Threshold for considering a field "mapped"
            required_threshold: Minimum confidence for required fields
            max_retries: Maximum retry attempts for AI calls
            retry_delay: Base delay between retries (exponential backoff)
        """
        self.api_key = anthropic_api_key or settings.ANTHROPIC_API_KEY
        self.confidence_threshold = confidence_threshold
        self.required_threshold = required_threshold
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Initialize Anthropic client if API key available
        self.client = None
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    async def process_job(
        self,
        job_id: str,
        product_id: str,
        template_schema_id: str,
        product_data: Optional[Dict[str, Any]] = None,
        schema_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a mapping job.

        Args:
            job_id: Unique job identifier
            product_id: Product identifier
            template_schema_id: Schema identifier
            product_data: Optional pre-loaded product data
            schema_data: Optional pre-loaded schema data

        Returns:
            Mapping job result dictionary
        """
        logger.info(f"Processing mapping job {job_id} for product {product_id}")

        try:
            # Load data if not provided
            if product_data is None:
                product_data = await self._load_product(product_id)

            if schema_data is None:
                schema_data = await self._load_schema(template_schema_id)

            # Normalize product
            normalized_product = normalize_product(product_data)

            # Run rule-based mapping
            rule_mappings = map_to_schema(normalized_product, schema_data)
            logger.info(f"Rule-based mapping completed for {len(rule_mappings)} fields")

            # Identify fields needing AI assistance
            unmapped_fields = get_unmapped_fields(
                rule_mappings, schema_data, self.confidence_threshold
            )

            # Call Claude for unmapped fields if available
            ai_mappings = {}
            if unmapped_fields and self.client:
                logger.info(f"Calling Claude for {len(unmapped_fields)} unmapped fields")
                ai_mappings = await self._call_claude_with_retry(
                    unmapped_fields,
                    schema_data["columns"],
                    normalized_product,
                )

            # Merge results
            final_mappings = self._merge_mappings(rule_mappings, ai_mappings)

            # Determine job status
            required_unmapped = get_required_unmapped(
                final_mappings, schema_data, self.required_threshold
            )

            if required_unmapped:
                status = MappingJobStatus.NEEDS_USER_INPUT
            else:
                status = MappingJobStatus.READY

            # Build job result
            job_result = {
                "job_id": job_id,
                "product_id": product_id,
                "template_schema_id": template_schema_id,
                "status": status.value,
                "mappings": final_mappings,
                "unmapped_fields": unmapped_fields,
                "required_unmapped": required_unmapped,
                "rule_based_count": sum(
                    1 for m in final_mappings.values()
                    if m.get("source", "").startswith(("product", "variant", "metafield"))
                ),
                "ai_assisted_count": sum(
                    1 for m in final_mappings.values()
                    if m.get("source", "").startswith("ai")
                ),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            # Save to database
            await self._save_mapping_job(job_result)

            logger.info(f"Job {job_id} completed with status: {status.value}")
            return job_result

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {e}")
            error_result = {
                "job_id": job_id,
                "product_id": product_id,
                "template_schema_id": template_schema_id,
                "status": MappingJobStatus.ERROR.value,
                "error": str(e),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            await self._save_mapping_job(error_result)
            raise

    async def _call_claude_with_retry(
        self,
        fields: List[str],
        columns: List[Dict],
        normalized_product: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Call Claude API with exponential backoff retry.

        Args:
            fields: Fields to extract
            columns: Schema columns
            normalized_product: Normalized product data

        Returns:
            AI mapping results
        """
        # Filter columns to only requested fields
        filtered_columns = [c for c in columns if c["canonical"] in fields]

        prompt = build_focused_extraction_prompt(
            fields, columns, normalized_product
        )

        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2048,
                    system=get_system_message(),
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                )

                # Parse response
                response_text = response.content[0].text.strip()

                # Clean up response if it has markdown code blocks
                if response_text.startswith("```"):
                    lines = response_text.split("\n")
                    response_text = "\n".join(lines[1:-1])

                ai_result = json.loads(response_text)

                # Mark all AI results with proper source
                for field, mapping in ai_result.items():
                    if isinstance(mapping, dict):
                        if mapping.get("source") == "ai_inferred" or "ai" in mapping.get("source", ""):
                            mapping["source"] = "ai"
                        elif mapping.get("source"):
                            mapping["source"] = f"ai_{mapping['source']}"
                        else:
                            mapping["source"] = "ai"

                return ai_result

            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error on attempt {attempt + 1}: {e}")
            except anthropic.APIError as e:
                logger.warning(f"API error on attempt {attempt + 1}: {e}")

            # Exponential backoff
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)

        logger.error("All Claude API retry attempts failed")
        return {}

    def _merge_mappings(
        self,
        rule_mappings: Dict[str, Dict[str, Any]],
        ai_mappings: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Merge rule-based and AI mappings.

        Strategy:
        - If rule-based has high confidence, keep it
        - If AI has a value and rule-based doesn't, use AI
        - If both have values, use higher confidence (AI discounted by 0.9)

        Args:
            rule_mappings: Results from rule-based mapping
            ai_mappings: Results from Claude AI

        Returns:
            Merged mapping results
        """
        merged = {}

        # Process all rule-based mappings
        for field, rule_result in rule_mappings.items():
            merged[field] = rule_result.copy()

            # Check if AI has a result for this field
            if field in ai_mappings:
                ai_result = ai_mappings[field]

                rule_value = rule_result.get("value")
                rule_conf = rule_result.get("confidence", 0.0)

                ai_value = ai_result.get("value")
                ai_conf = ai_result.get("confidence", 0.0)

                # Apply AI discount factor
                adjusted_ai_conf = ai_conf * 0.9

                # Decision logic
                if rule_value is None and ai_value is not None:
                    # Use AI result
                    merged[field] = {
                        "value": ai_value,
                        "source": ai_result.get("source", "ai"),
                        "confidence": adjusted_ai_conf,
                    }
                elif rule_value is not None and ai_value is not None:
                    # Both have values - use higher confidence
                    if adjusted_ai_conf > rule_conf:
                        merged[field] = {
                            "value": ai_value,
                            "source": ai_result.get("source", "ai"),
                            "confidence": max(rule_conf, adjusted_ai_conf),
                        }
                    else:
                        # Keep rule-based but note AI confirmation
                        if abs(adjusted_ai_conf - rule_conf) < 0.1:
                            # AI confirms rule-based - boost confidence
                            merged[field]["confidence"] = min(0.99, rule_conf + 0.05)

        # Add any AI-only fields not in rule mappings
        for field, ai_result in ai_mappings.items():
            if field not in merged:
                merged[field] = {
                    "value": ai_result.get("value"),
                    "source": ai_result.get("source", "ai"),
                    "confidence": ai_result.get("confidence", 0.0) * 0.9,
                }

        return merged

    async def _load_product(self, product_id: str) -> Dict[str, Any]:
        """
        Load product data from database.

        TODO: Implement MongoDB lookup

        Args:
            product_id: Product identifier

        Returns:
            Product data dictionary
        """
        # TODO: Implement actual MongoDB query
        # from ..dependencies import get_database
        # db = await get_database()
        # product = await db.products.find_one({"_id": product_id})

        logger.warning(f"Using mock product data for {product_id}")
        return {
            "id": product_id,
            "title": "Sample Product",
            "description": "Sample description",
            "variants": [],
        }

    async def _load_schema(self, schema_id: str) -> Dict[str, Any]:
        """
        Load schema data from database or file.

        Args:
            schema_id: Schema identifier

        Returns:
            Schema data dictionary
        """
        # Try loading from file first
        import os
        from pathlib import Path

        schema_path = (
            Path(__file__).parent.parent / "data" / "template_schemas" / f"{schema_id}.json"
        )

        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                return json.load(f)

        # TODO: Implement MongoDB lookup
        # from ..dependencies import get_database
        # db = await get_database()
        # schema = await db.template_schemas.find_one({"_id": schema_id})

        raise ValueError(f"Schema not found: {schema_id}")

    async def _save_mapping_job(self, job_data: Dict[str, Any]) -> None:
        """
        Save mapping job to database.

        TODO: Implement MongoDB save

        Args:
            job_data: Job data to save
        """
        # TODO: Implement actual MongoDB save
        # from ..dependencies import get_database
        # db = await get_database()
        # await db.mapping_jobs.update_one(
        #     {"_id": job_data["job_id"]},
        #     {"$set": job_data},
        #     upsert=True,
        # )

        logger.info(f"[MOCK] Saved mapping job: {job_data['job_id']}")


async def process_mapping_job(
    job_id: str,
    product_id: str,
    template_schema_id: str,
    product_data: Optional[Dict[str, Any]] = None,
    schema_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to process a mapping job.

    Args:
        job_id: Job identifier
        product_id: Product identifier
        template_schema_id: Schema identifier
        product_data: Optional pre-loaded product data
        schema_data: Optional pre-loaded schema data

    Returns:
        Mapping job result
    """
    worker = MappingWorker()
    return await worker.process_job(
        job_id, product_id, template_schema_id, product_data, schema_data
    )


def calculate_auto_fill_rate(mappings: Dict[str, Dict[str, Any]]) -> float:
    """
    Calculate the auto-fill rate (average confidence) for a mapping.

    Args:
        mappings: Mapping results

    Returns:
        Average confidence score (0.0 - 1.0)
    """
    if not mappings:
        return 0.0

    confidences = [
        m.get("confidence", 0.0)
        for m in mappings.values()
        if m.get("value") is not None
    ]

    if not confidences:
        return 0.0

    return sum(confidences) / len(confidences)
