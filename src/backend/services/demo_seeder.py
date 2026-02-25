"""
FaxTriage AI — Demo Data Seeder

Auto-seed demo data when database is empty.
Runs on startup to ensure visitors always see a populated dashboard.
"""
import logging
from pathlib import Path

from ..config import settings
from .. import database as db
from .document_service import upload_and_process

logger = logging.getLogger(__name__)

# Path to synthetic faxes (relative to project root)
DEMO_FAXES_DIR = Path(__file__).parent.parent.parent.parent / "data" / "synthetic-faxes"


def seed_demo_data() -> int:
    """
    Seed database with demo faxes if empty.

    Returns number of documents seeded (0 if DB was not empty).
    """
    # Check if DB already has documents
    stats = db.get_stats()
    if stats['total_documents'] > 0:
        logger.info(f"Database has {stats['total_documents']} documents, skipping demo seed")
        return 0

    # Find demo PDFs
    if not DEMO_FAXES_DIR.exists():
        logger.warning(f"Demo faxes directory not found: {DEMO_FAXES_DIR}")
        return 0

    pdf_files = sorted(DEMO_FAXES_DIR.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in demo faxes directory")
        return 0

    logger.info(f"Auto-seeding {len(pdf_files)} demo documents...")

    success_count = 0
    for i, pdf_path in enumerate(pdf_files, 1):
        try:
            logger.info(f"  [{i}/{len(pdf_files)}] Processing: {pdf_path.name}")
            with open(pdf_path, "rb") as f:
                content = f.read()
            upload_and_process(pdf_path.name, content)
            success_count += 1
        except Exception as e:
            logger.error(f"  Failed to seed {pdf_path.name}: {e}")
            # Continue with other files

    logger.info(f"Demo seeding complete: {success_count}/{len(pdf_files)} documents loaded")
    return success_count
