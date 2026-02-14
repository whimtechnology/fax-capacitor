# Backend — FaxTriage AI

API server and classification pipeline.

**Tech:** Python FastAPI or Node.js/Express (to be decided in Phase 2)

## Setup (Phase 2)

```bash
# TBD — will be populated during backend build phase
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/documents/upload | Upload PDFs for classification |
| GET | /api/documents | List documents (filterable) |
| GET | /api/documents/:id | Document details |
| PATCH | /api/documents/:id | Update status/type/notes |
| GET | /api/documents/:id/pdf | Serve original PDF |
| GET | /api/stats/summary | Dashboard stats |
