"""
FaxTriage AI — Classification Service

Sends document images to Claude Vision API for classification.
Ported from scripts/test_classification.py
"""
import json
import time
from typing import Optional

import anthropic

from ..config import settings
from ..prompts.classification import (
    CLASSIFICATION_PROMPT,
    VALID_DOCUMENT_TYPES,
    VALID_PRIORITIES
)


class ClassificationError(Exception):
    """Error during document classification."""
    pass


class ClassificationResult:
    """Result of document classification."""

    def __init__(self, data: dict, processing_time_ms: int, token_usage: dict):
        self.document_type: str = data.get('document_type', 'other')
        self.confidence: float = data.get('confidence', 0.0)
        self.priority: str = data.get('priority', 'low')
        self.extracted_fields: dict = data.get('extracted_fields', {})
        self.flags: list = data.get('flags', [])
        self.page_count_processed: int = data.get('page_count_processed', 0)
        self.page_quality: str = data.get('page_quality', 'unknown')
        self.is_continuation: bool = data.get('is_continuation', False)
        self.processing_time_ms: int = processing_time_ms
        self.token_usage: dict = token_usage
        self._raw: dict = data

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            'document_type': self.document_type,
            'confidence': self.confidence,
            'priority': self.priority,
            'extracted_fields': self.extracted_fields,
            'flags': self.flags,
            'processing_time_ms': self.processing_time_ms,
        }


def validate_classification(result: dict) -> list[str]:
    """Validate classification response structure. Returns list of errors."""
    errors = []

    required_fields = ["document_type", "confidence", "priority", "extracted_fields"]
    for field in required_fields:
        if field not in result:
            errors.append(f"Missing required field: {field}")

    if result.get("document_type") not in VALID_DOCUMENT_TYPES:
        errors.append(f"Invalid document_type: {result.get('document_type')}")

    if result.get("priority") not in VALID_PRIORITIES:
        errors.append(f"Invalid priority: {result.get('priority')}")

    confidence = result.get("confidence", -1)
    if not (0.0 <= confidence <= 1.0):
        errors.append(f"Confidence out of range: {confidence}")

    return errors


def classify_document(
    images: list[str],
    page_count: int,
    retry_on_failure: bool = True
) -> ClassificationResult:
    """
    Send document images to Claude Vision API for classification.

    Args:
        images: List of base64-encoded PNG image strings
        page_count: Total number of pages in the document
        retry_on_failure: If True, retry once on API error

    Returns:
        ClassificationResult with parsed classification data

    Raises:
        ClassificationError: If classification fails after retries
    """
    if not settings.anthropic_api_key:
        raise ClassificationError("ANTHROPIC_API_KEY not configured")

    client = anthropic.Anthropic()

    # Build content with all images
    content = []
    for img in images:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": img
            }
        })

    # Add instruction text
    pages_note = (
        f"(showing {len(images)} of {page_count} pages)"
        if len(images) < page_count
        else f"({len(images)} pages)"
    )
    content.append({
        "type": "text",
        "text": f"Classify this fax document {pages_note}."
    })

    # Call the API with retry logic
    last_error: Optional[Exception] = None
    attempts = 2 if retry_on_failure else 1

    for attempt in range(attempts):
        try:
            start_time = time.time()

            response = client.messages.create(
                model=settings.claude_model,
                max_tokens=1024,
                temperature=0,
                system=CLASSIFICATION_PROMPT,
                messages=[{"role": "user", "content": content}]
            )

            elapsed_ms = int((time.time() - start_time) * 1000)

            # Parse the JSON response
            response_text = response.content[0].text.strip()

            # Handle potential markdown code fences
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            result = json.loads(response_text)

            # Validate response structure
            errors = validate_classification(result)
            if errors:
                raise ClassificationError(f"Invalid response: {', '.join(errors)}")

            # Build token usage dict
            token_usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

            return ClassificationResult(result, elapsed_ms, token_usage)

        except json.JSONDecodeError as e:
            last_error = ClassificationError(f"Failed to parse JSON response: {e}")
        except anthropic.APIError as e:
            last_error = ClassificationError(f"API error: {e}")
        except Exception as e:
            last_error = ClassificationError(f"Unexpected error: {e}")

        # If we get here and have more attempts, we'll retry
        if attempt < attempts - 1:
            time.sleep(1)  # Brief pause before retry

    # All attempts failed
    raise last_error
