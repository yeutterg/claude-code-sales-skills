---
description: Generate or update a POV & Technical Validation Summary for an account. Focuses on the last 30-45 days of conversations and current MEDDPICC/TECHMAPS state to surface ONLY the painful, deal-gating items that must be validated before close.
argument-hint: <account name>
---

# POV & Technical Validation Summary

Generate a tight, actionable POV review for a sales account. Intentionally short. The point is to surface the 3-6 items that are **painful to the customer AND risky to closing** — not to exhaustively catalogue every feature the customer is evaluating.

## Arguments

- `account`: The account name (e.g., "Acme Corp", "Apple")

Examples:
- `/sales-pov Apple`

## Instructions

You are helping a Solutions Engineer create or update a focused POV review for: $ARGUMENTS.

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `name`, `initials`, `company`, `products`, `competitors`, `pdf_path`.

### Pre-check: Verify Account

Check the account folder at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/`. Stop if missing.

### Step 1: Gather Only What Matters

The entire point of this skill is to stay focused. Do NOT read the full history.

1. **Account file** (`{Account}.md`): read ONLY these sections as the source of truth for what's at stake:
   - CEP Stage + Salesforce Stage
   - MEDDPICC — especially **Decision Criteria**, **Pain / Business Impact**, **Champion**, **Economic Buyer**, **Paper Process**, **Competition**
   - TECHMAPS — especially **Technical Requirements**, **Gaps**, **Integration Points**
   - Command of the Message — the customer's stated WHY + top pain
   - Deal structure (amount, products, timeline) from frontmatter
2. **Recent meetings only**: read meeting files with `date >= today - 45 days`, ordered newest first. Skip meetings with empty notes/transcript. If there are more than 8 recent meetings, cap at the 8 most recent plus any older meeting explicitly flagged as pivotal in the ledger.
3. **Ledger.md**: read ONLY the most recent 10 entries. Use these to anchor "what's moving right now," not to build a full chronology.
4. **Contacts**: spot-check the Champion, Economic Buyer, and any Detractor files for role and stance — don't scan the full contacts folder.
5. **Existing POV Summary** (`POV Summary.md`), if present: read it to understand what's already captured, then incrementally update — don't rewrite sections that haven't changed.

**If the recent-meetings window is empty** (account has been dormant 45+ days), expand to 90 days and note the dormancy in the exec summary.

### Step 2: Identify the Painful + Risky Items

This is the core of the skill. Filter aggressively — most features the customer is "evaluating" don't belong in this document. Think critically about what is truly blocking the deal vs. nice-to-have.

**Scope — this is a POV / technical-validation document, not a deal-status dashboard.** The table captures **technical capabilities the SE must prove work in the customer's environment**. Full stop. Do NOT include:

- **Commercial / pricing / procurement items** (discount, pricing negotiation, tier selection) — those belong in deal notes, not POV.
- **Compliance / certification checkpoints** (FedRAMP, SOC2, HIPAA, security review) — those are **paper-process gates**, not technical validations. Mention them in "Top Risks to Close" if they're active blockers; do NOT put them in the POV table.
- **Professional Services / RSA / PS scoping** — those are commercial scope discussions, not technical validation. Mention in "Top Risks to Close" if the PS gap threatens close.
- **Stakeholder engagement / executive sponsor meetings** — those are deal-motion items. Put in "Top Risks to Close" or ledger, not POV.
- **Integration or training follow-through commitments** that happen AFTER purchase decision.

For a candidate technical capability to qualify, BOTH must be true:

**A. The customer has expressed actual pain about it in recent conversation.** Pain = a specific scenario, cost, or workaround they've described. Not "they're interested in feature X" — that's interest, not pain. The pain must come from a recent meeting transcript / summary (last 45 days), or an explicit MEDDPICC Pain entry traceable to a recent conversation. Quote the customer's words when you can.

**B. Not validating the capability puts the deal at risk.** Technical-risk only, per the scope above. Risk signals:
- Named as a Decision Criterion in MEDDPICC
- Technical gap in TECHMAPS that drives the customer toward "build" over "buy"
- Competitive differentiation where we lose the eval if we can't demonstrate it
- Champion or Economic Buyer has personally called out the capability as a must-prove

**Exclude** everything that is:
- "Nice to have" or "exploring" — soft signal, not a gate
- Already validated with no new challenges surfacing
- Generic product features we always show unless the customer flagged them specifically
- No named evaluator on the customer side
- Surfaced only in older meetings with no recent reinforcement

Aim for **3-5 items**. If you find 6+, filter harder — you probably captured interest items, not deal-gates. If <3 qualify, that's a finding: say so rather than padding.

**Order the table by product maturity, from foundational to frontier.** This reflects how the customer will and should validate: core plumbing first, advanced/newer capabilities last. Foundational capabilities (core feature management, SDK/API correctness, flag delivery semantics) come first because they anchor trust and must be rock-solid before evaluating newer pieces. Newer products (AI Configs, Guarded Releases, o11y) come last because they layer on top.

Within the same maturity tier, break ties by deal-gating severity.

### Step 3: Write the POV Summary

Write to `{config.vault_path}/{config.company_folder}/Accounts/{Account}/POV Summary.md`.

#### Document Structure

The document is deliberately short — target **2-3 pages of PDF** total. No exhaustive history, no competitive landscape matrix, no exhaustive timelines.

```markdown
# POV Technical Validation: {Account}

## Deal Status
- **Stage:** {Salesforce stage} / {CEP stage if different}
- **Deal:** {amount, plan tier, products}
- **Champion:** {Name, title} — {engagement signal in 8 words}
- **Economic Buyer:** {Name, title} — {engaged | not yet engaged | engagement gap in 8 words}
- **Paper Process:** {status — security review, procurement, legal, MSA — only mention the ones that are live/blocking}
- **Next committed step:** {the single next-step date and owner from the most recent meeting}

## What's Moving Right Now

{3-5 sentences. ONLY the last 30-45 days. What's changed, what's scheduled next, who's the current bottleneck. Cite 1-2 specific meetings by date. Do NOT recap the deal history.}

## Painful + Deal-Gating Items

Technical capabilities the customer has surfaced as pain AND that put the deal at risk if not validated in their environment. **Ordered by product maturity (foundational → frontier), not by recency or internal priority.**

| # | Capability | Problem | How {Company} Helps | Evaluator | Status |
|---|------------|---------|---------------------|-----------|--------|
| 1 | {short phrase in customer's language} | {≤15 words, customer's own phrasing or a close paraphrase of their scenario, with meeting date} | {≤15 words, name the specific {Company} product/feature from config.products — no marketing fluff} | {name, title} | {NOT STARTED / IN PROGRESS / VALIDATED / BLOCKED} |

Aim for 3-5 rows. If <3 qualify, write instead: *"No deal-gating technical pain surfaced in the last 45 days. Either the POV is on rails or we're under-discovering."*

**Column guidance:**
- **Capability:** short phrase using the customer's vocabulary, not {Company}-product marketing. If they call it "the CFS replacement" or "our homegrown portal parity," use that. Avoid product names like "Guarded Releases" or "AI Configs" in this column — put those in the How-{Company}-Helps column instead.
- **Problem:** ≤15 words. The customer's concrete pain in their words. Preferably a direct quote or close paraphrase. Include the meeting date.
- **How {Company} Helps:** ≤15 words. The specific product/feature answer, named directly (e.g., "Guarded Releases with metric-driven auto-rollback"). No "we empower teams to…" phrasing. Tie back to the problem language.
- **Evaluator:** named customer contact who owns judging whether this works. No evaluator → the row shouldn't exist.
- **Status:** NOT STARTED / IN PROGRESS / VALIDATED / BLOCKED. Justified by evidence.

**Ordering rule — product maturity:** foundational capabilities first (core feature management, SDK/API behavior, flag delivery semantics), then advanced targeting/workflow features, then newer products (Guarded Releases, AI Configs, o11y). This is the order the customer will actually validate in — trust in the core must land before the frontier capabilities carry weight. Within the same maturity tier, break ties by deal-gating severity.

## Top Risks to Close

Max 3-4 risks, ranked. Each is one paragraph:

**1. {Risk name — e.g., "EB not yet engaged"}**
What it is, evidence from recent meetings (cite date), and the single concrete mitigation.

**2. {…}**

Do NOT include generic risks (competitive pressure, timeline slip) unless there's specific recent evidence.

## Next Steps

Dated, owned, tied to the painful items above.

- **{YYYY-MM-DD}:** {Action} — {owner}
- **{YYYY-MM-DD}:** {Action} — {owner}

## Prior POV History (one-liner)

*{Only include if there were prior attempts. One sentence each. No full section.}*

- **2025 Q2:** Feature Flags trial stalled when Champion moved to a different team.

## Appendix: Source Meetings

Tight list of the recent meetings this summary was built from. No bullets, just links:

- [[{YYYY-MM-DD Meeting Name}]]
- [[{YYYY-MM-DD Meeting Name}]]
```

#### Writing Guidelines

- **Ruthless brevity.** If a sentence doesn't change what the SE does tomorrow, cut it.
- **Cite recent meetings by date** when stating pain or risk. Everything should trace back to conversation from the last 45 days.
- **Quote stakeholders directly** when a sentence of theirs is more precise than a paraphrase.
- **Tie every painful item to a named Evaluator.** If the item has no evaluator, it shouldn't be in the table.
- **Never restate the product.** Don't explain what AI Configs or Guarded Releases does. This is internal — the reader already knows.
- **Don't blend history.** Prior POV attempts get one sentence each, not a section. The active picture is what matters.
- **Status must be justified by evidence, not aspiration.** If an item is "IN PROGRESS," name the specific next meeting or action that moves it forward.

### Step 4: Export PDF

After writing the POV Summary, export it:

1. Create `mkdir -p "{config.pdf_path}/{YYYY-MM-DD}"`.
2. Preprocess the markdown:
   - Strip YAML frontmatter
   - Convert wiki-links (`[[Name]]`) to plain text (drop the brackets, keep the alias if `[[A|B]]`)
   - Convert Obsidian callouts (`> [!type] ...`) to bold headers
   - Add `*Generated {YYYY-MM-DD}*` after the H1
3. Use the shared CSS stylesheet at `/tmp/sales-pdf-style.css` (same as `/sales-pdf`).
4. Convert via pandoc:
   ```bash
   pandoc /tmp/sales-pov-{slug}.md -f markdown -t html5 --standalone --embed-resources \
     --css /tmp/sales-pdf-style.css --metadata pagetitle="{Account} POV Summary" \
     -o /tmp/sales-pov-{slug}.html
   ```
5. Start temp HTTP server, print to PDF via Playwright CLI (Letter, 0.5in margins, printBackground true), save to `{config.pdf_path}/{YYYY-MM-DD}/{YYYY-MM-DD} {Account} POV Summary.pdf`, then clean up.

Target PDF length: **2-3 pages**. If it's longer, the filter in Step 2 wasn't aggressive enough — tighten and regenerate.

### Step 5: Report

```
POV Summary {created | updated} for {Account}

File: {Account}/POV Summary.md
PDF: {pdf_path}/{YYYY-MM-DD}/{YYYY-MM-DD} {Account} POV Summary.pdf

Pain+risky items surfaced: {N}
Top risk: {1-line summary of #1 risk}
Source meetings: {count} from last {window} days
```

### Update Mode

If `POV Summary.md` already exists:
- Read it first
- Identify what's changed in the last 45 days (new meetings, status moves, new pain surfaced)
- Update only the Deal Status, What's Moving Right Now, table rows, and risks that changed
- Preserve Prior POV History verbatim — it's historical, not moving
- Regenerate the PDF

### Rules

- Never fabricate meeting content. If a meeting file is empty (no notes/transcript), skip it — don't invent.
- Use canonical product names from `config.products`, canonical competitor spellings from `config.competitors`.
- If no painful+risky items qualify, say so in the table section rather than padding with soft items. That's a valid finding (and a discovery prompt).
- If the account has never had a POV *and* nothing is surfacing in recent meetings, the document should be under 1 page and explicitly note "nothing active — recommend engagement to surface pain."
