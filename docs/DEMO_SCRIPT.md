# Demo Script (8-10 minutes)

This script is designed for a concise live walkthrough of the current prototype.

## Pre-demo setup (2-3 minutes)

1. Open terminal A (backend):

```powershell
cd E:\Claude-Workspace\fax-capacitor\fax-capacitor
pip install -r requirements.txt
$env:ANTHROPIC_API_KEY="<your-key>"
python -m uvicorn src.backend.main:app --reload --port 8000
```

Expected output (startup):
- `Uvicorn running on http://127.0.0.1:8000`
- `Application startup complete`

2. Open terminal B (frontend):

```powershell
cd E:\Claude-Workspace\fax-capacitor\fax-capacitor\src\frontend
npm install
npm run dev
```

Expected output:
- `Local: http://localhost:5173/`

3. Verify API health quickly:

```powershell
curl http://localhost:8000/api/health
```

Expected output:
```json
{"status":"healthy","service":"FaxTriage AI","version":"0.1.0"}
```

## Live demo flow (6-7 minutes)

### Step 1: Upload a small batch

Use either UI drag-and-drop or API command:

```powershell
cd E:\Claude-Workspace\fax-capacitor\fax-capacitor
curl -X POST http://localhost:8000/api/documents/upload \
  -F "files=@data/synthetic-faxes/01_lab_result_cbc.pdf" \
  -F "files=@data/synthetic-faxes/03_prior_auth_approved.pdf" \
  -F "files=@data/synthetic-faxes/08_junk_marketing_fax.pdf"
```

Expected output shape:
```json
{
  "uploaded": 3,
  "failed": 0,
  "documents": [{"id": 1, "status": "classified", "document_type": "...", "priority": "..."}],
  "errors": []
}
```

### Step 2: Show queue and prioritization

```powershell
curl "http://localhost:8000/api/documents?sort_by=upload_time&sort_order=desc&limit=10"
```

Expected output shape:
```json
{
  "documents": [
    {"id": 3, "filename": "08_junk_marketing_fax.pdf", "document_type": "marketing_junk", "priority": "none"},
    {"id": 2, "filename": "03_prior_auth_approved.pdf", "document_type": "prior_auth_decision", "priority": "high"}
  ],
  "total": 3,
  "limit": 10,
  "offset": 0
}
```

In UI (`http://localhost:5173`):
- Show the queue ordering
- Open one document and show extracted fields
- Show PDF preview panel

### Step 3: Show stats and workflow actions

```powershell
curl http://localhost:8000/api/stats/summary
```

Expected output shape:
```json
{
  "total_documents": 3,
  "counts_by_type": {"lab_result": 1},
  "counts_by_priority": {"high": 1, "none": 1},
  "counts_by_status": {"classified": 3},
  "documents_today": 3
}
```

Optional action update:

```powershell
curl -X PATCH http://localhost:8000/api/documents/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"reviewed","reviewed_by":"demo-user"}'
```

Expected output shape:
```json
{"id":1,"status":"reviewed","reviewed_by":"demo-user"}
```

## What to say (short narrative)

- "The problem is not fax receipt - it is triage speed and reliability after receipt."
- "This prototype keeps the existing workflow but inserts AI classification between intake and staff action."
- "The output is a prioritized queue with extracted metadata and confidence-informed review."
- "When confidence is low or rendering fails, the item stays visible for human handling rather than silent automation."

## Common demo pitfalls

- Missing `ANTHROPIC_API_KEY` causes uploads to fail classification.
- Running frontend without backend leads to empty/error API responses.
- Reusing stale browser tab can hide latest queue state; refresh before the live segment.
- Large PDFs can take longer; keep demo set to 2-5 synthetic files.
- On first run, dependency install time can consume demo time; pre-install before demo day.
