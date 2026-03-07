---
description: Push SE Status to Salesforce, scan accounts for opportunities and deal context, or discover all your open opportunities across Salesforce. Use this skill whenever the user mentions Salesforce, opportunities, deal updates, SE status, or wants to see all their accounts.
argument-hint: <account> or scan <account> or scan open <account> or my accounts
---

# Salesforce Integration

Four modes:

- **Push mode** (default): `/sales-salesforce <account>` — pushes SE Status to linked opportunities
- **Scan mode**: `/sales-salesforce scan <account>` — imports ALL opportunities with historical deal context
- **Scan open mode**: `/sales-salesforce scan open <account>` — pulls current deal context from open opportunities only
- **My accounts mode**: `/sales-salesforce my accounts` — discovers all open opportunities you're on, cross-references with Obsidian, and helps onboard missing accounts

## Arguments

- `account`: The account name (e.g., "Acme Corp", "Globex")
- `scan` (optional): Prefix to import all opportunities with history
- `scan open` (optional): Prefix to pull deal context from open opportunities
- `my accounts` (optional): List all your open opportunities and onboard missing accounts

## Prerequisites

Before first use, authenticate with the Salesforce CLI via SSO:

```
sf org login web --instance-url {config.salesforce_instance_url}
```

This opens a browser for SSO login (Okta). You only need to do this once per org — the token is stored locally until it expires.

To verify authentication:

```
sf org list
```

## Instructions

You are helping a Solutions Engineer manage Salesforce data for: $ARGUMENTS

### Step 0: Check Dependencies

1. Check if the Salesforce CLI is installed:
   ```bash
   which sf
   ```
2. Check if authenticated:
   ```bash
   sf org list 2>&1
   ```

- If `sf` is not found: Stop and tell the user: "Salesforce CLI is not installed. Run `/sales-setup salesforce` to install and configure it."
- If `sf org list` shows no connected orgs or returns an auth error: Stop and tell the user: "Salesforce CLI is not authenticated. Run `/sales-setup salesforce` to log in."
- Only proceed if both checks pass.

### Pre-check: Read Config

Read the config file at `~/.claude/skills/sales-config.md` and extract these values from its YAML frontmatter:

- `vault_path` — path to the Obsidian vault
- `company_folder` — subfolder name within the vault (e.g., "LaunchDarkly")
- `name` — the user's full name
- `initials` — the user's initials (e.g., "GY")
- `company` — the company name
- `salesforce_username` — Salesforce login email
- `salesforce_instance_url` — Salesforce instance base URL (e.g., `https://yourcompany.my.salesforce.com`)
- `salesforce_se_status_field` — the API name of the field to push SE notes to (e.g., `Technical_Blockers__c`)
- `salesforce_se_lookup_fields` — array of SE lookup field names on Opportunity (e.g., `["SE__c", "Solutions_Engineer__c"]`)
- `salesforce_custom_fields` — array of custom SOQL field names for deal context queries

If the config file doesn't exist or is missing required Salesforce fields (`salesforce_username`, `salesforce_instance_url`, `salesforce_se_status_field`), stop and tell the user: "Salesforce is not configured. Run `/sales-setup salesforce` to set it up."

Store all values as `config.*` for use throughout this skill.

### Step 1: Detect Mode and Parse Arguments

Parse `$ARGUMENTS`:
- If the arguments match `my accounts` (case-insensitive), go to **My Accounts Mode** below.
- If the arguments start with `scan open` (case-insensitive), extract the account name after "scan open" and go to **Scan Open Mode** below.
- If the arguments start with `scan` (case-insensitive), extract the account name after "scan" and go to **Scan Mode** below.
- Otherwise, extract the account name and go to **Push Mode** below.

If the mode requires an account name and it's empty, report an error and stop.

---

## Push Mode

### Step 2P: Read the Account File

Read the account file at:
`{config.vault_path}/{config.company_folder}/Accounts/{Account}/{Account}.md`

If the file doesn't exist, report an error and stop.

### Step 3P: Extract Salesforce Opportunity IDs

Parse the frontmatter and collect ALL Salesforce opportunity fields. These can be:
- `salesforce_opportunity` — the primary/default opportunity
- `salesforce_opportunity_*` — additional opportunities (e.g., `salesforce_opportunity_expansion`, `salesforce_opportunity_renewal`, `salesforce_opportunity_ai`, etc.)

Any frontmatter key matching `salesforce_opportunity` or `salesforce_opportunity_*` (anything after the second underscore) is a valid opportunity field.

For each opportunity field found, extract the Opportunity record ID — this is the 15 or 18-character alphanumeric ID that appears after `/Opportunity/` in the URL (e.g., from `{config.salesforce_instance_url}/lightning/r/Opportunity/0061Q00000AbCdEFGH/view`, extract `0061Q00000AbCdEFGH`).

- If NO opportunity fields are found or all are empty, warn the user: "No Salesforce opportunity URLs found in frontmatter for {Account}. Please add at least one `salesforce_opportunity` field to the account file frontmatter and try again." Then stop.
- Skip any opportunity fields that are empty.

### Step 4P: Extract the Salesforce Updates Content

Find the `## Salesforce Updates` section in the account file. Extract ONLY the content inside the triple-backtick code block (everything between the opening ``` and closing ```).

- If the `## Salesforce Updates` section doesn't exist, warn the user: "No ## Salesforce Updates section found in {Account}.md. Run /sales-summarize-account {Account} first to generate it." Then stop.
- If the code block is empty, warn the user: "The Salesforce Updates code block is empty for {Account}. Run /sales-summarize-account {Account} first to populate it." Then stop.

### Step 5P: Push to Salesforce

The `sf data update record --values` approach does NOT work for multiline content (it parses content as key=value pairs and breaks on special characters). Use the REST API with curl instead.

1. Write the extracted content to a temp file at `/tmp/sf_update.txt` using the Write tool
2. Get the access token and instance URL:

```bash
sf org display --target-org {config.salesforce_username} --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin)['result']; print(d['accessToken']); print(d['instanceUrl'])"
```

3. Build a JSON payload with the content. The field is HTML-formatted, so convert newlines to `<br>` tags and bold the section headers:

```bash
python3 -c "
import json, re
content = open('/tmp/sf_update.txt').read()
# Bold section headers (lines that are all-caps labels followed by a colon or standalone)
content = re.sub(r'^(MEDDPICC|TECHMAPS|TECH STACK|DEAL HISTORY):?', r'<b>\1</b>', content, flags=re.MULTILINE)
html_content = content.replace('\n', '<br>')
print(json.dumps({'{config.salesforce_se_status_field}': html_content}))
" > /tmp/sf_update.json
```

4. For EACH opportunity ID collected in Step 3P, push via REST API:

```bash
curl -s -w "\nHTTP_CODE:%{http_code}" -X PATCH \
  "{instance_url}/services/data/v62.0/sobjects/Opportunity/{id}" \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d @/tmp/sf_update.json
```

The field is `{config.salesforce_se_status_field}` (the configured SE status field).

- HTTP 204 = success (no response body)
- HTTP 401 = token expired, re-authenticate with `sf org login web --instance-url {config.salesforce_instance_url}`
- HTTP 400 = check response body for field name errors — run `sf sobject describe --sobject Opportunity --target-org {config.salesforce_username} --json` and search for the configured SE status field name to verify it exists
- HTTP 404 = verify the Opportunity ID extracted from frontmatter

Continue pushing to remaining opportunities even if one fails — report all successes and failures at the end.

5. Clean up temp files after all updates (success or failure):

```bash
rm -f /tmp/sf_update.txt /tmp/sf_update.json
```

### Step 6P: Clear Weekly Status Entry

After a successful push, the `(status)` ledger entry (added by `/sales-weekly`) is superseded by the active update.

1. Read `{config.vault_path}/{config.company_folder}/Accounts/{Account}/Ledger.md`
2. Search for a line containing `(status)` — e.g., `- 3/7 {config.initials} (status): No activity since 2/4`
3. If found, **remove that entire line** from the ledger (delete it, don't just clear the text)
4. Write the updated ledger back
5. If no `(status)` entry exists, skip silently

### Step 7P: Mark Daily Note Checkbox Complete

1. Find today's daily note at `{config.vault_path}/Daily/YYYY-MM-DD.md` (use today's date)
2. Search for an unchecked checkbox line containing `/sales-salesforce {Account}` (case-insensitive match on the account name). The line may also contain Salesforce opportunity links in parentheses after the account name — match regardless of what follows the account name on that line.
3. If found, mark it complete by changing `- [ ]` to `- [x]` and appending a completion timestamp. Preserve any existing Salesforce links on the line:
   ```
   - [x] Run `/sales-salesforce {Account}` ([Salesforce](url))  [completion:: YYYY-MM-DD]
   ```
4. If no matching unchecked checkbox is found, skip this step silently

### Step 8P: Report Results

Output a summary:
- Number of opportunities updated and their IDs (with labels from frontmatter key, e.g., "expansion", "renewal")
- Any failures and which opportunity they were for
- First 5 lines of the content that was pushed (as a preview)
- Whether the daily note checkbox was marked complete
- Confirmation message: "Salesforce SE Status updated successfully for {Account} ({N} opportunities)."

### Step 9P: Offer CLI Update (Only If Outdated)

Check if the Salesforce CLI has an available update:

```bash
brew outdated sf 2>/dev/null
```

- If `sf` appears in the output (meaning an update is available), ask the user: "Salesforce CLI update available. Would you like to update? (`brew upgrade sf`)"
  - If **yes**: Run `brew upgrade sf` and report the result.
  - If **no**: Skip.
- If `sf` does NOT appear in the output (already up to date), skip this step silently.

---

## Scan Mode

Imports ALL opportunities for an account with historical deal context. Creates opportunity files, a Dataview table, and a deal history narrative.

### Step 2S: Read Account File and Get Account ID

Read the account file at:
`{config.vault_path}/{config.company_folder}/Accounts/{Account}/{Account}.md`

If the file doesn't exist, report an error and stop.

Extract the Salesforce Account ID from the frontmatter. Look for:
- `salesforce_account` — contains a URL like `{config.salesforce_instance_url}/lightning/r/Account/0011K00002D40TEQAZ/view`
- Extract the 15 or 18-character ID after `/Account/` in the URL

If no `salesforce_account` field exists or is empty, check `salesforce_opportunity` fields — extract the Account ID from an Opportunity using the REST API:
```bash
curl -s "{instance_url}/services/data/v62.0/sobjects/Opportunity/{opp_id}?fields=AccountId" \
  -H "Authorization: Bearer {access_token}"
```

If no Account ID can be determined, ask the user for the Salesforce Account URL and save it to the `salesforce_account` frontmatter field.

### Step 3S: Get Access Token

```bash
sf org display --target-org {config.salesforce_username} --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin)['result']; print(d['accessToken']); print(d['instanceUrl'])"
```

### Step 4S: Query All Opportunities and History

Run multiple SOQL queries to collect opportunity data and activity history. Use Python with `urllib` to avoid shell escaping issues with the access token.

**Query 1 — Opportunities:**
```sql
SELECT Id, Name, StageName, Amount, CloseDate, Type, IsClosed, IsWon, CreatedDate, Description, NextStep
FROM Opportunity
WHERE AccountId = '{account_id}'
ORDER BY CloseDate DESC
```

Parse into a list with fields: `id`, `name`, `stage`, `amount`, `close_date`, `type`, `is_closed`, `is_won`, `created_date`, `description`, `next_step`, `status` (derived: Open/Closed Won/Closed Lost), `salesforce_url`.

**Query 2 — Stage History:**
```sql
SELECT OpportunityId, Field, OldValue, NewValue, CreatedDate
FROM OpportunityFieldHistory
WHERE Opportunity.AccountId = '{account_id}' AND Field = 'StageName'
ORDER BY CreatedDate ASC
```

**Query 3 — Events (meetings/calls):**
```sql
SELECT Id, Subject, StartDateTime, Description, WhatId
FROM Event
WHERE AccountId = '{account_id}'
ORDER BY StartDateTime DESC
```

**Query 4 — Notes:**
```sql
SELECT Id, Title, Body, CreatedDate, ParentId
FROM Note
WHERE ParentId IN (SELECT Id FROM Opportunity WHERE AccountId = '{account_id}')
ORDER BY CreatedDate DESC
```

Save all raw query results to a temp JSON file at `/tmp/sf_scan_{account}.json` for subagent consumption.

### Step 5S: Enrich Opportunities via Subagents

Launch subagents to process the raw Salesforce data into deal history narratives. Use the Task tool with `subagent_type: "general-purpose"` and `model: "sonnet"`.

**Group opportunities by era** to control granularity:
- **Recent** (last 12 months): Individual subagent per opportunity — extract detailed milestones
- **Older** (12-36 months ago): Batch into one subagent — extract key milestones only
- **Historical** (3+ years ago): Batch into one subagent — one-line summary per opportunity

Launch all subagents in parallel. Each subagent receives the relevant slice of the raw data from Step 4S.

**Subagent prompt template for recent opportunities:**

```
You are analyzing Salesforce opportunity data for a {config.company} sales account.

Account: {Account}
Opportunity: {Name}
- ID: {Id}
- Type: {Type}
- Stage: {StageName}
- Amount: {Amount}
- Created: {CreatedDate}
- Close Date: {CloseDate}
- Status: {Open|Closed Won|Closed Lost}
- Description: {Description}
- Next Step: {NextStep}

Stage History (chronological):
{list of stage changes with dates for this opp}

Events/Meetings:
{list of events linked to this opp, with Subject, Date, Description snippet}

Notes:
{any notes linked to this opp, with Title, Date, Body snippet}

Extract a deal history narrative focusing on KEY MILESTONES:
- When was the opportunity created and by whom (if inferable from owner changes)?
- What stages did it progress through and when?
- Were there demos, POVs, pricing discussions, or technical deep-dives?
- What was the outcome and why (if inferable)?
- Any key contacts or stakeholders mentioned?

Return EXACTLY this format:

---BEGIN OPP HISTORY---
OPP_ID: {Id}
OPP_NAME: {Name}
CREATED: {YYYY-MM-DD}
CLOSED: {YYYY-MM-DD}
STATUS: {Open|Closed Won|Closed Lost}
AMOUNT: {amount or N/A}
TIMELINE:
- {YYYY-MM-DD}: {milestone description}
- {YYYY-MM-DD}: {milestone description}
...
SUMMARY: {1-3 sentence narrative of this opportunity's arc}
KEY_CONTACTS: {names mentioned, comma-separated, or "none"}
---END OPP HISTORY---
```

**Subagent prompt template for older/historical batches:**

```
You are analyzing Salesforce opportunity data for a {config.company} sales account.

Account: {Account}

Opportunities (oldest to newest):
{for each opp in batch:}
---
Name: {Name}
ID: {Id}, Type: {Type}, Stage: {StageName}, Amount: {Amount}
Created: {CreatedDate}, Closed: {CloseDate}, Status: {status}
Description: {Description}
Stage History: {stage changes with dates}
Events: {event subjects and dates}
Notes: {note titles and dates}
---

For each opportunity, extract a brief summary. Focus on:
- Key deal milestones (POV, demo, pricing, decision)
- Outcome and reason if inferable
- Skip granular call-by-call details for older opportunities

{For older (12-36 months): "Provide 2-4 bullet points per opportunity."}
{For historical (3+ years): "Provide a single sentence per opportunity."}

Return EXACTLY this format for each opportunity:

---BEGIN OPP HISTORY---
OPP_ID: {Id}
OPP_NAME: {Name}
CREATED: {YYYY-MM-DD}
CLOSED: {YYYY-MM-DD}
STATUS: {Open|Closed Won|Closed Lost}
AMOUNT: {amount or N/A}
TIMELINE:
- {key milestones only}
SUMMARY: {1 sentence summary}
KEY_CONTACTS: {names or "none"}
---END OPP HISTORY---
```

### Step 6S: Create Opportunities Folder and Files

1. Create the `opportunities/` subdirectory under the account folder if it doesn't exist:
   ```
   {config.vault_path}/{config.company_folder}/Accounts/{Account}/opportunities/
   ```

2. For each opportunity, create or update a file at:
   ```
   opportunities/{Name}.md
   ```

   **Sanitize the filename:** Replace characters that are invalid in filenames (`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`) with `-`.

   **Disambiguate duplicate names:** If multiple opportunities share the same name, append `({CloseDate})` to the filename. If that's still not unique, append `({last 8 chars of Id})`.

   Each opportunity file should have this format:

   ```markdown
   ---
   account: "[[{Account}]]"
   opportunity_name: "{Name}"
   stage: "{StageName}"
   amount: {Amount or ""}
   close_date: {CloseDate}
   type: "{Type}"
   status: "{Open|Closed Won|Closed Lost}"
   salesforce_url: "{config.salesforce_instance_url}/lightning/r/Opportunity/{Id}/view"
   created_date: {CreatedDate as YYYY-MM-DD}
   ---

   # {Name}

   **Stage:** `= this.stage`
   **Amount:** `= this.amount`
   **Close Date:** `= this.close_date`
   **Type:** `= this.type`
   **Status:** `= this.status`

   **Links:** [Salesforce](`= this.salesforce_url`)
   ```

3. If an opportunity file already exists (same filename), update its frontmatter with the latest data from Salesforce but preserve any manually added content below the template section.

### Step 7S: Create or Update opportunities.base

Create or update `{config.vault_path}/{config.company_folder}/Accounts/{Account}/opportunities.base`:

```yaml
properties:
  file.name:
    displayName: Opportunity
    link: true
  type:
    displayName: Type
  stage:
    displayName: Stage
  amount:
    displayName: Amount
  close_date:
    displayName: Close Date
  status:
    displayName: Status
views:
  - type: table
    name: Opportunities
    filters:
      and:
        - file.inFolder(this.file.folder + "/opportunities")
    order:
      - file.name
      - type
      - stage
      - amount
      - close_date
      - status
    sort:
      - property: close_date
        direction: desc
```

### Step 8S: Update Account File and Deal Ledger

1. **Add `## Opportunity History` section** to the account file if it doesn't exist. Insert it after the `## Meetings` section (and its `![[meetings.base]]` embed):

   ```markdown
   ## Opportunity History

   ![[opportunities.base]]
   ```

   If the section already exists, leave it as-is.

2. **Build a Salesforce Deal History narrative** from the subagent results. Add or update a subsection under `## Opportunity History` below the base embed:

   ```markdown
   ### Salesforce Deal History

   {Narrative organized chronologically, newest first. Group by opportunity era:}

   **Recent (last 12 months):**
   - {Detailed timeline entries from subagent results}

   **Earlier Attempts (1-3 years ago):**
   - {Key milestone summaries}

   **Historical (3+ years ago):**
   - {One-line summaries}

   **Overall Pattern:** {1-2 sentence analysis of the account's opportunity history — e.g., "12 closed-lost new business attempts since 2019, but account is an existing customer (renewal managed outside tracked opportunities). Repeated attempts to expand into new teams have not yet converted."}
   ```

   **Important context note:** If ALL opportunities are closed-lost but the account appears to be an existing customer (based on account file content like renewal discussions, CSM assignments, or existing usage), note this discrepancy. The Salesforce opportunity history may not capture the original sale — it may predate the CRM or have been tracked differently.

3. **Update the Deal Ledger** (`Ledger.md`) with historical entries from the subagent results. Add a `### Salesforce History` section at the BOTTOM of the ledger (below existing entries) with key milestones:

   ```markdown
   ### Salesforce History
   - {M/D/YY}: {Key milestone from oldest to newest — created, stage change, demo, POV, pricing, closed}
   ```

   Only include meaningful milestones (stage transitions, meetings, decisions). Do NOT duplicate entries that already exist in the ledger from meeting notes.

4. **Update frontmatter links for open opportunities:**
   - For each **open** opportunity (not closed), add or update `salesforce_opportunity` fields in the frontmatter:
     - If there is exactly one open opp, set `salesforce_opportunity` to its URL
     - If there are multiple open opps, set `salesforce_opportunity` to the first one and add `salesforce_opportunity_{type}` fields for the rest (using the Type field lowercased as the suffix, e.g., `salesforce_opportunity_renewal`)
   - Do NOT clear existing `salesforce_opportunity` fields that point to open opportunities already tracked
   - If there are no open opportunities, leave `salesforce_opportunity` empty (don't clear `salesforce_account`)

5. **Ensure `salesforce_account` is set** in the frontmatter if it wasn't already.

6. **Update the Links line** in the account file to include the Salesforce Account link if not already present:
   ```
   **Links:** [Salesforce Account](`= this.salesforce_account`) | [Salesforce Opp](`= this.salesforce_opportunity`) | [Gong](`= this.gong_url`) | [Revenue Assets](`= this.revenue_assets_folder`)
   ```

7. Clean up temp files:
   ```bash
   rm -f /tmp/sf_scan_{account}.json
   ```

### Step 9S: Report Results

Output a summary table of all opportunities found:

```
Salesforce Scan Complete for {Account}

| # | Name | Type | Stage | Amount | Close Date | Status |
|---|------|------|-------|--------|------------|--------|
| 1 | Opp Name | Renewal | Closed Won | $500K | 2025-12-22 | Closed Won |
| 2 | Opp Name | New Business | Negotiation | $50K | 2026-03-15 | Open |
...

Total: {N} opportunities ({open} open, {closed_won} won, {closed_lost} lost)
Files created: {count} in opportunities/
Open opportunities linked in frontmatter: {list}
Deal history: {summary of what was added to the account file and ledger}
```

---

## Scan Open Mode

Pulls current deal context from all open opportunities to update the account file and ledger. Run this before `/sales-summarize-account` to ensure the account file has the latest Salesforce data.

### Step 2O: Read Account File and Collect Open Opportunity IDs

Read the account file at:
`{config.vault_path}/{config.company_folder}/Accounts/{Account}/{Account}.md`

If the file doesn't exist, report an error and stop.

Parse the frontmatter and collect ALL Salesforce opportunity fields (same logic as Push Mode Step 3P). Extract Opportunity record IDs from URLs.

- If NO opportunity fields are found or all are empty, warn the user: "No Salesforce opportunity URLs found in frontmatter for {Account}. Run `/sales-salesforce scan {Account}` first to import opportunities." Then stop.
- Skip any opportunity fields that are empty.

### Step 3O: Get Access Token

```bash
sf org display --target-org {config.salesforce_username} --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin)['result']; print(d['accessToken']); print(d['instanceUrl'])"
```

### Step 4O: Query Deal Context for Each Open Opportunity

For EACH opportunity ID, run two SOQL queries. Use Python with `urllib` to avoid shell escaping issues with the access token.

**Query 1 — Opportunity deal context fields:**

Build the SOQL SELECT clause using the standard Opportunity fields (Id, Name, StageName, Amount, CloseDate, Type, Probability, ForecastCategoryName, NextStep, Description, LeadSource, LastActivityDate, LastStageChangeDate) plus all fields from {config.salesforce_custom_fields}.

```sql
SELECT {standard fields}, {config.salesforce_custom_fields joined by commas}
FROM Opportunity WHERE Id = '{opp_id}'
```

**Query 2 — Recent stage history:**
```sql
SELECT Field, OldValue, NewValue, CreatedDate
FROM OpportunityFieldHistory
WHERE OpportunityId = '{opp_id}' AND Field = 'StageName'
ORDER BY CreatedDate DESC
LIMIT 10
```

Save the raw results to `/tmp/sf_deal_context.json`.

### Step 5O: Process Deal Context via Subagent

Launch a subagent (`subagent_type: "general-purpose"`, `model: "sonnet"`) to process the deal context and update the account file.

Pass it:
- The account file path
- The Ledger.md path
- The raw deal context JSON (all opportunities combined)
- The list of opportunity IDs and their labels from frontmatter

**Subagent prompt:**

```
You are updating a {config.company} sales account file with the latest deal context pulled from Salesforce.

Account: {Account}
Account file: {path}
Ledger file: {path}

Deal context for each open opportunity:
{JSON with all queried fields per opportunity}

Stage history:
{stage changes with dates}

Read the account file and Ledger.md, then perform these tasks:

1. **Update the Deal Ledger** — Add a brief entry at the TOP of Ledger.md if the deal has progressed since the last ledger entry. Use the stage dates, next steps, and notes to determine what's new. Format: `- M/D {config.initials} (from SF): {summary}. Next call: {from NextStep or TBD}`. Only add an entry if there is genuinely new information not already in the ledger.

2. **Update MEDDPICC fields** in the account file — Cross-reference the Salesforce MEDDPICC fields (Pain, Decision Criteria, Decision Process, Champion) with the existing MEDDPICC section. If Salesforce has information the account file is missing, add it with a "(from Salesforce)" attribution. Do NOT overwrite existing manually-written content — append new info only.

3. **Update deal metadata** — If the account file's frontmatter or body has stale deal information, flag it:
   - Stage changes (e.g., account file says "Discovery" but SF says "Tech Evaluating")
   - Close date changes
   - ARR/amount changes
   - Forecast category changes

4. **Summarize AE/CSM activity** — Extract useful context from CSM Notes, Manager Notes, Next Steps Details, and Competition Notes. Filter out noise:
   - INCLUDE: Deal milestones, pricing discussions, POV status, competitive dynamics, risk factors, renewal strategy, champion changes
   - EXCLUDE: Routine outreach attempts ("emailed X, no response"), cadence/sequence activity, administrative updates
   - Recent activity (last 30 days) can be more granular
   - Older activity should only include significant milestones

Return EXACTLY this format (one block per opportunity):

---BEGIN DEAL CONTEXT---
OPP_ID: {id}
OPP_NAME: {name}
CURRENT_STAGE: {stage}
AMOUNT: {amount}
CLOSE_DATE: {close_date}
FORECAST: {forecast category}
DAYS_IN_STAGE: {days}
LAST_ACTIVITY: {date}
NEW_LEDGER_ENTRY: {entry text, or "none" if nothing new}
MEDDPICC_UPDATES: {bullet list of new info to add, or "none"}
STALE_FIELDS: {list of fields that need updating in account file, or "none"}
AE_CSM_CONTEXT: {filtered summary of deal activity, or "none"}
---END DEAL CONTEXT---
```

### Step 6O: Apply Updates

After the subagent returns, apply its recommendations:
1. Add new ledger entries (subagent writes directly)
2. Append MEDDPICC updates (subagent writes directly)
3. Collect stale fields and AE/CSM context for the report

Clean up temp files:
```bash
rm -f /tmp/sf_deal_context.json
```

### Step 7O: Report Results

Output a summary for each open opportunity:

```
Salesforce Deal Context for {Account}

Opportunity: {Name} ({stage})
- Amount: {amount} | Close: {close_date} | Forecast: {forecast}
- Days in stage: {days} | Last activity: {date}
- New info added to MEDDPICC: {yes/no — what was added}
- New ledger entry: {yes/no}
- Stale fields: {list, or "all current"}

AE/CSM Context:
{filtered summary of deal activity}
```

---

## My Accounts Mode

Discovers all open Salesforce opportunities where you are the SE, cross-references with existing Obsidian accounts, onboards missing accounts, scans all accounts for current deal context, and creates daily note todos for follow-up.

### Step 2M: Get Access Token

```bash
sf org display --target-org {config.salesforce_username} --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin)['result']; print(d['accessToken']); print(d['instanceUrl'])"
```

### Step 3M: Query All Open Opportunities Where You Are SE

Find the SE user's Salesforce User ID first, then query for open opportunities with that SE assigned. Use the SE lookup fields from config ({config.salesforce_se_lookup_fields}) to query for opportunities where the current user is assigned as SE.

```sql
SELECT Id FROM User WHERE Email = '{config.salesforce_username}' LIMIT 1
```

Then query for all open opportunities using the SE lookup fields from config. Build a WHERE clause that checks each field in `{config.salesforce_se_lookup_fields}` with OR logic (e.g., `SE__c = '{user_id}' OR Solutions_Engineer__c = '{user_id}'`):

Build the SOQL SELECT clause using the standard Opportunity fields (Id, Name, StageName, Amount, CloseDate, Type, Probability, ForecastCategoryName, Account.Name, Account.Id, AccountId, NextStep, Owner.Name, Owner.Email, CreatedDate, LastActivityDate) plus all fields from {config.salesforce_custom_fields} that are relevant to opportunity overview (e.g., SE_Next_Steps__c, Days_in_Stage__c, ARR fields).

```sql
SELECT {standard fields}, {config.salesforce_custom_fields relevant to overview}
FROM Opportunity
WHERE ({config.salesforce_se_lookup_fields joined with OR, each = '{user_id}'}) AND IsClosed = false
ORDER BY CloseDate ASC
```

If none of the configured SE lookup fields work, fall back to a broader query using the SE's name in text fields, then ask the user to confirm.

Use Python with `urllib` to run these queries via the REST API (same pattern as Scan Mode).

### Step 4M: Group Opportunities by Account

Group the results by `Account.Name` (using `AccountId` as the key). For each account, collect:
- Account name
- Salesforce Account ID and URL (`{config.salesforce_instance_url}/lightning/r/Account/{AccountId}/view`)
- List of open opportunities with: name, stage, amount, close date, type, owner (AE), forecast category

Present the full list to the user:

```
Your Open Opportunities ({N} opps across {M} accounts)

| # | Account | Opportunity | Stage | Amount | Close Date | AE | In Obsidian? |
|---|---------|------------|-------|--------|------------|----|-------------|
| 1 | Acme Corp | Acme - Expansion | Tech Eval | $150K | 2026-04-15 | Jane Doe | Yes |
| 2 | Acme Corp | Acme - Renewal | Negotiation | $200K | 2026-06-01 | Jane Doe | Yes |
| 3 | NewCo | NewCo - New Business | Discovery | $50K | 2026-05-01 | John Smith | No |
...
```

### Step 5M: Cross-Reference with Obsidian Accounts

1. List all existing account folders in `{config.vault_path}/{config.company_folder}/Accounts/`
2. For each Salesforce account, check if a matching folder exists (case-insensitive match, also try common variations like removing "Inc.", "LLC", etc.)
3. Mark each account as "Yes" or "No" in the table above

Separate accounts into three lists:
- **Existing accounts**: Already have an Obsidian folder
- **Missing accounts (actionable)**: No Obsidian folder, and has at least one opportunity where the SE is actively engaged — New Business, Expansion, or any opp that isn't purely a renewal
- **Skipped accounts**: No Obsidian folder, but all opportunities are renewal/auto-renewal types (managed by CSMs/AEs, not requiring SE account tracking). List these at the bottom of the report for visibility but don't create accounts for them.

To determine if an account is actionable, check the `Type` field on each opportunity. Skip accounts where ALL opps match renewal types: "Renewal", "Auto-Renewal", "Renewal - Auto", or any type containing "renewal" (case-insensitive). If an account has even one non-renewal opp, it is actionable.

### Step 6M: Onboard Missing Accounts

For each **actionable** missing account (not renewal-only), automatically create it using `/sales-create-account`. Pass both the account name and the Salesforce Account URL:

```
/sales-create-account {Account Name} {config.salesforce_instance_url}/lightning/r/Account/{AccountId}/view
```

Process missing accounts sequentially (each `/sales-create-account` invocation creates the folder structure, populates business context, etc.).

After each account is created, also add the `salesforce_account` field to the frontmatter if not already set by the creation process.

### Step 7M: Scan All Accounts for Open Opportunities

For each account (both existing and newly created), run `/sales-salesforce scan open {Account}` to pull in the latest deal context and ensure all open opportunity URLs are in the frontmatter.

Process these sequentially since they share Salesforce API authentication.

### Step 8M: Update Daily Note with Todos

Find today's daily note at `{config.vault_path}/Daily/YYYY-MM-DD.md`.

For each account that was newly created (not existing), add todo items under `### Today` in the `## Meetings` section. Group todos by account:

```markdown
- [[{config.company_folder}/Accounts/{Account}/{Account}|{Account}]]: Onboarding
	- [x] Run `/sales-salesforce my accounts`  [completion:: YYYY-MM-DD]
	- [ ] Run `/sales-gong {Account} {gong_url}` (historical import)
	- [ ] Run `/sales-summarize-account {Account}`
```

For the Gong historical import todo:
- If the account file has a `gong_url` in frontmatter (set during `/sales-create-account`), include the URL in the todo
- If no `gong_url`, use: `Run '/sales-gong {Account}' (find account in Gong first)`

Only add todos for **newly created** accounts. Existing accounts presumably already have their Gong history imported and are being maintained via the regular workflow.

### Step 9M: Report Results

Output a comprehensive summary:

```
My Accounts Summary

Accounts found: {M} ({existing} existing, {new} newly created, {skipped} renewal-only skipped)
Open opportunities: {N}

Existing Accounts (updated with latest deal context):
| Account | Opps | Total Amount | Nearest Close |
|---------|------|-------------|---------------|
| Acme Corp | 2 | $350K | 2026-04-15 |
...

Newly Created Accounts:
| Account | Opps | Total Amount | Nearest Close | Todos Added |
|---------|------|-------------|---------------|-------------|
| NewCo | 1 | $50K | 2026-05-01 | Yes |
...

Skipped (renewal-only — no SE account needed):
| Account | Opps | Type | Amount |
|---------|------|------|--------|
| OldCo | 1 | Renewal | $100K |
...

Next steps for new accounts:
1. Import Gong history: /sales-gong {Account}
2. Summarize account: /sales-summarize-account {Account}
```
