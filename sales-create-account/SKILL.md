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

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `name`, `initials`, `company`

If the config file does not exist, stop and tell the user: "Config not found. Run `/sales-setup` to create your configuration."

### Pre-check: Verify Vault Path

Check that the Obsidian vault directory exists:
```bash
test -d "{config.vault_path}/{config.company_folder}/Accounts"
```
If the directory does not exist, stop and tell the user: "Obsidian vault not found. Run `/sales-setup` to configure your vault path and create the folder structure."

### Execution Strategy
Use subagents for independent research tasks — web searches for company info, Salesforce queries, and Gong imports can run in parallel. Fan out for reads/extraction, fan in for writes.

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
revenue_assets_folder:
---

**AE:** `= this.ae`
**SE:** `= this.se`
**CSM:** `= this.csm`
**Deal Type:** `= this.deal_type`
**Next Call:** `= this.next_call`
**Next Call Agenda:** `= this.next_call_agenda`

**Links:** [Salesforce Account](`= this.salesforce_account`) | [Salesforce Opp](`= this.salesforce_opportunity`) | [Gong](`= this.gong_url`) | [Revenue Assets](`= this.revenue_assets_folder`)

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

If `gong_url` is set AND Playwright CLI is configured (`playwright_configured` is true in config):
- Automatically invoke `/sales-gong {Account} {gong_url}` to run the bulk historical import. No need to ask, just do it.

If Playwright CLI is not configured, mention it in the output:
- "Tip: To import historical Gong calls, install Playwright CLI and run `/sales-gong {Account}`."

### Step 9: Automatic Account Summarization

After both Salesforce and Gong imports are complete (or skipped), automatically run `/sales-summarize-account {Account}` to process all imported meeting data.

This will:
- Populate MEDDPICC, Command of the Message, and TECHMAPS sections from meeting transcripts
- Build the deal ledger from meeting history
- Enrich contacts with roles and influence levels
- Generate the Salesforce Updates section
- Create the tech stack summary and architecture diagram

**Skip this step if:**
- No Gong import was performed (no meeting transcripts to summarize)
- The account has zero meeting files

### Output

After completing all steps, provide:
1. Confirmation of created directory structure
2. List of files created
3. Business context summary (what you learned about the company)
4. Path to the new account for easy access
5. Salesforce import status (opportunities found, open opps linked)
6. Gong import status (auto-triggered if URL provided and Playwright available)
7. Summarization status (completed, skipped, or errors)
