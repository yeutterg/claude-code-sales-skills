---
description: Daily sales workflow — morning prep or evening wrap-up with calendar scan, Gong imports, account summaries, and Salesforce updates
argument-hint: [morning | evening]
---

# Daily Sales Workflow

Orchestrates the daily sales workflow based on time of day. In the morning, scans today's calendar and sets up meetings. In the evening, processes the day's meetings (Gong imports, summaries, Salesforce updates) and scans tomorrow's calendar. On Friday evenings through Monday mornings, also runs the weekly review.

Designed to be run as a scheduled task in Claude Desktop — set it to run daily in the evening after your last call.

## Arguments

- No arguments: Auto-detect morning (before noon) or evening (noon or later)
- `morning`: Force morning mode
- `evening`: Force evening mode

## Instructions

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract all config values.

If `calendar_configured` is not `true`, warn: "Google Calendar is not configured. Run `/sales-setup calendar` first. Skipping calendar scan." — continue with non-calendar steps.

### Step 1: Determine Mode and Day

Run `date "+%Y-%m-%d %H:%M %u %A"` to get:
- Current date
- Current time (for morning/evening detection)
- Day of week number (1=Monday, 7=Sunday)
- Day name

**Mode detection (if no argument provided):**
- Before 12:00 PM → morning mode
- 12:00 PM or later → evening mode

**Weekend detection:**
- If day is Friday (5) and mode is evening → set `run_weekly = true`
- If day is Saturday (6) or Sunday (7) → set `run_weekly = true`
- If day is Monday (1) and mode is morning → set `run_weekly = true`
- Otherwise → `run_weekly = false`

Report: "Running **{morning/evening}** workflow for **{Day, Month Date}**..."

---

## Morning Mode

### Morning Step 1: Scan Today's Calendar

Run `/sales-calendar` (no arguments — it will default to today since it's morning).

This creates meeting notes and daily note entries for today's meetings.

### Morning Step 2: Handle New Accounts

Check the `/sales-calendar` output for any **Unrecognized External Meetings** (meetings with external attendees that didn't match an existing account).

For each unrecognized meeting:
1. Run `/sales-create-account {Company Name}` to create the account folder
2. After creation, add checklist items to the daily note under the new meeting entry:
   ```
   - [[{Account}]]: [[{meeting path}|{meeting name}]]
   	- [ ] Paste Salesforce Opportunity URL into [[{Account}.md]] frontmatter `salesforce_opportunity:`
   	- [ ] Paste Gong Activity URL into [[{Account}.md]] frontmatter `gong_url:`
   	- [ ] Copy Gong transcript into meeting note
   	- [ ] Run `/sales-summarize-account {Account}`
   	- [ ] Run `/sales-salesforce {Account}`
   ```

Do NOT run `/sales-gong`, `/sales-summarize-account`, or `/sales-salesforce` for new accounts — the user needs to paste the Salesforce and Gong URLs first.

### Morning Step 3: Process Outstanding Items from Previous Days

Read the current daily note. Look for any **deal meeting entries from previous daily notes** that have been carried forward with unchecked items. These are entries under `### Past` in the `## Meetings` section.

For each account with unchecked items under `### Past`:

1. **If "Copy Gong Transcript" is unchecked:** Run `/sales-gong {account}` in scan mode to find and import any unimported Gong recordings for recent meetings.
2. **If "Run `/sales-summarize-account`" is unchecked:** Run `/sales-summarize-account {account}`.
3. **If "Run `/sales-salesforce`" is unchecked:** Run `/sales-salesforce {account}`.

Process accounts in parallel using subagents where possible.

Skip any account where the "Paste Salesforce Opportunity URL" or "Paste Gong Activity URL" checkboxes exist and are unchecked — the user hasn't provided the URLs yet.

### Morning Step 4: Weekly Review (if applicable)

If `run_weekly` is true, run `/sales-weekly`.

### Morning Step 5: Report

Output a summary:
```
Morning workflow complete.

## Calendar
- {N} meetings set up for today
- {N} new accounts created (pending Salesforce/Gong URLs)

## Catch-Up (from previous days)
- {N} Gong transcripts imported
- {N} accounts summarized
- {N} Salesforce updates pushed

## Pending Action
These accounts need your attention before they can be processed:
- {Account}: Paste Salesforce URL and Gong URL into account file

{If weekly ran: ## Weekly Review\n{weekly summary}}
```

---

## Evening Mode

### Evening Step 1: Process Today's Meetings

Read today's daily note. Look for deal meeting entries under `## Meetings` (any subsection: Today, Upcoming, Past) that have unchecked items.

For each account with unchecked items:

1. **If "Copy Gong Transcript" is unchecked:** Run `/sales-gong {account}` in scan mode. Gong typically processes calls within 1-2 hours, so evening is the ideal time to import.
2. **If "Run `/sales-summarize-account`" is unchecked:** Run `/sales-summarize-account {account}`.
3. **If "Run `/sales-salesforce`" is unchecked:** Run `/sales-salesforce {account}`.

Process accounts in parallel using subagents where possible.

Skip any account where "Paste Salesforce Opportunity URL" or "Paste Gong Activity URL" checkboxes exist and are unchecked.

### Evening Step 2: Scan Tomorrow's Calendar

Run `/sales-calendar tomorrow`.

This creates meeting notes and daily note entries for tomorrow's meetings.

### Evening Step 3: Handle New Accounts

Same as Morning Step 2 — create accounts for unrecognized external meetings and add the URL-paste checklist items.

### Evening Step 4: Weekly Review (if applicable)

If `run_weekly` is true, run `/sales-weekly`.

### Evening Step 5: Report

Output a summary:
```
Evening workflow complete.

## Today's Meetings Processed
- {N} Gong transcripts imported
- {N} accounts summarized
- {N} Salesforce updates pushed

## Tomorrow's Calendar
- {N} meetings set up for tomorrow
- {N} new accounts created (pending Salesforce/Gong URLs)

## Pending Action
These accounts need your attention before they can be processed:
- {Account}: Paste Salesforce URL and Gong URL into account file

{If weekly ran: ## Weekly Review\n{weekly summary}}
```

---

## Rules

- Never run `/sales-summarize-account` or `/sales-salesforce` on an account that has no `salesforce_opportunity` in its frontmatter — skip and report it in the "Pending Action" section
- Never run `/sales-gong` on an account that has no `gong_url` in its frontmatter — skip and report it
- When processing multiple accounts, use subagents to parallelize the work
- Check off daily note items as they are completed (change `- [ ]` to `- [x]`)
- If a Gong import fails (e.g., recording not yet available), leave the checkbox unchecked and note it in the report — it will be picked up on the next run
- If `/sales-weekly` is triggered, run it AFTER all daily processing is complete
- Do not ask for user input during the workflow — run autonomously from start to finish
- If Playwright MCP is not configured (`playwright_configured` is not true in config), skip all Gong import steps and note in the report: "Gong imports skipped — Playwright MCP not configured. Run `/sales-setup playwright` to enable."
