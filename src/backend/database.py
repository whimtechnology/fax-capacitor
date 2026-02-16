"""
FaxTriage AI — Database Setup and Connection

SQLite database with documents and processing_log tables.
"""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional

from .config import settings


# SQL Schema
SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    page_count INTEGER,
    status TEXT DEFAULT 'pending',
    document_type TEXT,
    confidence REAL,
    priority TEXT,
    extracted_fields JSON,
    flags JSON,
    processing_time_ms INTEGER,
    notes TEXT,
    reviewed_by TEXT,
    reviewed_at DATETIME
);

CREATE TABLE IF NOT EXISTS processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER REFERENCES documents(id),
    event_type TEXT,
    event_data JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_priority ON documents(priority);
CREATE INDEX IF NOT EXISTS idx_documents_upload_time ON documents(upload_time);
CREATE INDEX IF NOT EXISTS idx_processing_log_document_id ON processing_log(document_id);
"""


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    """Convert SQLite row to dictionary."""
    fields = [column[0] for column in cursor.description]
    return dict(zip(fields, row))


def init_database():
    """Initialize the database with schema."""
    settings.ensure_directories()
    conn = sqlite3.connect(settings.database_path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Get a database connection with dict row factory."""
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = dict_factory
    try:
        yield conn
    finally:
        conn.close()


# --- Document Operations ---

def create_document(filename: str, file_path: str, page_count: Optional[int] = None) -> int:
    """Create a new document record. Returns the document ID."""
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO documents (filename, file_path, page_count, status)
               VALUES (?, ?, ?, 'pending')""",
            (filename, file_path, page_count)
        )
        conn.commit()
        return cursor.lastrowid


def update_document_status(doc_id: int, status: str):
    """Update document status."""
    with get_db() as conn:
        conn.execute(
            "UPDATE documents SET status = ? WHERE id = ?",
            (status, doc_id)
        )
        conn.commit()


def update_document_classification(
    doc_id: int,
    document_type: str,
    confidence: float,
    priority: str,
    extracted_fields: dict,
    flags: list,
    processing_time_ms: int
):
    """Update document with classification results."""
    with get_db() as conn:
        conn.execute(
            """UPDATE documents SET
               status = 'classified',
               document_type = ?,
               confidence = ?,
               priority = ?,
               extracted_fields = ?,
               flags = ?,
               processing_time_ms = ?
               WHERE id = ?""",
            (
                document_type,
                confidence,
                priority,
                json.dumps(extracted_fields),
                json.dumps(flags),
                processing_time_ms,
                doc_id
            )
        )
        conn.commit()


def update_document_error(doc_id: int, error_message: str):
    """Mark document as errored."""
    with get_db() as conn:
        conn.execute(
            """UPDATE documents SET
               status = 'error',
               notes = ?
               WHERE id = ?""",
            (error_message, doc_id)
        )
        conn.commit()


def update_document(doc_id: int, **fields) -> Optional[dict]:
    """Update document fields. Returns updated document or None."""
    allowed_fields = {'status', 'document_type', 'notes', 'reviewed_by'}
    update_fields = {k: v for k, v in fields.items() if k in allowed_fields and v is not None}

    if not update_fields:
        return get_document(doc_id)

    # Auto-set reviewed_at timestamp when:
    # 1. reviewed_by is being set, OR
    # 2. status is being changed to 'reviewed'
    if 'reviewed_by' in update_fields or update_fields.get('status') == 'reviewed':
        update_fields['reviewed_at'] = datetime.utcnow().isoformat()

    set_clause = ", ".join(f"{k} = ?" for k in update_fields.keys())
    values = list(update_fields.values()) + [doc_id]

    with get_db() as conn:
        conn.execute(
            f"UPDATE documents SET {set_clause} WHERE id = ?",
            values
        )
        conn.commit()

    return get_document(doc_id)


def get_document(doc_id: int) -> Optional[dict]:
    """Get a single document by ID."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?",
            (doc_id,)
        ).fetchone()

    if row:
        # Parse JSON fields
        if row.get('extracted_fields'):
            row['extracted_fields'] = json.loads(row['extracted_fields'])
        if row.get('flags'):
            row['flags'] = json.loads(row['flags'])
    return row


def list_documents(
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by: str = "upload_time",
    sort_order: str = "desc",
    limit: int = 50,
    offset: int = 0
) -> tuple[list[dict], int]:
    """
    List documents with filters. Returns (documents, total_count).

    Args:
        status: Filter by status (single value)
        document_type: Filter by document type (single value)
        priority: Filter by priority (supports comma-separated values, e.g., "high,critical")
        sort_by: Field to sort by
        sort_order: Sort order ("asc" or "desc")
        limit: Maximum number of results
        offset: Offset for pagination
    """
    conditions = []
    params = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if document_type:
        conditions.append("document_type = ?")
        params.append(document_type)
    if priority:
        # Support comma-separated priority values (e.g., "high,critical")
        priority_values = [p.strip() for p in priority.split(',') if p.strip()]
        if len(priority_values) == 1:
            conditions.append("priority = ?")
            params.append(priority_values[0])
        elif priority_values:
            placeholders = ','.join('?' * len(priority_values))
            conditions.append(f"priority IN ({placeholders})")
            params.extend(priority_values)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    # Validate sort fields to prevent SQL injection
    allowed_sort_fields = {'upload_time', 'document_type', 'priority', 'status', 'confidence', 'filename'}
    if sort_by not in allowed_sort_fields:
        sort_by = 'upload_time'
    sort_order = 'DESC' if sort_order.lower() == 'desc' else 'ASC'

    with get_db() as conn:
        # Get total count
        count_row = conn.execute(
            f"SELECT COUNT(*) as count FROM documents{where_clause}",
            params
        ).fetchone()
        total = count_row['count']

        # Get paginated results
        rows = conn.execute(
            f"""SELECT * FROM documents{where_clause}
                ORDER BY {sort_by} {sort_order}
                LIMIT ? OFFSET ?""",
            params + [limit, offset]
        ).fetchall()

    # Parse JSON fields
    for row in rows:
        if row.get('extracted_fields'):
            row['extracted_fields'] = json.loads(row['extracted_fields'])
        if row.get('flags'):
            row['flags'] = json.loads(row['flags'])

    return rows, total


# --- Processing Log Operations ---

def log_event(document_id: int, event_type: str, event_data: Optional[dict] = None):
    """Log a processing event."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO processing_log (document_id, event_type, event_data)
               VALUES (?, ?, ?)""",
            (document_id, event_type, json.dumps(event_data) if event_data else None)
        )
        conn.commit()


def get_document_logs(document_id: int) -> list[dict]:
    """Get processing logs for a document."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM processing_log
               WHERE document_id = ?
               ORDER BY timestamp ASC""",
            (document_id,)
        ).fetchall()

    for row in rows:
        if row.get('event_data'):
            row['event_data'] = json.loads(row['event_data'])
    return rows


# --- Statistics ---

def get_stats() -> dict:
    """Get dashboard statistics."""
    with get_db() as conn:
        # Total documents
        total = conn.execute("SELECT COUNT(*) as count FROM documents").fetchone()['count']

        # Counts by type
        type_rows = conn.execute(
            """SELECT document_type, COUNT(*) as count FROM documents
               WHERE document_type IS NOT NULL
               GROUP BY document_type"""
        ).fetchall()
        counts_by_type = {row['document_type']: row['count'] for row in type_rows}

        # Counts by priority
        priority_rows = conn.execute(
            """SELECT priority, COUNT(*) as count FROM documents
               WHERE priority IS NOT NULL
               GROUP BY priority"""
        ).fetchall()
        counts_by_priority = {row['priority']: row['count'] for row in priority_rows}

        # Counts by status
        status_rows = conn.execute(
            """SELECT status, COUNT(*) as count FROM documents
               GROUP BY status"""
        ).fetchall()
        counts_by_status = {row['status']: row['count'] for row in status_rows}

        # Documents today
        today_count = conn.execute(
            """SELECT COUNT(*) as count FROM documents
               WHERE date(upload_time) = date('now')"""
        ).fetchone()['count']

        # Average confidence
        avg_conf = conn.execute(
            """SELECT AVG(confidence) as avg FROM documents
               WHERE confidence IS NOT NULL"""
        ).fetchone()['avg']

        # Average processing time
        avg_time = conn.execute(
            """SELECT AVG(processing_time_ms) as avg FROM documents
               WHERE processing_time_ms IS NOT NULL"""
        ).fetchone()['avg']

        # Count of flagged documents (where flags is non-empty JSON array)
        flagged_count = conn.execute(
            """SELECT COUNT(*) as count FROM documents
               WHERE flags IS NOT NULL AND flags != '[]' AND flags != 'null'"""
        ).fetchone()['count']

    return {
        'total_documents': total,
        'counts_by_type': counts_by_type,
        'counts_by_priority': counts_by_priority,
        'counts_by_status': counts_by_status,
        'documents_today': today_count,
        'flagged_count': flagged_count,
        'avg_confidence': round(avg_conf, 3) if avg_conf else None,
        'avg_processing_time_ms': round(avg_time, 1) if avg_time else None,
    }
