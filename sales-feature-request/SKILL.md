---
description: Identify missing product features customers have asked for, separating must-haves from nice-to-haves. Reads all meeting notes for an account and writes a categorized list with dates, sources, classification rationale, and status. Cross-account log enables pattern review.
argument-hint: <account name>
---

# Feature Requests

Surface every product feature the customer has asked for that {config.company} doesn't ship today, classified into Must-Have (deal-gating) and Nice-to-Have (wishlist) buckets.

This skill captures **gaps in {config.company}'s product** — things the customer has explicitly asked for that don't exist or aren't fully shipped. It is NOT a catalog of features they're already using, features they're considering using, or features the SE is positioning. The signal is: *the customer asked for X, and X is missing.*

## Arguments

- `account`: The account name (e.g., "Apple", "Acme Corp")

Example: `/sales-feature-request Apple`

## Instructions

You are helping a Solutions Engineer catalog the product gaps a customer has surfaced for the account: $ARGUMENTS

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `name`, `initials`, `company`, `products`.

### Pre-check: Verify Account

Check the account folder at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/`. Stop if missing: "Account not found. Run `/sales-create-account {Account}` first."

### Step 1: Discovery

1. Read the main account file `{Account}.md`. Note the current MEDDPICC Decision Criteria and CEP Key Risks — these will be cross-referenced in Step 4.
2. List all meeting files in `meetings/`.
3. List contact files in `contacts/` (used for resolving who raised each request — EB / Champion / IC).
4. From the account frontmatter, capture: `ae`, `se`, `csm`, `deal_type`. These help weight requests (a request from an EB carries more signal than a request from a junior IC).

### Step 2: Extract Requests via Parallel Subagents

Launch one subagent per meeting in parallel (single message, multiple Task tool calls, `subagent_type: general-purpose`, `model: sonnet`).

Each subagent prompt:

```
You are scanning a single {config.company} sales meeting note for **product feature requests** the customer made — gaps in {config.company}'s product they explicitly asked for.

Read the meeting file at: {full path}

Account frontmatter context:
- AE: {ae}, SE: {se}, CSM: {csm}
- Account contacts: {comma-separated contact filenames}

**What counts as a feature request:**
- Customer named a capability that {config.company} doesn't currently ship
- Customer asked "does X exist?" / "can LD do Y?" / "we need Z" and the answer was no, partial, or "on the roadmap"
- Customer flagged a workaround they're forced to use because the feature is missing
- Customer stated a hard requirement that maps to a known {config.company} product gap (FedRAMP High, specific compliance posture, integration that doesn't exist)

**What does NOT count:**
- Features the customer is already using or about to use (those go in Tech Stack / TECHMAPS)
- Features the SE is positioning that the customer hasn't asked for
- General competitive comparisons unless the customer named a specific missing capability
- Implementation help / RSA work / "how do I configure X"
- Sales education gaps ("they didn't know LD has Y") — those are SE follow-ups, not product gaps

**Classification heuristic — apply per request:**

MUST-HAVE signals (any one is enough; multiple compound):
- Customer language: "we need", "must have", "required", "won't proceed without", "deal blocker", "hard requirement", "non-negotiable", "if not on roadmap then..."
- Raised by Economic Buyer, CISO, CTO, VP-level, or named Champion
- Tied to compliance / security review / contract / legal red-line
- Mentioned in this meeting AND already in the account's MEDDPICC Decision Criteria as a dealbreaker
- Blocks an active POV milestone or stage gate

NICE-TO-HAVE signals:
- Customer language: "would be nice", "interesting", "wishlist", "future state", "long-term", "cool if you had..."
- Raised by IC / engineer attending an RSA session
- No urgency timeframe attached
- Customer offered a workaround they accept

UNCLASSIFIED:
- If you can't confidently place it, return "unclassified" and let the merge step decide.
- Default to nice-to-have when ambiguous, NEVER default to must-have.

For EACH feature request found, return a JSON object on a single line (NDJSON-style). If none, return an empty list.

Return EXACTLY this format and nothing else (no preamble, no commentary):

---BEGIN REQUESTS---
{"feature": "short name", "description": "one sentence on what they want", "classification": "must-have|nice-to-have|unclassified", "rationale": "why classified that way — quote the customer if possible", "raised_by": "Person Name (role)", "quote": "verbatim customer quote if available, else null", "context": "1-2 sentence context — what triggered the ask", "status": "open|on-roadmap|in-progress|shipped|declined|unknown", "status_evidence": "what makes you say that status, or null"}
{"feature": ...}
---END REQUESTS---
```

Aggregate the structured output from all subagents.

### Step 3: Merge + Dedupe

Many features will be raised across multiple meetings. Group them.

**Matching rule:** two requests refer to the same feature if EITHER (a) their `feature` names match (case-insensitive, ignoring articles/punctuation) OR (b) their `description` semantically describes the same capability. Use judgment — "post-auth IP allowlist for session tokens" and "UI IP allowlisting" and "session-based IP allowlist" are the same feature.

For each merged group, build a consolidated record:

```json
{
  "feature": "canonical name",
  "description": "best one-liner across all mentions",
  "classification": "must-have | nice-to-have | unclassified",  // see Step 4 for re-classification rules
  "all_mentions": [
    {"date": "YYYY-MM-DD", "meeting": "filename", "raised_by": "Name", "quote": "...", "context": "..."}
  ],
  "first_raised": "YYYY-MM-DD",
  "last_raised": "YYYY-MM-DD",
  "mention_count": N,
  "status": "open | on-roadmap | in-progress | shipped | declined | unknown",
  "status_evidence": "..."
}
```

### Step 4: Re-classify After Merge

After deduping, refine each request's classification using cross-mention signals:

1. **Frequency upgrade:** If `mention_count >= 3`, upgrade unclassified → must-have. If `mention_count >= 2` AND any mention quotes the customer using must-have language ("we need", "required", "blocker"), upgrade.
2. **Stakeholder upgrade:** If raised by anyone identified as Economic Buyer, Champion, CISO, CTO, or VP-level in the account contacts/MEDDPICC, upgrade → must-have.
3. **MEDDPICC cross-reference:** Read the account file's MEDDPICC > Decision Criteria. If a feature in our list maps to a Decision Criteria bullet AND that criteria is described as a hard requirement / dealbreaker, upgrade → must-have.
4. **CEP Key Risk cross-reference:** Read the account file's `## CEP Stage Analysis > **Key Risks:**` (if present). If a feature corresponds to a listed Key Risk, upgrade → must-have AND link the two in the rationale.
5. **Status downgrade:** If `status == "shipped"`, classification becomes `delivered` regardless of original tier — feature is no longer a gap.
6. **Anything still unclassified after the above → nice-to-have.** Never leave unclassified in the final output.

### Step 5: Status Enrichment

For each open request, look for status evidence:

- `shipped`: customer or SE confirmed in a more recent meeting that the feature now exists. Look for "now available", "GA'd", "we shipped", or a recent meeting where the SE demoed it.
- `in-progress`: SE has cited an internal ticket, EPIC, or PR. Look for phrases like "engineering is building", "in development", "scheduled for {quarter}".
- `on-roadmap`: SE confirmed it's planned but no firm date. Look for "on the roadmap", "Q{N} target", "next year".
- `declined`: SE or PM has explicitly said no / not planned. Look for "won't build", "not on roadmap", "out of scope".
- `open`: customer asked, no LD-side response committed.
- `unknown`: can't tell.

Default to `open` if unclear. Note any status evidence with a meeting reference so the rep can verify.

### Step 6: Write to Account File

Add or update a `## Feature Requests` section in the main account file. **Position: after `## Tech Stack` and before `## Architecture Diagram`.** If `## Architecture Diagram` doesn't exist, position before `## Salesforce Updates`.

Format:

```markdown
## Feature Requests

> [!summary] Feature Requests Summary
> **Must-Have (open):** {count} — {comma-separated short names}
> **Must-Have (in-flight/shipped):** {count} — {names}
> **Nice-to-Have (open):** {count}
> Last refresh: {YYYY-MM-DD}

### Must-Haves (deal-gating)

#### {Feature Name}
- **What:** {description}
- **Status:** {status} {status_evidence sentence if present}
- **First raised:** {M/D} by [[{Person}]] in [[meeting-link]]
- **Last raised:** {M/D} ({mention_count} total mentions across {N} meetings)
- **Why must-have:** {rationale — cite the customer quote, EB engagement, or MEDDPICC/CEP cross-reference}
- **Notable mentions:**
  - {M/D} [[meeting]] — {who} — "{quote or paraphrase}"
  - {M/D} [[meeting]] — {who} — "{quote or paraphrase}"
  - (cap at 3 most-significant mentions; collapse the rest into "+ N more mentions")

#### {Next Feature}
...

### Nice-to-Haves (wishlist)

#### {Feature Name}
- **What:** {description}
- **Status:** {status}
- **Raised:** {M/D} by [[{Person}]] in [[meeting]] ({mention_count} mention{s})
- **Context:** {1 sentence}

### Delivered (formerly requested, now shipped)

- **{Feature}** — shipped {date if known}; first asked {M/D} in [[meeting]]. Worth verifying customer is now using it.
```

**Formatting rules:**
- Use full wiki-link paths to meetings: `[[{config.company_folder}/Accounts/{Account}/meetings/{filename}|{display}]]` (display = filename without `.md`).
- Empty subsections (e.g., no Nice-to-Haves) → omit the H3 entirely. Don't render empty buckets.
- If there are 0 feature requests across all classifications, write a single line under `## Feature Requests`: `No outstanding feature requests surfaced from {N} meetings as of {date}.` and skip the subsections.

### Step 7: Surface in CEP Key Risks

For each **open Must-Have**, check the account file's `## CEP Stage Analysis > **Key Risks:**` block (if present). If the feature is NOT already listed, append a new Key Risk bullet matching the existing format:

```
- {Feature name} — open must-have ({first-raised} → {last-raised}, {mention_count}×) (S{current_stage})
```

This makes sure `/sales-meeting`'s Conviction-CEP-questions step (Step 2.5) picks up open must-have gaps as discovery questions on the next meeting.

If `## CEP Stage Analysis` doesn't exist on the account yet, skip this step silently — the next `/sales-cep` run will surface the gap on its own.

### Step 8: Append to Cross-Account Log

Append one line per feature request to `~/.claude/skills/sales-feature-request/requests.jsonl`:

```json
{"ts": "ISO timestamp", "account": "Apple", "feature": "name", "classification": "must-have", "status": "open", "first_raised": "YYYY-MM-DD", "last_raised": "YYYY-MM-DD", "mention_count": N, "raised_by_roles": ["EB", "Champion", "IC"], "deal_type": "{from frontmatter}"}
```

This enables future cross-account analysis: "which features are 5+ accounts asking for?" → feeds product-feedback meetings, EBR planning, and `/sales-review-learnings`.

**Dedup against prior runs:** before appending, read the existing `requests.jsonl` for entries matching `(account, feature)`. If a prior entry exists, replace it (don't duplicate). Keep only the most recent state per (account, feature).

### Step 9: Final Report to User

Print a compact summary:

```
Feature requests for {Account} (refreshed {date}):

Must-Haves (open): {N}
  1. {feature} — {mention_count}× since {first_raised}, last {last_raised}
  ...

Must-Haves (delivered/in-flight): {N}
  1. {feature} — {status}

Nice-to-Haves: {N}
  1. {feature} — {first_raised}

Wrote: {account file path} (## Feature Requests section)
Logged: {N} requests to ~/.claude/skills/sales-feature-request/requests.jsonl
{If CEP Key Risks were updated:} Added {M} open must-haves to CEP Key Risks.
```

## Rules

- **Customer-asked, not SE-positioned.** Only catalog what the customer raised. If the SE pitched it and the customer nodded, that's not a feature request — that's qualification.
- **Don't hallucinate features.** If a meeting transcript is thin and you can't tie the request to a quote or paraphrase from the customer, mark it unclassified and let merge/cross-reference upgrade it (or drop it).
- **Default to nice-to-have on ambiguity.** The rep can promote later. Inflating must-have count makes the section noise.
- **Quote the customer.** Paraphrase if no quote, but always show the source — meeting + speaker. This is the audit trail the SE needs when an open must-have stalls a deal.
- **Status defaults to `open`.** Don't claim a feature is shipped or on-roadmap without explicit evidence in a meeting.
- **Surface, don't filter.** Even if a feature is small / weird, list it. The cross-account log finds patterns.
- **Re-runnable.** This skill should overwrite the `## Feature Requests` section cleanly on each run. the rep's manual additions in that section will be lost — note this in the section header.
- **No write to ## Tasks**. Same rule as `/sales-summarize-account`.
