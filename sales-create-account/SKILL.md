---
description: Create a new account folder structure with template files and business context
argument-hint: <account name> [gong_url] [salesforce_url]
---

# Create Account

Create a new account folder structure with template files.

## Arguments

- `account`: The account name in Title Case (e.g., "Acme Corp")
- URLs (optional): Any combination of:
  - **Gong activity URL** (contains `gong.io/account/activity`): Saved to `gong_url` frontmatter field
  - **Salesforce Account URL** (contains `/Account/` in the path): Saved to `salesforce_account` frontmatter field
  - **Salesforce Opportunity URL** (contains `/Opportunity/` in the path): Saved to `salesforce_opportunity` frontmatter field

URLs can appear in any order after the account name. The skill auto-detects the URL type by checking the path segment (`/Account/` vs `/Opportunity/`).

## Instructions

You are helping a Solutions Engineer set up a new account for tracking sales notes. The account name is: $ARGUMENTS

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `name`, `initials`, `company`, `uses_enterpret`, `salesforce_username`, `salesforce_instance_url`, `salesforce_se_lookup_fields`

If the config file does not exist, stop and tell the user: "Config not found. Run `/sales-setup` to create your configuration."

### Pre-check: Verify Vault Path

Check that the Obsidian vault directory exists:
```bash
test -d "{config.vault_path}/{config.company_folder}/Accounts"
```
If the directory does not exist, stop and tell the user: "Obsidian vault not found. Run `/sales-setup` to configure your vault path and create the folder structure."

### Execution Strategy
Use subagents for independent research tasks — web searches for company info, Salesforce queries, and Gong imports can run in parallel. Fan out for reads/extraction, fan in for writes.

### Step 0a: Auto-Discover Salesforce Account and Gong URLs (if not provided)

If **both** a Salesforce Account URL and Gong URL were already provided as arguments, skip this step entirely — manual URLs always take priority.

If either URL is missing AND `config.uses_enterpret` is `true`, attempt to discover them from the Enterpret knowledge graph and Salesforce:

**Salesforce Account URL (if not provided):**

1. Query Salesforce for accounts matching the account name:
   ```sql
   SELECT Id, Name FROM Account WHERE Name LIKE '%{Account}%' ORDER BY Name LIMIT 5
   ```
   Use the Salesforce CLI REST API (same pattern as `/sales-salesforce`).

2. **If exactly 1 match:** Use it. Construct the URL: `{config.salesforce_instance_url}/lightning/r/Account/{Id}/view`. Store as `salesforce_account`.

3. **If multiple matches:** Present the options to the user and ask them to pick:
   ```
   Multiple Salesforce accounts found for "{Account}":
   1. {Name} ({Id})
   2. {Name} ({Id})
   Which one? (enter number, or 'skip' to enter manually later)
   ```

4. **If 0 matches:** Notify the user: "No Salesforce account found for '{Account}'. You can add the `salesforce_account` URL to the frontmatter later."

5. **If a Salesforce Account is found**, also query for open opportunities assigned to the user:
   ```sql
   SELECT Id, Name, StageName, Amount, CloseDate, Type
   FROM Opportunity
   WHERE AccountId = '{account_id}'
     AND ({config.salesforce_se_lookup_fields joined with OR, each = '{user_id}'})
     AND IsClosed = false
   ORDER BY CloseDate ASC
   ```
   - If exactly 1 open opp: auto-set `salesforce_opportunity` to its URL
   - If multiple open opps: set `salesforce_opportunity` to the first and add `salesforce_opportunity_{type}` for the rest
   - If 0 open opps: leave `salesforce_opportunity` empty

**Gong Activity URL (if not provided):**

1. Use the wisdom MCP to search for the account in Enterpret:
   ```
   mcp__wisdom__search_knowledge_graph: query = "{Account}"
   ```
   Or use a Cypher query to find Account nodes and their linked transcripts:
   ```cypher
   MATCH (n:NaturalLanguageInteraction)-[:PROVIDED_BY_ACCOUNT]->(a:Account)
   WHERE a.origin_record_id IS NOT NULL
   AND n.uf_account_name_X7sdHQ__list CONTAINS '{Account}'
   RETURN DISTINCT n.gong_externallink AS gong_url, a.salesforce_id AS sf_id
   LIMIT 5
   ```

2. Extract the `gong_externallink` from the results. This is a direct Gong call URL. To get the **account activity URL** (which is what `gong_url` frontmatter expects), transform it:
   - Extract the account ID from the Gong URL path
   - Construct: `https://us-{config.gong_workspace_id}.app.gong.io/account/activity?id={gong_account_id}`
   - If the workspace ID is not in config, use the workspace ID from the Gong URL itself

3. **If exactly 1 Gong account match:** Use it. Store as `gong_url`.

4. **If multiple distinct Gong accounts match:** Present options to the user.

5. **If 0 matches or wisdom MCP not connected:** Notify the user: "No Gong activity found for '{Account}' in Enterpret. You can add the `gong_url` to the frontmatter later or run `/sales-gong {Account}` manually."

**Important:**
- This step requires `uses_enterpret: true` in config. If Enterpret is not enabled, skip the Gong discovery and just try the Salesforce lookup.
- Manually provided URLs always override auto-discovered ones.
- If auto-discovery fails for either URL, continue with account creation — the URLs can always be added later.
- Run the Salesforce and Enterpret lookups in parallel for speed.

### Step 0: Early Gong Browser Auth

If a Gong activity URL was provided AND Playwright CLI is configured (`playwright_configured` is true in config):

1. Verify Playwright CLI is available: `which playwright-cli`
2. Derive the session name (account slug): e.g., "Acme Corp" → `gong_acme_corp`
3. **Immediately open the Gong browser** for authentication:
   ```bash
   playwright-cli -s=gong_{account_slug} open {gong_activity_url} --headed --persistent
   ```
4. Tell the user: "**Gong browser opened — please log in if prompted.** The account setup will continue in the background while you authenticate."
5. Do NOT wait for the user to confirm login — proceed immediately to Step 1. The Gong import (Step 8) will check auth status later and the browser session persists.

This ensures the user can authenticate early and walk away while the rest of the setup runs. The browser stays open with `--persistent` and the auth cookies will be ready by the time Step 8 runs the actual import.

If no Gong URL was provided or Playwright is not configured, skip this step.

### Step 1: Create Directory Structure

1. Create the account directory at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/`
2. Create the `meetings/` subdirectory
3. Create the `contacts/` subdirectory

### Step 2: Create Main Account File

Create `{Account}.md` with the following template. Populate URL frontmatter fields based on the URLs provided as arguments (see Arguments section for auto-detection rules):

```markdown
---
ae:
se: {config.name}
csm:
deal_type: Net New
next_call:
next_call_agenda:
salesforce_account:
salesforce_opportunity:
gong_url:
tech_validation_url:
slack_channel:
revenue_assets_folder:
---

**AE:** `= this.ae`
**SE:** `= this.se`
**CSM:** `= this.csm`
**Deal Type:** `= this.deal_type`
**Next Call:** `= this.next_call`
**Next Call Agenda:** `= this.next_call_agenda`

**Links:** [Salesforce Account](`= this.salesforce_account`) | [Salesforce Opp](`= this.salesforce_opportunity`) | [Gong](`= this.gong_url`) | [Tech Validation](`= this.tech_validation_url`) | [Revenue Assets](`= this.revenue_assets_folder`)

## Deal Ledger

![[Ledger]]

## Open Tasks

```dataview
TASK
FROM "{config.company_folder}/Accounts/{Account}"
WHERE !completed
```

## Stakeholders

![[contacts.base]]

## Meetings

![[meetings.base]]

---

## Business Context

### About the Company
<!-- 1-2 bullets on line of business -->

### Recent News
<!-- Relevant headlines with date and link - leadership changes, acquisitions, layoffs, data breaches, etc. -->

---

## MEDDPICC

> [!summary] Summary
> - **Metrics:**
> - **Economic Buyer:**
> - **Decision Criteria:**
> - **Decision Process:**
> - **Paper Process:**
> - **Identified Pain:**
> - **Champion:**
> - **Competition:**

### Metrics

### Economic Buyer

### Decision Criteria

### Decision Process

### Paper Process

### Identified Pain

### Champion

### Competition

---

## Command of the Message

> [!summary] Summary
> **Before:**
> **Pain:**
> **Required:**
> **After:**
> **Value:**

### Before Scenario

### Negative Consequences

### Required Capabilities

### Value Drivers

### After Scenarios

### Positive Business Outcomes

### Compelling Event

---

## TECHMAPS

> [!summary] TECHMAPS Summary
> **Technical Requirements:**
> **Environment:**
> **Competitors:**
> **Hero:**
> **Metrics:**
> **Alignment:**
> **Plan:**
> **Support:**

### Technical Requirements & Scalability

### Environment

### Competitors

### Hero (Technical Champion)

### Metrics

### Alignment

### Plan for Tech Validation

### Support

---

## Tech Stack

> [!summary] Summary
>

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      {ACCOUNT} ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  <!-- Add architecture details as discovered -->                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Salesforce Updates

```
- M/DD {config.initials}: [Most recent ledger entry]

MEDDPICC:
[Summary when populated]

TECHMAPS:
[Summary when populated]

TECH STACK:
[One-line summary when populated]

DEAL HISTORY:
- [Ledger entries]
```
```

### Step 3: Create Ledger File

Create `Ledger.md`:

```markdown
# Deal Ledger

```

### Step 4: Create Meetings Base File

Create `meetings.base`:

```
properties:
  file.name:
    displayName: Meeting
    link: true
  date:
    displayName: Date
  meeting_type:
    displayName: Type
  attendees:
    displayName: Attendees
views:
  - type: table
    name: Meetings
    filters:
      and:
        - file.inFolder(this.file.folder + "/meetings")
    order:
      - file.name
      - date
      - meeting_type
      - attendees
    sort:
      - property: date
        direction: desc
```

### Step 5: Create Contacts Base File

Create `contacts.base`:

```
properties:
  file.name:
    displayName: Name
    link: true
  company:
    displayName: Company
  role:
    displayName: Role
  influence:
    displayName: Influence
  _meetingCount:
    displayName: Mtgs
    formula: 'length(filter(pages(replace(file.folder, "contacts", "meetings")), (p) => contains(p.attendees, file.link)))'
  email:
    displayName: Email
  linkedin:
    displayName: LinkedIn
  notes:
    displayName: Notes
views:
  - type: table
    name: Contacts
    order:
      - file.name
      - company
      - role
      - influence
      - _meetingCount
      - email
      - linkedin
      - notes
    filters:
      and:
        - file.inFolder(this.file.folder + "/contacts")
```

### Step 6: Populate Business Context

Use web search to gather business context:

1. **About the Company**: Search for "{Account} company" to understand their line of business. Add 1-2 bullet points describing:
   - What they do (products/services)
   - Industry and target market

2. **Recent News**: Search for "{Account} news" (current year) and look for relevant headlines such as:
   - Leadership changes (new CEO, CTO, etc.)
   - Acquisitions or mergers
   - Layoffs or restructuring
   - Data breaches or security incidents
   - Major product launches
   - Funding rounds, IPO news, or stock performance (for public companies)
   - Major partnerships or customer wins
   - Financial results or earnings (revenue growth, profitability changes)

   Format each news item as: `- **M/DD/YYYY**: [Headline summary](URL)`

   **CRITICAL: Only include news items where you have a direct URL to the actual article about that specific event.**
   - Link to the specific article (e.g., BusinessWire press release, TechCrunch article, news outlet story)
   - Do NOT link to company profile pages (Tracxn, Crunchbase, ZoomInfo company pages)
   - Do NOT link to generic newsroom landing pages
   - Do NOT include a news item if you cannot find a direct source article - no source = don't include it
   - Acceptable sources: BusinessWire, PRNewswire, TechCrunch, news outlets, TrueUp layoff tracker, specific Glassdoor review pages

   Only include news from the past 6 months that would be relevant to a sales conversation. Skip routine press releases or minor announcements.

### Formatting

- No blank line between heading and first bullet
- No blank line between last bullet and next heading
- Sections flow directly into each other

### Step 7: Automatic Salesforce Import

After creating the account, check which Salesforce URL was provided and run the appropriate import. These steps require the Salesforce CLI to be configured (`salesforce_configured` is true in config). If not configured, skip and note in the output: "Salesforce not configured. Run `/sales-setup salesforce` to enable."

**If a Salesforce Account URL was provided** (saved to `salesforce_account`):
1. Run `/sales-salesforce scan {Account}` to discover all opportunities (open and closed) for this account
2. This will create opportunity files, update the frontmatter with `salesforce_opportunity` and `salesforce_opportunity_*` fields for open opps, add deal history to the ledger, and populate the Opportunity History section

**If a Salesforce Opportunity URL was provided** (saved to `salesforce_opportunity`):
1. Extract the Opportunity ID from the URL (the 15-18 character ID after `/Opportunity/`)
2. Use the Salesforce REST API to get the parent Account ID:
   ```bash
   sf org display --target-org {config.salesforce_username} --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin)['result']; print(d['accessToken']); print(d['instanceUrl'])"
   ```
   ```bash
   curl -s "{instance_url}/services/data/v62.0/sobjects/Opportunity/{opp_id}?fields=AccountId" \
     -H "Authorization: Bearer {access_token}"
   ```
3. Build the Salesforce Account URL from the Account ID and save it to the `salesforce_account` frontmatter field:
   `{config.salesforce_instance_url}/lightning/r/Account/{account_id}/view`
4. Run `/sales-salesforce scan {Account}` to discover all opportunities (open and closed), including the one already provided

**If no Salesforce URL was provided**, skip this step.

### Step 8: Automatic Gong Historical Import

After creating the account (and after Salesforce import if applicable), check if the `gong_url` frontmatter field was populated.

First, try `/sales-enterpret {Account} last 90 days` to bulk-import recent Gong transcripts from Enterpret (faster, no browser needed).

If Enterpret returns no results or the wisdom MCP is not connected, and `gong_url` is set AND Playwright CLI is configured (`playwright_configured` is true in config):
- The browser session from Step 0 should already be open and authenticated.
- Fall back to `/sales-gong {Account} {gong_url}` to run the bulk historical import. No need to ask, just do it.
- **CRITICAL: Never skip Gong imports.** Even if meeting files already have user-pasted notes or Granola summaries, Gong recordings contain the full transcript and AI brief which are always valuable. The only reason to skip a specific call is if Gong has no recording for it (voicemail, missed call).
- If the browser session has an auth issue (SSO expired, login page shown), tell the user to log in and wait — do NOT skip the import.

If neither Enterpret nor Playwright CLI is available, mention it in the output:
- "Tip: To import historical Gong calls, run `/mcp` to connect Enterpret, or install Playwright CLI and run `/sales-gong {Account}`."

### Step 9: Automatic Account Summarization

After both Salesforce and Gong imports are complete (or skipped), automatically run `/sales-summarize-account {Account}` to process all imported meeting data.

This will:
- Populate MEDDPICC, Command of the Message, and TECHMAPS sections from meeting transcripts
- Build the deal ledger from meeting history
- Enrich contacts with roles and influence levels
- Generate the Salesforce Updates section
- Create the tech stack summary and architecture diagram

**Skip this step if:**
- The account has zero meeting files (no data to summarize)

### Output

After completing all steps, provide:
1. Confirmation of created directory structure
2. List of files created
3. Business context summary (what you learned about the company)
4. Path to the new account for easy access
5. Salesforce import status (opportunities found, open opps linked)
6. Gong import status (auto-triggered if URL provided and Playwright available)
7. Summarization status (completed, skipped, or errors)
