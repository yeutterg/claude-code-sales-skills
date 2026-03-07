---
description: Create meeting notes for a sales account and link them in the daily note
argument-hint: <account> [topic] [date]
---

# Meeting Note

Create a meeting note for a sales account and link it in today's daily note.

## Arguments

- `account`: The account name (e.g., "Acme Corp", "Globex")
- `topic`: The meeting topic (e.g., "Experimentation Demo", "Discovery Call")
- `date` (optional): Meeting date in YYYY-MM-DD format. Defaults to today.

Example: `/sales-meeting Acme Corp Discovery Call`

## Instructions

### Pre-check: Verify Vault Path

Check that the Obsidian vault directory exists:
```bash
test -d "{config.vault_path}/{config.company_folder}/Accounts"
```
If the directory does not exist, stop and tell the user: "Obsidian vault not found. Run `/sales-setup` to configure your vault path and create the folder structure."

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract the following values:
- `vault_path` — path to the Obsidian vault
- `company_folder` — folder name for the company (e.g., "Acme Corp")
- `name` — user's full name
- `initials` — user's initials
- `company` — company name

Use these values wherever `{config.*}` placeholders appear below.

### Step 1: Parse Arguments

Extract the account name and topic from the arguments. The account name is typically one or two words, and the topic is the rest.

If the account name is ambiguous, check existing folders in `{config.vault_path}/{config.company_folder}/Accounts/`

**If no topic is specified (only account name provided), default the topic to "Call".**

Example: `/sales-meeting Acme Corp` → creates "2026-02-26 Call.md"

### Step 2: Determine Date

- If no date provided, use today's date
- Format: YYYY-MM-DD

### Step 3: Create Meeting File

**IMPORTANT: Always capitalize the topic in Title Case before creating the file.**

Examples:
- "prep call" → "Prep Call"
- "discovery" → "Discovery"
- "VP call" → "VP Call"
- "intro meeting" → "Intro Meeting"

Create the meeting note at:
`{config.vault_path}/{config.company_folder}/Accounts/{Account}/meetings/YYYY-MM-DD {Topic}.md`

Use this template (based on ld_meeting.md):

```markdown
---
account: "[[{Account}]]"
date: YYYY-MM-DD
gong_url: ""
attendees: []
---
## Tasks
- [ ]
## Summary
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
### Key Discussion Points
### Technical Details
### Next Steps
## External Summary
## Transcript
```

### Step 4: Get Account URLs and Team Names

Read the account file at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/{Account}.md`

Extract from frontmatter:
- `gong_url` - the Gong account URL
- `salesforce_opportunity` - the primary Salesforce opportunity URL
- `salesforce_opportunity_*` - any additional opportunity URLs (e.g., `salesforce_opportunity_expansion`, `salesforce_opportunity_renewal`)
- `ae` - the Account Executive name (e.g., `"[[Jane Doe]]"`)
- `csm` - the Customer Success Manager name (e.g., `"[[Bob Chen]]"`)

### Step 5: Update Daily Note

**IMPORTANT: Only add meetings to the daily note if the meeting date is today or in the future.**

- If meeting date < today (past meeting): **SKIP** - Do not add to daily note. These are historical meetings being retroactively documented.
- If meeting date = today: Add to `### Today` subsection
- If meeting date > today: Add to `### Upcoming` subsection

**Why skip past meetings?** Historical meetings that are being retroactively documented don't need to clutter the daily note with new todo items. Only current and future meetings need action items.

Find the daily note for **today** at `{config.vault_path}/Daily/YYYY-MM-DD.md` (use today's date, not the meeting date)

**Meeting section structure:**
```
## Meetings
### Today
- [meetings for today]
### Upcoming
- [meetings after today]
### Past
- [meetings before today that still need action]
```

Add a backlink to the appropriate subsection with nested todo items.

**CRITICAL: You MUST use the full path for BOTH the account link and the meeting link.**

**CRITICAL: You MUST include ALL FOUR standard checklist items for every meeting:**

1. Copy [Gong Transcript]({gong_url}) into meeting note
2. Run `/sales-summarize-account {Account}`
3. Run `/sales-salesforce {Account}` with linked Salesforce opportunities (see format below)
4. Send update to stakeholders: {stakeholder names from account frontmatter}

**Salesforce link format for checklist item 3:**
- If ONE opportunity (`salesforce_opportunity` only): `Run `/sales-salesforce {Account}` ([Salesforce]({url}))`
- If MULTIPLE opportunities: `Run `/sales-salesforce {Account}` ([Salesforce {label1}]({url1}), [{label2}]({url2}))` — where labels come from the key suffix (e.g., `salesforce_opportunity_renewal` → "renewal", `salesforce_opportunity_expansion` → "expansion"). The primary `salesforce_opportunity` is labeled "Salesforce" and additional ones use their suffix.
- If NO opportunity URLs in frontmatter: `Run `/sales-salesforce {Account}`` (no link)

Example for Acme Corp Discovery on 2026-02-06 (single opportunity):
```
### Today
- [[{config.company_folder}/Accounts/Acme Corp/Acme Corp|Acme Corp]]: [[{config.company_folder}/Accounts/Acme Corp/meetings/2026-02-06 Discovery|2026-02-06 Discovery]]
	- [ ] Copy [Gong Transcript](https://app.gong.io/...) into meeting note
	- [ ] Run `/sales-summarize-account Acme Corp`
	- [ ] Run `/sales-salesforce Acme Corp` ([Salesforce](https://yourcompany.my.salesforce.com/lightning/r/Opportunity/0061Q00000AbCdEFGH/view))
	- [ ] Send update to stakeholders: {AE name} {CSM name}
```

Example with multiple opportunities:
```
	- [ ] Run `/sales-salesforce Acme` ([Salesforce](https://yourcompany.my.salesforce.com/.../view), [renewal](https://yourcompany.my.salesforce.com/.../view))
```

**IMPORTANT:** The stakeholder names should be the actual AE and CSM names from the account frontmatter, not placeholder text. Format: `[[AE Name]] [[CSM Name]]`. If either field is empty in frontmatter, omit that name. If both are empty, still include the checkbox but just say "Send update to stakeholders".

**DO NOT use short links like `[[Acme Corp]]` or `[[2026-02-06 Discovery]]`** because they won't resolve correctly. Always use the full path format:
- Account: `[[{config.company_folder}/Accounts/{Account}/{Account}|{Account}]]`
- Meeting: `[[{config.company_folder}/Accounts/{Account}/meetings/YYYY-MM-DD {Topic}|YYYY-MM-DD {Topic}]]`

**Subsection creation:**
- If a subsection doesn't exist, create it in the order: Today, Upcoming, Past
- If the Meetings section doesn't exist, create it with all three subsections
- Add the meeting as a new bullet under the appropriate subsection

### Step 6: Confirm

Report:
- Path to the new meeting file
- If meeting is today or future: Confirmation that daily note was updated
- If meeting is in the past: Note that it was NOT added to daily note (historical meeting)

### Formatting

- No blank line between heading and first bullet
- No blank line between last bullet and next heading
- Sections flow directly into each other

### Rules

- If the account folder doesn't exist, ask before creating it
- If a meetings subfolder doesn't exist, create it
- Don't overwrite existing meeting files with the same name
- Use the exact account folder name (case-sensitive)
