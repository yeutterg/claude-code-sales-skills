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

### Playwright CLI

This skill requires the Playwright CLI for browser automation. Install from [microsoft/playwright-cli](https://github.com/microsoft/playwright-cli):

```bash
npm install -g @playwright/cli@latest
playwright-cli install
```

**Note:** You will likely need to authenticate in the browser each time you run this skill. Gong's SSO session expires frequently, so expect a login prompt on the first page load. Complete the authentication manually and the skill will continue automatically.

## Playwright CLI Reference

Key commands used by this skill:

```bash
# Open browser (always use --headed --persistent for Gong)
playwright-cli -s={session} open {url} --headed --persistent

# Take page snapshot (returns element refs for clicking)
playwright-cli -s={session} snapshot

# Click an element by ref
playwright-cli -s={session} click {ref}

# Scroll the page
playwright-cli -s={session} mousewheel 0 {pixels}

# Run JavaScript on the page (MUST use arrow function syntax)
playwright-cli -s={session} eval "() => document.title"
playwright-cli -s={session} eval "() => { var x = 1; return x; }"

# Tab management (for parallel call processing)
# NOTE: tab-new opens a blank tab. Use tab-select + goto to navigate it.
playwright-cli -s={session} tab-new about:blank
playwright-cli -s={session} tab-select {index}
playwright-cli -s={session} goto {url}
playwright-cli -s={session} tab-list
playwright-cli -s={session} tab-close {index}

# Auth state management (transfer auth between sessions)
playwright-cli -s={session} state-save /tmp/gong_auth_state.json
playwright-cli -s={other_session} state-load /tmp/gong_auth_state.json

# Close session
playwright-cli -s={session} close
```

**CRITICAL `eval` rules:**
- Always wrap code in an arrow function: `"() => expression"` or `"() => { statements; return value; }"`
- Do NOT use regex literals inside eval — they cause "not well-serializable" errors. Use `string.indexOf()` or `new RegExp()` instead.
- Example (WRONG): `eval "() => /foo/.test(x)"`
- Example (RIGHT): `eval "() => x.indexOf('foo') >= 0"`

**Video/audio pausing:** Always pause media on call pages to avoid playing recordings:
```bash
playwright-cli -s={session} eval "() => { var v = document.querySelectorAll('video,audio'); for (var i = 0; i < v.length; i++) { v[i].pause(); v[i].muted = true; } return 'ok'; }"
```

**Data extraction via eval:** Prefer `eval` over `snapshot` for extracting text content. It's faster and returns content directly:
```bash
# Extract brief text
playwright-cli -s={session} eval "() => { var panel = document.querySelector('[role=tabpanel]'); return panel ? panel.innerText : 'none'; }"

# Click a specific tab by text content
playwright-cli -s={session} eval "() => { var tabs = document.querySelectorAll('[role=tab]'); for (var i = 0; i < tabs.length; i++) { if (tabs[i].textContent.indexOf('Transcript') >= 0) { tabs[i].click(); return 'clicked'; } } return 'not found'; }"
```

**Browser refocusing:** The `--headed` flag causes the browser window to refocus on every interaction. There is no workaround currently — warn the user that the browser will steal focus during import.

## Instructions

You are helping a Solutions Engineer import call recordings for the account: $ARGUMENTS

### CRITICAL: Never Skip Gong Imports

**Gong imports are MANDATORY for every call that has a recording.** Follow these rules without exception:

1. **Never skip a Gong import because the meeting file already has notes.** User-pasted notes, Granola summaries, and manually typed content do NOT replace Gong data. Gong briefs and transcripts are always imported alongside existing content using the Append Rules.
2. **The only valid reason to skip a call is if Gong has no recording** (voicemail, missed call, cancelled call, or "no recording" indicator on the call page).
3. **If authentication fails** (SSO expired, login page shown, session timeout), do NOT skip the import. Instead:
   - Tell the user: "Gong authentication required. Please log in to the browser window."
   - Wait for the page to load the expected content (poll every 5 seconds up to 2 minutes)
   - If auth still fails after 2 minutes, remind the user again
   - Never give up — keep prompting until the user authenticates or explicitly tells you to stop
4. **Existing `gong_url` in a meeting file does NOT mean it was already imported.** The URL may have been set without the brief/transcript being extracted. Always check if `## External Summary` and `## Transcript` sections have Gong content before skipping.

### Execution Strategy
When processing multiple Gong calls, use subagents to process each call in parallel. Fan out for reads/extraction, fan in for writes.

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `name`, `initials`, `company`, `gong_workspace_id`. Use these values throughout the rest of this skill wherever `{config.*}` placeholders appear.

### Pre-check: Verify Vault Path

Check that the accounts directory exists:
```bash
test -d "{config.vault_path}/{config.company_folder}/Accounts"
```
If the directory does not exist, stop and tell the user: "Obsidian vault not found. Run `/sales-setup` to configure your vault path and create the folder structure."

### Pre-check: Derive Session Name

Create a unique Playwright session name for this account by converting the account name to a lowercase slug (spaces → underscores, remove special characters). For example:
- "Acme Corp" → `gong_acme_corp`
- "Globex Industries" → `gong_globex_industries`

Use this as the `-s={session}` value in all `playwright-cli` commands.

### Pre-check: Verify Playwright CLI

Check that Playwright CLI is available:
```bash
which playwright-cli
```
If not available, tell the user to install it: `npm install -g @playwright/cli@latest && playwright-cli install`

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
3. List all meeting files in `meetings/` and read the frontmatter and content of each
4. Identify meetings that are candidates for Gong import. A meeting needs Gong import if ANY of these are true:
   - The `gong_url` field is empty (never checked)
   - The `gong_url` is set BUT `## External Summary` has no "Gong Brief" content and `## Transcript` has no "Gong Transcript" content (URL was set but data wasn't extracted)
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

1. Open the browser and navigate to the Gong activity page:
   ```bash
   playwright-cli -s=gong_{account_slug} open {gong_activity_url} --headed --persistent
   ```
2. **Login check:** Take a snapshot and check if the page URL contains `sign-in`. If so, tell the user to log in and wait for them to confirm.
3. Ensure the calls-only filter is active. Use eval to check the checkbox state:
   ```bash
   playwright-cli -s=gong_{account_slug} eval "() => { var cb = document.querySelector('input[type=checkbox][class*=calls-only], .calls-only-checkbox input'); return cb ? cb.checked : 'not found'; }"
   ```
   If not checked, take a snapshot and click the "Calls only" checkbox ref.

### Step 4S: Extract Call List from Activity Page

Use JavaScript eval to extract all calls from the DOM:

```bash
playwright-cli -s=gong_{account_slug} eval "() => { var items = document.querySelectorAll('.activity-item.call-activity'); var results = []; for (var i = 0; i < items.length; i++) { var item = items[i]; var title = item.querySelector('.activity-title'); var dateGroup = item.closest('.activity-items-wrapper'); var dateEl = dateGroup ? dateGroup.querySelector('.activity-date') : null; var dur = item.querySelector('[class*=styles-module]'); var text = item.innerText; var isVoicemail = text.indexOf('voicemail') >= 0; results.push({ i: i, date: dateEl ? dateEl.textContent : '', title: title ? title.textContent : '', duration: dur ? dur.textContent.trim().split('\\n')[0] : '', voicemail: isVoicemail }); } return JSON.stringify(results); }"
```

### Step 5S: Get Call URLs

Click each call entry and extract the "Go to call" URL from the right panel:

```bash
# Click call entry N
playwright-cli -s=gong_{account_slug} eval "() => { var items = document.querySelectorAll('.activity-item.call-activity'); items[{N}].click(); return 'clicked'; }"
# Wait briefly, then extract URL
sleep 0.8
playwright-cli -s=gong_{account_slug} eval "() => { var link = document.querySelector('a[href*=\"/call?\"]'); return link ? link.href : 'none'; }"
```

### Step 6S: Match and Import

For each meeting file missing a `gong_url`:
1. Find a Gong call on the **same date** in the extracted call list
2. If matched, process using the **Parallel Import** steps below

Present matches and proceed immediately. Never ask for confirmation.

---

## Bulk Path (activity page URL provided)

### Step 2B: Navigate and Verify

1. Open the browser and navigate to the Gong activity page:
   ```bash
   playwright-cli -s=gong_{account_slug} open {activity_page_url} --headed --persistent
   ```
2. **Login check:** Snapshot and check if the page URL contains `sign-in`. If so, tell user to log in and wait.
3. Ensure the calls-only filter is active. Snapshot, check the checkbox.
4. **Save Gong URL to account file:** Update the account file's `gong_url` frontmatter field with the activity page URL if it's currently empty or different.

### Step 3B: Collect Call List

Use the JavaScript eval approach from Step 4S above to extract all calls. Scroll down to load all entries if needed:

```bash
playwright-cli -s=gong_{account_slug} mousewheel 0 5000
```

Then re-extract the call list to pick up any newly loaded entries.

**Auto-skip** these calls (do not import):
- Voicemail calls (`innerText.indexOf('voicemail') >= 0`)
- Missed/cancelled calls
- Calls where the text mentions "reached the wrong person" or similar

### Step 4B: Get All Call URLs

Click each non-skipped call entry sequentially and extract the "Go to call" URL:

```bash
for each call index N:
  playwright-cli -s=gong_{account_slug} eval "() => { document.querySelectorAll('.activity-item.call-activity')[{N}].click(); return 'clicked'; }"
  sleep 0.8
  playwright-cli -s=gong_{account_slug} eval "() => { var link = document.querySelector('a[href*=\"/call?\"]'); return link ? link.href : 'none'; }"
```

Collect all URLs before proceeding to import.

Present the list, then **proceed immediately with the import. Never ask for confirmation.**

```
Found {N} calls for {Account} ({M} skipped: voicemail/missed):

| # | Date | Title | Duration |
|---|------|-------|----------|
| 1 | 2026-01-15 | Discovery Call | 45m |
| 2 | 2026-01-22 | Demo | 30m |
...

Importing all {N} calls...
```

### Step 5B: Pre-create Meeting Files

Before launching any subagents, create all needed meeting files:

For each call:
1. Parse the date from the Gong date string (e.g., "Tue, Jan 27" → 2026-01-27, "Mar 17, 2025" → 2025-03-17)
2. Extract topic from the call title (remove account name patterns like "Acme Corp<>YourCompany", "Acme Corp <> YourCompany |", "Call with Acme Corp -")
3. Check if `meetings/{YYYY-MM-DD} {Topic}.md` exists
4. If not, create it with `/sales-meeting {Account} {Topic} {YYYY-MM-DD}`

### Step 6B: Parallel Import

Use the **Parallel Import** steps below to process all calls.

---

## Parallel Import (used by Bulk and Scan paths)

Process calls in parallel using browser tabs. Open up to 3 call pages simultaneously in the same browser session, extract data from each, then launch subagents to write to meeting files.

### Pipeline

1. **Open a batch of tabs** (up to 3 calls at once). Tab 0 uses `goto`, additional tabs use `tab-new` + `tab-select` + `goto`:
   ```bash
   # Tab 0: navigate existing tab
   playwright-cli -s=gong_{account_slug} goto {call_url_1}
   # Tab 1: open new tab and navigate
   playwright-cli -s=gong_{account_slug} tab-new about:blank
   playwright-cli -s=gong_{account_slug} goto {call_url_2}
   # Tab 2: open new tab and navigate
   playwright-cli -s=gong_{account_slug} tab-new about:blank
   playwright-cli -s=gong_{account_slug} goto {call_url_3}
   ```
   Wait 2-3 seconds for pages to load. **Verify each tab loaded** by selecting it and checking the page title or URL — stale/blank tabs produce garbage data.

2. **Pause all videos** on every tab immediately after loading:
   ```bash
   for tab in 0 1 2:
     playwright-cli -s=gong_{account_slug} tab-select {tab}
     playwright-cli -s=gong_{account_slug} eval "() => { var v = document.querySelectorAll('video,audio'); for (var i = 0; i < v.length; i++) { v[i].pause(); v[i].muted = true; } return 'ok'; }"
   ```

3. **Extract briefs from all tabs** — select each tab, click Briefs tab, extract via eval, save to temp file:
   ```bash
   playwright-cli -s=gong_{account_slug} tab-select {tab}
   playwright-cli -s=gong_{account_slug} eval "() => { var tabs = document.querySelectorAll('[role=tab]'); for (var i = 0; i < tabs.length; i++) { if (tabs[i].textContent.indexOf('Brief') >= 0) { tabs[i].click(); break; } } return 'ok'; }"
   playwright-cli -s=gong_{account_slug} eval "() => { var panel = document.querySelector('[role=tabpanel]'); return panel ? panel.innerText : 'none'; }"
   ```
   Save the result to `/tmp/gong_brief_{date}_{slug}.md`

4. **Extract transcripts from all tabs** — click Transcript tab on each, wait for content to load, then extract via eval:
   ```bash
   playwright-cli -s=gong_{account_slug} tab-select {tab}
   playwright-cli -s=gong_{account_slug} eval "() => { var tabs = document.querySelectorAll('[role=tab]'); for (var i = 0; i < tabs.length; i++) { if (tabs[i].textContent.indexOf('Transcript') >= 0) { tabs[i].click(); break; } } return 'ok'; }"
   sleep 1
   playwright-cli -s=gong_{account_slug} eval "() => document.querySelector('[role=tabpanel]').innerText"
   ```
   Save the result to `/tmp/gong_transcript_{date}_{slug}.txt`. **Verify** the transcript is non-empty before saving — if the tab panel returned empty or very short content, wait another second and retry.

5. **Close extra tabs** (keep tab 0 for the next batch). Close in reverse order to avoid index shifting:
   ```bash
   for i in {tab_count-1} down to 1:
     playwright-cli -s=gong_{account_slug} tab-close {i}
   ```
   **Important:** Always close ALL extra tabs before starting the next batch. Leftover tabs from a previous batch will have stale content and cause data corruption if accidentally read.

6. **Launch background subagents** (`run_in_background: true`) for each call in the batch. Each subagent reads the brief and transcript temp files and writes to the meeting file using Append Rules. Subagents don't need the browser — they only do file I/O.

7. **Repeat** for the next batch of 3 calls. Don't wait for subagents — proceed immediately to the next batch of browser extractions.

The main agent handles all browser interaction. Subagents handle file writing in parallel. This maximizes throughput while using a single browser session.

---

## Call Processing Steps (for extracting data from a call page)

These steps apply to whichever tab/page is currently showing a Gong call.

### CP1: Extract Attendees

1. Take a snapshot of the call page
2. Extract **attendee names** from the participant list. If there's a "+N more" button, click it first.
3. Resolve Gong display names to full names (e.g., "Jsmith" → "Jane Smith") using existing contact files in `{account}/contacts/`
4. Check if the page has a Briefs tab — if not, this is a **non-recorded call**

### CP2: Handle Non-Recorded Calls

If the call has no recording:
1. Update the meeting file's frontmatter:
   - Set `gong_url` to the call URL
   - Set `attendees` as `"[[Name]]"` links
2. Done — skip brief and transcript extraction

### CP3: Extract Brief

**IMPORTANT: Extract the brief BEFORE clicking Transcript.** The Briefs tab is selected by default.

1. Extract the brief content from the snapshot. Look for the `tabpanel "Briefs"` region or equivalent.
2. This includes: Recap, Key Points, and Next Steps sections.
3. Save to temp file: `/tmp/gong_brief_{date}_{slug}.md`

### CP4: Extract Transcript

1. Click the **"Transcript"** tab:
   ```bash
   playwright-cli -s=gong_{account_slug} click {transcript_tab_ref}
   ```
2. Take a snapshot. The transcript will be large.
3. Save the snapshot path for the subagent to process.

### CP5: Write to Meeting File (done by subagent)

The subagent reads the brief and transcript files and updates the meeting file:
- Set `gong_url` in frontmatter
- Set `attendees` in frontmatter as `"[[Name]]"` links
- **Append** brief under `## External Summary` (see Append Rules)
- **Append** transcript under `## Transcript` (see Append Rules)

---

## Gong Path (single call URL provided)

### Step 2G: Navigate and Extract Metadata

1. Open the browser and navigate to the Gong call URL:
   ```bash
   playwright-cli -s=gong_{account_slug} open {gong_call_url} --headed --persistent
   ```
2. **Login check:** Snapshot and check if the page URL contains `sign-in`. If shown, tell user to log in and wait.
3. Extract from the call page snapshot:
   - **Call date** from the header
   - **Call title** from the page title or heading
   - **Call duration** from the header
   - **Attendee names** from the participant list
   - **Participant details** from the Speakers section

### Step 3G: Check for Existing Meeting File

Look for an existing meeting file matching the date and topic at:
`{config.vault_path}/{config.company_folder}/Accounts/{Account}/meetings/{YYYY-MM-DD} {Topic}.md`

- If a file exists: proceed to populate it (don't skip)
- If no file exists: use `/sales-meeting {Account} {Topic} {YYYY-MM-DD}` to create one

### Step 4G: Extract Brief

Follow CP3 above.

### Step 5G: Extract Transcript

Follow CP4 above.

### Step 6G: Write to Meeting File

1. Resolve Gong display names to full names using contact files
2. Update the meeting file per CP5
3. Close the session: `playwright-cli -s=gong_{account_slug} close`

---

## Granola Path (Granola URL provided)

### Step 2R: Navigate and Extract Content

1. Open the browser and navigate to the Granola URL:
   ```bash
   playwright-cli -s=granola open {granola_url} --headed
   ```
2. **Dismiss prompts:** If a "Download Granola" dialog appears, find and click "Maybe later" via snapshot + click.
3. Take a snapshot and extract:
   - **Meeting title** from the page heading (h1)
   - **Meeting date** from the page metadata
   - **Summary content**: structured notes preserving markdown hierarchy
   - **Note:** Shared Granola links only include the summary, NOT the transcript.

### Step 3R: Check for Existing Meeting File

Look for an existing meeting file matching the date at:
`{config.vault_path}/{config.company_folder}/Accounts/{Account}/meetings/{YYYY-MM-DD} *.md`

- If a file exists for that date: use it
- If no file exists: infer a topic and use `/sales-meeting {Account} {Topic} {YYYY-MM-DD}` to create one

### Step 4R: Write Content to Meeting File

**Do NOT** store the Granola URL in the frontmatter.

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

## Gong DOM Reference

Key CSS selectors and DOM patterns for the Gong activity page:

**Activity page:**
- Call entries: `.activity-item.call-activity`
- Call title: `.activity-title` (child of call entry)
- Date header: `.activity-date` (inside `.activity-items-wrapper` parent)
- Duration: first `[class*=styles-module]` child with text like "18m", "57m"
- "Calls only" checkbox: look for `[ref]` with text "Calls only" in snapshot
- "Go to call" link: `a[href*="/call?"]` (appears in right panel after clicking a call)
- Call URL pattern: `/call?id={call_id}&account-id={account_id}`

**Call page:**
- Briefs tab is selected by default (contains Recap, Key Points, Next Steps)
- Transcript tab: click to switch, then snapshot to extract
- Attendee list: look for participant names in the call details area
- "+N more" button: click to expand full attendee list

---

### Report Result

After completion, report:

```
Imported: {YYYY-MM-DD} {Topic} (from {Gong|Granola})
  - File: meetings/{YYYY-MM-DD} {Topic}.md
  - Attendees: {count} people (if extracted)
  - Summary: {word count} words
  - Transcript: {word count} words
```

For Scan Mode and Bulk Import, report a summary table:

```
Import Complete for {Account}

Imported: {N} calls
Skipped (voicemail/missed): {M} calls
Failed: {F} calls

Files:
- meetings/2026-01-15 Discovery.md (briefing + transcript)
- meetings/2026-01-22 Demo.md (briefing + transcript)
- meetings/2026-01-25 Check-in.md (attendees only, no recording)
...

Next steps:
- Run `/sales-summarize-account {Account}` to process all meeting notes
```

### Cleanup

When finished with all imports, close the browser session:
```bash
playwright-cli -s=gong_{account_slug} close
```

### Error Handling

- **Login required:** Pause and tell the user to log in. Do NOT skip the import. Poll every 5 seconds (check page URL for `sign-in`) and resume automatically once auth succeeds. If no auth after 2 minutes, remind the user again. The `--headed --persistent` flags make re-auth easier.
- **No recording:** Still update the meeting file with attendees and `gong_url`. Log as "no recording" and continue. This is the ONLY valid reason to skip extracting a brief/transcript.
- **Existing content:** Always preserve existing content. Append new data using subheadings. Never skip a call because the meeting file already has notes from another source (Granola, manual notes, etc.).
- **No Gong URL in account file:** Ask the user for the Gong account activity URL.
- **Gong rate limiting:** If Gong returns errors or CAPTCHAs, pause and tell the user. Do NOT skip — wait for resolution.
- **Session timeout:** If the Gong session expires mid-import, pause and ask the user to re-authenticate. Do NOT skip remaining calls.
- **"not well-serializable" error:** This means a regex literal was used in `eval`. Replace with `indexOf()` or `new RegExp()`.

### Notes

- Scan Mode imports Gong recordings into EXISTING meeting files that are missing `gong_url`. It does not create new meeting files.
- Bulk Import creates new meeting files for all calls found on the activity page.
- For Gong: The Briefs tab is extracted BEFORE clicking Transcript to avoid navigating back.
- For Granola: Shared links only contain summary notes (no transcript available).
- Parallel processing uses browser tabs (up to 3 at a time) within a single session.
- Multiple `/sales-gong` invocations for different accounts can run in parallel (different session names).
- The `--persistent` flag preserves auth cookies across browser restarts.
- All meeting files are created by the main agent before launching subagents to prevent race conditions.
- Never ask for confirmation. The skill runs fully autonomously — skip voicemail/missed calls and import everything else.
