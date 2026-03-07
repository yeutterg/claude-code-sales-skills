---
description: Import Gong calls or Granola meetings into Obsidian meeting notes, or bulk import all calls for an account
argument-hint: <account name> [gong_or_granola_url]
---

# Import Call Recording

Import Gong calls or Granola meetings into Obsidian meeting notes. Supports single URL import, Granola summary import, scan mode (match existing meetings to Gong recordings), and bulk import of all historical calls.

## Arguments

- `account`: The account name (e.g., "Acme Corp", "Globex")
- `url` (optional): A direct Gong call URL, Granola meeting URL, or Gong activity page URL

Examples:
- `/sales-gong Acme Corp https://app.gong.io/call?id=1234567890&account-id=9876543210` (single Gong call)
- `/sales-gong Acme Corp https://notes.granola.ai/t/abcd1234-5678-efgh-ijkl-mnopqrstuvwx` (Granola summary)
- `/sales-gong Globex` (scan for unimported Gong recordings)
- `/sales-gong Acme Corp https://app.gong.io/account/activity?id=...` (bulk import all calls)

## Prerequisites

### Playwright MCP Server

This skill requires the Playwright MCP server. If not already configured, add it to your Claude Code MCP settings:

```bash
claude mcp add playwright -- npx @playwright/mcp@latest --browser chromium
```

**Note:** You will likely need to authenticate in the Chromium browser each time you run this skill. Gong's SSO session expires frequently, so expect a login prompt on the first page load. Complete the authentication manually and the skill will continue automatically.

**Browser install:** If you get an error "Browser chromium is not installed", call `mcp__playwright__browser_install` to install it before retrying navigation.

## Instructions

You are helping a Solutions Engineer import call recordings for the account: $ARGUMENTS

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `name`, `initials`, `company`, `gong_workspace_id`. Use these values throughout the rest of this skill wherever `{config.*}` placeholders appear.

### Pre-check: Verify Vault Path

Check that the accounts directory exists:
```bash
test -d "{config.vault_path}/{config.company_folder}/Accounts"
```
If the directory does not exist, stop and tell the user: "Obsidian vault not found. Run `/sales-setup` to configure your vault path and create the folder structure."

### Pre-check: Verify Playwright MCP

Confirm the Playwright MCP tools are available by attempting to use `mcp__playwright__browser_navigate` or similar. If the tools are not available, tell the user to add the Playwright MCP server and restart.

### Step 1: Detect Mode and Parse Arguments

1. Extract the account name from the arguments
2. Verify the account directory exists at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/`
3. **Detect the mode:**
   - URL containing `gong.io/call` → **Single Gong Import** (go to Gong Path)
   - URL containing `granola.ai` → **Single Granola Import** (go to Granola Path)
   - URL containing `gong.io/account/activity` → **Bulk Import** (go to Bulk Path)
   - **No URL provided** → **Scan Mode** (go to Scan Path)

---

## Scan Path (no URL provided)

### Step 2S: Find Meetings Missing Gong Data

1. Read the account file at `{Account}.md` to get the `gong_url` from frontmatter (this is the Gong activity page URL)
2. If no `gong_url` exists, ask the user for the Gong account activity URL
3. List all meeting files in `meetings/` and read the frontmatter of each
4. Identify meetings that have an **empty `gong_url`** field — these are candidates for Gong import
5. Present the list to the user:

```
Found {N} meetings without Gong recordings:

| # | Date | Topic | Has External Summary? |
|---|------|-------|-----------------------|
| 1 | 2026-03-04 | Call | Yes (Granola) |
| 2 | 2026-02-23 | VP Call | No |
...

Checking Gong for matching recordings...
```

### Step 3S: Navigate to Gong Activity Page

1. Navigate to the Gong activity page URL using Playwright
2. **Login check:** If the page shows a login screen, tell the user to log in and wait for confirmation
3. Ensure the calls-only filter is active — check the "Calls only" checkbox. If not checked, click it.
4. Scroll through the call list to load all entries

### Step 4S: Match Gong Calls to Meeting Files

For each meeting file missing a `gong_url`:
1. Look for a Gong call on the **same date** in the activity list
2. If a match is found, extract the call title
3. If multiple calls exist for the same date, list all candidates

Present the matches and proceed with importing automatically — no confirmation needed.

### Step 5S: Import Each Matched Call

For each matched call, process it using the **Call Processing Steps** below. Both recorded and non-recorded calls are imported:
- **Recorded calls:** Extract attendees, brief, and transcript
- **Non-recorded calls:** Extract attendees only, update `gong_url` and attendees in frontmatter

Write the data to the existing meeting file using the Append Rules. Navigate back to the activity page for the next call.

Report progress after each import.

---

## Bulk Path (activity page URL provided)

### Step 2B: Navigate and Verify

1. Navigate to the Gong activity page URL using Playwright
2. **Login check:** If the page shows a login screen, tell the user to log in and wait for confirmation
3. Ensure the calls-only filter is active — check the "Calls only" checkbox. If not checked, click it.
4. **Save Gong URL to account file:** Update the account file's `gong_url` frontmatter field with the activity page URL if it's currently empty or different.

### Step 3B: Collect Call List

**Gong activity page layout:**
- **Left column:** A horizontal scrollable timeline of date markers, plus a vertical activity list below. Each entry shows: date header, time, call title, duration (if recorded), participant buttons with names/roles, and a summary snippet.
- **Right column / detail panel:** Details of the selected call, including attendee list, company groupings, and a "Go to call" link for recorded calls.

Scroll through the left column to load all calls (infinite scroll).

For each call entry, extract:
- **Date** of the call
- **Title/topic**
- **Duration** (if visible)

**Skip** missed/cancelled calls and calls where the summary says "reached the wrong person" or similar failed connections. Include calls with zero or missing duration — they may have participant info.

Present the list to the user:

```
Found {N} calls for {Account}:

| # | Date | Title | Duration |
|---|------|-------|----------|
| 1 | 2026-01-15 | Discovery Call | 45m |
| 2 | 2026-01-22 | Demo | 30m |
| 3 | 2026-01-28 | Check-in | -- |
...

Proceed with importing all {N} calls? Or specify which ones to skip (e.g., "skip 3, 5, 7").
```

**Do NOT wait for confirmation — proceed immediately with the import.** Only pause if the user explicitly asked to review first.

### Step 4B: Process Each Call

Process calls **sequentially** in the browser (they share a single browser session), but use **background subagents** for transcript processing. This creates a pipeline: while a subagent processes one call's transcript, the main agent navigates to the next call and extracts its brief.

**Optimized bulk import flow:**
1. Navigate to call page → extract brief from Briefs tab (default) → save brief to temp file
2. Click Transcript tab → snapshot auto-saves to tool-results file
3. Launch background subagent with brief file path + transcript file path
4. Immediately navigate to next call (don't wait for subagent)
5. Repeat

For each call:

1. **Check for existing meeting file** at `meetings/{YYYY-MM-DD} {Topic}.md`
   - If no file exists: use `/sales-meeting` to create one: `/sales-meeting {Account} {Topic} {YYYY-MM-DD}`
   - If file exists: proceed to populate it with Gong data
2. **Process the call** using the Call Processing Steps below
3. Navigate directly to the next call URL (faster than going back to activity page)
4. Report progress periodically (every 5-10 calls)

---

## Call Processing Steps (shared by Scan and Bulk paths)

These steps handle extracting data from a single Gong call and writing it to the meeting file.

### CP1: Click Call and Extract Attendees

1. Click the call entry in the left column to load details in the right panel
2. Extract **attendee names** from the participant list. Click "+N more" buttons to expand full lists.
3. Check if there's a **"Go to call" button** — this only appears for recorded calls

### CP2: Handle Non-Recorded Calls

If no "Go to call" button exists:
1. Update the meeting file's frontmatter:
   - Set `gong_url` to the activity page URL with the call selected
   - Set `attendees` as `"[[Name]]"` links
2. Done — proceed to next call

### CP3: Navigate to Call Page (Recorded Calls)

1. Click "Go to call" or navigate directly to the call page URL
2. **Important:** "Go to call" may open a new tab. Use `mcp__playwright__browser_tabs` to switch if needed.

### CP4: Extract Brief FIRST

**IMPORTANT: Extract the brief BEFORE clicking Transcript.** The Briefs tab is selected by default.

1. Extract the full brief text from the `tabpanel "Briefs"` region in the snapshot
2. This includes: Recap, Key Points, and Next Steps sections
3. Store this text for writing to the meeting file

### CP5: Extract Transcript via Subagent

1. Click the **"Transcript"** tab on the call page
2. The transcript snapshot will be very large (200-600KB+) and auto-saved to a tool-results file automatically when it exceeds the token limit
3. **Launch a background subagent** (`run_in_background: true`) to handle reading the transcript file and writing everything to the meeting file. For bulk imports, this allows you to continue navigating to the next call while the subagent processes.

**Brief storage for subagent:** Save the brief text to a temp file (e.g., `/tmp/gong_{date}_{topic}_brief.md`) before launching the subagent. This keeps the main agent's context clean and gives the subagent a reliable file to read.

Pass the subagent:
- The meeting file path
- The Gong call URL (for `gong_url` frontmatter)
- The attendee list (for `attendees` frontmatter) — resolve Gong display names to full names (e.g., "Gschultz" → "Geoff Schultz", "Pkandhari" → "Puneet Kandhari") using existing contact files in the account's `contacts/` folder
- The brief file path (saved in the step above)
- The path to the transcript snapshot file (the auto-saved tool-results file)
- The participant details (names, roles, talk percentages)

The subagent should:
1. Read the transcript snapshot file in chunks (500 lines at a time) and extract all transcript entries
2. Format the transcript with call title, date, duration, participants, and timestamped entries
3. Update the meeting file:
   - Set `gong_url` in frontmatter
   - Set `attendees` in frontmatter as `"[[Name]]"` links
   - **Append** brief text under `## External Summary` (see Append Rules below)
   - **Append** formatted transcript under `## Transcript` (see Append Rules below)

### CP6: Navigate Back

Close the call page tab or navigate back to the activity page.

---

## Gong Path (single call URL provided)

### Step 2G: Navigate and Extract Metadata

1. Navigate to the Gong call URL using Playwright
2. **Login check:** If the page shows a login screen, tell the user to log in and wait for confirmation
3. Extract from the call page:
   - **Call date** from the header (e.g., "May 21, 2025")
   - **Call title** from the page title or heading. The call title format varies by organization — extract the account name and topic from the page title or heading.
   - **Call duration** from the header
   - **Attendee names** from the meeting details overlay. Click "+N more" to expand if needed.
   - **Participant details** from the Speakers section (names, roles, talk percentages)

### Step 3G: Check for Existing Meeting File

Look for an existing meeting file matching the date and topic at:
`{config.vault_path}/{config.company_folder}/Accounts/{Account}/meetings/{YYYY-MM-DD} {Topic}.md`

The topic should be extracted from the Gong call title. Convert to Title Case.

- If a file exists: proceed to populate it with Gong data (don't skip it)
- If no file exists: use `/sales-meeting` to create one:
  ```
  /sales-meeting {Account} {Topic} {YYYY-MM-DD}
  ```

### Step 4G: Extract Brief

The **"Briefs"** tab is selected by default on the call page.

1. Extract the full brief text from the `tabpanel "Briefs"` region in the snapshot
2. This includes: Recap, Key Points, and Next Steps sections
3. Store this text for writing to the meeting file

### Step 5G: Extract Transcript via Subagent

1. Click the **"Transcript"** tab on the call page
2. The transcript snapshot will be very large (200-600KB+) and auto-saved to a tool-results file automatically when it exceeds the token limit
3. **Launch a subagent** to handle reading the transcript file and writing everything to the meeting file

**Brief storage for subagent:** Save the brief text to a temp file (e.g., `/tmp/gong_{date}_{topic}_brief.md`) before launching the subagent.

Pass the subagent:
- The meeting file path
- The Gong call URL (for `gong_url` frontmatter)
- The attendee list (for `attendees` frontmatter) — resolve Gong display names to full names using existing contact files
- The brief file path (saved in the step above)
- The path to the transcript snapshot file (the auto-saved tool-results file)
- The participant details (names, roles, talk percentages)

The subagent should:
1. Read the transcript snapshot file in chunks (500 lines at a time) and extract all transcript entries
2. Format the transcript with call title, date, duration, participants, and timestamped entries
3. Update the meeting file:
   - Set `gong_url` in frontmatter
   - Set `attendees` in frontmatter as `"[[Name]]"` links
   - **Append** brief text under `## External Summary` (see Append Rules below)
   - **Append** formatted transcript under `## Transcript` (see Append Rules below)

---

## Granola Path (Granola URL provided)

### Step 2R: Navigate and Extract Content

1. Navigate to the Granola URL using Playwright
2. **Dismiss prompts:** If a "Download Granola" dialog appears, click "Maybe later" to dismiss it
3. Take a snapshot of the page
4. Extract:
   - **Meeting title** from the page heading (h1)
   - **Meeting date** from the page metadata (e.g., "Yesterday", "Mar 4")
   - **Summary content** — the structured notes section with headers (e.g., "# Topic Name") and nested bullet points. Extract these preserving the markdown hierarchy.
   - **Note:** Shared Granola links only include the summary notes, NOT the transcript. There is no transcript to extract.

### Step 3R: Check for Existing Meeting File

Look for an existing meeting file matching the date at:
`{config.vault_path}/{config.company_folder}/Accounts/{Account}/meetings/{YYYY-MM-DD} *.md`

- If a file exists for that date: use it (proceed to populate)
- If no file exists: infer a topic from the Granola meeting title and use `/sales-meeting` to create one:
  ```
  /sales-meeting {Account} {Topic} {YYYY-MM-DD}
  ```

### Step 4R: Write Content to Meeting File

**Do NOT** store the Granola URL in the frontmatter (no `gong_url` or `granola_url` field).

1. **Append** the Granola summary under `## External Summary` (see Append Rules below)

---

## Append Rules (All Sources)

**CRITICAL: Never overwrite existing content in `## External Summary` or `## Transcript`.**

When writing to these sections:

1. **If the section is empty** (just the heading, no content below it):
   - Write the content directly under the heading

2. **If the section already has content:**
   - Add a subheading to distinguish the new content from the existing:
     - For Gong: `### Gong Brief` / `### Gong Transcript`
     - For Granola: `### Granola Summary`
   - Append the new content under the subheading, preserving all existing content above it

---

### Step 6: Report Result

After completion, report:

```
Imported: {YYYY-MM-DD} {Topic} (from {Gong|Granola})
  - File: meetings/{YYYY-MM-DD} {Topic}.md
  - Attendees: {count} people (if extracted)
  - Summary: {word count} words
  - Transcript: {word count} words
```

For Scan Mode and Bulk Import, report a summary table of all imports at the end:

```
Import Complete for {Account}

Imported: {N} calls
Skipped (already existed): {M} calls
Failed: {F} calls

Files:
- meetings/2026-01-15 Discovery.md (briefing + transcript)
- meetings/2026-01-22 Demo.md (briefing + transcript)
- meetings/2026-01-25 Check-in.md (attendees only, no recording)
...

Next steps:
- Run `/sales-summarize-account {Account}` to process all meeting notes
```

### Error Handling

- **Login required:** Pause and ask user to log in
- **No recording:** Still update the meeting file with attendees and `gong_url`. Log as "no recording" and continue.
- **Existing content:** Always preserve existing content. Append new data using subheadings.
- **No Gong URL in account file:** Ask the user for the Gong account activity URL
- **Gong rate limiting:** If Gong starts returning errors or showing CAPTCHAs, pause and tell the user.
- **Session timeout:** If the Gong session expires mid-import, pause and ask the user to re-authenticate.

### Notes

- Scan Mode imports Gong recordings into EXISTING meeting files that are missing `gong_url`. It does not create new meeting files.
- Bulk Import creates new meeting files for all calls found on the activity page.
- For Gong: The Briefs tab is extracted BEFORE clicking Transcript to avoid navigating back.
- For Gong: Transcript extraction is delegated to a subagent to keep the main agent's context window clean.
- For Granola: Shared links only contain summary notes (no transcript available).
- Calls are processed sequentially because they share a single Playwright browser session.
