"""
Tests for the mapping worker.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.workers.mapping_worker import (
    MappingWorker,
    MappingJobStatus,
    calculate_auto_fill_rate,
)


class TestMappingWorker:
    """Tests for the MappingWorker class."""

    def test_merge_mappings_rule_only(self):
        """Test merging when only rule-based has results."""
        worker = MappingWorker()

        rule_mappings = {
            "sku": {"value": "TEST-001", "source": "variant.sku", "confidence": 0.95},
            "title": {"value": "Test Product", "source": "product.title", "confidence": 0.95},
        }
        ai_mappings = {}

        merged = worker._merge_mappings(rule_mappings, ai_mappings)

        assert merged["sku"]["value"] == "TEST-001"
        assert merged["title"]["value"] == "Test Product"

    def test_merge_mappings_ai_fills_gaps(self):
        """Test that AI fills in missing values."""
        worker = MappingWorker()

        rule_mappings = {
            "sku": {"value": "TEST-001", "source": "variant.sku", "confidence": 0.95},
            "color": {"value": None, "source": "not_found", "confidence": 0.0},
        }
        ai_mappings = {
            "color": {"value": "Blue", "source": "ai_description", "confidence": 0.80},
        }

        merged = worker._merge_mappings(rule_mappings, ai_mappings)

        assert merged["sku"]["value"] == "TEST-001"
        assert merged["color"]["value"] == "Blue"
        assert "ai" in merged["color"]["source"]
        # AI confidence is discounted by 0.9
        assert merged["color"]["confidence"] == pytest.approx(0.72, rel=0.01)

    def test_merge_mappings_higher_confidence_wins(self):
        """Test that higher confidence value wins."""
        worker = MappingWorker()

        rule_mappings = {
            "fabric": {"value": "Polyester", "source": "extracted", "confidence": 0.60},
        }
        ai_mappings = {
            "fabric": {"value": "Cotton", "source": "ai_description", "confidence": 0.90},
        }

        merged = worker._merge_mappings(rule_mappings, ai_mappings)

        # AI (0.90 * 0.9 = 0.81) > rule (0.60), so AI wins
        assert merged["fabric"]["value"] == "Cotton"

    def test_merge_mappings_rule_keeps_when_higher(self):
        """Test that rule-based value is kept when higher confidence."""
        worker = MappingWorker()

        rule_mappings = {
            "sku": {"value": "EXACT-SKU", "source": "variant.sku", "confidence": 0.95},
        }
        ai_mappings = {
            "sku": {"value": "AI-SKU", "source": "ai", "confidence": 0.70},
        }

        merged = worker._merge_mappings(rule_mappings, ai_mappings)

        # Rule (0.95) > AI (0.70 * 0.9 = 0.63), so rule wins
        assert merged["sku"]["value"] == "EXACT-SKU"


class TestCalculateAutoFillRate:
    """Tests for auto-fill rate calculation."""

    def test_full_confidence(self):
        """Test with all high confidence values."""
        mappings = {
            "sku": {"value": "TEST", "confidence": 0.95},
            "title": {"value": "Product", "confidence": 0.95},
            "price": {"value": "29.99", "confidence": 0.95},
        }

        rate = calculate_auto_fill_rate(mappings)
        assert rate == pytest.approx(0.95, rel=0.01)

    def test_mixed_confidence(self):
        """Test with mixed confidence values."""
        mappings = {
            "sku": {"value": "TEST", "confidence": 0.95},
            "title": {"value": "Product", "confidence": 0.95},
            "color": {"value": "Blue", "confidence": 0.60},
        }

        rate = calculate_auto_fill_rate(mappings)
        expected = (0.95 + 0.95 + 0.60) / 3
        assert rate == pytest.approx(expected, rel=0.01)

    def test_excludes_null_values(self):
        """Test that null values are excluded from calculation."""
        mappings = {
            "sku": {"value": "TEST", "confidence": 0.95},
            "title": {"value": None, "confidence": 0.0},
            "price": {"value": "29.99", "confidence": 0.90},
        }

        rate = calculate_auto_fill_rate(mappings)
        expected = (0.95 + 0.90) / 2
        assert rate == pytest.approx(expected, rel=0.01)

    def test_empty_mappings(self):
        """Test with empty mappings."""
        rate = calculate_auto_fill_rate({})
        assert rate == 0.0

    def test_all_null_values(self):
        """Test when all values are null."""
        mappings = {
            "sku": {"value": None, "confidence": 0.0},
            "title": {"value": None, "confidence": 0.0},
        }

        rate = calculate_auto_fill_rate(mappings)
        assert rate == 0.0


class TestMappingJobStatus:
    """Tests for job status determination."""

    def test_status_values(self):
        """Test status enum values."""
        assert MappingJobStatus.PENDING.value == "pending"
        assert MappingJobStatus.PROCESSING.value == "processing"
        assert MappingJobStatus.NEEDS_USER_INPUT.value == "needs_user_input"
        assert MappingJobStatus.READY.value == "ready"
        assert MappingJobStatus.COMPLETED.value == "completed"
        assert MappingJobStatus.ERROR.value == "error"
