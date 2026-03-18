---
description: Post-clone setup: configure vault path, name, role, company, symlinks, and optional Salesforce CLI / Playwright CLI / Google Calendar. Re-run anytime to pull upstream updates and re-apply your config.
argument-hint: [salesforce | playwright | calendar]
---

# LD Skills Setup

Guided onboarding for the Obsidian sales skills. Walks the user through configuration, creates a persistent config file, and sets up integrations. Re-run anytime to pull upstream updates — your config is preserved.

## Arguments

- No arguments: Full initial setup, or pull updates and re-apply config
- `salesforce`: Just Salesforce CLI setup
- `playwright`: Just Playwright CLI setup (for `/sales-gong`)

## Instructions

You are helping a seller set up the Obsidian sales skills on their machine.

Check `$ARGUMENTS`:
- If `$ARGUMENTS` is `salesforce`, skip to **Salesforce CLI Setup** below.
- If `$ARGUMENTS` is `playwright`, skip to **Playwright CLI Setup** below.
- If `$ARGUMENTS` is `calendar`, skip to **Google Calendar Setup** below.
- Otherwise, run the **Full Setup** flow.

---

## Full Setup

### Step 1: Detect Repo and Check for Updates

Determine the repo path by finding where this skill file lives. The repo root is the parent directory of the `ld-setup/` folder — e.g., if this skill is at `~/repos/claude-code-obsidian-commands/sales-setup/SKILL.md`, the repo root is `~/repos/claude-code-obsidian-commands/`.

Verify the repo root contains `ld-*/SKILL.md` files. If not, report an error and stop.

**Check for upstream updates:**

```bash
cd {REPO_ROOT}
if git remote | grep -q upstream; then
  git fetch upstream 2>/dev/null
  LOCAL=$(git rev-parse HEAD)
  REMOTE=$(git rev-parse upstream/main 2>/dev/null)
  if [ "$LOCAL" != "$REMOTE" ]; then
    echo "updates_available"
  else
    echo "up_to_date"
  fi
else
  git fetch origin 2>/dev/null
  LOCAL=$(git rev-parse HEAD)
  REMOTE=$(git rev-parse origin/main 2>/dev/null)
  if [ "$LOCAL" != "$REMOTE" ]; then
    echo "updates_available"
  else
    echo "up_to_date"
  fi
fi
```

- If **updates are available**, tell the user: "There are new updates available from the main repo. Would you like to pull them before continuing?" If yes, merge. If no, skip.
- If **up to date**, continue silently.
- If there are uncommitted local changes that would conflict with the merge, warn: "You have uncommitted changes that would conflict. Commit or stash them first, then re-run `/sales-setup`."

```bash
# Merge if user said yes
cd {REPO_ROOT}
if git remote | grep -q upstream; then
  git merge upstream/main --no-edit
else
  git merge origin/main --no-edit
fi
```

### Step 2: Check for Existing Config

Check if a config file exists at `~/.claude/skills/sales-config.md`:

```bash
test -f ~/.claude/skills/sales-config.md && echo "exists" || echo "not found"
```

If the config exists, read it and extract all values from the YAML frontmatter. These become **defaults** for the questions below — the user can confirm or change each one.

If re-running with an existing config, tell the user: "Found your existing configuration. I'll re-apply your settings to the updated skill files. You can change any values or press Enter to keep the defaults."

### Step 3: Gather Information

Ask the user these questions using AskUserQuestion. If a config file exists, pre-fill the defaults and let the user confirm or change.

**Question 1 — Role:**
"What is your role?"

Present these options:
- Solutions Engineer
- Solutions Architect
- Technical Account Manager
- Account Executive
- AE Manager
- SE Manager
- Customer Success Manager
- Value Engineer

Accept any of these (case-insensitive, abbreviations like SE/SA/TAM/AE/CSM/VE are fine — map them to the full title). Also accept any custom role not on the list. Store the full title (e.g., "Solutions Engineer", not "SE").

If a default exists from config: "What is your role? (current: {role})"

**Question 2 — Company:**
"What company do you work for?"

If a default exists from config: "What company do you work for? (current: {company})"

**Question 3 — Full Name:**
"What is your full name? (This will be used as the default SE on new accounts.)"
- Example: "Jane Smith"

If a default exists from config: "What is your full name? (current: {name})"

**Question 4 — Initials (confirmation):**
Derive initials from their name by taking the first letter of each word and uppercasing (e.g., "Jane Smith" → "JS", "Mary Jane Watson" → "MJW").

Propose the initials: "Your initials would be **{INITIALS}** (used in ledger entries like '3/6 {INITIALS}: ...'). Would you like to change them?"
- If the user says no or confirms: keep the derived initials
- If the user provides different initials: use those instead

**Question 5 — Vault Path:**
"What is the absolute path to your Obsidian vault?"
- Example: `/Users/jane/Documents/Obsidian Vault`

If a default exists from config: "What is the absolute path to your Obsidian vault? (current: {vault_path})"

**Question 6 — Company Folder:**
Propose a folder name derived from the company name: "Your account notes will be stored under `{vault_path}/{Company}/Accounts/`. Would you like a different folder name?"

The default should be the company name as entered (e.g., "LaunchDarkly", "Acme Corp"). Accept any alternative.

If a default exists from config: "Company folder name? (current: {company_folder})"

**Question 7 — Public Repo Path (optional):**
"Do you have a public sales skills repo for sharing generic versions of your skills? If so, provide the absolute path (e.g., `~/repos/claude-code-sales-skills`). `/sales-git` will automatically sync changes to it."

- If provided, store the path
- If the user says no or skips, leave empty
- If a default exists from config: "Public repo path? (current: {public_repo_path}, or press Enter to keep)"

### Step 4: Research Company Products

Search the web for "{COMPANY} products" and "{COMPANY} company overview" to generate:
1. A brief company description (1-2 sentences)
2. A list of the company's main products/services

Present the results to the user for review:

```
Based on my research, here's what I found about {COMPANY}:

Description: {generated description}

Products:
- {Product 1}: {brief description}
- {Product 2}: {brief description}
- ...

Would you like to edit any of this? You can add, remove, or rename products.
```

Accept corrections. If the user adds products, include them. If they remove products, exclude them. Store the final list.

Also ask: "Are there any competitors you'd like to track? For each, provide the name and a brief description. You can also add misspellings that transcription tools commonly produce."

Example format:
```
- Kameleoon: Experimentation and personalization platform (misspellings: Chameleon, Kameleon)
- Eppo: Feature flagging and experimentation (misspellings: Epo)
```

If the user doesn't want to add competitors now, that's fine — they can be added later or will auto-grow as they appear in deal notes.

### Step 5: Save Config File

Write the config to `~/.claude/skills/sales-config.md`. This file persists across repo updates and is read by skills at runtime. It is git-ignored in the repo.

```markdown
---
name: {SE_NAME}
initials: {SE_INITIALS}
role: {ROLE}
company: {COMPANY}
company_description: {generated company description}
company_folder: {COMPANY_FOLDER}
vault_path: {VAULT_PATH}
repo_path: {REPO_ROOT}
public_repo_path: {PUBLIC_REPO_PATH or empty}
salesforce_username: {SF_USERNAME or empty}
salesforce_instance_url: {SF_INSTANCE_URL or empty}
salesforce_se_status_field: {SF_SE_STATUS_FIELD or empty}
salesforce_deal_health_field: {SF_DEAL_HEALTH_FIELD or empty}
salesforce_se_lookup_fields:
  - {field name, e.g., SE__c}
salesforce_custom_fields:
  - {list of custom SOQL field names}
salesforce_configured: {true/false}
playwright_configured: {true/false}
calendar_id: {Google Calendar ID, e.g., user@company.com}
calendar_user_emails: [{list of user's own email addresses}]
calendar_mode: {all or deals}
calendar_include_prep: {true/false}
calendar_configured: {true/false}
gong_workspace_id: {workspace ID or empty}
pdf_export: {true/false}
pdf_path: {PDF output path or empty}
products:
  - name: {Product Name}
    description: {brief description}
    aliases: [{optional alternative names}]
  - name: {Product Name}
    description: {brief description}
competitors:
  - name: {Competitor Name}
    description: {brief description}
    misspellings: [{common misspellings}]
setup_date: {YYYY-MM-DD}
last_updated: {YYYY-MM-DD}
---

# Skills Configuration

This file is generated by `/sales-setup` and persists your local configuration.
It is read by skills at runtime and survives repo updates.

To reconfigure or pull updates, run `/sales-setup` again.
```

If the config already existed, preserve the `salesforce_username`, `salesforce_instance_url`, `salesforce_se_status_field`, `salesforce_deal_health_field`, `salesforce_se_lookup_fields`, `salesforce_custom_fields`, `salesforce_configured`, `playwright_configured`, `calendar_id`, `calendar_user_emails`, `calendar_mode`, `calendar_include_prep`, `calendar_configured`, `gong_workspace_id`, `pdf_export`, `pdf_path`, `public_repo_path`, and `setup_date` values from the old config. Update `last_updated` to today.

### Step 6: Create Symlinks

Create symlinks from `~/.claude/skills/` to each `ld-*` directory in the repo:

```bash
mkdir -p ~/.claude/skills
for d in {REPO_ROOT}/sales-*/; do
  skill_name=$(basename "$d")
  # Remove existing symlink if present (idempotent)
  rm -f ~/.claude/skills/"$skill_name"
  ln -s "$d" ~/.claude/skills/"$skill_name"
done
```

List the created symlinks to confirm.

### Step 7: Create Vault Folder Structure

Check if the required vault folders exist. Use the company folder name from config (not hardcoded):

```bash
test -d "{VAULT_PATH}/Daily" && test -d "{VAULT_PATH}/{COMPANY_FOLDER}/Accounts"
```

- If both exist: Report "Vault folder structure already exists" and continue.
- If the vault path itself doesn't exist (e.g., no Obsidian vault at all): Ask the user: "The vault path `{VAULT_PATH}` doesn't exist. Would you like to create it?" If yes, create it. If no, warn that skills won't work until the vault exists, and continue.
- If the vault exists but `Daily/` or `{COMPANY_FOLDER}/Accounts/` is missing: Ask the user: "Your vault is missing the required folders (`Daily/` and/or `{COMPANY_FOLDER}/Accounts/`). Would you like to create them?" If yes, create the missing folders. If no, warn that skills won't work until these folders exist, and continue.

```bash
mkdir -p "{VAULT_PATH}/Daily"
mkdir -p "{VAULT_PATH}/{COMPANY_FOLDER}/Accounts"
```

### Step 8: Migrate Old Commands

Check if `~/.claude/commands/` contains any `ld-*.md` files:

```bash
ls ~/.claude/commands/sales-*.md 2>/dev/null
```

If old command files are found:
1. Remove them: `rm ~/.claude/commands/sales-*.md`
2. Inform the user: "Removed old command files from `~/.claude/commands/`. These have been replaced by the new skills format — no workflow changes needed, skill names are the same."

If no old command files exist, skip this step silently.

### Step 9: Migrate Legacy Frontmatter

Scan all account files in `{VAULT_PATH}/{COMPANY_FOLDER}/Accounts/*/` for the old `salesforce_url` frontmatter field. For each account file that has `salesforce_url`, rename it to `salesforce_opportunity` (preserve the value, just change the key name).

```bash
grep -rl '^salesforce_url:' "{VAULT_PATH}/{COMPANY_FOLDER}/Accounts/"
```

If any files were migrated, report: "Renamed `salesforce_url` → `salesforce_opportunity` in N account files."

If none found, skip silently.

### Step 10: Salesforce CLI (Optional)

Ask the user: "Would you like to set up the Salesforce CLI for pushing SE notes to Salesforce? (This is optional — you can always run `/sales-setup salesforce` later.)"

Options:
- **Yes** — Run the **Salesforce CLI Setup** flow below
- **No** — Skip

### Step 11: Google Calendar (Optional)

Ask the user: "Would you like to set up Google Calendar integration? This lets `/sales-calendar` scan your calendar and auto-create meeting notes for upcoming calls. (Optional — you can always run `/sales-setup calendar` later.)"

Options:
- **Yes** — Run the **Google Calendar Setup** flow below
- **No** — Skip

### Step 12: Playwright CLI (Optional)

Ask the user: "Would you like to set up Playwright CLI for automatic Gong call imports? (This is optional. You can always run `/sales-setup playwright` later.)"

Options:
- **Yes** — Run the **Playwright CLI Setup** flow below
- **No** — Skip

### Step 13: PDF Export (Optional)

Ask the user: "Would you like to export account PDFs daily when running `/sales-today`? This generates clean, shareable PDFs of your account files. (y/n)"

Options:
- **Yes:**
  1. Suggest default path: `{VAULT_PATH}/{COMPANY_FOLDER}/PDFs` and ask: "Where should PDFs be saved? (default: `{VAULT_PATH}/{COMPANY_FOLDER}/PDFs`)"
  2. Accept the default or a custom path
  3. Create the PDFs folder if it doesn't exist: `mkdir -p "{chosen_path}"`
  4. Update config with `pdf_export: true` and `pdf_path: {chosen_path}`
- **No:**
  - Set `pdf_export: false` in config, leave `pdf_path` empty

### Step 14: Report

Output a summary of everything that was done:

```
Setup complete!

  Role:       {ROLE}
  Company:    {COMPANY}
  Name:       {SE_NAME}
  Initials:   {SE_INITIALS}
  Vault:      {VAULT_PATH}
  Company Folder: {COMPANY_FOLDER}
  Repo:       {REPO_ROOT}
  Config:     ~/.claude/skills/sales-config.md

  Products:   {N} products configured
  Competitors: {N} competitors configured
  Skills:     {N} skills linked
  Salesforce: {configured/not configured}
  Calendar:   {configured/not configured}
  Playwright: {configured/not configured}
  PDF Export: {enabled (path) / not configured}

To pull updates and re-apply your config, just run /sales-setup again.
```

---

## Salesforce CLI Setup

### Step 1: Check for Homebrew

```bash
which brew
```

If `brew` is not found:
- Tell the user: "Homebrew is not installed. Install it first by running:"
  ```
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- Stop and ask the user to install Homebrew, then re-run `/sales-setup salesforce`.

### Step 2: Check if sf CLI is Installed

```bash
which sf
```

If `sf` is not found:
- Tell the user: "The Salesforce CLI (`sf`) is not installed. Installing via Homebrew..."
- Run: `brew install sf`
- If the install fails, show the error and stop.

### Step 3: Determine Instance URL

Read the config to check if `salesforce_instance_url` is already set.

If not, ask the user: "What is your Salesforce instance URL? (e.g., `https://yourcompany.my.salesforce.com`)"

### Step 4: Authenticate

Once `sf` is installed, run the login command using the instance URL:

```bash
sf org login web --instance-url {SALESFORCE_INSTANCE_URL}
```

This opens a browser for SSO login. Wait for the user to complete authentication.

### Step 5: Verify and Extract Username

After authentication, verify the connection:

```bash
sf org list --json
```

Check the output for a connected org with the instance URL. Extract the username (e.g., `user@company.com`).

### Step 6: Discover Salesforce Custom Fields

After authentication, discover the custom fields available on the Opportunity object. This detects which MEDDPICC, deal context, and SE-specific fields exist in the user's Salesforce org.

```bash
sf sobject describe --sobject Opportunity --target-org {SF_USERNAME} --json
```

From the output, look for custom fields (ending in `__c`) in these categories:

**SE Status field** (for pushing SE notes):
- Search for fields with names containing: `Technical_Blockers`, `SE_Status`, `SE_Notes`, `Solution_Engineer_Notes`, `SE_Update`
- Present candidates to the user: "Which field should SE notes be pushed to?" and let them confirm

**SE Lookup field** (for querying "my accounts"):
- Search for fields with names containing: `SE__c`, `Solutions_Engineer`, `SE_Primary`, `Sales_Engineer`
- These are lookup fields (type: reference) to User
- Store as an array of fallback field names

**Deal Health field** (for pushing Red/Yellow/Green health scores):
- Search for fields with names containing: `Health`, `SE_Health`, `Opportunity_Health`, `Deal_Health`, `SE_Opportunity_Health`
- These are picklist fields with values like Green, Yellow, Red (or similar traffic-light values)
- If found, store as `salesforce_deal_health_field`
- If not found, leave empty — the weekly review will still generate health scores locally but won't push to Salesforce

**MEDDPICC / Deal Context fields** (for pulling deal context):
- Search for fields containing: `Pain`, `Champion`, `Decision_Criteria`, `Decision_Process`, `Competition`, `Forecast`, `POV_Status`, `Trial_Status`, `CSM`, `Manager_Notes`, `SE_Next_Steps`, `Next_Steps`, `ARR`, `Loss_Reason`, `Business_Value`, `Use_Case`, `Solution_Fit`, `Lead_Source`
- Store all found custom field API names

Present the discovered fields to the user:
```
Found these Salesforce custom fields:

SE Status field: Technical_Blockers__c
SE Lookup fields: SE__c, Solutions_Engineer__c
Deal Health field: SE_Opportunity_Health__c (Green/Yellow/Red)
Deal context fields: Pain__c, Decision_Criteria__c, Champion_formula__c, ...

Does this look right? You can adjust if needed.
```

### Step 7: Discover Gong Workspace ID

Ask the user: "Do you use Gong? If so, what is your Gong workspace ID? (Found in Gong URLs like `https://us-XXXXX.app.gong.io/...`)"

If provided, store it. If not, skip.

### Step 8: Update Config

Update `~/.claude/skills/sales-config.md` frontmatter:
- `salesforce_username: {extracted username}`
- `salesforce_instance_url: {instance URL}`
- `salesforce_se_status_field: {discovered field}`
- `salesforce_deal_health_field: {discovered field or empty}`
- `salesforce_se_lookup_fields: {discovered fields}`
- `salesforce_custom_fields: {discovered fields}`
- `salesforce_configured: true`
- `gong_workspace_id: {if provided}`
- `last_updated: {today}`

### Step 9: Report

- If successful: "Salesforce CLI is authenticated and ready. You can now use `/sales-salesforce` to push SE notes."
- If failed: Show the error and suggest re-running `/sales-setup salesforce`.

---

## Google Calendar Setup

`/sales-calendar` uses the **Claude.ai built-in Google Calendar integration** (`mcp__claude_ai_Google_Calendar__*` tools). This integration is managed through the Claude Desktop app and supports one Google account at a time. It uses Anthropic's verified OAuth, so it works with corporate Google Workspace accounts that block unverified third-party apps.

### Step 1: Connect Google Calendar in Claude Desktop

Check if the `mcp__claude_ai_Google_Calendar__gcal_list_calendars` tool is available by attempting to call it.

**If the tool is available**, list the calendars and show the user which account is connected. Skip to Step 2.

**If the tool is NOT available**, guide the user through setup:

```
To connect Google Calendar:

1. Open the Claude Desktop app
2. Click the gear icon (top-right) to open Settings
3. Navigate to "Integrations" (or "Connected Apps")
4. Find "Google Calendar" and click "Connect"
5. Sign in with your work Google account (e.g., user@company.com)
6. Grant calendar access when prompted
7. Return here and re-run `/sales-setup calendar`

Note: The Claude.ai integration supports one Google account. Use your primary
work account — you can still view other calendars shared with that account.
```

Stop and wait for the user to complete the setup in the Desktop app.

### Step 2: Identify Calendar and User Email

Call `mcp__claude_ai_Google_Calendar__gcal_list_calendars` and find the primary calendar. Extract the user's email from the primary calendar ID.

Present:
```
Connected Google Calendar account: user@company.com

Calendar ID for scanning: user@company.com (primary)

Is this the correct account for scanning meetings?
```

Store the calendar ID as `calendar_id` (single string, not a list).

### Step 3: Identify User Emails

Ask: "What email addresses are yours? These will be excluded from meeting attendee lists. (comma-separated)"

Pre-fill with the primary calendar email. The user may add additional personal emails. Let the user confirm or modify.

Store as `calendar_user_emails` list.

### Step 4: Meeting Mode

Ask: "What types of meetings should `/sales-calendar` create notes for?"

Options:
- **All meetings** (deal meetings + internal meetings like standups, 1:1s): Store `calendar_mode: all`
- **Deal meetings only** (only meetings that match an existing account): Store `calendar_mode: deals`

Default: `all`

### Step 5: Prep Meeting Preference

Ask: "Should `/sales-calendar` also create notes for internal deal prep/debrief meetings? (meetings that match an account name but have no external attendees)"

- **Yes**: Store `calendar_include_prep: true`
- **No**: Store `calendar_include_prep: false`

Default: `true`

### Step 6: Update Config

Update `~/.claude/skills/sales-config.md` frontmatter:
- `calendar_id: {primary calendar email}`
- `calendar_user_emails: [{user emails}]`
- `calendar_mode: {all or deals}`
- `calendar_include_prep: {true/false}`
- `calendar_configured: true`
- `last_updated: {today}`

Remove `calendar_accounts` if it exists from a previous setup (replaced by `calendar_id`).

### Step 7: Report

"Google Calendar is configured via the Claude.ai integration. You can now use `/sales-calendar` to scan your calendar and auto-create meeting notes."

Show a quick usage guide:
```
Usage:
  /sales-calendar              — Today (morning) or tomorrow (afternoon)
  /sales-calendar week         — This week's meetings
  /sales-calendar next week    — Next week's meetings
  /sales-calendar 2026-03-15   — Specific date
```

---

## Playwright CLI Setup

### Step 1: Check if Node.js/npm is Available

```bash
which npm
```

If `npm` is not found, tell the user: "Node.js is not installed. Install it via Homebrew (`brew install node`) or from https://nodejs.org, then re-run `/sales-setup playwright`."

### Step 2: Install Playwright CLI

Run:
```bash
npm install -g @playwright/cli@latest
```

Verify installation:
```bash
playwright-cli --version
```

This installs the Playwright CLI globally. `/sales-gong` uses it to automate Gong browser interactions for importing call recordings.

### Step 3: Check for Old Playwright MCP Server

Check if the old Playwright MCP server is configured:
```bash
claude mcp list 2>/dev/null | grep -i playwright
```

If a Playwright MCP server is found, ask the user: "You have an old Playwright MCP server configured. Would you like to remove it? The new Playwright CLI replaces it and is more token-efficient. (default: no)"

- If **yes**: Run `claude mcp remove playwright` and report that it was removed.
- If **no** (default): Leave it in place. Note: "Keeping the old Playwright MCP server. You can remove it later with `claude mcp remove playwright`."

### Step 4: Update Config

Update `~/.claude/skills/sales-config.md` frontmatter:
- `playwright_configured: true`
- `last_updated: {today}`

### Step 5: Report

- If successful: "Playwright CLI is installed. You can now use `/sales-gong` to import Gong call recordings into meeting notes."
- If failed: Show the error and suggest re-running `/sales-setup playwright`.
