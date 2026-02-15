# Demo Guide

## Key Messages

1. **Real-world document understanding:** FaxTriage AI addresses a genuine healthcare operations problem — manual fax triage — by building an AI pipeline that transforms unstructured fax images into structured, prioritized, actionable data using Claude's Vision capabilities.

2. **Constraint navigation:** Healthcare AI deployment is defined by constraints: HIPAA, legacy infrastructure, user resistance to new systems. This prototype was designed to work within those constraints, not around them. The practice changes nothing about how they receive faxes.

3. **Pipeline to agent evolution:** The MVP is an intelligent document processing pipeline. The architecture supports agentic capabilities in Phase 2 — like automated follow-up for missing information — where the system observes patterns, decides on actions, and executes them autonomously.

4. **Transferable pattern:** This pattern — unstructured documents in, structured data out, integrated into existing workflows — applies across industries. Healthcare is the domain; the architecture is transferable.

---

## Recommended Demo Flow (15–17 minutes)

### 1. Problem Statement (2 min)
- The fax triage problem: 75% of healthcare communication is fax
- Small practice reality: 30–80 faxes/day, one person sorting manually
- Enterprise solutions exist but are out of reach ($50K+, IT staff required)
- The gap: digitization happened (cloud fax), but triage is still manual

### 2. Live Walkthrough (5 min)
- Upload 4–5 synthetic fax PDFs (batch upload)
- Show processing status (submitted → processing → classified)
- Walk through the prioritized queue: urgent items surfaced, junk auto-dismissed
- Click into a document: show extracted metadata alongside original PDF
- Demonstrate filter/sort controls
- Show a low-confidence item flagged for review

### 3. Architecture Deep-Dive (5 min)
- Three-stage pipeline: Ingestion → Classification → Presentation
- Prompt engineering decisions: why structured JSON, how confidence calibration works
- Technology choices and rationale
- Known limitations: form variance, scan quality, multi-page challenges
- Be honest about what breaks and why

### 4. Phase 2 Discussion (3 min)
- Agentic evolution: pattern detection → automated follow-up
- The pipeline-to-agent distinction and why it matters
- Email inbox integration, routing rules, analytics
- HIPAA production deployment path

### 5. Meta-Narrative (2 min)
- How Claude was used throughout the process
- Brainstorming → architecture → critical review → code generation → project planning
- This is how enterprise customers should use the product
- The prototype is a proof point; the process is the real demonstration

---

## Anticipated Questions & Responses

### Technical

**Q: How would you handle HIPAA in production?**
BAA with Anthropic, encryption at rest/transit, RBAC, audit logging, data retention policies. The lowest-risk path is on-premise with Claude API as the only external call. Acknowledge this is the primary barrier between prototype and production.

**Q: What happens when classification is wrong?**
Confidence scores flag low-certainty items for manual review. Human-in-the-loop is by design, not a limitation. The system augments staff judgment, doesn't replace it. Over time, correction data can improve prompts.

**Q: Why not just use OCR + rules-based classification?**
Medical faxes are too varied for rules. Layout, terminology, and formatting differ across every sending provider. An LLM handles the long tail that rules cannot. OCR gives you text; Claude gives you understanding.

**Q: How does this scale?**
API-based architecture scales horizontally. Batch processing for high-volume practices. Queue-based async processing. Caching for repeated form layouts. The bottleneck is API cost, not architecture.

**Q: What about multi-page faxes?**
Each page is processed individually, then grouped. The system prompt instructs Claude to identify whether a page is a continuation. Classification is based on the first page with fallback to full-document analysis for ambiguous cases.

### Product / Business

**Q: What's the business model?**
SaaS subscription per practice ($50–150/mo) based on fax volume. API costs are roughly $0.01–0.05 per document. Value prop: saves 1–2 hours/day of staff time at $20–30/hr = $400–1,200/mo in labor value.

**Q: Why wouldn't practices just use a full EMR with built-in fax management?**
Many already have an EMR (even small ones use Athena, eClinicalWorks, etc.) but the EMR's fax integration is often limited or poorly implemented. This tool works alongside any EMR, not instead of one.

**Q: Who's the buyer?**
Practice manager or office administrator. Not the physician. This is an operations tool, not a clinical tool. The pitch is staff time savings and reduced risk of missed urgent documents.

### Architecture

**Q: How would you implement something similar for a different domain?**
Start with document taxonomy workshop — what types of documents are being processed, what are the extraction requirements, what are the downstream workflows? Then prototype the classification pipeline against the actual document corpus. Validate accuracy before building UI. This project followed that exact methodology.

**Q: What would you change if you had more time?**
Automated accuracy benchmarking with a labeled test set. More sophisticated confidence calibration. Email inbox integration for hands-free ingestion. And the agentic follow-up capability, which is the most interesting technical challenge.

**Q: Why Claude for this vs. other models?**
Claude's Vision API handles the full pipeline in one call: OCR, understanding, classification, and structured extraction. Competing approaches require chaining multiple models (OCR → NLP → classification). Claude's structured JSON output mode eliminates response parsing complexity.
