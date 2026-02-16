"""
FaxTriage AI — Document Service

Business logic layer for document operations.
"""
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import settings
from .. import database as db
from .pdf_processor import pdf_to_base64_images, get_page_count, PDFProcessingError
from .classifier import classify_document, ClassificationError


class DocumentProcessingError(Exception):
    """Error during document processing."""
    pass


def save_uploaded_file(filename: str, file_content: bytes) -> tuple[str, Path]:
    """
    Save uploaded file to the uploads directory.

    Returns:
        Tuple of (stored filename, full path)
    """
    settings.ensure_directories()

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    stored_filename = f"{timestamp}_{safe_filename}"
    file_path = settings.upload_dir / stored_filename

    # Write file
    with open(file_path, "wb") as f:
        f.write(file_content)

    return stored_filename, file_path


def validate_pdf(filename: str, file_content: bytes) -> list[str]:
    """
    Validate uploaded file.

    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Check extension
    if not filename.lower().endswith('.pdf'):
        errors.append("File must be a PDF")

    # Check file size
    max_size = settings.max_file_size_mb * 1024 * 1024
    if len(file_content) > max_size:
        errors.append(f"File exceeds maximum size of {settings.max_file_size_mb}MB")

    # Check PDF magic bytes
    if not file_content.startswith(b'%PDF'):
        errors.append("File does not appear to be a valid PDF")

    return errors


def process_document(doc_id: int, file_path: Path) -> dict:
    """
    Process a document through the classification pipeline.

    Args:
        doc_id: Database document ID
        file_path: Path to the PDF file

    Returns:
        Classification result dict

    Raises:
        DocumentProcessingError: If processing fails
    """
    try:
        # Update status to processing
        db.update_document_status(doc_id, 'processing')
        db.log_event(doc_id, 'processing_start')

        # Convert PDF to images
        images, page_count = pdf_to_base64_images(str(file_path))

        if not images:
            raise DocumentProcessingError("Failed to extract images from PDF")

        # Classify the document
        result = classify_document(images, page_count)

        # Update database with results
        db.update_document_classification(
            doc_id=doc_id,
            document_type=result.document_type,
            confidence=result.confidence,
            priority=result.priority,
            extracted_fields=result.extracted_fields,
            flags=result.flags,
            processing_time_ms=result.processing_time_ms
        )

        # Log the classification event
        db.log_event(doc_id, 'classify', {
            'document_type': result.document_type,
            'confidence': result.confidence,
            'priority': result.priority,
            'token_usage': result.token_usage,
        })

        return result.to_dict()

    except PDFProcessingError as e:
        # Graceful degradation — document MUST appear in the queue
        db.update_document_classification(
            doc_id=doc_id,
            document_type="other",
            confidence=0.0,
            priority="high",
            extracted_fields={"key_details": f"PDF processing failed: {e}"},
            flags=["pdf_processing_failed"],
            processing_time_ms=0
        )
        db.log_event(doc_id, 'error', {'error': str(e), 'type': 'pdf_processing'})
        return db.get_document(doc_id)

    except ClassificationError as e:
        # Graceful degradation — document MUST appear in the queue
        db.update_document_classification(
            doc_id=doc_id,
            document_type="other",
            confidence=0.0,
            priority="high",
            extracted_fields={"key_details": f"Classification failed: {e}"},
            flags=["classification_failed"],
            processing_time_ms=0
        )
        db.log_event(doc_id, 'error', {'error': str(e), 'type': 'classification'})
        return db.get_document(doc_id)

    except Exception as e:
        # Graceful degradation — document MUST appear in the queue
        db.update_document_classification(
            doc_id=doc_id,
            document_type="other",
            confidence=0.0,
            priority="high",
            extracted_fields={"key_details": f"Processing failed: {e}"},
            flags=["processing_failed"],
            processing_time_ms=0
        )
        db.log_event(doc_id, 'error', {'error': str(e), 'type': 'unknown'})
        return db.get_document(doc_id)


def upload_and_process(filename: str, file_content: bytes) -> dict:
    """
    Complete upload and processing workflow.

    1. Validate the file
    2. Save to disk
    3. Create database record
    4. Process through classification pipeline
    5. Return complete document record

    Args:
        filename: Original filename
        file_content: File bytes

    Returns:
        Complete document record dict

    Raises:
        DocumentProcessingError: If any step fails
    """
    # Validate
    errors = validate_pdf(filename, file_content)
    if errors:
        raise DocumentProcessingError("; ".join(errors))

    # Save file
    stored_filename, file_path = save_uploaded_file(filename, file_content)

    # Get page count
    try:
        page_count = get_page_count(str(file_path))
    except Exception:
        page_count = None

    # Create database record
    doc_id = db.create_document(
        filename=filename,
        file_path=str(file_path),
        page_count=page_count
    )

    # Log upload event
    db.log_event(doc_id, 'upload', {
        'original_filename': filename,
        'stored_filename': stored_filename,
        'page_count': page_count,
    })

    # Process through classification (always succeeds — errors result in fallback values)
    process_document(doc_id, file_path)

    # Return the complete document record
    return db.get_document(doc_id)


def update_document(
    doc_id: int,
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    notes: Optional[str] = None,
    reviewed_by: Optional[str] = None
) -> Optional[dict]:
    """
    Update document fields and log the change.

    Returns updated document or None if not found.
    """
    # Get current state for logging
    current = db.get_document(doc_id)
    if not current:
        return None

    # Build change log
    changes = {}
    if status and status != current.get('status'):
        changes['status'] = {'from': current.get('status'), 'to': status}
    if document_type and document_type != current.get('document_type'):
        changes['document_type'] = {'from': current.get('document_type'), 'to': document_type}
    if notes is not None:
        changes['notes'] = {'updated': True}
    if reviewed_by:
        changes['reviewed_by'] = reviewed_by

    # Update document
    updated = db.update_document(
        doc_id,
        status=status,
        document_type=document_type,
        notes=notes,
        reviewed_by=reviewed_by
    )

    # Log changes
    if changes:
        event_type = 'reassign' if 'document_type' in changes else 'review'
        if status == 'dismissed':
            event_type = 'dismiss'
        db.log_event(doc_id, event_type, changes)

    return updated


def get_document_file_path(doc_id: int) -> Optional[Path]:
    """
    Get the file path for a document's PDF.

    Includes path traversal protection to ensure the file is within
    the uploads directory.
    """
    doc = db.get_document(doc_id)
    if not doc:
        return None

    file_path = Path(doc['file_path'])

    # Path traversal protection: resolve to absolute path and verify
    # it's within the uploads directory
    try:
        resolved_path = file_path.resolve()
        uploads_dir = settings.upload_dir.resolve()

        # Check that the resolved path is within the uploads directory
        if not str(resolved_path).startswith(str(uploads_dir)):
            return None
    except (OSError, ValueError):
        return None

    if not file_path.exists():
        return None

    return file_path
