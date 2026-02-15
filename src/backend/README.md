# Backend — FaxTriage AI

FastAPI server with Claude Vision API classification pipeline.

## Setup

```bash
# From project root
cd fax-capacitor

# Install dependencies
pip install -r requirements.txt

# Set API key (one of these methods)
# Option 1: Environment variable
export ANTHROPIC_API_KEY=sk-ant-...

# Option 2: .env file in project root
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Run the server
python -m uvicorn src.backend.main:app --reload --port 8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Health check |
| POST | /api/documents/upload | Upload PDFs for classification |
| GET | /api/documents | List documents (filterable) |
| GET | /api/documents/{id} | Document details |
| PATCH | /api/documents/{id} | Update status/type/notes |
| GET | /api/documents/{id}/pdf | Serve original PDF |
| GET | /api/stats/summary | Dashboard stats |

## Query Parameters for GET /api/documents

- `status`: Filter by status (pending, processing, classified, reviewed, dismissed, error)
- `document_type`: Filter by type (lab_result, referral_response, etc.)
- `priority`: Filter by priority (critical, high, medium, low, none)
- `sort_by`: Sort field (upload_time, document_type, priority, status, confidence, filename)
- `sort_order`: Sort order (asc, desc)
- `limit`: Results per page (1-200, default 50)
- `offset`: Pagination offset

## Testing

```bash
# Upload a test PDF
curl -X POST http://localhost:8000/api/documents/upload \
  -F "files=@data/synthetic-faxes/01_lab_result_cbc.pdf"

# List all documents
curl http://localhost:8000/api/documents

# Get stats
curl http://localhost:8000/api/stats/summary
```

## Project Structure

```
src/backend/
├── main.py              # FastAPI app entry point
├── config.py            # Settings, API keys, paths
├── models.py            # Pydantic request/response schemas
├── database.py          # SQLite connection and operations
├── routers/
│   ├── documents.py     # Document CRUD endpoints
│   ├── upload.py        # Upload and processing endpoint
│   └── stats.py         # Dashboard statistics endpoint
├── services/
│   ├── pdf_processor.py # PDF-to-image conversion
│   ├── classifier.py    # Claude API classification
│   └── document_service.py  # Business logic layer
└── prompts/
    └── classification.py    # System prompt constant
```
