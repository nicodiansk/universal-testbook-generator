# ABOUTME: Input validation utilities for the testbook generator.
# ABOUTME: Handles image validation, size limits, and content verification.

import logging

# Image validation constants
MAX_IMAGE_SIZE_MB = 10
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
MAX_IMAGES = 5

# Text input limits (characters)
MAX_USER_STORY_CHARS = 50000
MAX_GLOSSARY_CHARS = 20000
MAX_INSTRUCTIONS_CHARS = 5000

# Magic bytes for supported image formats
IMAGE_SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpeg",
}

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


def validate_image(data: bytes, filename: str) -> None:
    """Validate image data for size and content type."""
    if len(data) > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(
            f"Image '{filename}' exceeds {MAX_IMAGE_SIZE_MB}MB limit"
        )

    if not _is_valid_image(data):
        raise ValidationError(
            f"Image '{filename}' is not a valid PNG or JPEG file"
        )


def _is_valid_image(data: bytes) -> bool:
    """Check if data starts with valid image magic bytes."""
    for signature in IMAGE_SIGNATURES:
        if data.startswith(signature):
            return True
    return False


def read_and_validate_images(uploaded_files: list) -> list[bytes]:
    """Read uploaded files with validation and error handling."""
    if len(uploaded_files) > MAX_IMAGES:
        raise ValidationError(f"Maximum {MAX_IMAGES} images allowed")

    validated = []
    for f in uploaded_files:
        try:
            data = f.read()
        except Exception as e:
            logger.warning(f"Failed to read file {f.name}: {e}")
            raise ValidationError(f"Could not read file '{f.name}'")

        validate_image(data, f.name)
        validated.append(data)

    return validated
