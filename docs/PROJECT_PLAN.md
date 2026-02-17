# FaxTriage AI — Project Plan

## Executive Summary

FaxTriage AI is a lightweight, AI-powered document classification and routing tool designed for small healthcare practices that receive high volumes of inbound faxes. Despite the digitization of healthcare, fax remains the dominant interoperability mechanism for small and mid-size practices across the United States.

This prototype demonstrates how Claude's vision and language capabilities can be applied to a constrained, real-world healthcare operations problem: transforming an unstructured pile of inbound fax PDFs into a prioritized, classified queue with extracted metadata — without requiring practices to adopt new systems, change workflows, or integrate with their EMR.

### Problem Statement

Small healthcare practices (1–10 providers) typically receive 30–80+ faxes per day. These include lab results, referral responses, prior authorization decisions, pharmacy requests, insurance correspondence, and unsolicited marketing. A single staff member — often the practice manager or front desk coordinator — must manually open each PDF, determine its type and urgency, identify the relevant patient, and route it to the appropriate person or workflow. This process consumes 1–2+ hours daily and introduces risk when urgent documents (critical lab values, time-sensitive prior auth denials) are buried in the queue.

### Proposed Solution

FaxTriage AI ingests fax PDFs (via watched email inbox, folder drop, or manual upload), applies Claude's Vision API to classify each document by type, extracts key metadata (patient name, sending provider, document date, urgency indicators), and presents results in a prioritized dashboard.

### Strategic Relevance

This project addresses a genuine operational pain point in healthcare delivery and demonstrates how modern AI capabilities can be applied to document processing workflows in highly constrained environments.

---

## Market Context

An estimated 75% of healthcare communication still occurs via fax. While large health systems have invested in enterprise fax management platforms (Solarity, OpenText, Kofax), small practices — which represent the majority of U.S. healthcare delivery points — are underserved by these solutions due to cost, implementation complexity, and IT resource requirements.

Cloud fax services (eFax, RingCentral, Ooma) have solved the digitization problem: most small practices now receive faxes as PDF files in an email inbox or web portal. However, the triage and routing step remains entirely manual. This is the gap FaxTriage AI targets.

**Target:** 1–10 provider practices, 30–80+ daily faxes, using cloud fax services, no dedicated IT staff.

**Why underserved:** Enterprise solutions require $50K+ investment, dedicated IT, and EMR integration — out of reach for small practices.

---

## MVP Scope

### In Scope (Weekend Build)

1. Synthetic fax test corpus (6–8 documents covering each taxonomy category)
2. Core classification pipeline: PDF → Claude Vision API → structured JSON
3. Web-based React dashboard with prioritized queue
4. Manual upload interface (drag-and-drop / file picker)
5. Optimized system prompts for classification accuracy
6. Workflow narrative for demo presentation

### Explicitly Out of Scope

- Email inbox monitoring or automated ingestion
- EMR integration of any kind
- HIPAA-compliant infrastructure (prototype uses synthetic data only)
- User authentication or multi-practice tenancy
- Auto-response fax capability (Phase 2)
- Production deployment or real patient data
- Mobile interface

### Phase 2 Vision (Discussion Material)

- **Automated follow-up:** System detects consistently missing data from specific senders and queues a follow-up fax. This is where the system transitions from pipeline to agent.
- **Email inbox integration:** Watched inbox auto-ingests new fax PDFs.
- **Analytics dashboard:** Trends, accuracy metrics, volume by type.
- **Staff workflow integration:** Routing rules with notification triggers.

---

## Build Sequence

### Phase 1: Technical Validation (2–3 hours)

**Goal:** Confirm Claude's Vision API can reliably classify and extract data from synthetic fax documents.

**Tasks:**
1. Create synthetic fax corpus (6–8 documents, varied quality)
2. Develop and test classification system prompt
3. Document accuracy per category, failure modes, confidence calibration
4. Test edge cases: multi-page, poor quality, ambiguous documents

**Go/No-Go:** Classification accuracy >80% across categories with consistent JSON output.

### Phase 2: Backend Pipeline (3–4 hours)

**Goal:** Build the complete ingestion-to-output pipeline as a working API.

**Tasks:**
1. API server setup (Node.js/Express or Python FastAPI)
2. PDF processing module (page extraction, image conversion)
3. Claude API integration with validated prompts
4. SQLite persistence (documents, extracted fields, processing log)
5. REST endpoints: GET /documents, GET /documents/:id, POST /documents/upload

### Phase 3: Frontend Dashboard (3–4 hours)

**Goal:** Build a clean dashboard a medical office worker would find intuitive.

**Tasks:**
1. Priority queue view (color-coded, sortable, filterable)
2. Document detail panel (metadata, PDF viewer, action buttons)
3. Upload interface (drag-and-drop with processing status)

### Phase 4: Demo Preparation (2–3 hours)

**Goal:** Polish prototype and prepare demonstration materials.

**Tasks:**
1. End-to-end flow verification with test corpus
2. Document known limitations honestly
3. Demo script: problem → live walkthrough → architecture → Phase 2 vision
4. Architecture diagram
5. Talking points for HIPAA, scaling, agentic evolution

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React + Tailwind CSS | Fast prototyping, responsive |
| Backend | Python FastAPI or Node.js/Express | Lightweight; Python preferred for PDF processing |
| AI Engine | Claude Sonnet — Vision API | Best-in-class document understanding |
| Storage | SQLite (MVP) → PostgreSQL | Zero-config; easy migration |
| PDF Processing | PyMuPDF / pdf2image | Page extraction, image conversion |
| Hosting | Local / Vercel / Railway | Simple demo deployment |

---

## Handoff Prompts

Copy-paste prompts for each build phase in a new Claude conversation:

### Step 1: Synthetic Fax Corpus
> "I'm building a prototype AI fax triage tool for small healthcare practices. I need to create 6–8 synthetic fax documents as test data. The document types are: lab result, referral response, prior authorization decision, pharmacy refill request, insurance correspondence, patient records request, and marketing/junk fax. Each should use clearly fictional patient data, vary in format quality, and be realistic enough to test an AI classification pipeline. Please help me design the content for each document type, then we'll generate them as PDFs."

### Step 2: Prompt Engineering
> "I'm building FaxTriage AI — an AI-powered fax classification tool for small healthcare practices. I have synthetic fax PDFs ready for testing. I need to develop a system prompt for Claude's Vision API that: (1) classifies each fax into one of these categories: Lab Result, Referral Response, Prior Auth Decision, Pharmacy Request, Insurance Correspondence, Records Request, Marketing/Junk, Other; (2) extracts key fields: patient name, DOB, sending provider, document date, urgency indicators; (3) returns structured JSON with classification, confidence score, and extracted fields. Let's start by designing the system prompt, then test it against my sample documents."

### Step 3: Backend Build
> "I'm building the backend for FaxTriage AI. I've validated the Claude Vision API classification pipeline and have working prompts. Now I need: (1) a Python FastAPI server (or Node.js/Express); (2) PDF upload endpoint with file validation; (3) PDF-to-image conversion for Claude Vision API; (4) Claude API integration using my validated prompts; (5) SQLite database for classification results; (6) REST endpoints for the frontend. Here's my validated system prompt: [paste]. Let's build step by step."

### Step 4: Frontend Build
> "I'm building the frontend for FaxTriage AI. The backend API is running and returns classified fax documents as JSON. I need a React + Tailwind dashboard with: (1) priority queue view color-coded by type; (2) columns: document type, patient name, sending provider, received time, confidence, status; (3) filter/sort controls; (4) detail panel with metadata and PDF viewer; (5) action buttons: mark reviewed, reassign, flag, dismiss, add note. The UI should feel like something a medical office front desk worker would use. Here's my API schema: [paste endpoints]."

### Step 5: Demo Prep
> "FaxTriage AI prototype is built and working. I need help preparing demonstration materials. Please help me: (1) create a clean architecture diagram; (2) write a demo script (15–17 min); (3) prepare answers for likely technical and product questions; (4) identify weak points to acknowledge proactively."
