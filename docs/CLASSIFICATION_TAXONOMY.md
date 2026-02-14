# Document Classification Taxonomy

## Overview

This taxonomy defines the document types the AI pipeline classifies. Designed around the most common inbound fax types for small primary care and specialty practices.

---

## Document Types

### Lab Result
- **Priority:** High (critical values elevated to Critical)
- **Frequency:** Very High
- **Accuracy Target:** >90%
- **Description:** Blood work, pathology reports, imaging results, urinalysis
- **Key Extraction Fields:** Patient name, DOB, ordering provider, lab/facility name, test date, result date, critical/abnormal flags
- **Urgency Indicators:** "CRITICAL VALUE", "STAT", "ABNORMAL", "PANIC", flagged reference ranges
- **Common Senders:** Quest Diagnostics, LabCorp, hospital labs, imaging centers

### Referral Response
- **Priority:** Medium–High
- **Frequency:** High
- **Accuracy Target:** >85%
- **Description:** Specialist consultation notes, referral acknowledgments, appointment confirmations, consult reports
- **Key Extraction Fields:** Patient name, referring provider, specialist name/practice, appointment date, diagnosis/reason
- **Urgency Indicators:** "URGENT CONSULT", pending follow-up actions
- **Challenge:** High format variance across specialist offices

### Prior Authorization Decision
- **Priority:** High (denials are critical)
- **Frequency:** Medium
- **Accuracy Target:** >90%
- **Description:** Approval, denial, or pending notices from insurance payers for procedures, medications, referrals
- **Key Extraction Fields:** Patient name, member ID, procedure/medication, decision (approved/denied/pending), payer name, auth number, expiration date, appeal deadline
- **Urgency Indicators:** "DENIED" (time-sensitive appeal windows), expiration dates
- **Common Senders:** Insurance payers, PBMs, utilization review companies

### Pharmacy Request
- **Priority:** Medium
- **Frequency:** Medium
- **Accuracy Target:** >85%
- **Description:** Refill requests, prior auth for medications, formulary alternative suggestions, drug interaction alerts
- **Key Extraction Fields:** Patient name, medication name/dosage, pharmacy name/number, prescriber, request type
- **Urgency Indicators:** "URGENT", controlled substance requests, interaction alerts
- **Common Senders:** CVS, Walgreens, independent pharmacies, PBMs

### Insurance Correspondence
- **Priority:** Low–Medium
- **Frequency:** Medium
- **Accuracy Target:** >80%
- **Description:** EOBs, coverage change notifications, claim correspondence, eligibility updates, provider credentialing
- **Key Extraction Fields:** Patient name, member ID, payer, document type, effective dates, claim numbers
- **Urgency Indicators:** Termination notices, retroactive coverage changes
- **Common Senders:** Insurance companies, Medicaid/Medicare

### Patient Records Request
- **Priority:** Medium
- **Frequency:** Low
- **Accuracy Target:** >80%
- **Description:** Records requests from other providers, attorneys, insurance companies, or patients themselves
- **Key Extraction Fields:** Patient name, DOB, requesting party, records requested, date range, authorization/consent status
- **Urgency Indicators:** Legal deadlines, subpoenas
- **Challenge:** Must verify authorization/consent is included

### Marketing / Junk
- **Priority:** None (auto-dismiss candidate)
- **Frequency:** High
- **Accuracy Target:** >95%
- **Description:** Vendor solicitations, medical equipment sales, continuing education ads, supply catalogs, unsolicited service offers
- **Key Extraction Fields:** None needed — classification sufficient
- **Auto-action:** Flag for bulk dismissal, do not surface in priority queue
- **Note:** High confidence threshold required to avoid auto-dismissing legitimate documents

### Other / Unclassified
- **Priority:** Flagged for manual review
- **Frequency:** Low
- **Accuracy Target:** N/A
- **Description:** Anything not matching above categories
- **Action:** Always surfaces in queue with "Needs Review" status
- **Purpose:** Catch-all that prevents the system from forcing incorrect classifications

---

## Classification Confidence Handling

| Confidence Range | Action |
|-----------------|--------|
| ≥ 0.85 | Auto-classify, display in queue with type label |
| 0.65 – 0.84 | Classify but flag with "Low Confidence" indicator |
| < 0.65 | Classify as "Other / Unclassified" regardless of predicted type |

---

## Priority Color Coding (Dashboard)

| Priority | Color | When |
|----------|-------|------|
| Critical | 🔴 Red | Critical lab values, prior auth denials near appeal deadline |
| High | 🟠 Orange | Lab results, prior auth decisions |
| Medium | 🟡 Yellow | Referral responses, pharmacy requests, records requests |
| Low | 🟢 Green | Insurance correspondence, routine items |
| None | ⚫ Gray | Marketing/junk (auto-dismissed from default view) |
| Review | 🔵 Blue | Low-confidence classifications, unclassified items |
