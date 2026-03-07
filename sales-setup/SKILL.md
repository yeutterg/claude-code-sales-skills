---
description: Post-clone setup — configure vault path, name, role, company, symlinks, and optional Salesforce CLI / Playwright MCP. Re-run anytime to pull upstream updates and re-apply your config.
argument-hint: [salesforce | playwright]
---

# Sales Skills Setup

Guided onboarding for the Obsidian sales skills. Walks the user through configuration, creates a persistent config file, and sets up integrations. Re-run anytime to pull upstream updates — your config is preserved.

## Arguments

- No arguments: Full initial setup, or pull updates and re-apply config
- `salesforce`: Just Salesforce CLI setup
- `playwright`: Just Playwright MCP setup (for `/sales-gong`)

## Instructions

You are helping a seller set up the Obsidian sales skills on their machine.

Check `$ARGUMENTS`:
- If `$ARGUMENTS` is `salesforce`, skip to **Salesforce CLI Setup** below.
- If `$ARGUMENTS` is `playwright`, skip to **Playwright MCP Setup** below.
- Otherwise, run the **Full Setup** flow.

---

## Full Setup

### Step 1: Detect Repo and Check for Updates

Determine the repo path by finding where this skill file lives. The repo root is the parent directory of the `sales-setup/` folder — e.g., if this skill is at `~/repos/claude-code-sales-skills/sales-setup/SKILL.md`, the repo root is `~/repos/claude-code-sales-skills/`.

Verify the repo root contains `sales-*/SKILL.md` files. If not, report an error and stop.

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

The default should be the company name as entered (e.g., "Acme Corp"). Accept any alternative.

If a default exists from config: "Company folder name? (current: {company_folder})"

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
- Competitor A: Description of competitor (misspellings: Misspelling1, Misspelling2)
- Competitor B: Description of competitor (misspellings: Misspelling1)
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
salesforce_username: {SF_USERNAME or empty}
salesforce_instance_url: {SF_INSTANCE_URL or empty}
salesforce_se_status_field: {SF_SE_STATUS_FIELD or empty}
salesforce_se_lookup_fields:
  - {field name, e.g., SE__c}
salesforce_custom_fields:
  - {list of custom SOQL field names}
salesforce_configured: {true/false}
playwright_configured: {true/false}
gong_workspace_id: {workspace ID or empty}
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

If the config already existed, preserve the `salesforce_username`, `salesforce_instance_url`, `salesforce_se_status_field`, `salesforce_se_lookup_fields`, `salesforce_custom_fields`, `salesforce_configured`, `playwright_configured`, `gong_workspace_id`, and `setup_date` values from the old config. Update `last_updated` to today.

### Step 6: Create Symlinks

Create symlinks from `~/.claude/skills/` to each `sales-*` directory in the repo:

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

Check if `~/.claude/commands/` contains any `sales-*.md` files:

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

### Step 11: Playwright MCP (Optional)

Ask the user: "Would you like to set up Playwright MCP for automatic Gong call imports? (This is optional — you can always run `/sales-setup playwright` later.)"

Options:
- **Yes** — Run the **Playwright MCP Setup** flow below
- **No** — Skip

### Step 12: Report

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
  Playwright: {configured/not configured}

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

**MEDDPICC / Deal Context fields** (for pulling deal context):
- Search for fields containing: `Pain`, `Champion`, `Decision_Criteria`, `Decision_Process`, `Competition`, `Forecast`, `POV_Status`, `Trial_Status`, `CSM`, `Manager_Notes`, `SE_Next_Steps`, `Next_Steps`, `ARR`, `Loss_Reason`, `Business_Value`, `Use_Case`, `Solution_Fit`, `Lead_Source`
- Store all found custom field API names

Present the discovered fields to the user:
```
Found these Salesforce custom fields:

SE Status field: Technical_Blockers__c
SE Lookup fields: SE__c, Solutions_Engineer__c
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
- `salesforce_se_lookup_fields: {discovered fields}`
- `salesforce_custom_fields: {discovered fields}`
- `salesforce_configured: true`
- `gong_workspace_id: {if provided}`
- `last_updated: {today}`

### Step 9: Report

- If successful: "Salesforce CLI is authenticated and ready. You can now use `/sales-salesforce` to push SE notes."
- If failed: Show the error and suggest re-running `/sales-setup salesforce`.

---

## Playwright MCP Setup

### Step 1: Check if Node.js/npx is Available

```bash
which npx
```

If `npx` is not found, tell the user: "Node.js is not installed. Install it via Homebrew (`brew install node`) or from https://nodejs.org, then re-run `/sales-setup playwright`."

### Step 2: Add Playwright MCP Server

Run:
```bash
claude mcp add playwright -- npx @playwright/mcp@latest --browser chromium
```

This registers the Playwright MCP server with Claude Code. It will launch a visible Chromium browser window when activated.

### Step 3: Update Config

Update `~/.claude/skills/sales-config.md` frontmatter:
- `playwright_configured: true`
- `last_updated: {today}`

### Step 4: Report

- If successful: "Playwright MCP is configured. Restart Claude Code for the changes to take effect. You can now use `/sales-gong` to import Gong call recordings into meeting notes."
- If failed: Show the error and suggest re-running `/sales-setup playwright`.
