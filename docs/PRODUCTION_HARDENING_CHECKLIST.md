# PRODUCTION_HARDENING_CHECKLIST

## Future-state checklist

- [ ] Execute BAA coverage review for every third-party handling PHI, including model/API providers.
- [ ] Complete PHI data-flow mapping and minimum-necessary access analysis.
- [ ] Enforce RBAC across API and UI with least-privilege role definitions.
- [ ] Integrate SSO (OIDC/SAML) with MFA and session hardening.
- [ ] Implement immutable audit logging for document access, classification actions, and admin changes.
- [ ] Define and enforce retention/deletion policies by document class and regulatory requirement.
- [ ] Encrypt data in transit (TLS 1.2+) and at rest (database, object/file storage, backups).
- [ ] Rotate secrets via managed secret store; remove static keys from developer environments.
- [ ] Add human-in-the-loop review gates for low-confidence, high-priority, and exception paths.
- [ ] Require dual-control approval for taxonomy/routing rule changes in production.
- [ ] Add signed release process, dependency scanning, and SBOM generation.
- [ ] Implement tenant isolation controls if serving multiple practices.
- [ ] Create incident response runbooks covering PHI exposure and model misclassification events.
- [ ] Establish RTO/RPO targets and disaster recovery tests for database and storage layers.
- [ ] Build continuous evaluation suite for model accuracy and confidence calibration drift.
- [ ] Add observability baseline (structured logs, metrics, traces, alerting) for end-to-end pipeline health.
- [ ] Conduct periodic penetration testing and remediation tracking.
- [ ] Validate legal/regulatory alignment with HIPAA Security Rule administrative, physical, and technical safeguards.
