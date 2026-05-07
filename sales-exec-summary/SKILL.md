---
name: ld-exec-summary
description: Generate a 1-page executive summary for an LD account, anchored on customer-confirmed signal and tied to canonical product capabilities. Four modes (migration / pov-recap / deal-brief / exec-readout). Reads MEDDPICC + TECHMAPS + recent meetings from the account file, plus /sales-product/knowledge.md for product capability mappings and inline doc URLs. Outputs a clean 1-page PDF the SE can walk into a customer or stakeholder call with. Use when the user wants a tight LD-flavored exec summary for an account, especially before customer calls where conviction matters.
---

# LD Executive Summary Generator

Generate a 1-page LD-specific exec summary for an account. Distilled from the patterns refined through the Acme Corp migration plan iterations: customer-language anchoring, customer-confirmed metrics + scale + stated business direction, arrow notation for deltas, required-capability mapping table with inline LD docs, positive outcome framing, no FOMO, no em-dashes.

## Arguments

- `<account>` (required): Account name (e.g., `Acme Corp`, `Initech`, `Globex`)
- `<mode>` (optional, default `deal-brief`): one of:
    - `migration`: replace homegrown / competitor system with LD; multi-phase plan with phase-by-phase capability deployment
    - `pov-recap`: distilled POV plan summary for an exec stakeholder; condensed from `/sales-pov` output
    - `deal-brief`: executive deal brief for internal alignment / leadership readout
    - `exec-readout`: post-meeting exec brief from a specific recent meeting
- `[meeting <YYYY-MM-DD or topic>]` (optional, only for `exec-readout`): which meeting to recap

Examples:
- `/sales-exec-summary Acme Corp migration`
- `/sales-exec-summary Initech pov-recap`
- `/sales-exec-summary Globex deal-brief`
- `/sales-exec-summary Stark Industries exec-readout meeting 2026-05-05`

## Inheritance

- `/obsidian-format`: no em-dashes (BLOCKER), markdown rules
- `/effective-communication`: sentence craft + persuasion + narrative principles
- Inherits the canonical product knowledge from `~/.claude/skills/sales-product/knowledge.md`

## Pre-check: Read Config + Inputs

1. Read `~/.claude/skills/sales-config.md` for `vault_path`, `company_folder`, `name`, `pdf_path`
2. Verify account folder at `{vault_path}/{company_folder}/Accounts/{Account}/`
3. Read `~/.claude/skills/sales-product/knowledge.md` for canonical capability descriptions, doc URLs, common confusions
4. Read the account file (`{Account}.md`):
    - Frontmatter: salesforce_opportunity, ae, csm, deal stage, deal amount, close date
    - **MEDDPICC**: Metrics (customer-confirmed only; flag discovery gaps), Economic Buyer, Champion, Identified Pain, Competition, Decision Criteria
    - **TECHMAPS**: T/E/C/H/M/A/P/S statuses with Findings + Risks
    - **Command of the Message**: Required Capabilities, Compelling Event, Business Value
5. Read recent meetings (last 45 days from `meetings/`, newest first; cap at 8 most recent + any older meeting flagged pivotal in Ledger)
6. Read `Ledger.md` (most recent 10 entries)

## Mode: `migration`

For customers replacing a homegrown system or competitor product with LD. Anchored on the next high-value initiative the customer is already running.

### Structure

1. **Title:** `Migration Plan: {Account} {Source System} to LaunchDarkly`
    - Source system: name from MEDDPICC > Competition (e.g., "Homegrown Flag System") or generic "Existing System" if not named.
2. **Subtitle:** `*Prepared {YYYY-MM-DD} for [[{Champion or EB}]] and {Account} leadership.*`
3. **Recommendation** (bullets, with bold falsifiable lead):
    - Bold lead: `**{N}-month, SDK-first migration anchored on {Account}'s next {specific high-value initiative}.**`
        - Recommended N: 3-6 months for mid-market; 6-12 months for enterprise. Use customer's stated urgency from MEDDPICC > Compelling Event.
        - Specific initiative: name a real customer-confirmed initiative from MEDDPICC > Identified Pain or Compelling Event (e.g., Acme Corp's "8-cohort payment-platform rollout"), NOT what we wish they'd buy.
    - Sub-bullet block: `End-to-end {their stated #1 capability from MEDDPICC > Decision Criteria} operational from Phase 1.`
    - Nested outcomes block:
        - Header: `**Outcomes at {Account}'s scale** ({customer-confirmed scale facts; cite source})`:
        - 2-4 sub-bullets, each with arrow notation: `{operational metric}: **{current state} → {target state}**`
        - Use customer-confirmed metrics from MEDDPICC > Identified Pain. Bold the deltas. Tie to stated business direction (compelling event) where possible.
    - Boundary conditions bullet at end: `Phase 2 does not start if Phase 1 misses success criteria. {Out-of-scope condition, e.g., "Legacy flags untouched in N months are out of scope."}`
4. **Phase 1 ({0-N months}): {next initiative ships on LD}**
    - **Anchor:** the named initiative
    - **Deploy:** `[SDK]({sdk_url}) + [{capability}]({url}) + [{capability}]({url}) + [{capability}]({url})`. Pull canonical names + URLs from `/sales-product/knowledge.md`.
    - **Success criteria (co-signed pre-kickoff):** one-sentence list (cycle target, blast-radius cap, validation event).
    - **{Account} effort:** team size + sprint count
5. **Phase 2 ({N1-N2 months}): {expansion scope}**
    - All net-new flags on LD; existing system enters maintenance mode
    - **Add:** capabilities to layer in (with inline LD doc URLs)
    - **Outcome:** quantified compression metrics
6. **(Optional) Phase 3 ({N2-N3 months}): selective legacy migration** — only if N3 ≤ 12 months
7. **What LaunchDarkly Delivers (Mapped to Your Required Capabilities)**
    - Two-column table: customer's stated capability (from MEDDPICC > Decision Criteria + TECHMAPS > Technical Requirements) → LD capability that delivers it (from `/sales-product/knowledge.md`, with inline doc URLs)
    - Order rows by customer-engagement priority (heaviest engagement on calls first)
    - Drop rows for capabilities the customer DIDN'T engage with (don't oversell). Quality bar: only include capabilities surfaced in MEDDPICC > Decision Criteria, TECHMAPS > Technical Requirements, or recent meeting notes.
    - Common confusions: when a row maps to a product the customer has confused with another (per `/sales-product/knowledge.md` Common Confusions Index), include a parenthetical note (e.g., "Workflows + Guarded Releases pair: Workflows for cadence, Guarded Releases for metric gate").

## Mode: `pov-recap`

Distilled POV plan summary, written for an exec audience (one level above the technical evaluator). Different shape than `/sales-pov`'s full POV plan.

### Structure

1. **Title:** `POV Recap: {Account}`
2. **Subtitle:** `*Prepared {date} for {EB or exec sponsor} | {AE} | {SE}.*`
3. **POV scope** (1 bullet): one sentence on what's being validated.
4. **Why now** (2-3 bullets): the compelling event from MEDDPICC, customer-confirmed, in customer's language.
5. **Success criteria** (3-5 bullets, co-signed): falsifiable outcomes with named evaluators per criterion.
6. **Status today** (table): each criterion → status (NOT STARTED / IN PROGRESS / VALIDATED / BLOCKED) → blocker if any.
7. **Risks to close** (max 3 risks, ranked, each one paragraph): risk + evidence + named mitigation. Pull from `/sales-pov` content if it exists, else extract from TECHMAPS > Risks per dimension.
8. **Decision needed from exec** (bullet): the specific ask. (POV go-ahead / Phase 2 funding / specific blocker resolution.)

## Mode: `deal-brief`

Executive deal brief for internal alignment / leadership readout. Less customer-facing; more deal-team-facing.

### Structure

1. **Title:** `Deal Brief: {Account}`
2. **Subtitle:** `*Internal | Prepared {date} | {Stage} | ${Amount} | Close {date}.*`
3. **Deal shape** (3-4 bullets): champion, EB, current stage, what's blocking progression.
4. **Where we are** (2-3 bullets): what's true today (most recent meeting outcomes, MEDDPICC delta since last brief).
5. **Top risks** (max 3, ranked): with named mitigation owner.
6. **Asks** (bullet list): what the deal team needs from leadership / cross-functional partners (named asks per stakeholder).
7. **Key dates** (bullet list): next milestones with owners.

## Mode: `exec-readout`

Post-meeting executive brief from a specific recent meeting. Provides leadership the key signal without making them read the full meeting note.

### Structure

1. **Title:** `Meeting Readout: {Account} | {Topic} | {Date}`
2. **Subtitle:** `*Internal | {Attendees}*`
3. **Three things that changed** (3 bullets, max 1 line each): the deal-state delta from this meeting.
4. **Three things that surfaced** (3 bullets): pain / capability / objection signal worth tracking.
5. **What we committed to** (bullet list): named commitments with owners + due dates.
6. **What they committed to** (bullet list): named customer commitments with owners + due dates.
7. **What's at risk if next step misses** (1-2 bullets): the cost of the meeting failing to land its commitment.

## Output

1. Write the markdown file to `{vault_path}/{company_folder}/Accounts/{Account}/{YYYY-MM-DD} {mode-title} {Account}.md`
    - mode-title examples: "Migration Plan", "POV Recap", "Deal Brief", "Meeting Readout"
2. Mirror the inline LD doc URLs throughout (every product mention links).
3. Apply `/obsidian-format` rules: no em-dashes (use colons / parens / arrows), no horizontal rules, wiki-links for people / accounts, fenced summary callout where relevant.
4. Generate PDF to `{pdf_path}/{YYYY-MM-DD}/{YYYY-MM-DD} {Account} {mode-title}.pdf` using the same preprocessing pattern as `/sales-pov` and `/create-pdf`:
    - Strip frontmatter
    - Resolve wiki-links to plain text (`[[Name]]` → `Name`, `[[A|B]]` → `B`)
    - Strip dataview blocks
    - Render via pandoc + Playwright at Letter size with 0.5in margins
    - Style: 10pt body, 1.4 line-height, blue-dark hyperlinks, table at 9pt
    - Verify single-page output: `mdls -name kMDItemNumberOfPages` must return 1; if 2, tighten and regenerate

## Quality Bar (the load-bearing rules)

These are the rules that make the difference between a generic 1-pager and a high-conviction one:

1. **Anchor on a customer-named initiative they're already running.** Not what we want them to buy. Not a hypothetical use case. A real, named, in-flight initiative from MEDDPICC > Identified Pain or Compelling Event. (Acme Corp example: 8-cohort payment-platform rollout.)
2. **Use customer's language for capabilities.** Their phrase for "end-to-end rollout management in one platform" stays as their phrase, not as our product names. The Required Capabilities table maps customer-language → product-language; the recommendation stays in customer-language.
3. **Customer-confirmed metrics only.** Operational metrics from MEDDPICC > Identified Pain are customer-confirmed and safe to cite. Public-earnings facts are OK with provenance label. Discovery gaps stay flagged honestly; never fabricate KPIs in $$ / conversion / NPS that haven't been customer-confirmed.
4. **Bold the deltas.** Arrow notation: `{current state} → {target state}` with bold formatting. Customers scan this in milliseconds. The bolding does the work.
5. **Inline LD doc URLs for every product mention.** The customer treats them as homework. Pull from `/sales-product/knowledge.md` (single source of truth).
6. **Drop rows / bullets that don't have customer engagement.** Don't oversell. If the customer didn't engage with Experimentation on calls, it stays out of the table. The table reflects what THEY asked for.
7. **Common confusions surface.** When a customer-asked capability has known confusion patterns from `/sales-product/knowledge.md` (e.g., Workflows vs Guarded Releases), include a clarifying parenthetical in the mapping row. Defuses the confusion before it becomes a blocker.
8. **Positive outcome framing by default.** Lead with what they gain, not what they lose. Loss-aversion only when explicitly invoked (override the default with the user's request).
9. **No em-dashes.** Use colons / commas / parens / arrows. (Standing rule from `/obsidian-format`.)
10. **Boundary conditions explicit.** Every recommendation names what gates progression and what's out of scope. Without this, the doc is wishful; with it, the doc is governance-grade.
11. **Single page.** Always. If 2 pages, the doc isn't tight enough. Tighten cells and bullets, not font (font stays readable at 10pt body).

## Rules

- Never fabricate customer commitments. If MEDDPICC fields are empty, surface as discovery gaps.
- Never oversell capabilities the customer hasn't engaged with. The mapping table reflects customer-asked capabilities, not our wishlist.
- Always pull canonical product names + URLs from `/sales-product/knowledge.md`. If a capability isn't in `knowledge.md`, flag the gap so the user can update.
- Always run the single-page check on the generated PDF. If it's 2 pages, fix and regenerate before reporting complete.
- Run autonomously per memory `feedback_no_input_evening.md`: do not ask for input mid-generation. If account data is incomplete, surface gaps in the output rather than blocking.

## Cross-References

- `/sales-product` (`~/.claude/skills/sales-product/knowledge.md`): canonical capability info + URLs
- `/sales-pov`: full POV plan generator (different from this skill's `pov-recap` mode, which is a distilled exec version)
- `/sales-techmaps`: canonical TECHMAPS framework
- `/sales-pdf`: PDF export for full account files
- `/1-page-exec-summary`: vendor-agnostic 1-pager (this skill is the LD-specific equivalent)
- `/effective-communication`: sentence-craft and persuasion principles inherited
- `/obsidian-format`: markdown formatting rules inherited
