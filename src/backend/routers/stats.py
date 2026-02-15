"""
FaxTriage AI — Statistics Router

Dashboard statistics endpoint.
"""
from fastapi import APIRouter

from .. import database as db
from ..models import StatsSummary

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
def get_stats_summary():
    """
    Get dashboard statistics summary.

    Returns:
    - total_documents: Total number of documents
    - counts_by_type: Document counts grouped by type
    - counts_by_priority: Document counts grouped by priority
    - counts_by_status: Document counts grouped by status
    - documents_today: Documents uploaded today
    - avg_confidence: Average classification confidence
    - avg_processing_time_ms: Average processing time in milliseconds
    """
    stats = db.get_stats()
    return StatsSummary(**stats)
