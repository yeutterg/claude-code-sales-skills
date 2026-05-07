---
description: Generate a Solutions Architect / Professional Services prep document for a LaunchDarkly account. Creates a standalone note in the account folder and exports to PDF. Use this skill when the user wants to create an SA prep doc, PS handoff doc, or professional services prep for an account.
argument-hint: <account>
---

# SA / Professional Services Prep

Generates a concise prep document that a Solutions Architect can read before engaging with an account. Creates the note in the account folder and exports to PDF via `/sales-pdf`.

## Arguments

- `account` (required): The account name (e.g., "Acme Corp")

## Instructions

You are creating an SA Prep document for: {account}

### Pre-check: Read Config

Read the config file at `~/.claude/skills/sales-config.md` and extract:

- `vault_path` — path to the Obsidian vault
- `company_folder` — subfolder name within the vault
- `name` — the user's full name
- `initials` — the user's initials
- `salesforce_instance_url` — Salesforce instance base URL

### Step 1: Read Account Data

Read these files from `{config.vault_path}/{config.company_folder}/Accounts/{Account}/`:

1. **`{Account}.md`** — main account file (MEDDPICC, TECHMAPS, CoM, Business Context, Architecture Diagram, Tech Stack, Salesforce Updates)
2. **`Ledger.md`** — deal history
3. **Recent meeting notes** (last 5-10 meetings from the `meetings/` folder) — scan for PS-relevant context: technical requirements, integration discussions, architecture decisions, stakeholder alignment

### Step 2: Generate the SA Prep Document

Create `{config.vault_path}/{config.company_folder}/Accounts/{Account}/SA Prep.md` with the following structure. Write this as a **dense, opinionated briefing** — not a template dump. The SA should be able to read this in 10 minutes and walk into a call prepared.

```markdown
# {Account} - SA Prep

**Last Updated:** {YYYY-MM-DD}
**AE:** {from frontmatter} | **SE:** {from frontmatter} | **CSM:** {from frontmatter}
**SF Stage:** {from Salesforce Updates or CEP} | **Deal Type:** {from frontmatter}

---

## TL;DR

- **Company:** {1 line — name, what they do, size/revenue, key fact}
- **Relationship:** {1 line — how long a customer, what they use, contract status}
- **Deal:** {1 line — what's being sold/expanded}
- **Status:** {1 line — current deal status, any risks}
- **Key context:** {2-3 bullet points of the most important things the SA needs to know — champion changes, technical blockers, political dynamics, timeline pressure}

---

## The Business

{5-8 bullets synthesized from Business Context. Focus on what matters for a technical engagement:}
- Company size, industry, what they do
- Key business initiatives or transformations
- Relevant recent news (acquisitions, leadership changes, financial pressure)
- Cultural context that affects technical decisions (cost-conscious CEO, risk-averse culture, etc.)

---

## Why They Have LaunchDarkly

{What products they use, how they use them, how embedded LD is in their stack. Include:}
- Current products and usage (service connections, MAUs, etc.)
- How LD fits into their development workflow
- Any over/under-contracting context
- Teams using LD and how broadly adopted

---

## The Pain (Why {Product/Service} Matters)

{Organize by pain theme, not by MEDDPICC field. Each theme should be a ### subsection with 3-5 bullets. Connect pain to the specific product/service being proposed.}

### {Pain Theme 1}
- {Specific pain point with concrete details — numbers, timeframes, impact}

### {Pain Theme 2}
- ...

### What's at Stake
- {Quantified business risk if pain isn't addressed}

---

## Tech Stack

{Table format — same as account file. Include a "Key integration points for SA" section below the table highlighting what the SA needs to understand for implementation planning.}

| Layer | Tools |
|-------|-------|
| ... | ... |

**Key integration points for SA:**
- {Integration considerations specific to the proposed engagement}

---

## Architecture Diagram

{Copy the mermaid diagram from the main account file's ## Architecture Diagram section. Include it exactly as-is (```mermaid ... ```). If no diagram exists, note: "No architecture diagram available. Run `/sales-architecture-diagram {Account}` to generate one."}

---

## People Map

{Table format. Include stance (Champion/Supportive/Neutral/Detractor/Skeptic) and 1-line notes. Separate into Active Stakeholders, Departed (if relevant), and Expansion Contacts (if relevant).}

### Active Stakeholders
| Name | Role | Stance | Notes |
|------|------|--------|-------|
| ... | ... | ... | ... |

{Add Departed or Expansion sections only if relevant}

---

## Deal Status & Strategy

### Current State
{What's happening right now with the deal — 3-5 bullets}

### Recovery/Acceleration Strategy
{If deal is at risk: numbered recovery steps. If deal is progressing: next milestones and what needs to happen.}

### Pricing/Contract Lever
{Any relevant contract context — over-contracting, renewal timing, bundling opportunity}

---

## What {Product/Service} Solves for Them

{Table mapping pain → solution. Be specific to their environment, not generic product marketing. Pull canonical product names + doc URLs from `~/.claude/skills/sales-product/knowledge.md` so every solution cell links to the right docs page.}

| Pain | Solution |
|------|----------|
| ... | [Capability]({url-from-/sales-product}) doing X for this customer's environment |

---

## Recommended Implementation Sequence

This is the SE/SA prescription, not a status report. The SA should walk in with a point of view about what to deploy first, what to deploy second, what to defer, and which risk to plan around — not arrive ready to discover. Pull canonical capability info + doc URLs from `~/.claude/skills/sales-product/knowledge.md`.

**Sequencing rule:** foundation first, value-bearing capability second, frontier last. Specifically:
1. **SDK + targeting + segments** before anything else. Without the substrate, downstream capabilities don't deliver.
2. **The single highest-leverage capability for THIS customer** second. Pick the one that addresses their #1 stated pain (from MEDDPICC > Identified Pain) AND has the named champion ready to validate it.
3. **Frontier capabilities** (Guarded Releases for metric-driven safety; AI Configs for AI feature delivery; Experimentation for variant testing) last. These compound on the substrate; they don't replace it.

### Phase 1 (0-{N} weeks): Foundation
- **Deploy in order:** [SDK]({sdk-url}) → [contexts]({contexts-url}) → [segments]({segments-url})
- **Customer-side prerequisites:** {what the customer's eng team needs to do first; cite from TECHMAPS > Environment}
- **Success criteria (co-signed pre-kickoff):** SDK integrated in {N} services; first flag evaluated in production; user context streaming validated
- **{Account} effort:** {team size + sprint estimate based on TECHMAPS > Environment}

### Phase 2 ({N1}-{N2} weeks): Highest-leverage capability
- **Anchor:** {the customer's #1 stated pain from MEDDPICC, named in their language}
- **Deploy in order:** {capability + URL} + {supporting capability + URL}
- **Success criteria:** {falsifiable outcome that proves Phase 2 worked, in customer-language}
- **Risk to plan around:** {the implementation risk most likely to derail this phase, with mitigation}

### Phase 3 ({N2}+ weeks): Layered capabilities
- **What lands here:** {remaining capabilities the customer is buying, deferred to Phase 3 because they layer on Phase 1+2}
- **Deploy in order:** {list capabilities with URLs in the order they should ship}
- **What we'd hold back / not deploy unless customer specifically asks:** {capabilities the customer hasn't engaged with on calls; mention only if asked}

**Out of scope for this engagement** (explicit):
- {capabilities mentioned in Decision Criteria but lower priority for THIS engagement; flag for follow-on}
- {legacy items the customer wants to migrate eventually but aren't critical for go-live}

**Why this sequence and not others:** one-line rationale tying back to the customer's compelling event + named champion. (e.g., "Phase 2 leads with Guarded Releases because the env-misalignment incident is what surfaces in every meeting; the champion is engaged on this specifically; without it, Phase 3 capabilities have nothing to gate.")

## Key Technical Considerations for SA

{Numbered list of the most important technical topics the SA needs to be prepared for. Each should be 2-3 sentences explaining what it is, why it matters for this account, and any known context. Reference Common Confusions Index from `~/.claude/skills/sales-product/knowledge.md` — if the customer has confused two LD products on calls, the SA needs to walk in calibrated.}

1. **{Topic}.** {Why it matters for this specific account. What's known so far. If a Common Confusion applies, name it explicitly: e.g., "Customer conflated Workflows with Guarded Releases on 4/29 — SA should clarify the distinction early."}
2. ...

---

## Upcoming Milestones

- **{Event}:** {Date and context}
- ...

---

## Questions the SA Should Be Ready For

{7-10 questions the customer is likely to ask, based on their pain points, tech stack, and deal history. These should be specific to the account, not generic.}

1. {Specific question based on their environment}
2. ...
```

### Step 2.5: Generate Salesforce Context

After generating the SA Prep document, output two blocks of text the user can copy-paste into Salesforce PS request fields:

**Request Summary** (2-3 sentences):
```
Request to engage a solutions architect to start planning a services engagement. {1-2 more sentences about what the customer needs help with, referencing specific products and technical context.}
```

**Success Criteria** (single comma-separated line, ~150 characters max):
```
{outcome 1}, {outcome 2}, {outcome 3}, {outcome 4}, {outcome 5}
```
Keep each outcome to 3-6 words. No bullet points — one flat line the user can paste directly into a Salesforce text field. Example: "OTel/Honeycomb integration validated, Kafka context propagation design, mobile SDK impact assessed, flag lifecycle cleanup plan, progressive rollout adoption path"

### Step 3: Generate PDF

After creating the SA Prep note, export it to PDF. The H1 heading (`# {Account} - SA Prep`) should be **kept in the PDF** as the document title.

**PDF export steps:**
1. Read the SA Prep markdown file
2. Strip the first line if it's an H1 heading (starts with `# `)
3. Convert to HTML via pandoc with the standard `/sales-pdf` CSS (sans-serif: `-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif`)
4. Inject Mermaid JS if the file contains architecture diagrams
5. Print to PDF via Playwright at `{config.vault_path}/{config.company_folder}/PDFs/{YYYY-MM-DD}/{YYYY-MM-DD} {Account} SA Prep.pdf`

**Do not use em dashes (—) anywhere in the SA Prep.** Use hyphens (-) or colons instead.

### Step 4: Report

Output:
- Path to the SA Prep note
- Path to the exported PDF
- The Request Summary and Success Criteria text blocks for Salesforce
- Any gaps identified (missing data, no architecture diagram, sparse meeting notes, etc.)

## Writing Guidelines

- **Dense and opinionated.** The SA is busy. Lead with what matters, skip boilerplate.
- **Concrete over generic.** "700 flags with 5:1 dependency ratio" not "significant technical debt."
- **Account-specific.** Every section should reference this customer's actual environment, people, and situation. If you catch yourself writing generic product marketing, rewrite it.
- **Honest about risk.** If the deal is at risk, say so. If there are gaps in knowledge, flag them.
- **Synthesize, don't copy.** Pull from multiple sources (MEDDPICC, meetings, ledger) and weave into a coherent narrative. Don't just relocate sections from the account file.
