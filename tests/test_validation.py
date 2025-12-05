# ABOUTME: Unit tests for validation.py module.
# ABOUTME: Tests image validation and input sanitization.

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validation import (
    ValidationError,
    validate_image,
    _is_valid_image,
    read_and_validate_images,
    MAX_IMAGE_SIZE_BYTES,
    MAX_IMAGES,
)


# PNG magic bytes (minimal valid PNG header)
PNG_HEADER = b"\x89PNG\r\n\x1a\n"
JPEG_HEADER = b"\xff\xd8\xff"


class TestIsValidImage:
    """Tests for image magic bytes detection."""

    def test_valid_png(self):
        data = PNG_HEADER + b"\x00" * 100
        assert _is_valid_image(data) is True

    def test_valid_jpeg(self):
        data = JPEG_HEADER + b"\x00" * 100
        assert _is_valid_image(data) is True

    def test_invalid_format(self):
        data = b"not an image"
        assert _is_valid_image(data) is False

    def test_empty_data(self):
        assert _is_valid_image(b"") is False

    def test_gif_not_supported(self):
        gif_header = b"GIF89a"
        assert _is_valid_image(gif_header) is False


class TestValidateImage:
    """Tests for image validation function."""

    def test_valid_small_png(self):
        data = PNG_HEADER + b"\x00" * 100
        validate_image(data, "test.png")  # Should not raise

    def test_valid_small_jpeg(self):
        data = JPEG_HEADER + b"\x00" * 100
        validate_image(data, "test.jpg")  # Should not raise

    def test_too_large_raises_error(self):
        data = PNG_HEADER + (b"\x00" * (MAX_IMAGE_SIZE_BYTES + 1))
        with pytest.raises(ValidationError, match="exceeds"):
            validate_image(data, "huge.png")

    def test_invalid_format_raises_error(self):
        data = b"not an image at all"
        with pytest.raises(ValidationError, match="not a valid PNG or JPEG"):
            validate_image(data, "fake.png")

    def test_error_includes_filename(self):
        data = b"not an image"
        with pytest.raises(ValidationError, match="myfile.png"):
            validate_image(data, "myfile.png")


class TestReadAndValidateImages:
    """Tests for file reading and validation."""

    def test_empty_list(self):
        result = read_and_validate_images([])
        assert result == []

    def test_too_many_files(self):
        mock_files = [MagicMock() for _ in range(MAX_IMAGES + 1)]
        with pytest.raises(ValidationError, match=f"Maximum {MAX_IMAGES}"):
            read_and_validate_images(mock_files)

    def test_valid_files(self):
        mock_file = MagicMock()
        mock_file.read.return_value = PNG_HEADER + b"\x00" * 100
        mock_file.name = "test.png"

        result = read_and_validate_images([mock_file])
        assert len(result) == 1
        assert result[0].startswith(PNG_HEADER)

    def test_read_failure_raises_error(self):
        mock_file = MagicMock()
        mock_file.read.side_effect = IOError("Read failed")
        mock_file.name = "broken.png"

        with pytest.raises(ValidationError, match="Could not read"):
            read_and_validate_images([mock_file])

    def test_invalid_content_raises_error(self):
        mock_file = MagicMock()
        mock_file.read.return_value = b"not an image"
        mock_file.name = "fake.png"

        with pytest.raises(ValidationError, match="not a valid PNG or JPEG"):
            read_and_validate_images([mock_file])
