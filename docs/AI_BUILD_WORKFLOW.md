# AI Build Workflow (Responsible Use)

## Purpose

This repo demonstrates a practical workflow for building AI-assisted software with human review at each critical decision point.

## Workflow used in this project

1. Define constraints first
- Clarify what cannot change (existing workflow assumptions, compliance boundaries, prototype scope).
- Keep decisions explicit in docs before writing code.

2. Use prompt discipline
- Prefer small, scoped prompts tied to one outcome (taxonomy draft, endpoint contract, UI state shape).
- Request structured outputs (tables/JSON/checklists) to reduce interpretation drift.

3. Review loop before merge
- Validate generated artifacts against existing interfaces.
- Reject or revise outputs that introduce hidden architecture changes.
- Keep commits small and attributable.

4. Evidence-driven quality checks
- Use synthetic fixtures for repeatable behavior checks.
- Track known failure modes and manual fallback paths.
- Document limitations directly, instead of masking uncertainty.

5. Human-in-the-loop decisions
- Human owner approves taxonomy definitions, confidence thresholds, and routing implications.
- AI assists with generation and iteration; humans retain accountability.

## How partner teams can safely extend taxonomy

- Start with a change request that includes:
  - New class name and business rationale
  - Required extracted fields
  - Downstream action owner
  - Risk level if misclassified
- Add/update synthetic examples for the new class before changing prompts.
- Run classification checks on representative mixed batches to detect regressions.
- Keep backward-compatible naming where possible; deprecate old labels in a documented transition.
- Require reviewer sign-off from both domain owner (operations/clinical) and technical owner.

## Guardrails to keep

- Do not auto-route high-impact decisions without review in early phases.
- Keep prompts and taxonomy in version control.
- Prefer additive docs and explicit checklists over implicit assumptions.
