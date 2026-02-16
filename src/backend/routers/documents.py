"""
FaxTriage AI — Documents Router

CRUD endpoints for document management.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from .. import database as db
from ..models import DocumentResponse, DocumentListResponse, DocumentUpdate
from ..services.document_service import update_document, get_document_file_path
from ..prompts.classification import VALID_DOCUMENT_TYPES

# Valid statuses for PATCH endpoint
VALID_STATUSES = {'classified', 'reviewed', 'dismissed', 'flagged'}

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _strip_file_path(doc: dict) -> dict:
    """Remove file_path from document dict to prevent leaking internal paths."""
    return {k: v for k, v in doc.items() if k != 'file_path'}


@router.get("", response_model=DocumentListResponse)
def list_documents(
    status: Optional[str] = Query(None, description="Filter by status"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    sort_by: str = Query("upload_time", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    limit: int = Query(50, ge=1, le=200, description="Results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """List documents with optional filtering and pagination."""
    documents, total = db.list_documents(
        status=status,
        document_type=document_type,
        priority=priority,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )

    return DocumentListResponse(
        documents=[DocumentResponse(**_strip_file_path(doc)) for doc in documents],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int):
    """Get a single document by ID."""
    doc = db.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(**_strip_file_path(doc))


@router.patch("/{doc_id}", response_model=DocumentResponse)
def patch_document(doc_id: int, update: DocumentUpdate):
    """
    Update document fields.

    Allowed updates:
    - status: Change document status
    - document_type: Reassign document type
    - notes: Add/update notes
    - reviewed_by: Mark as reviewed by user
    """
    # Validate status if provided
    if update.status is not None and update.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status '{update.status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
        )

    # Validate document_type if provided
    if update.document_type is not None and update.document_type not in VALID_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid document_type '{update.document_type}'. Must be one of: {', '.join(sorted(VALID_DOCUMENT_TYPES))}"
        )

    updated = update_document(
        doc_id=doc_id,
        status=update.status,
        document_type=update.document_type,
        notes=update.notes,
        reviewed_by=update.reviewed_by
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(**_strip_file_path(updated))


@router.get("/{doc_id}/pdf")
def get_document_pdf(doc_id: int):
    """Serve the original PDF file for the frontend viewer."""
    file_path = get_document_file_path(doc_id)

    if not file_path:
        raise HTTPException(status_code=404, detail="Document or file not found")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"}
    )