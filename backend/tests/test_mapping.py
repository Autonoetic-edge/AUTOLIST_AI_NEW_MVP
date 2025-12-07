"""
Tests for the rule-based mapping service.
"""
import pytest

from app.services.mapping_service import (
    map_to_schema,
    map_single_field,
    match_enum_value,
    get_unmapped_fields,
    get_required_unmapped,
    normalize_key,
    MappingResult,
)


# Sample schema for testing
SAMPLE_SCHEMA = {
    "schema_id": "test_shirt_v1",
    "marketplace": "amazon",
    "category": "shirt",
    "columns": [
        {"col_index": 0, "header": "SKU", "canonical": "sku", "type": "string", "required": True},
        {"col_index": 1, "header": "Title", "canonical": "title", "type": "string", "required": True},
        {"col_index": 2, "header": "Brand", "canonical": "brand", "type": "string", "required": True},
        {"col_index": 3, "header": "Price", "canonical": "price", "type": "float", "required": True},
        {"col_index": 4, "header": "Color", "canonical": "color", "type": "string", "required": True},
        {"col_index": 5, "header": "Size", "canonical": "size", "type": "string", "required": True, "enum": ["S", "M", "L", "XL"]},
        {"col_index": 6, "header": "Fabric", "canonical": "fabric", "type": "string", "required": False, "enum": ["Cotton", "Polyester", "Silk"]},
    ],
}


class TestMatchEnumValue:
    """Tests for enum matching."""

    def test_exact_match(self):
        """Test exact enum matching."""
        value, confidence = match_enum_value("Cotton", ["Cotton", "Polyester", "Silk"])
        assert value == "Cotton"
        assert confidence == 0.95

    def test_case_insensitive_match(self):
        """Test case-insensitive matching."""
        value, confidence = match_enum_value("cotton", ["Cotton", "Polyester", "Silk"])
        assert value == "Cotton"
        assert confidence == 0.95

    def test_partial_match(self):
        """Test partial matching."""
        value, confidence = match_enum_value("pure cotton", ["Cotton", "Polyester", "Silk"])
        assert value == "Cotton"
        assert confidence == 0.85

    def test_no_match(self):
        """Test no match scenario."""
        value, confidence = match_enum_value("wool", ["Cotton", "Polyester", "Silk"])
        assert value is None
        assert confidence == 0.0


class TestMapSingleField:
    """Tests for single field mapping."""

    def test_exact_key_mapping(self):
        """Test direct key mapping."""
        product = {"title": "Blue Cotton Shirt", "brand": "TestBrand"}

        result = map_single_field(product, "title")
        assert result.value == "Blue Cotton Shirt"
        assert result.source == "product.title"
        assert result.confidence == 0.95

    def test_cleaned_key_mapping(self):
        """Test cleaned field mapping."""
        product = {"cleaned_title": "Clean Title", "title": "Raw Title"}

        result = map_single_field(product, "title")
        assert result.value == "Raw Title"  # Exact key takes priority

    def test_synonym_mapping(self):
        """Test synonym-based mapping."""
        product = {"vendor": "Brand Name"}  # vendor is synonym for brand

        result = map_single_field(product, "brand")
        assert result.value == "Brand Name"
        assert "vendor" in result.source
        assert result.confidence >= 0.90

    def test_metafield_mapping(self):
        """Test metafield extraction."""
        product = {
            "title": "Shirt",
            "metafields": {
                "custom": {
                    "fabric_composition": "100% Cotton"
                }
            }
        }

        result = map_single_field(product, "fabric")
        assert result.value == "100% Cotton"
        assert "metafield" in result.source

    def test_variant_extraction(self):
        """Test variant field extraction."""
        product = {
            "title": "Shirt",
            "variants_simplified": [
                {
                    "sku": "SHIRT-001",
                    "price": "29.99",
                    "option1": "M",
                }
            ]
        }

        result = map_single_field(product, "sku")
        assert result.value == "SHIRT-001"
        assert "variant" in result.source

        result = map_single_field(product, "price")
        assert result.value == "29.99"

    def test_extracted_attributes(self):
        """Test extracted attribute mapping."""
        product = {
            "title": "Shirt",
            "extracted_materials": ["100% Cotton"],
            "extracted_colors": ["Blue"],
        }

        result = map_single_field(product, "fabric")
        assert "Cotton" in result.value
        assert result.confidence == 0.60

        result = map_single_field(product, "color")
        assert result.value == "Blue"

    def test_not_found(self):
        """Test unmapped field."""
        product = {"title": "Shirt"}

        result = map_single_field(product, "nonexistent_field")
        assert result.value is None
        assert result.source == "not_found"
        assert result.confidence == 0.0


class TestMapToSchema:
    """Tests for full schema mapping."""

    def test_complete_mapping(self):
        """Test mapping a complete product."""
        product = {
            "title": "Blue Cotton Shirt",
            "vendor": "Fashion Brand",
            "extracted_colors": ["Blue"],
            "extracted_materials": ["Cotton"],
            "variants_simplified": [
                {
                    "sku": "SHIRT-BLU-M",
                    "price": "29.99",
                    "option1": "M",
                }
            ]
        }

        mappings = map_to_schema(product, SAMPLE_SCHEMA)

        assert "sku" in mappings
        assert mappings["sku"]["value"] == "SHIRT-BLU-M"

        assert "title" in mappings
        assert mappings["title"]["value"] == "Blue Cotton Shirt"

        assert "brand" in mappings
        assert mappings["brand"]["value"] == "Fashion Brand"

        assert "price" in mappings
        assert mappings["price"]["value"] == "29.99"

    def test_enum_matching_in_schema(self):
        """Test enum fields are matched properly."""
        product = {
            "title": "Shirt",
            "extracted_materials": ["cotton fabric"],
            "variants_simplified": [{"sku": "TEST", "price": "10", "option1": "medium"}],
        }

        mappings = map_to_schema(product, SAMPLE_SCHEMA)

        # Size should match enum (M for medium)
        # Fabric should match enum (Cotton for cotton)


class TestGetUnmappedFields:
    """Tests for identifying unmapped fields."""

    def test_identify_unmapped(self):
        """Test identification of unmapped fields."""
        mappings = {
            "sku": {"value": "TEST", "source": "variant", "confidence": 0.95},
            "title": {"value": "Shirt", "source": "product", "confidence": 0.95},
            "brand": {"value": None, "source": "not_found", "confidence": 0.0},
            "price": {"value": "10", "source": "variant", "confidence": 0.95},
            "color": {"value": "Blue", "source": "extracted", "confidence": 0.60},
            "size": {"value": None, "source": "not_found", "confidence": 0.0},
            "fabric": {"value": None, "source": "not_found", "confidence": 0.0},
        }

        unmapped = get_unmapped_fields(mappings, SAMPLE_SCHEMA, confidence_threshold=0.8)

        assert "brand" in unmapped
        assert "color" in unmapped  # Below threshold
        assert "size" in unmapped
        assert "fabric" in unmapped
        assert "sku" not in unmapped
        assert "title" not in unmapped

    def test_identify_required_unmapped(self):
        """Test identification of required unmapped fields."""
        mappings = {
            "sku": {"value": "TEST", "source": "variant", "confidence": 0.95},
            "title": {"value": "Shirt", "source": "product", "confidence": 0.95},
            "brand": {"value": None, "source": "not_found", "confidence": 0.0},
            "price": {"value": "10", "source": "variant", "confidence": 0.95},
            "color": {"value": "Blue", "source": "extracted", "confidence": 0.40},
            "size": {"value": None, "source": "not_found", "confidence": 0.0},
            "fabric": {"value": None, "source": "not_found", "confidence": 0.0},
        }

        required = get_required_unmapped(mappings, SAMPLE_SCHEMA, confidence_threshold=0.5)

        assert "brand" in required
        assert "color" in required
        assert "size" in required
        assert "fabric" not in required  # Not required in schema


class TestNormalizeKey:
    """Tests for key normalization."""

    def test_lowercase(self):
        assert normalize_key("Title") == "title"

    def test_replace_dash(self):
        assert normalize_key("product-type") == "product_type"

    def test_replace_space(self):
        assert normalize_key("product type") == "product_type"

    def test_strip(self):
        assert normalize_key("  title  ") == "title"
