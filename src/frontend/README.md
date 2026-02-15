# Frontend — FaxTriage AI (Fax Capacitor)

React dashboard for fax triage queue.

**Tech:** Vite + React + Tailwind CSS

## Setup

```bash
npm install
npm run dev
```

The dev server runs at `http://localhost:5173` with API proxy to `http://localhost:8000`.

## Build

```bash
npm run build
```

Output is in `dist/` folder, ready for static serving.

## Architecture

```
src/
├── App.jsx                  # Main layout, data fetching, state management
├── main.jsx                 # Entry point
├── index.css                # Tailwind imports + custom styles
├── api.js                   # API client (fetch wrapper)
├── constants.js             # Colors, labels, config maps
└── components/
    ├── Header.jsx           # App header with logo + practice name + date
    ├── StatsBar.jsx         # Clickable stat cards row
    ├── FilterBar.jsx        # Type filter, status filter, clear button, count
    ├── DocumentQueue.jsx    # Main table with sortable columns
    ├── DocumentRow.jsx      # Single table row
    ├── DocumentDetail.jsx   # Right side detail panel
    ├── PriorityDot.jsx      # Colored dot with hover tooltip
    ├── ConfidenceBadge.jsx  # Percentage badge with color coding
    ├── FlagBadge.jsx        # Flag indicator badge
    ├── ActionButtons.jsx    # Reviewed / Flag / Dismiss buttons
    ├── Tooltip.jsx          # Reusable tooltip component
    ├── UploadZone.jsx       # Drag-and-drop PDF upload area
    └── PdfViewer.jsx        # Embedded PDF viewer (iframe)
```

## Features

- **Queue View** — Priority-sorted list of classified faxes, color-coded by type
- **Document Detail** — Side panel with extracted metadata + embedded PDF viewer
- **Upload** — Drag-and-drop PDF upload with processing status
- **Stats Bar** — Clickable cards for quick filtering (Urgent, Flagged, etc.)
- **Filtering** — By document type and status
- **Sorting** — Click column headers to sort

## API Endpoints Used

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/documents/upload | Upload PDFs for classification |
| GET | /api/documents | List documents with filters |
| GET | /api/documents/{id} | Get single document |
| PATCH | /api/documents/{id} | Update document status |
| GET | /api/documents/{id}/pdf | Serve original PDF |
| GET | /api/stats/summary | Dashboard statistics |
