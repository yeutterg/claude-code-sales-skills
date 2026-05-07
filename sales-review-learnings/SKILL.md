---
description: Review patterns and insights discovered by skills — competitors, objections, feature requests, model performance, and template drift. Use when the daily note flags new skill learnings for review.
---

# Review Skill Learnings

Review and act on patterns discovered by `/sales-summarize-account` and `/sales-weekly`.

## Instructions

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract the `## Learnings` section.

### Step 1: Show Pending Discoveries

Read the `### Pending Review` section under `## Learnings > ### Discovered Patterns`.

If empty, tell the user: "No pending learnings to review." and stop.

Otherwise, group items by tag and present them:

```
## Pending Skill Learnings

### Competitors ({N} new)
- {Name}: {context} (from {Account}, {date})

### Objections ({N} new)
- {pattern}: {details} (from {Account}, {date})

### Feature Requests ({N} new)
- {request}: {context} (from {Account}, {date})

### Technical Patterns ({N} new)
- {pattern}: {details} (from {Account}, {date})

### Portfolio Insights ({N} new)
- {insight} ({date})
```

### Step 2: Ask for Action

For each category with items, ask:

> "For each item: **keep** (move to Reviewed), **act** (create a task in today's daily note), or **dismiss** (remove)?"

The user can respond with shorthand like "keep all competitors, dismiss objections, act on the feature request about X".

### Step 3: Process Decisions

- **Keep**: Move the item from `#### Pending Review` to `#### Reviewed` in `sales-config.md`
- **Act**: Create a task in today's daily note under the appropriate section ({config.company} for company-related items) and move to Reviewed
- **Dismiss**: Remove the item entirely

### Step 4: Show Model Performance

Read the `### Model Performance` table. If there are any task types with >20% failure rate, highlight them:

```
## Model Performance Alerts

- "contact-enrichment" on haiku: 40% failure rate (4/10 failed)
  → Recommendation: escalate to sonnet for this task type
```

If no alerts, say: "All models performing within acceptable ranges."

### Step 5: Show Template Drift

Read the `### Template Feedback` table. If any section has 3+ edits, highlight it:

```
## Template Drift

- MEDDPICC section edited 4 times (Acme Corp, Globex, Initech, Megacorp)
  → Common change: "User shortens bullet points"
  → Consider updating the summarize-account prompt to generate shorter bullets
```

If no drift, skip silently.

### Step 6: Show LD Product Learnings Queue

Read `~/.claude/skills/sales-product/learnings.md`. Surface every entry under `## Pending Queue` with `status: pending-review`, grouped by category:

```
## Pending LD Product Learnings

### Capability Gaps ({N} new)
- {YYYY-MM-DD-NNN} ({account}): {observation} → proposed: {section + change}

### Competitor Encounters ({N} new)
- {YYYY-MM-DD-NNN} ({competitor name}, {account}): {observation}

### Pricing Pushback ({N} new)
- {YYYY-MM-DD-NNN} ({account}): {observation}

### Customer Confusions ({N} new)
- {YYYY-MM-DD-NNN} ({account}): {confusion pattern}

### Tradeoff Revelations ({N} new)
- {YYYY-MM-DD-NNN} ({account}): {tradeoff}

### New Use Cases ({N} new)
- {YYYY-MM-DD-NNN} ({account}): {use case}

### Roadmap Mentions ({N} new)
- {YYYY-MM-DD-NNN} ({account}): {ask + LD response}
```

For each entry, ask the user: **promote** (merge into `~/.claude/skills/sales-product/knowledge.md`), **reject** (mark as rejected and archive), or **hold** (leave as `pending-review` for more signal).

**Promotion process** (per entry chosen for promote):
1. Read the proposed update from the entry
2. Find the target section in `knowledge.md`
3. Edit `knowledge.md` per the proposal (keep the rest of the file intact)
4. In `learnings.md`, change the entry's `status` from `pending-review` to `promoted`, add a `status-date`, and move the entry block from `## Pending Queue` to `## Promoted History (Archive)`
5. Append a one-liner under the archived entry noting the resulting `knowledge.md` change for audit trail

**Rejection process:**
1. In `learnings.md`, change `status: pending-review` to `status: rejected`, add `status-date`, and move the entry to `## Rejected History (Archive)`. Knowledge.md is not changed.

**Hold:** leave the entry where it is, no change.

The user can respond with shorthand like "promote all capability gaps, reject the customer confusions, hold the rest" and the skill processes per-category in batch.

If `~/.claude/skills/sales-product/learnings.md` has no pending entries, skip this step silently.

### Step 7: Clean Up

- Mark today's daily note task as complete if one exists
- Clear `pending_daily_surface` flag if set
- Report summary: "{N} ld-config items reviewed, {N} kept, {N} actioned, {N} dismissed; {N} ld-product items reviewed, {N} promoted, {N} rejected, {N} held"
