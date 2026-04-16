---
description: Generate or update a POV & Technical Validation Summary for an account. Synthesizes all meetings, transcripts, and deal context into a structured review of every POV attempt.
argument-hint: <account name>
---

# POV & Technical Validation Summary

Generate or update a comprehensive POV review document for a sales account. This document synthesizes all meeting notes, transcripts, ledger entries, and deal context into a structured analysis of every POV attempt, trial, and technical validation — past and present.

The output is a living document that helps the SE and deal team understand what's been tried, what worked, what failed, and what's different about the current approach.

## Arguments

- `account`: The account name (e.g., "Acme Corp", "Globex")

Examples:
- `/sales-pov Acme Corp` (generate or update POV Summary)

## Instructions

You are helping a Solutions Engineer create or update a POV review document for the account: $ARGUMENTS

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `name`, `initials`, `company`, `products`, `competitors`.

### Pre-check: Verify Account

Check that the account folder exists at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/`. If not, stop: "Account not found."

### Step 1: Gather All Context

Read the following files to build a complete picture of the account:

1. **Account file** (`{Account}.md`) — MEDDPICC, Command of the Message, TECHMAPS, CEP Stage, Business Context, Tech Stack
2. **Ledger.md** — chronological history of every meeting and milestone
3. **ALL meeting files** in `meetings/` — read summaries, external summaries, and transcripts. For accounts with many meetings, prioritize the most recent 10-15 and any meetings with transcripts.
4. **Contacts** — scan `contacts/` for key stakeholders, roles, and influence levels
5. **Existing POV Summary** (`POV Summary.md`) — if it exists, read it to understand what's already documented and what needs updating

### Step 2: Identify POV Initiatives

From the meeting history and ledger, identify every distinct POV, trial, evaluation, or technical validation initiative. Group meetings by initiative. Each initiative typically has:

- A distinct **topic/capability** being evaluated (e.g., "Feature Flags POV", "AI Configs Trial", "Experimentation Expansion")
- A **time range** (start to end or ongoing)
- A **set of stakeholders** involved
- An **outcome** (SUCCESS, STALLED, ACTIVE, PLANNED, EARLY, DEEMPHASIZED)

Also identify:
- **Cold outreach or failed engagements** that never progressed to evaluation
- **Internal prep sessions** that shaped strategy
- **On-sites or executive meetings** that were pivotal

### Step 3: Analyze Patterns

Across all initiatives, identify:

1. **Common success factors** — what was present when things worked (EB alignment, clear pain, specific champions)
2. **Common failure modes** — what was missing when things stalled (no exec sponsor, champion without budget authority, organizational distraction, key skeptic not persuaded)
3. **What's different now** — if there's an active evaluation, articulate specifically what has changed vs. prior failed attempts
4. **Risk patterns** — recurring blockers, organizational dynamics, competitive concerns

### Step 4: Write the POV Summary

Create or update `{config.vault_path}/{config.company_folder}/Accounts/{Account}/POV Summary.md`.

#### Document Structure

```markdown
# POV & Technical Validation Summary for {Account}

## Executive Summary

- **{N} initiatives total:** {count by status — e.g., "1 clean win, 2 stalled, 1 active"}
- **Common success factor:** {pattern}
- **Common failure mode:** {pattern}
- **What's different now:** {key changes that make the current attempt viable}
- **Current approach:** {brief description of active evaluation strategy}
- **Deal structure:** {amount, plan, products included}
- **Key risk:** {single biggest risk to the current evaluation}

---

## {Most Recent Initiative} ({date range})

**Topic:** {what's being evaluated}
**Stakeholders:** {customer contacts with titles}
**LD Team:** {internal team with roles}
**Status:** {ACTIVE | PLANNED | EARLY | SUCCESS | STALLED | DEEMPHASIZED}

### Timeline
- **M/D Event:** Description of what happened and key outcomes
- **M/D Event:** ...

### Current POV Approach
{Only for ACTIVE initiatives}
- Format, success criteria, timeline, parallel tracks

### Key Findings
{Insights from transcripts and meetings}

### Stakeholder Dynamics
{Who supports, who blocks, who's neutral — with specific evidence}

### Risk: {Top risk for this initiative}
{Details and mitigation plan}

---

## {Previous Initiative} ({date range})

**Topic:** ...
**Stakeholders:** ...
**LD Team:** ...
**Status:** STALLED | SUCCESS | etc.

- {Key bullet points about what happened}
- **Why it {succeeded/stalled}:**
  - {Specific reasons with evidence from meetings/transcripts}

---

## Prior Attempts ({date range})

{For older/less detailed attempts, a consolidated section is fine}

### Pattern Analysis
{What consistently failed and why}

---

## Competitive Landscape

| Competitor | Status | Risk Level |
|------------|--------|-----------|
| ... | ... | ... |

---

## Success Criteria Summary

### Must-Win for POV
1. {Specific technical validation criteria}
2. {Key stakeholder sign-off needed}

### Must-Win for Deal
1. {Deal-level requirements}
2. {Blockers that need resolution}
```

#### Writing Guidelines

- **Be candid and analytical, not promotional.** This is an internal document for the deal team. Call out failures honestly. Quote stakeholders directly when possible.
- **Ground everything in evidence.** Reference specific meetings, dates, and what was said. Don't make claims without backing them up from the meeting history.
- **Lead with the executive summary.** A reader should understand the full deal history in 30 seconds from the exec summary alone.
- **Chronological within each initiative, reverse-chronological across initiatives.** Most recent/active initiative first, oldest last.
- **Use status labels consistently:** ACTIVE, PLANNED, EARLY, SUCCESS, STALLED, DEEMPHASIZED
- **Include LD team members.** Knowing who was involved helps with continuity when SEs change.
- **Flag what's different.** When an account has failed attempts, the most valuable analysis is articulating specifically what has changed that makes the current attempt viable.
- **Keep prior attempts concise.** The active initiative gets the most detail. Old attempts get enough detail to understand what happened and why, not a full blow-by-blow.

### Step 5: Export PDF

After writing the POV Summary, export it to PDF:

1. Create output directory: `mkdir -p "{config.pdf_path}/{YYYY-MM-DD}"`
2. Preprocess the markdown:
   - Remove any YAML frontmatter
   - Convert wiki-links (`[[Name]]`) to plain text
   - Convert Obsidian callouts (`> [!type]`) to bold headers
   - Add trailing spaces for line breaks on consecutive blockquote lines
   - Add `*Generated {YYYY-MM-DD}*` after the H1 title
3. Create CSS stylesheet at `/tmp/sales-pdf-style.css` (same as `/sales-pdf` skill)
4. Convert to HTML via pandoc:
   ```bash
   pandoc /tmp/sales-pov-{slug}.md -f markdown -t html5 --standalone --embed-resources \
     --css /tmp/sales-pdf-style.css --metadata pagetitle="{Account} POV Summary" \
     -o /tmp/sales-pov-{slug}.html
   ```
5. Start temp HTTP server: `cd /tmp && python3 -m http.server 18765 &`
6. Print to PDF via Playwright MCP:
   - Navigate to `http://localhost:18765/sales-pov-{slug}.html`
   - Print with Letter format, 0.5in margins, printBackground: true
   - Save to `{config.pdf_path}/{YYYY-MM-DD}/{YYYY-MM-DD} {Account} POV Summary.pdf`
7. Clean up: kill HTTP server, remove temp files

### Step 6: Report

```
POV Summary {created | updated} for {Account}

File: {Account}/POV Summary.md
PDF: {pdf_path}/{YYYY-MM-DD}/{YYYY-MM-DD} {Account} POV Summary.pdf

Initiatives documented:
- {Initiative 1} ({date range}) — {STATUS}
- {Initiative 2} ({date range}) — {STATUS}
...

Key insight: {single most important takeaway from the analysis}
```

### Update Mode

When `POV Summary.md` already exists:
- Read the existing document first
- Identify what's new since the last update (new meetings, new ledger entries, status changes)
- Update the relevant initiative sections with new data
- Update the Executive Summary if the overall picture has changed
- Don't rewrite sections that haven't changed — preserve existing analysis and just add new information
- Always regenerate the PDF

### Rules

- Never fabricate meeting content. If a meeting file is empty (no notes/transcript), note that explicitly.
- Quote stakeholders when their exact words matter (e.g., "If you want the sale, prove you can handle the AI piece quickly")
- Use the canonical product names from config
- Use canonical competitor spellings from config
- If the account has never had a POV or evaluation, create a minimal document noting the current state and what would need to happen
