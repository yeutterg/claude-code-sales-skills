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

### Morning Step 3: Generate Deal Prep & Recap

After the calendar scan, generate a short exec summary for each deal meeting scheduled. These summaries are organized by call/account so each one can be sent individually to the right stakeholders.

**Stakeholder identification:**

For each deal meeting, the "send to" list is:
1. The **AE** from the account frontmatter (`ae` field) — always included
2. Any other **internal {config.company} team members** on the calendar event invite (CSMs, managers, other SEs, leadership, etc.)

Look up internal attendees by matching calendar event attendee emails/names against known {config.company} team members. The user (SE) is excluded from the send list.

**How to build each prep summary:**

1. **For each deal meeting**, read the account file (`{Account}.md`) and check the calendar event attendees to understand who will be on the call. Extract:
   - **Who's on the call**: Look up each external attendee in the account's contacts folder. Note their role, seniority, and how they've participated in past meetings (from meeting notes and ledger). This shapes the entire summary — questions and insights should be relevant to the people actually in the room.
   - **Agenda from calendar**: `/sales-calendar` extracts agenda from the calendar event description (Step 2b). Include if present.
   - **MEDDPICC/TECHMAPS gaps relevant to these attendees**: Only flag gaps that the people on the call can actually address. A technical IC can't answer Paper Process questions. A VP can't answer SDK integration questions. Match gaps to attendee roles.
   - **Deal-moving actions**: Based on the account state and who's on the call, identify 1-2 things that would advance the deal.

2. **Write max 3-4 concise bullet points per meeting.** The *first bullet must always be the single biggest objective for the call* — what we absolutely need to walk away with. Remaining bullets are supporting context. Each bullet should be actionable, specific, and relevant to the attendees. Avoid generic advice. Shorter is better — these get copy-pasted into Slack.

**Add to daily note:**

Insert a new section `## Deal Prep` in the daily note, **after** `## Meetings`. Each meeting gets its own subsection with a send checkbox.

**IMPORTANT — Slack-compatible formatting:** The code block content will be copied from Obsidian into Slack. Use Slack-compatible markdown:
- `*bold*` for emphasis (Slack uses single asterisks, not double)
- `-` for bullet lists
- No em dashes (`—`). Use colons, periods, or line breaks instead.
- No wiki-links or Obsidian-specific syntax inside the blockquote
- Use bold liberally to make objectives and key names scannable

````
## Deal Prep
### {Account} | {meeting topic}, {time}
- [ ] Send to [[{AE Name}]], [[{Other Internal Attendee}]]
```markdown
Prep: {Day of Week}, {Mon} {Date}

*{Account}* | {meeting topic}, {time}
Attendees: [{Name}]({linkedin_url}) ({Role}, Champion), *{Name}* ({Role}, EB), *{Internal Name}*, *{Internal Name}*
- *OBJECTIVE:* {The single most important thing we need from this call}
- {Supporting context or insight tied to who's on the call}
- {Gap or action relevant to attendee roles}
```

### {Account 2} | {meeting topic}, {time}
- [ ] Send to [[{AE Name}]]
```markdown
Prep: {Day of Week}, {Mon} {Date}

*{Account 2}* | {meeting topic}, {time}
Attendees: *{Name}* ({Role}, Detractor)
- *OBJECTIVE:* {What we need to walk away with}
- {Supporting insight}
```
````

**Formatting rules:**
- Each meeting gets its own `### {Account} | {topic}, {time}` heading, send checkbox, and ` ```markdown ` code block
- The send checkbox lists the AE (always) plus any other internal team members on the calendar invite, as wiki-links: `- [ ] Send to [[AE Name]], [[CSM Name]], [[Manager Name]]`
- Wrap each meeting's content in a ` ```markdown ` fenced code block. Copy-paste the block content directly into Slack.
- Use Slack markdown inside code blocks: `*bold*` (single asterisk), `-` for lists
- *First bullet is always the call objective* in bold (`*OBJECTIVE:*`). This is the single biggest thing we need from this meeting. Be specific: "Get Lee to commit to workshop date" not "Discuss next steps."
- No em dashes (`—`). Use colons, periods, pipes, or line breaks instead.
- Use `|` as a separator in the heading and account header line (not em dash)
- **Times must be in Pacific time** (PT). When reading calendar events, use `timeZone: America/Los_Angeles` and append "PT" to times in the summary (e.g., "10:30 AM PT").
- Bold key names, amounts, dates, and action items so the summary is scannable
- **Attendee annotations:** After each attendee's role, add their MEDDPICC role in parentheses if they are an Economic Buyer (EB), Champion, Coach, or Detractor. Only add the label if it applies. Examples: `*Jane Smith* (Sr TPM, Champion)`, `*Tim Cook* (VP Platform Eng, EB)`, `*Bob Chen* (Dir Platform Eng, Detractor)`. If the person has no special MEDDPICC role, just show name and title.
- **LinkedIn hyperlinks:** If a contact has a `linkedin` field in their contact file, hyperlink their name using standard markdown link format: `[Name](https://linkedin.com/in/person)`. Slack renders these as clickable links when pasted. If no LinkedIn URL exists, just bold the name: `*Name*`.
- **List ALL attendees** from the calendar event, both internal ({config.company} team) and external (customer). Include everyone so stakeholders know exactly who will be in the room.
- **Roles and titles for customer attendees only.** Internal team members (AEs, SEs, CSMs, managers, etc.) are listed by name only, without role or company annotations. Customer attendees get their title and MEDDPICC role (if applicable).
- Start each account with the full attendee list
- Keep bullets short and punchy. One line each, no sub-bullets, max 3-4 per account
- Tailor insights to the attendees. If a VP is on the call, focus on business value and decision process. If an engineer is on the call, focus on technical gaps and integration questions. Don't suggest asking an IC about budget or a VP about SDK configuration.
- Reference past interactions with these specific people when possible ("Last call with {Name}, they mentioned X. Follow up.")
- **Order meetings chronologically** by time within the section.

#### Yesterday's Recap

After the prep section, add a recap of the previous day's deal meetings. This goes in a `## Deal Recap` section, after `## Deal Prep`.

**How to build the recap:**

1. Read the previous day's daily note. Find all deal meetings that occurred (under `## Meetings`).
2. For each meeting, read the meeting note (summary, notes, transcript) and the account's latest ledger entry.
3. Write 1-5 concise bullets per account focused on: what changed in the deal, key learnings, new risks or wins, and next steps committed.

**Stakeholders for recaps:** Same rule as prep — the AE plus any other internal team members who were on the calendar invite for the meeting that happened.

**Format in daily note:**

````
## Deal Recap
### {Account} | {meeting topic}
- [ ] Send to [[{AE Name}]], [[{Other Internal Attendee}]]
```markdown
Recap: {Day of Week}, {Mon} {Date}

*{Account}* | {meeting topic}
- {Key outcome or learning}
- {Deal change: new stakeholder, risk surfaced, next step locked, etc.}
```

### {Account 2} | {meeting topic}
- [ ] Send to [[{AE Name}]]
```markdown
Recap: {Day of Week}, {Mon} {Date}

*{Account 2}* | {meeting topic}
- {One-liner if nothing major changed}
```
````

**Recap rules:**
- Each meeting gets its own `### {Account} | {topic}` heading with a send checkbox listing stakeholders
- Be very concise. 1 bullet if nothing notable happened, up to 5 if the deal moved significantly.
- Focus on *what changed* and *what we learned*, not a rehash of the agenda.
- If a meeting had no notes or transcript yet, note that: "No notes captured yet."
- Include the recap even in morning mode (recap yesterday) and evening mode (recap today).

#### Coaching Tip

Generate **one coaching tip** based on analyzing the user's actual behavior in recent call transcripts. Add it to the daily note inside the `## Meetings` section, right after the section heading and before any subsection (`### Today`, etc.).

**How to generate the tip:**

1. **Read 3-5 recent transcripts** from the accounts on today's schedule (or the most recent transcripts if today has no scheduled meetings). Focus on the `## Transcript` sections, specifically the user's (SE's) speaking turns.

2. **Analyze the SE's behavior in the transcripts.** Look for specific, concrete patterns — cite the account name and what happened. Categories to watch for:

   - **Talk ratio**: Is the SE talking too much vs. listening? In discovery calls, the customer should be talking 60-70% of the time. In demos, the SE talks more but should still pause for reactions.
   - **Question quality**: Is the SE asking open-ended questions that uncover pain ("Walk me through what happens when a deploy fails") or closed ones that get yes/no answers ("Do you use feature flags?")? Are they following up on pain statements or moving on too quickly?
   - **Solutioning too early**: Does the SE jump to "here's how we solve that" before fully understanding the problem? Does the customer get to articulate the full impact before the SE starts pitching?
   - **Pausing and listening**: Does the SE pause after asking a question, or fill the silence? Does the SE talk over the customer or interrupt?
   - **Tying back to pain**: During demos, does the SE connect each capability to the customer's stated pain, or just show features in isolation?
   - **Next steps and commitment**: Does the SE confirm specific next steps with owners and dates at the end of calls, or leave it vague ("we'll follow up")?
   - **Stakeholder mapping**: Does the SE ask who else should be involved, who the decision maker is, or what the approval process looks like?
   - **Competitive positioning**: When competitors come up, does the SE acknowledge and differentiate, or dismiss? Does the SE probe what the customer liked about the competitor?
   - **Quantifying impact**: Does the SE help the customer put numbers on the pain ("How many hours per week does that cost your team?") or leave it qualitative?
   - **Technical depth calibration**: Does the SE match the technical depth to the audience? Too deep for execs, too shallow for engineers?

3. **Pick the single most impactful observation** — something specific from a real transcript, not a generic best practice. Reference the actual account and moment.

**Format in daily note:**

```
## Meetings
> [!tip] Coaching
> {One specific, actionable tip that references what actually happened in a recent call. Example: "In the Acme Corp discovery (3/4), you asked 'Do you use canary deployments?' and got a yes/no. Try instead: 'Walk me through your current release process step by step' — that would've uncovered the manual QA bottleneck they mentioned later without prompting."}
### Today
...
```

**Coaching Log:**

Read the coaching log at `{config.vault_path}/{config.company_folder}/Resources/Coaching Log.md` before generating the tip. If the `Resources/` folder or `Coaching Log.md` file doesn't exist, create them:

```bash
mkdir -p "{config.vault_path}/{config.company_folder}/Resources"
```

Then create `Coaching Log.md` with this template:

```markdown
---
type: coaching-log
---

## Playbook

Personalized scripts and techniques refined from transcript analysis. The coaching system checks these during tip generation and flags deviations.

## Active Focus Areas

## Retired

## Tip History
```

This file tracks:

- **Playbook**: Personalized scripts and techniques (introductions, objection handling, etc.) refined from transcript analysis. When generating tips, check if the user deviated from their own playbook — that's a high-value coaching moment.
- **Active Focus Areas**: Patterns currently being worked on, with observation dates and frequency
- **Retired**: Patterns the user has improved on
- **Tip History**: Chronological log of every tip given

**How to use the log:**

1. **Before generating a tip**, read the log. Check Active Focus Areas for recurring patterns. Prioritize following up on an active pattern over introducing a new one.

2. **Check for improvement.** When reading today's transcripts, compare against Active Focus Areas. If the user demonstrably improved on a pattern (e.g., they paused after a question when they previously didn't), note the improvement:
   - Update the Active Focus Area entry with "Improvement seen: {date}, {account}"
   - If improved consistently across 3+ calls, move to Retired with a note
   - Make today's coaching tip a positive reinforcement: "In the {Account} call, you did X. That landed well because Y. Keep it up."

3. **Check the Playbook.** If the log has a `## Playbook` section with personalized scripts (introductions, objection handling, etc.), compare the user's actual behavior in transcripts against their playbook. Deviations are high-value coaching moments — "You have a tight 15-word AI intro in your playbook, but in the Acme call you fell back to the 3-sentence version."

4. **Generate the tip.** Either:
   - **Flag a playbook deviation** with the specific moment and the playbook script they should have used
   - **Follow up** on an active pattern with a new example from today's transcripts
   - **Introduce a new pattern** if all active areas are improving or retired
   - **Reinforce improvement** if the user fixed something

5. **Update the log** after generating the tip:
   - Add to Tip History: `- M/D: {tip summary} | Account: {account} | Focus: {category} | Status: {new/recurring/improved/retired}`
   - If this is a new pattern, add it to Active Focus Areas with the date and account
   - If following up on an existing pattern, increment the count in Active Focus Areas

**Rules:**
- Exactly one tip per day — keep it focused
- **Must be grounded in a real transcript.** Reference the account name and the specific moment. If no transcripts exist yet, skip the coaching tip entirely rather than giving generic advice.
- Never give the same tip twice in a row. Check Tip History.
- Be constructive and specific. Quote or paraphrase what the SE actually said, then suggest what would have been more effective and why.
- Focus on high-leverage patterns — things that, if changed, would meaningfully improve deal outcomes. Don't nitpick minor phrasing.
- **Celebrate wins.** When improvement is real, say so. Positive reinforcement builds habits faster than constant critique.

### Morning Step 4: Process Outstanding Items from Previous Days

Read the current daily note. Look for any **deal meeting entries from previous daily notes** that have been carried forward with unchecked items. These are entries under `### Past` in the `## Meetings` section.

For each account with unchecked items under `### Past`:

1. **If "Copy Gong Transcript" is unchecked:** Run `/sales-gong {account}` in scan mode to find and import any unimported Gong recordings for recent meetings.
2. **If "Run `/sales-summarize-account`" is unchecked:** Run `/sales-summarize-account {account}`.
3. **If "Run `/sales-salesforce`" is unchecked:** Run `/sales-salesforce {account}`.

Process accounts in parallel using subagents where possible.

Skip any account where the "Paste Salesforce Opportunity URL" or "Paste Gong Activity URL" checkboxes exist and are unchecked — the user hasn't provided the URLs yet.

### Morning Step 5: Export PDFs (if enabled)

If `pdf_export` is `true` in config, run `/sales-pdf` for all deal accounts that appear in the AE Exec Summaries (Step 3) — both prep accounts (today's meetings) and recap accounts (yesterday's meetings). This ensures every deal the user is briefing their AE on has a fresh PDF ready to share.

Collect the list of unique account names from both the prep and recap sections, then run `/sales-pdf {account}` for each one.

### Morning Step 6: Weekly Review (if applicable)

If `run_weekly` is true, run `/sales-weekly`.

### Morning Step 7: Report

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

{If pdf_export enabled: ## PDFs Exported\n- {N} account PDFs exported to {pdf_path}}

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

### Evening Step 4: Generate Deal Prep & Recap for Tomorrow

Same as Morning Step 3, but for tomorrow's deal meetings. Generate deal prep for each meeting scheduled tomorrow.

Add the `## Deal Prep` and `## Deal Recap` sections to **today's** daily note (the day the workflow runs), using the same format as Morning Step 3. This keeps all prep and recap content in one place for the user to review tonight.

### Evening Step 5: Export PDFs (if enabled)

If `pdf_export` is `true` in config, run `/sales-pdf` for all deal accounts that appear in the AE Exec Summaries (Step 4) — both prep accounts (tomorrow's meetings) and recap accounts (today's meetings). This ensures every deal the user is briefing their AE on has a fresh PDF ready to share.

Collect the list of unique account names from both the prep and recap sections, then run `/sales-pdf {account}` for each one.

### Evening Step 6: Weekly Review (if applicable)

If `run_weekly` is true, run `/sales-weekly`.

### Evening Step 7: Report

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

{If pdf_export enabled: ## PDFs Exported\n- {N} account PDFs exported to {pdf_path}}

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
- If `pdf_export` is `true` in config, run `/sales-pdf` after Deal Prep and Deal Recap are generated in both morning and evening modes. Export all deal accounts that appear in the prep or recap sections — not just accounts summarized during this run. This ensures fresh PDFs are available for every deal being briefed.
