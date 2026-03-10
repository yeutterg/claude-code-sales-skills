---
description: Scan Google Calendar for upcoming meetings, match them to accounts, and auto-create meeting notes via /sales-meeting
argument-hint: [week | next week | YYYY-MM-DD]
---

# Calendar Meeting Setup

Scan Google Calendar for upcoming meetings, identify which ones map to existing accounts, and automatically create meeting notes and daily note entries. Suggests account creation for unrecognized companies.

## Arguments

- No arguments: Today (if morning) or tomorrow (if afternoon/evening)
- `week`: All meetings for the current week (Monday-Friday)
- `next week`: All meetings for the following week (Monday-Friday)
- `YYYY-MM-DD`: All meetings on a specific date
- `tomorrow`: Explicitly target tomorrow regardless of time of day

Example: `/sales-calendar`, `/sales-calendar week`, `/sales-calendar next week`

## Instructions

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract:
- `vault_path` -- path to the Obsidian vault
- `company_folder` -- folder name for the company
- `name` -- user's full name
- `initials` -- user's initials
- `calendar_id` -- Google Calendar ID to scan (e.g., `"user@company.com"`)
- `calendar_user_emails` -- list of the user's own email addresses to exclude from attendee lists
- `calendar_mode` -- `"all"` (deal + internal meetings), `"deals"` (deal meetings only)
- `calendar_include_prep` -- whether to create notes for deal prep meetings (true/false)
- `calendar_configured` -- whether calendar has been set up

If `calendar_configured` is not `true`, stop: "Google Calendar is not configured. Run `/sales-setup calendar` to set it up."

**Legacy config migration:** If the config has `calendar_accounts` (list) instead of `calendar_id` (string), use the first account in the list and note to the user that they should re-run `/sales-setup calendar` to update their config.

### Step 1: Determine Date Range

Get the current time and timezone by running `date` in the shell.

**Default behavior (no arguments):**
- If current time is **before 12:00 PM (noon)**: target = today
- If current time is **12:00 PM or later**: target = tomorrow

**With arguments:**
- `week`: Monday through Friday of the current week
- `next week`: Monday through Friday of the following week
- `tomorrow`: tomorrow's date
- `YYYY-MM-DD`: that specific date

Report: "Scanning calendar for {date range description}..."

### Step 2: Fetch Events

Call `mcp__claude_ai_Google_Calendar__gcal_list_events` with:
- `calendarId`: the `calendar_id` from config
- `timeMin` and `timeMax`: cover the target date range (full days, midnight to midnight), in RFC3339 format without timezone suffix
- `timeZone`: the user's local timezone (from the `date` command)
- `condenseEventDetails`: `false` (to get full attendee details)

**Filter out:**
- All-day events (these are not meetings)
- Events with no attendees (personal blocks, focus time)
- Events the user has declined (responseStatus = "declined")
- Events that are cancelled
- Events with summary "Busy" (Notion Calendar blocks)

#### 2b: Extract Event Agenda

For each event that passes the filter, check the event `description` field for agenda content. Calendar event descriptions often contain meeting agendas, discussion topics, or context set by the organizer.

**Extraction rules:**
- If the event has a `description` field with substantive content (not just a video call link or "Join Zoom Meeting" boilerplate), extract it as the event's **agenda**
- Strip out video conferencing boilerplate (Zoom/Teams/Google Meet join links, dial-in numbers, passcodes, "Do not edit this section" blocks)
- Strip out HTML tags — convert to plain text
- Preserve the meaningful content: agenda items, discussion topics, goals, context, links to documents
- Store the extracted agenda with the event for use in Step 4 (meeting note creation) and for the exec summary in `/sales-today`

### Step 3: Classify Each Event

For each remaining event, classify it into one of these categories:

#### 3a: Identify Existing Accounts

List all account folders in `{config.vault_path}/{config.company_folder}/Accounts/`. Build a lookup of:
- Account folder names (e.g., "Acme Corp", "Globex")
- For each account, read the frontmatter of `{Account}.md` to get any `aliases` field

**Match events to accounts** by checking (in order):
1. **Event title contains account name** (case-insensitive, partial match OK): e.g., "Globex Discovery" → Globex
2. **Event title contains an account alias**: e.g., "Globex Inc Demo" matches alias "Globex Inc"
3. **External attendee email domain matches a known account**: Read account frontmatter `website` or `domain` fields if available. Also try matching the company name against the domain (e.g., attendee `@globex.com` → "Globex")

**Categories:**
- **Deal meeting**: Event matches an existing account AND has external attendees (people not in `calendar_user_emails` and not from `{config.company}` email domain)
- **Deal prep meeting**: Event matches an existing account but has NO external attendees (internal prep/debrief for a deal). Common patterns: title contains "prep", "debrief", "internal", "sync" alongside an account name
- **Internal meeting**: No account match, no external attendees (team standup, 1:1s, all-hands, etc.)
- **External non-deal**: Has external attendees but doesn't match any account (potential new account or non-deal meeting)

#### 3b: Apply Mode Filter

Based on `calendar_mode`:
- `"all"`: Process deal meetings, deal prep (if `calendar_include_prep` is true), internal meetings, and external non-deal
- `"deals"`: Only process deal meetings and deal prep (if `calendar_include_prep` is true). Skip internal and external non-deal.

### Step 4: Create Meeting Notes

Process meetings in parallel where possible using subagents.

#### Deal Meetings (matched to account)

For each deal meeting, create a meeting note following the `/sales-meeting` pattern:

1. **Determine topic**: Extract the topic from the event title by removing the account name. If nothing remains, use "Call".
   - "Globex Discovery" → topic: "Discovery"
   - "Acme Corp" → topic: "Call"
   - "Technical Deep-Dive - Globex" → topic: "Technical Deep-Dive"

2. **Create meeting file** at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/meetings/YYYY-MM-DD {Topic}.md` using the same template as `/sales-meeting`:

```markdown
---
account: "[[{Account}]]"
date: YYYY-MM-DD
gong_url: ""
attendees:
  - "[[{config.name}]]"
  - "[[{Attendee 1 Name}]]"
  - "[[{Attendee 2 Name}]]"
---
## Tasks
- [ ]
## Summary
## Agenda
{If the event had an extracted agenda from Step 2b, insert it here as bullet points. Otherwise, leave this section empty.}
### Questions to Ask
{Generated questions — see Step 4, substep 4a/4b below.}
## Attendees
```dataview
TABLE WITHOUT ID file.link AS "Name", default(account, team) AS "Company/Team", role AS "Role", notes AS "Notes"
WHERE contains(this.attendees, file.link)
```
### New Customer Contacts
| Name | Role | Notes |
| ---- | ---- | ----- |
|      |      |       |
## Notes
## External Summary
## Transcript
```

3. **Populate attendees**: For each attendee NOT in `calendar_user_emails`:
   - Use the display name from the calendar event if available
   - If no display name, derive from email (capitalize first/last name parts)
   - Add as `"[[Display Name]]"` in the frontmatter attendees list
   - Also fill in the "New Customer Contacts" table with Name and any info available

4. **Generate questions and competitive context**: After creating the meeting file and reading the account file (for attendees/frontmatter), populate the `### Questions to Ask` section:

   **4a. Question bank** — Read the account file's MEDDPICC, TECHMAPS, and Command of the Message sections. Generate 3-5 targeted questions based on:
   - **MEDDPICC gaps**: Empty or thin fields → generate discovery questions (e.g., empty Decision Process → "Who else needs to evaluate this, and what does your approval process look like?")
   - **TECHMAPS gaps**: Missing technical details → generate technical discovery questions (e.g., empty Environment → "Can you walk us through your current deployment pipeline and infrastructure?")
   - **Meeting type**: Tailor questions to the meeting topic. Discovery calls need open-ended pain questions. Technical deep-dives need architecture questions. POV reviews need success criteria questions.
   - **Deal stage**: Early-stage deals need broader discovery. Late-stage deals need validation and closing questions.

   **4b. Competitive intelligence** — Read the account file's Competition section (under MEDDPICC) and the Ledger for any competitor mentions. If a competitor has been mentioned in this account:
   - Add a question about the competitor's current status: "Last time we spoke, {competitor} was also being evaluated — where does that stand?"
   - Cross-reference `~/.claude/skills/sales-config.md` learnings (`[competitor]` patterns) for insights from other accounts about the same competitor. If found, add a targeted question: e.g., "Other teams evaluating {competitor} have raised concerns about {issue} — is that something you've encountered?"
   - If no competitors mentioned yet but the account is in early stages, add: "Are you evaluating any other solutions alongside us?"

   Format each question as a bullet point in the `### Questions to Ask` section. Keep questions conversational and natural — not robotic.

5. **Update daily note** following `/sales-meeting` Step 5 rules:
   - Read account frontmatter for `gong_url`, `salesforce_opportunity*`, `ae`, `csm`
   - Add to the appropriate daily note subsection (Today/Upcoming/Past) with the standard 4-item checklist
   - Use full wiki-link paths

6. **Skip if file exists**: If a meeting file with the same name already exists, skip it and report it.

#### Deal Prep Meetings (if calendar_include_prep is true)

For each deal prep meeting:

1. Create a simpler meeting file at the same account meetings path: `YYYY-MM-DD {Account} Prep.md` (or use the event title if more descriptive)

```markdown
---
account: "[[{Account}]]"
date: YYYY-MM-DD
attendees:
  - "[[{config.name}]]"
  - "[[{Internal Attendee}]]"
---
## Tasks
- [ ]
## Notes
## Action Items
```

2. Add to daily note under the appropriate subsection, but with a simpler checklist:
```
- [[{path}|YYYY-MM-DD {Topic}]] (prep)
```

#### Internal Meetings (if calendar_mode is "all")

For each internal meeting, create a simple meeting note at the vault root (not under any account):

File: `{config.vault_path}/YYYY-MM-DD {Event Title}.md`

```markdown
---
date: YYYY-MM-DD
attendees:
  - "[[{config.name}]]"
  - "[[{Attendee Name}]]"
---
## Notes
```

Add to daily note under `## Meetings` (no subsection needed, no checklist):
```
- [[YYYY-MM-DD {Event Title}]]
```

If the file already exists, skip.

#### External Non-Deal Meetings

Create a meeting note at the vault root like internal meetings, but track the company for the end-of-run report.

### Step 5: Report Results

Output a structured summary:

```
Calendar scan complete for {date range}.

## Deal Meetings Created
| Account | Meeting | Date | Attendees |
|---------|---------|------|-----------|
| Acme Corp | Discovery | 3/10 | Jane Smith, Bob Chen |
| Globex | Technical Review | 3/10 | Tim Cook, Mark Zuckerberg |

## Deal Prep Meetings Created (or "Skipped — prep meetings disabled")
| Account | Meeting | Date |
|---------|---------|------|
| Acme Corp | Prep | 3/10 |

## Internal Meetings Created (or "Skipped — deals-only mode")
- 2026-03-10 Team Standup
- 2026-03-10 1:1 with Manager

## Skipped (already existed)
- Acme Corp: 2026-03-10 Discovery.md already exists

## Unrecognized External Meetings
These meetings have external attendees but don't match any account:

| Meeting | Attendees | Likely Company |
|---------|-----------|---------------|
| Intro Call with Contoso | dan@contoso.com | Contoso |
| Coffee Chat | jane@newstartup.io | New Startup |

Would you like to create accounts for any of these?
- `/sales-create-account Contoso`
- `/sales-create-account New Startup`
```

If there are unrecognized external meetings, ask the user: "Would you like me to run `/sales-create-account` for any of these? I can create the accounts and then set up the meeting notes."

If the user says yes for any, run `/sales-create-account` for each, then create the meeting notes for those events.

### Rules

- Never overwrite existing meeting files
- Always use Title Case for meeting topics
- Use full wiki-link paths in daily notes (same as `/sales-meeting`)
- Exclude the user's own emails from attendee lists
- When multiple events match the same account on the same day, create separate meeting files for each (append a distinguishing topic)
- If two events have the exact same account + topic + date, append a number: "Discovery 2"
- Handle timezone correctly: use the timezone from `get-current-time` for all date comparisons
- For multi-day ranges (week/next week), create all meeting files but only update daily notes for days that fall on today or in the future (skip past dates per `/sales-meeting` rules)
