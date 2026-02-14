# HIPAA & Compliance Considerations

## Prototype Safeguards

This prototype uses **exclusively synthetic data**. No protected health information (PHI) is processed, stored, or transmitted at any point.

- All test documents use clearly fictional patient information
- No PHI is sent to the Claude API
- All data remains on the development machine
- No cloud storage of documents in the prototype

---

## Production Deployment Requirements

A production deployment of FaxTriage AI would process PHI and must comply with HIPAA regulations. The following requirements would apply:

### Business Associate Agreements (BAAs)

| Party | Requirement |
|-------|-------------|
| Anthropic | BAA required for Claude API processing PHI. Anthropic offers BAAs for enterprise API customers. |
| Cloud hosting | BAA with hosting provider (AWS, GCP, Azure all offer HIPAA-eligible services) |
| Cloud fax provider | BAA likely already in place between practice and their eFax/RingCentral provider |

### Technical Safeguards

| Requirement | Implementation |
|-------------|---------------|
| Encryption at rest | AES-256 for stored documents and database. Full-disk encryption for servers. |
| Encryption in transit | TLS 1.2+ for all API calls and web interface |
| Access controls | Role-based access (admin, office staff, provider). Principle of least privilege. |
| Audit logging | Complete log of document ingestion, classification, access, and all actions taken |
| Session management | Automatic timeout, secure session tokens |
| Data retention | Configurable policies aligned with state medical records requirements |
| Backup & recovery | Encrypted backups with tested restoration procedures |

### Administrative Safeguards

- Designated security officer
- Workforce training on PHI handling
- Incident response procedures for potential breaches
- Regular security assessments
- Documentation of all policies and procedures

### Physical Safeguards

- For cloud deployment: inherited from HIPAA-eligible cloud provider
- For on-premise: standard server room security requirements

---

## Risk Assessment for Interview Discussion

**Lowest risk path to production:** On-premise deployment at the practice using a local server, with the Claude API call as the only external data transmission (covered by Anthropic BAA). This minimizes the attack surface and compliance burden.

**Key discussion point:** The HIPAA compliance requirements are not unique to this application — they apply to any healthcare AI tool processing PHI. The architecture is designed to be compliance-ready without being compliance-burdened in the prototype phase. This mirrors how enterprise customers approach proof-of-concept vs. production deployment.
