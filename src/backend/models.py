"""
FaxTriage AI — Pydantic Models

Defines request/response schemas for the API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Extracted Fields from Classification ---

class ExtractedFields(BaseModel):
    """Fields extracted from the document during classification."""
    patient_name: Optional[str] = None
    patient_dob: Optional[str] = None
    sending_provider: Optional[str] = None
    sending_facility: Optional[str] = None
    document_date: Optional[str] = None
    fax_origin_number: Optional[str] = None
    urgency_indicators: list[str] = Field(default_factory=list)
    key_details: Optional[str] = None


# --- Document Models ---

class DocumentBase(BaseModel):
    """Base document fields."""
    filename: str
    file_path: str


class DocumentCreate(DocumentBase):
    """Fields for creating a new document record."""
    page_count: Optional[int] = None


class DocumentClassification(BaseModel):
    """Classification result fields."""
    document_type: str
    confidence: float
    priority: str
    extracted_fields: ExtractedFields
    flags: list[str] = Field(default_factory=list)
    processing_time_ms: int


class DocumentUpdate(BaseModel):
    """Fields that can be updated via PATCH."""
    status: Optional[str] = None
    document_type: Optional[str] = None
    notes: Optional[str] = None
    reviewed_by: Optional[str] = None


class DocumentResponse(BaseModel):
    """Full document response model."""
    id: int
    filename: str
    file_path: str
    upload_time: datetime
    page_count: Optional[int] = None
    status: str
    document_type: Optional[str] = None
    confidence: Optional[float] = None
    priority: Optional[str] = None
    extracted_fields: Optional[dict] = None
    flags: Optional[list] = None
    processing_time_ms: Optional[int] = None
    notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Paginated document list response."""
    documents: list[DocumentResponse]
    total: int
    limit: int
    offset: int


# --- Processing Log Models ---

class ProcessingLogEntry(BaseModel):
    """A single processing log entry."""
    id: int
    document_id: int
    event_type: str
    event_data: Optional[dict] = None
    timestamp: datetime


# --- Stats Models ---

class StatsSummary(BaseModel):
    """Dashboard statistics summary."""
    total_documents: int
    counts_by_type: dict[str, int]
    counts_by_priority: dict[str, int]
    counts_by_status: dict[str, int]
    documents_today: int
    flagged_count: int = 0  # Documents with non-empty flags array
    avg_confidence: Optional[float]
    avg_processing_time_ms: Optional[float]


# --- Upload Response ---

class UploadResponse(BaseModel):
    """Response for single file upload."""
    success: bool
    document: Optional[DocumentResponse] = None
    error: Optional[str] = None


class BatchUploadResponse(BaseModel):
    """Response for batch upload."""
    uploaded: int
    failed: int
    documents: list[DocumentResponse]
    errors: list[dict]
