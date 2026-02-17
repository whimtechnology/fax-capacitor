# Known Limitations

This document captures current prototype limitations and likely failure modes.

| Limitation / Failure mode | How we mitigate today | Future improvements |
|---|---|---|
| PDF render/conversion failure on corrupted scans | Mark item as error and keep available for manual handling | Add OCR fallback path, preflight repair, and retry strategy |
| Low-confidence classification on ambiguous documents | Preserve confidence and flags for manual review in queue | Calibrate confidence thresholds with labeled eval set |
| Variability across fax layouts/providers | Use broad prompt guidance and taxonomy coverage | Provider-specific adapters and few-shot exemplars |
| Multi-page context can be inconsistent | Process full file synchronously and store page_count | Add page-linking heuristics and section continuity checks |
| Taxonomy gaps for unseen document types | Route uncertain outputs to review flow | Controlled taxonomy extension workflow with regression checks |
| No production auth/RBAC on prototype UI/API | Use synthetic data only and local/demo deployment | Add role-based access control and environment hardening |
| Limited auditability for compliance evidence | Basic status/processing logs in SQLite | Immutable audit log stream and retention controls |
| SQLite/file storage limits concurrency and durability | Keep scope to MVP/demo usage | Move to managed PostgreSQL + object storage |
| No inbox automation in current MVP | Manual upload keeps flow deterministic for demo | IMAP ingestion worker with idempotent processing |
| Prompt/model dependency risk (classification drift) | Keep prompts versioned in-repo for reviewability | Prompt version pinning, A/B eval, and drift alerting |
| No guaranteed SLA/throughput controls | Small-batch processing for demo reliability | Queue workers, backpressure, and per-tenant rate controls |
| Security/compliance controls are incomplete for PHI | Explicitly marked as non-production prototype | Full HIPAA program with BAA, encryption, RBAC, and audit controls |

## Notes

- This repository is currently best positioned as a prototype and architecture proof point.
- All sample files in the repo are synthetic and intended for demonstration only.
