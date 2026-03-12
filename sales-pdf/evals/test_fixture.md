---
ae: "[[Jane Doe]]"
se: Bob Chen
csm:
deal_type: Net New
next_call: 2026-03-15 - Technical Review
next_call_agenda:
  - Review architecture
  - Discuss SDK integration
  - Address security requirements
salesforce_account: https://example.salesforce.com/lightning/r/Account/001/view
salesforce_opportunity: https://example.salesforce.com/lightning/r/Opportunity/006/view
gong_url: https://app.gong.io/account?id=123
---
**AE:** `= this.ae`
**SE:** `= this.se`
**CSM:** `= this.csm`
**Deal Type:** `= this.deal_type`
**Next Call:** `= this.next_call`
**Next Call Agenda:** `= this.next_call_agenda`

**Links:** [Salesforce](`= this.salesforce_opportunity`) | [Gong](`= this.gong_url`)

## Deal Ledger

- 3/11 BC: Discovery call. Identified pain points. Next call: 3/15 Technical Review

## MEDDPICC

> [!summary] Summary
> - **Metrics:** 500+ flags, 2M MAU, targeting 10M experiment keys
> - **Economic Buyer:** John Smith (VP Eng), prefers usage-based pricing
> - **Decision Criteria:** Mobile-first, Datadog integration required
> - **Decision Process:** Technical POV → business case → procurement
> - **Paper Process:** 60-day procurement cycle, security review required
> - **Identified Pain:** Slow releases, no targeting, manual rollbacks
> - **Champion:** Sarah Lee (Sr Eng Manager) - runs experimentation program
> - **Competition:** Firebase (legacy), Split.io (evaluated)

### Metrics
- 500+ feature flags in production

## Command of the Message

> [!summary] Summary
> **Before:** Manual deployments, 2-week release cycles, no feature targeting
> **Pain:** Slow releases, high blast radius, no rollback capability
> **Required:** API-first flags, SDK support, Datadog integration
> **After:** Trunk-based dev, progressive rollouts, instant kill-switch

## TECHMAPS

> [!summary] TECHMAPS Summary
> **Technical Requirements:** Cross-platform SDKs, API-first CI/CD, streaming
> **Environment:** AWS + CloudFront, React SPA, Node.js, Datadog
> **Competitors:** Split.io evaluated, Firebase legacy
> **Hero:** Sarah Lee (Champion, driving adoption)
> **Metrics:** 500+ flags, 2M MAU
> **Alignment:** Strong fit for feature flags and release management
> **Plan:** 8-week implementation starting Q2
> **Support:** Standard support plan

## Tech Stack

> [!summary] Summary
> AWS, React SPA, Node.js, Datadog APM/RUM, PagerDuty, PostgreSQL, Redis
