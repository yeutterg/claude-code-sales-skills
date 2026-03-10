---
description: Daily sales workflow — morning prep or evening wrap-up with calendar scan, Gong imports, account summaries, and Salesforce updates
argument-hint: [morning | evening] [no gong]
---

# Daily Sales Workflow

Orchestrates the daily sales workflow based on time of day. In the morning, scans today's calendar and sets up meetings. In the evening, processes the day's meetings (Gong imports, summaries, Salesforce updates) and scans tomorrow's calendar. On Friday evenings through Monday mornings, also runs the weekly review.

Designed to be run as a scheduled task in Claude Desktop — set it to run daily in the evening after your last call.

## Arguments

- No arguments: Auto-detect morning (before noon) or evening (noon or later)
- `morning`: Force morning mode
- `evening`: Force evening mode
- `no gong`: Skip all Gong import steps (useful for automated/scheduled runs where Gong auth may not be available). Can be combined with morning/evening: `/sales-today evening no gong`, `/sales-today no gong`

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

**Flag detection:**
- If arguments contain `no gong` (case-insensitive): set `skip_gong = true`. Remove `no gong` from the arguments before parsing mode.

**Mode detection (if no mode argument provided):**
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

### Morning Step 3: Generate AE Exec Summaries

After the calendar scan, generate a short exec summary for each AE who has deal meetings scheduled. These summaries help the user prep their AEs before calls.

**How to build the summaries:**

1. **Group today's deal meetings by AE**: For each deal meeting created in Step 1, read the account frontmatter `ae` field. Group all accounts under the same AE.

2. **For each account, read the account file** (`{Account}.md`) and also check the calendar event attendees to understand who will be on the call. Extract:
   - **Who's on the call**: Look up each external attendee in the account's contacts folder. Note their role, seniority, and how they've participated in past meetings (from meeting notes and ledger). This shapes the entire summary — questions and insights should be relevant to the people actually in the room.
   - **Agenda from calendar**: `/sales-calendar` extracts agenda from the calendar event description (Step 2b). Include if present.
   - **MEDDPICC/TECHMAPS gaps relevant to these attendees**: Only flag gaps that the people on the call can actually address. A technical IC can't answer Paper Process questions. A VP can't answer SDK integration questions. Match gaps to attendee roles.
   - **Deal-moving actions**: Based on the account state and who's on the call, identify 1-2 things that would advance the deal.

3. **Write max 3-4 concise bullet points per account.** Each bullet should be actionable, specific, and relevant to the attendees. Avoid generic advice. Shorter is better — these get copy-pasted into Slack.

**Add to daily note:**

Insert a new section `## AE Exec Summaries` in the daily note, **after** `## Meetings`. Format it as a Slack-ready text block per AE with a checkbox to send.

**IMPORTANT — Slack-compatible formatting:** The blockquote content will be copied from Obsidian into Slack. Use Slack-compatible markdown:
- `*bold*` for emphasis (Slack uses single asterisks, not double)
- `-` for bullet lists
- No wiki-links or Obsidian-specific syntax inside the blockquote

```
## AE Exec Summaries
### {AE Name}
- [ ] Send exec summary to [[{AE Name}]]
> *{Account 1}* — {meeting topic}, {time}
> Attendees: {Name} ({Role}), {Name} ({Role})
> - {Agenda or context, if available}
> - {Insight tied to who's on the call — e.g., "Last time we met with Sarah she flagged X — follow up on that"}
> - {Gap or action relevant to attendee roles}
>
> *{Account 2}* — {meeting topic}, {time}
> Attendees: {Name} ({Role})
> - {Concise insight}
> - {Deal-moving action}

### {AE Name 2}
- [ ] Send exec summary to [[{AE Name 2}]]
> *{Account 3}* — {meeting topic}, {time}
> Attendees: {Name} ({Role}), {Name} ({Role})
> - ...
```

**Formatting rules:**
- Use a Markdown blockquote (`>`) for the summary body so it's easy to select and copy into Slack
- Use Slack markdown inside blockquotes: `*bold*` (single asterisk), `-` for lists
- Start each account with attendee names and roles so the AE knows who to expect
- Keep bullets short and punchy — one line each, no sub-bullets, max 3-4 per account
- Tailor insights to the attendees. If a VP is on the call, focus on business value and decision process. If an engineer is on the call, focus on technical gaps and integration questions. Don't suggest asking an IC about budget or a VP about SDK configuration.
- Reference past interactions with these specific people when possible ("Last call with {Name}, they mentioned X — follow up")

#### Coaching Tip

While reading account files and meeting history for the exec summaries, also generate **one coaching tip** for the user. Add it to the daily note inside the `## Meetings` section, right after the section heading and before any subsection (`### Today`, etc.).

**How to generate the tip:**

Review recent meeting notes (transcripts, summaries, external summaries) across the accounts on today's schedule. Look for one concrete, specific thing the user could improve:

- **Verbal patterns**: Filler words, talking over the customer, jumping to solutioning before fully understanding the problem, not pausing after asking a question
- **Discovery technique**: Asking closed questions when open ones would uncover more, not following up on pain statements, missing opportunities to quantify business impact
- **Demo/technical flow**: Spending too long on setup before showing value, not tying features back to stated pain, skipping the "so what" after a capability demo
- **Meeting management**: Not setting an agenda upfront, not confirming next steps at the end, not assigning owners to action items
- **Stakeholder engagement**: Not asking who else should be involved, not confirming the champion's priorities, not validating assumptions from previous calls
- **Competitive handling**: Dismissing competitors instead of acknowledging and differentiating, not probing what the customer liked about a competitor

Pick the **single most impactful** observation. If there aren't enough transcripts to find a real pattern, base it on the types of meetings scheduled today (e.g., "Discovery calls are most effective when you let the customer describe their current workflow before introducing any product concepts").

**Format in daily note:**

```
## Meetings
> [!tip] Coaching
> {One specific, actionable sentence. No generic advice — reference a real pattern observed or a technique relevant to today's meeting types.}
### Today
...
```

**Rules:**
- Exactly one tip per day — keep it focused
- Never repeat the same tip on consecutive days (check previous daily notes if they exist)
- Be specific and constructive, not vague ("Try pausing 3 seconds after asking about their decision process — in the last Acme call you jumped in before they finished answering" is good; "Ask better questions" is bad)
- If no transcripts exist yet (new user or new accounts), tailor the tip to the meeting types on the schedule

### Morning Step 4: Process Outstanding Items from Previous Days

Read the current daily note. Look for any **deal meeting entries from previous daily notes** that have been carried forward with unchecked items. These are entries under `### Past` in the `## Meetings` section.

For each account with unchecked items under `### Past`:

1. **If "Copy Gong Transcript" is unchecked:** Run `/sales-gong {account}` in scan mode to find and import any unimported Gong recordings for recent meetings.
2. **If "Run `/sales-summarize-account`" is unchecked:** Run `/sales-summarize-account {account}`.
3. **If "Run `/sales-salesforce`" is unchecked:** Run `/sales-salesforce {account}`.

Process accounts in parallel using subagents where possible.

Skip any account where the "Paste Salesforce Opportunity URL" or "Paste Gong Activity URL" checkboxes exist and are unchecked — the user hasn't provided the URLs yet.

### Morning Step 5: Weekly Review (if applicable)

If `run_weekly` is true, run `/sales-weekly`.

### Morning Step 6: Report

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

### Evening Step 4: Generate AE Exec Summaries for Tomorrow

Same as Morning Step 3, but for tomorrow's deal meetings. Generate exec summaries for each AE with accounts scheduled for tomorrow.

Add the `## AE Exec Summaries` section to **tomorrow's** daily note (since that's the day the meetings are on), using the same format as Morning Step 3.

### Evening Step 5: Weekly Review (if applicable)

If `run_weekly` is true, run `/sales-weekly`.

### Evening Step 6: Report

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
- If Playwright CLI is not configured (`playwright_configured` is not true in config), skip all Gong import steps and note in the report: "Gong imports skipped: Playwright CLI not configured. Run `/sales-setup playwright` to enable."
- If `skip_gong` is true (from `no gong` argument), skip all Gong import steps. Leave Gong transcript checkboxes unchecked — they will be picked up on a future manual run. Note in the report: "Gong imports skipped: `no gong` flag set." Still proceed with `/sales-summarize-account` and `/sales-salesforce` for accounts that already have transcripts.
