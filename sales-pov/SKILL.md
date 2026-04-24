---
description: Generate or update a POV & Technical Validation Summary for an account. Focuses on the last 30-45 days of conversations and current MEDDPICC/TECHMAPS state to surface ONLY the painful, deal-gating items that must be validated before close.
argument-hint: <account name>
---

# POV & Technical Validation Summary

Generate a tight, actionable POV review for a sales account. Intentionally short. The point is to surface the 3-6 items that are **painful to the customer AND risky to closing** — not to exhaustively catalogue every feature the customer is evaluating.

## Arguments

- `account`: The account name (e.g., "Acme Corp", "Acme Corp")

Examples:
- `/sales-pov Acme Corp`

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

This is the core of the skill. Filter aggressively — most features the customer is "evaluating" don't belong in this document.

For each candidate capability / requirement / integration, it **only qualifies** if BOTH are true:

**A. The customer has expressed actual pain about it in recent conversation.** Pain = a specific scenario, cost, or workaround they've described, ideally with a quote. Not "they're interested in feature X" — that's interest, not pain. The pain must come from:
- A recent meeting transcript or summary (last 45 days)
- Or an explicit entry in MEDDPICC Pain / Business Impact that's traceable to a recent conversation

**B. Not validating it puts the deal at risk.** Risk = one of:
- Named as a Decision Criterion in MEDDPICC
- Called out as a blocker by the Economic Buyer or Champion
- Competitive differentiation where we lose if we can't demonstrate it
- Technical gap in TECHMAPS that would cause the customer to choose "build" over "buy"
- Paper-process gate (security review, procurement checklist, compliance)

**Exclude** everything that is:
- "Nice to have" or "exploring" — the customer said so or the signal is soft
- Already validated (status VALIDATED in prior POV summary, no new challenges)
- Generic product features we always show (basic flag creation, default SDK integration) unless the customer specifically flagged them as risky
- Capabilities where no evaluator has been named — if no one on the customer side owns judging it, it's not gate-closing
- Items surfaced only in older meetings with no recent mention

Aim for **3-6 items** in the final table. If you find yourself writing 8+, you haven't filtered hard enough. The customer can have broad interest in a product; this document only captures what must land for the deal to close.

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

Items the customer has surfaced as pain AND that put the deal at risk if not validated. Filtered for this deal, this moment — not a feature checklist.

| # | Capability | Problem (customer pain) | How {Company} Helps | Evaluator | Status |
|---|------------|-------------------------|------------------------|-----------|--------|
| 1 | {capability required, specific to their environment} | {the concrete problem the customer is trying to solve in their own words — quote + date of meeting where they said it. Describe the *problem*, not the feature.} | {1-2 sentences on how LD's capability maps to this problem. Be specific: name the LD product / feature / integration, not a vague "we solve that." Tie directly back to the problem language.} | {name, title} | {NOT STARTED / IN PROGRESS / VALIDATED / BLOCKED} |

Order by deal-gating priority. Aim for 3-6 rows. If fewer than 3 items qualify, say so explicitly (`## Painful + Deal-Gating Items` — *"No deal-gating pain surfaced in the last 45 days. Either the POV is on rails or we're under-discovering."*).

**Column guidance:**
- **Capability:** short phrase for the thing that must be proven (e.g., "Multi-LLM experimentation with auto-rollback", not "AI Configs").
- **Problem:** the customer's stated pain, grounded in a quote or scenario from a recent meeting. Include the meeting date. If it's a scenario rather than a quote, describe it in the customer's language.
- **How {Company} Helps:** the specific product answer. Name the product/feature (from `config.products`), the integration, the workflow — not marketing phrasing. This is where the SE's value proposition gets pinned to each pain.
- **Evaluator:** named customer contact who owns judging whether this works. No evaluator → the row shouldn't exist.
- **Status:** NOT STARTED / IN PROGRESS / VALIDATED / BLOCKED. Justified by evidence.

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
