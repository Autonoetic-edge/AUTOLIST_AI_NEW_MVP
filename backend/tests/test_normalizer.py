"""
Tests for the normalizer worker.
"""
import pytest

from app.workers.normalizer import (
    clean_text,
    clean_title,
    clean_description,
    extract_materials,
    extract_colors,
    extract_sizes,
    simplify_variants,
    normalize_product,
)


class TestCleanText:
    """Tests for text cleaning functions."""

    def test_clean_text_removes_html(self):
        """Test that HTML tags are removed."""
        text = "<p>This is <strong>bold</strong> text</p>"
        result = clean_text(text)
        assert "<" not in result
        assert ">" not in result
        assert "bold" in result

    def test_clean_text_normalizes_whitespace(self):
        """Test that multiple spaces are normalized."""
        text = "Too   many    spaces   here"
        result = clean_text(text)
        assert "  " not in result

    def test_clean_title_removes_marketing(self):
        """Test that marketing phrases are removed from titles."""
        title = "Buy Premium Cotton Shirt Online"
        result = clean_title(title)
        assert "buy" not in result.lower()
        assert "online" not in result.lower()
        assert "cotton" in result.lower()


class TestMaterialExtraction:
    """Tests for material extraction."""

    def test_extract_materials_percentage(self):
        """Test extraction of materials with percentages."""
        text = "Made from 100% pure cotton fabric"
        materials = extract_materials(text)
        assert len(materials) >= 1
        assert any("cotton" in m.lower() for m in materials)

    def test_extract_materials_multiple(self):
        """Test extraction of multiple materials."""
        text = "60% cotton, 40% polyester blend"
        materials = extract_materials(text)
        assert len(materials) >= 2
        assert any("cotton" in m.lower() for m in materials)
        assert any("polyester" in m.lower() for m in materials)

    def test_extract_materials_traditional(self):
        """Test extraction of traditional fabric names."""
        text = "Handwoven khadi fabric with banarasi work"
        materials = extract_materials(text)
        assert any("khadi" in m.lower() for m in materials)


class TestColorExtraction:
    """Tests for color extraction."""

    def test_extract_colors_basic(self):
        """Test extraction of basic colors."""
        text = "Beautiful blue t-shirt with white stripes"
        colors = extract_colors(text)
        assert "Blue" in colors
        assert "White" in colors

    def test_extract_colors_shades(self):
        """Test extraction of color shades."""
        text = "Elegant navy blue kurta with maroon embroidery"
        colors = extract_colors(text)
        assert "Navy Blue" in colors
        assert "Maroon" in colors

    def test_extract_colors_no_false_positives(self):
        """Test that non-color words are not extracted."""
        text = "Premium quality fabric material"
        colors = extract_colors(text)
        assert len(colors) == 0


class TestSizeExtraction:
    """Tests for size extraction."""

    def test_extract_sizes_letter(self):
        """Test extraction of letter sizes."""
        text = "Available in S, M, L, XL sizes"
        sizes = extract_sizes(text)
        assert "S" in sizes
        assert "M" in sizes
        assert "L" in sizes
        assert "XL" in sizes

    def test_extract_sizes_numeric(self):
        """Test extraction of numeric sizes."""
        text = "Size 38 and 40 available"
        sizes = extract_sizes(text)
        assert "38" in sizes
        assert "40" in sizes

    def test_extract_sizes_free_size(self):
        """Test extraction of free size."""
        text = "One size fits all, free size garment"
        sizes = extract_sizes(text)
        assert "Free Size" in sizes


class TestNormalizeProduct:
    """Tests for full product normalization."""

    def test_normalize_complete_product(self):
        """Test normalization of a complete product."""
        product = {
            "id": "12345",
            "title": "Buy Premium 100% Cotton Blue T-Shirt Online",
            "description": "<p>Soft cotton fabric. Available in S, M, L sizes.</p>",
            "vendor": "Fashion Brand",
            "product_type": "Shirt",
            "tags": ["cotton", "casual"],
            "variants": [
                {
                    "id": "v1",
                    "sku": "SHIRT-BLU-S",
                    "title": "Small",
                    "price": "29.99",
                    "option1": "Small",
                    "option2": "Blue",
                    "inventory_quantity": 50,
                }
            ],
            "images": [
                {"src": "https://example.com/image1.jpg"},
                {"src": "https://example.com/image2.jpg"},
            ],
        }

        result = normalize_product(product)

        # Check cleaned fields
        assert "buy" not in result["cleaned_title"].lower()
        assert "online" not in result["cleaned_title"].lower()
        assert "cotton" in result["cleaned_title"].lower()

        # Check extracted attributes
        assert any("cotton" in m.lower() for m in result["extracted_materials"])
        assert "Blue" in result["extracted_colors"]
        assert any(s in result["sizes"] for s in ["S", "M", "L"])

        # Check variants
        assert len(result["variants_simplified"]) == 1
        assert result["variants_simplified"][0]["sku"] == "SHIRT-BLU-S"

        # Check images
        assert result["main_image_url"] == "https://example.com/image1.jpg"
        assert len(result["other_image_urls"]) == 1

    def test_normalize_product_with_metafields(self):
        """Test normalization extracts from metafields."""
        product = {
            "id": "67890",
            "title": "Elegant Kurta",
            "description": "Traditional wear",
            "variants": [],
            "images": [],
            "metafields": {
                "custom": {
                    "fabric_composition": "100% Silk",
                    "care_instructions": "Dry clean only",
                }
            },
        }

        result = normalize_product(product)

        # Should extract silk from metafields
        assert any("silk" in m.lower() for m in result["extracted_materials"])

    def test_normalize_product_minimal(self):
        """Test normalization handles minimal product data."""
        product = {
            "id": "99999",
            "title": "Simple Product",
        }

        result = normalize_product(product)

        assert result["original_id"] == "99999"
        assert result["cleaned_title"] == "Simple Product"
        assert result["cleaned_description"] == ""
        assert result["variants_simplified"] == []
        assert result["main_image_url"] == ""
