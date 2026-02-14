# Technical Architecture

## System Overview

FaxTriage AI follows a three-stage pipeline architecture: **Ingestion → Processing → Presentation**. Each stage is independently testable with clear input/output contracts.

The MVP is an **intelligent document processing pipeline** — not an agent. The AI makes sophisticated decisions (classification, extraction, priority assignment) but the flow is linear and predetermined. Agentic capabilities (automated follow-up, pattern detection) are designed into the architecture for Phase 2.

---

## Pipeline Stages

### Stage 1: Document Ingestion

| Component | Details |
|-----------|---------|
| Input Sources | Manual PDF upload via web interface (MVP); watched email inbox (Phase 2) |
| Supported Formats | PDF (primary), TIFF (secondary — converted to PDF on ingestion) |
| Pre-processing | Page count detection, image quality assessment, multi-page grouping |
| Output | Normalized page images ready for Claude Vision API |

**Processing flow:**
```
PDF Upload → Validate file type/size → Extract pages as images → 
Quality check → Queue for classification
```

### Stage 2: AI Classification & Extraction

| Component | Details |
|-----------|---------|
| AI Model | Claude Sonnet (Anthropic API) — Vision + Text |
| Classification | 8-type taxonomy (see CLASSIFICATION_TAXONOMY.md) |
| Extraction | Patient name, DOB, sending provider, document date, fax origin, urgency flags |
| Confidence | Score returned per classification; low-confidence items flagged for review |
| Output | Structured JSON per document |

**Output schema:**
```json
{
  "document_type": "lab_result",
  "confidence": 0.94,
  "priority": "high",
  "extracted_fields": {
    "patient_name": "Jane Doe",
    "patient_dob": "1980-01-15",
    "sending_provider": "Quest Diagnostics",
    "document_date": "2026-02-10",
    "fax_origin": "555-0123",
    "urgency_indicators": ["critical value", "STAT"]
  },
  "flags": [],
  "page_count": 2,
  "processing_time_ms": 1240
}
```

### Stage 3: Dashboard & Presentation

| Component | Details |
|-----------|---------|
| Interface | React web app — desktop-first for front desk workstations |
| Primary View | Priority queue: color-coded by urgency, grouped by type, sortable/filterable |
| Document Detail | Side panel: extracted metadata, confidence score, embedded PDF viewer |
| Actions | Mark reviewed, reassign type, flag for follow-up, dismiss, add notes |
| Summary | Daily dashboard: counts by type, items pending, accuracy metrics |

---

## Data Model (SQLite MVP)

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    page_count INTEGER,
    status TEXT DEFAULT 'pending', -- pending, processing, classified, reviewed, dismissed
    document_type TEXT,
    confidence REAL,
    priority TEXT, -- critical, high, medium, low, none
    extracted_fields JSON,
    flags JSON,
    processing_time_ms INTEGER,
    notes TEXT,
    reviewed_by TEXT,
    reviewed_at DATETIME
);

CREATE TABLE processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER REFERENCES documents(id),
    event_type TEXT, -- upload, classify, review, reassign, dismiss, flag
    event_data JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/documents/upload | Upload one or more PDFs for classification |
| GET | /api/documents | List documents (with filter/sort params) |
| GET | /api/documents/:id | Get document details + extracted fields |
| PATCH | /api/documents/:id | Update status, type, notes, flags |
| GET | /api/documents/:id/pdf | Serve original PDF for viewer |
| GET | /api/stats/summary | Dashboard summary statistics |

---

## Phase 2: Agentic Evolution

The architecture supports future agentic capabilities without redesign:

**Automated Missing Data Detection:**
- System tracks extracted fields per sending provider over time
- When a provider consistently omits a key field (e.g., insurance info on referrals), the system flags the pattern
- Phase 2a: Alert office staff to the pattern
- Phase 2b: Generate and queue a standardized follow-up fax requesting the missing information
- This is where the system transitions from pipeline (fixed flow) to agent (observes, decides, acts)

**Email Inbox Integration:**
- IMAP/POP3 listener for cloud fax email delivery
- Auto-ingestion of PDF attachments matching fax patterns
- Configurable filtering rules

**Routing Rules Engine:**
- Lab results → Nursing queue
- Prior auth → Billing queue  
- Referrals → Scheduling queue
- Notification triggers (email, SMS) for high-priority items
