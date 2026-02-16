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

router = APIRouter(prefix="/api/documents", tags=["documents"])


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
        documents=[DocumentResponse(**doc) for doc in documents],
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
    return DocumentResponse(**doc)


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
    updated = update_document(
        doc_id=doc_id,
        status=update.status,
        document_type=update.document_type,
        notes=update.notes,
        reviewed_by=update.reviewed_by
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(**updated)


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