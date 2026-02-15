"""
FaxTriage AI — Upload Router

Handles PDF file uploads and processing.
"""
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException

from ..models import DocumentResponse, BatchUploadResponse
from ..services.document_service import upload_and_process, DocumentProcessingError

router = APIRouter(prefix="/api/documents", tags=["upload"])


@router.post("/upload", response_model=BatchUploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload one or more PDF files for classification.

    Accepts multipart form data with one or more PDF files.
    Each file is validated, saved, and processed through the
    classification pipeline synchronously.

    Returns array of created document records plus any errors.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    documents = []
    errors = []

    for file in files:
        try:
            # Read file content
            content = await file.read()

            # Process the document
            doc = upload_and_process(file.filename, content)
            documents.append(DocumentResponse(**doc))

        except DocumentProcessingError as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": f"Unexpected error: {str(e)}"
            })

    return BatchUploadResponse(
        uploaded=len(documents),
        failed=len(errors),
        documents=documents,
        errors=errors
    )
