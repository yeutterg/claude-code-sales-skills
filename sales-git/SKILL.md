---
description: Commit and push skill changes and auto-regenerate the README
---

# Update Skills Repo

Commit and push any changes to the skills GitHub repo.

## Instructions

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract from the YAML frontmatter:
- `repo_path` -- the local repo path
- `public_repo_path` -- the public sales-* repo path (optional)
- `company` -- the company name
- `company_folder` -- the company folder name in the vault
- `vault_path` -- the vault path
- `name` -- the user's name
- `initials` -- the user's initials
- `salesforce_username` -- the SF username
- `salesforce_instance_url` -- the SF instance URL

If the config doesn't exist, use the current working directory as the repo path.

### Step 1: Pull Latest Updates

```bash
cd {config.repo_path}
if git remote | grep -q upstream; then
  git fetch upstream && git merge upstream/main --no-edit
else
  git pull origin main
fi
```
If there are uncommitted local changes that would conflict with the pull, stash them first (`git stash`), pull, then pop (`git stash pop`). If the merge introduces conflicts, warn the user and stop.

### Step 2: Check for Proprietary Information

**Before committing, scan all `*/SKILL.md` files in the repo for proprietary information that should be in the config file instead.**

Build a list of proprietary patterns to check from the config:

1. **User identity:** `{config.name}`, `{config.initials}` (as standalone word in examples), `{config.salesforce_username}`
2. **Company-specific paths:** `{config.vault_path}` (the full path), `{config.company_folder}/Accounts` (only flag if `{config.company_folder}` is NOT a generic placeholder like `{config.company_folder}`)
3. **Salesforce URLs:** `{config.salesforce_instance_url}` (if set)
4. **Real customer names:** List all folder names in `{config.vault_path}/{config.company_folder}/Accounts/` -- any of these appearing in SKILL.md files are proprietary
5. **Named persons from deal notes:** Scan all contact files in `{config.vault_path}/{config.company_folder}/Accounts/*/contacts/` to build a list of real person names. Any of these names appearing in SKILL.md files (in examples, prompts, or instructions) are proprietary. Skills should reference deal contacts via `{config.name}` or generic placeholder names -- never real contact names.

Also check for these hardcoded patterns regardless of config:
- Email addresses matching `*@*.com` that aren't in generic examples
- Salesforce record IDs (15-18 char alphanumeric starting with `00` or `a0`) that look like real IDs (not the example `0061Q00000AbCdEFGH`)
- Gong workspace IDs (pattern: `us-NNNNN` where N is a digit)
- Person names that appear alongside real customer account names or in `ae:`, `se:`, `csm:` field examples

**For each finding:**

```
Proprietary information found in SKILL.md files:

| File | Line | Type | Value | Suggested Fix |
|------|------|------|-------|---------------|
| ld-meeting/SKILL.md | 32 | Customer name | "Globex" | Replace with generic example |
| ld-salesforce/SKILL.md | 106 | SF username | "user@company.com" | Use {config.salesforce_username} |
...
```

**Auto-fix:** For each finding, automatically:
1. Replace the proprietary value with the appropriate config reference or generic example
2. If the value is a customer name in an example, replace with "Acme Corp", "Globex", or "Initech"
3. If the value is a staff/contact name in an example, replace with well-known public figures (e.g., "Mark Zuckerberg", "Tim Cook", "Satya Nadella") or generic names ("Jane Smith", "Bob Chen"). Use public figures for named-person examples where a realistic name helps readability.
4. If the value is a path, replace with `{config.vault_path}/{config.company_folder}/...`
5. If the value is a Salesforce URL, replace with `{config.salesforce_instance_url}`

Report what was fixed.

**Important:** Do NOT flag these as proprietary:
- Skill command names (`/sales-meeting`, `/sales-salesforce`, etc.) -- these are the skill identifiers, not proprietary info
- Generic examples already using placeholder names (Acme Corp, Jane Smith, etc.)
- Config variable references like `{config.vault_path}` -- these ARE the correct pattern
- The word "LaunchDarkly" when it appears as a default value suggestion (e.g., "default: LaunchDarkly") in ld-setup only

### Step 3: Check Git Status

```bash
cd {config.repo_path}
git status
```

### Step 4: Regenerate README.md

Read every `*/SKILL.md` file in subdirectories. For each skill, extract the first heading, the `description`, and `argument-hint` from its frontmatter.

**4a: Validate the Skill Dependency Graph**

Before regenerating, scan each SKILL.md for references to other skills (patterns like `/sales-*` invocations). Build the actual dependency graph from these references and compare it to the `## Skill Dependency Graph` mermaid diagram in the current README.md. If there are missing or extra edges, update the diagram to match reality.

For example, if `/sales-create-account` now invokes `/sales-summarize-account` but the diagram doesn't show that edge, add it.

**4b: Regenerate content**

Then rewrite `README.md` using this template. For the Skills section, generate both the summary table AND a detailed subsection for each skill with usage (from argument-hint), a short paragraph describing what it does and what inputs it takes:

```markdown
# Claude Code Skills for Sales Teams

Claude Code skills for interacting with Obsidian sales notes. These skills integrate with an [Obsidian](https://obsidian.md) vault to manage account tracking, meeting notes, and deal documentation.

## Table of Contents

- [Skills](#skills)
  - [Subsections for each skill]
- [Prerequisites](#prerequisites)
- [Obsidian Vault Setup](#obsidian-vault-setup)
- [Getting Started](#getting-started)
  - [1. Install the skills](#1-install-the-skills)
  - [2. Run `/sales-setup`](#2-run-sales-setup)
- [Workflow](#workflow)
  - [New account onboarding](#new-account-onboarding)
  - [Ongoing usage](#ongoing-usage)
  - [Asking questions about a deal](#asking-questions-about-a-deal)
  - [Fixing formatting](#fixing-formatting)
- [Customizing and creating skills](#customizing-and-creating-skills)
  - [Updating existing skills](#updating-existing-skills)
  - [Creating new skills](#creating-new-skills)
  - [Ideas for improvements](#ideas-for-improvements)
- [Contributing](#contributing)

## Skills

| Skill | Description |
|-------|-------------|
| `/skill-name` | Brief description extracted from frontmatter |

### `/skill-name`

**Usage:** `/skill-name <argument-hint>`

Brief paragraph describing what the skill does, its inputs, and key behaviors. Generated from reading the SKILL.md content.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI)
- [Obsidian](https://obsidian.md) with the [Dataview](https://github.com/blacksmithgu/obsidian-dataview) plugin enabled
  - In Dataview settings, enable **Enable Inline Queries** -- this is required for inline expressions like `` `= this.ae` `` to render in account files
- *Optional, for `/sales-salesforce`:* [Homebrew](https://brew.sh) and [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli) (`brew install sf`)
- *Optional, for `/sales-gong`:* [Homebrew](https://brew.sh) and [Playwright MCP](https://github.com/anthropics/claude-code/blob/main/docs/mcp.md) (`claude mcp add playwright -- npx @playwright/mcp@latest --browser chromium`)

## Obsidian Vault Setup

These skills expect the following top-level folder structure in your Obsidian vault:

```
Vault/
├── Daily/                          # Daily notes (YYYY-MM-DD.md)
└── {Company}/
    └── Accounts/                   # Account folders (created by /sales-create-account)
```

`/sales-setup` will create these folders for you during initial setup. After that, `/sales-create-account` creates the full per-account folder structure automatically:

> **Example after creating an account:**
> ```
> Vault/
> ├── Daily/
> └── {Company}/
>     └── Accounts/
>         └── Acme Corp/
>             ├── Acme Corp.md          # Main account file (MEDDPICC, CoM, TECHMAPS, etc.)
>             ├── Ledger.md             # Deal ledger with chronological entries
>             ├── meetings.base         # Dataview table config for meetings
>             ├── contacts.base         # Dataview table config for contacts
>             ├── meetings/             # Meeting notes (YYYY-MM-DD Topic.md)
>             └── contacts/             # Contact cards ({Person Name}.md)
> ```

You can add additional folders under `{Company}/` as you see fit -- for example, `Resources/` for shared collateral, competitive intel, or internal templates. The skills only read from `Accounts/` and `Daily/`.

## Getting Started

### 1. Install the skills

1. Fork this repo on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/claude-code-obsidian-commands.git ~/repos/claude-code-obsidian-commands
   ```
3. Add upstream so you can pull future updates from the original repo:
   ```bash
   cd ~/repos/claude-code-obsidian-commands
   git remote add upstream https://github.com/<original-author>/claude-code-obsidian-commands.git
   ```

To pull upstream updates later, just run `/sales-setup` -- it checks for updates automatically.

### 2. Run `/sales-setup`

Run `/sales-setup` in Claude Code. It will:
- Ask for your role, company, name, and Obsidian vault path
- Search for your company's products and let you review them
- Create a persistent config file at `~/.claude/skills/sales-config.md`
- Create symlinks in `~/.claude/skills/`
- Set up your vault folder structure
- Optionally configure the Salesforce CLI and Playwright MCP

## Workflow

### New account onboarding

1. **Create the account:**
   ```
   /sales-create-account Acme Corp
   ```
   This creates the full folder structure, populates business context from the web, and sets up template files.

2. **Import historical calls from Gong:**
   Search for the account in Gong, go to the Activity tab, and check "Calls Only." Then run `/sales-meeting` with all the call dates and descriptions. The input is freeform -- Claude is pretty smart at figuring out what you mean, so just list them however is fastest:
   ```
   /sales-meeting Acme Corp

   1/15 Discovery
   1/22 Platform Demo
   2/3 Technical sync
   2/10
   2/14 Follow-up with VP Eng
   ```
   Comma-separated works too, and you can mix date formats:
   ```
   /sales-meeting Acme Corp
   Jan 15 Discovery, 1/22 Platform Demo, 2/3 Technical sync, Feb 10, 2/14 Follow-up with VP Eng
   ```

3. **Fill in transcripts:**
   Open each Gong recording in a new tab. For each meeting note that was just created, paste the **Briefing** from Gong into the `## External Summary` section and the **Transcript** into the `## Transcript` section.

4. **Summarize the account:**
   ```
   /sales-summarize-account Acme Corp
   ```
   This launches subagents to process each meeting in parallel, then aggregates everything into the main account file: deal ledger, MEDDPICC, Command of the Message, TECHMAPS, tech stack, architecture diagram, and Salesforce-ready updates.

5. **Update Salesforce and share:**
   ```
   /sales-salesforce Acme Corp
   ```
   This pushes the Salesforce Updates section to all linked Opportunities. Export the main account file as a PDF to share with stakeholders (AEs, CSMs) -- it doubles as an executive summary to bring anyone up to speed.

### Ongoing usage

After each new meeting:

1. **Create the meeting note:**
   ```
   /sales-meeting Acme Corp Technical Deep-Dive
   ```

2. **Take your own notes** during the call in the meeting file.

3. **Add external transcripts** once Gong (or other tools) finish processing -- paste the summary and transcript into the meeting note.

4. **Re-summarize:**
   ```
   /sales-summarize-account Acme Corp
   ```
   This incrementally updates all account sections with the new meeting data, refreshes the Salesforce update, and commits changes.

5. **Push to Salesforce** and share the updated PDF with your deal team:
   ```
   /sales-salesforce Acme Corp
   ```

### Asking questions about a deal

Beyond the skills, you can use Claude Code to interact with your account data conversationally. Just ask whatever's on your mind -- Claude has access to all the meeting notes, contacts, and account context in your vault.

**Deal strategy:**
```
What are the biggest risks in the Acme Corp deal right now?
Who haven't we talked to in over a month?
What open tasks do I have across all my accounts?
```

**Meeting prep:**
```
What should I cover in tomorrow's call with Acme Corp?
Summarize what their VP of Engineering cares about based on past meetings.
What technical objections have come up so far?
```

**Research and context:**
```
What's Acme Corp's current tech stack?
Which accounts are evaluating us against a competitor?
How far along is the Globex POV?
```

### Fixing formatting

If something in an account file doesn't look quite right in Obsidian, just tell Claude what's off and it'll fix it:

```
The MEDDPICC summary callout in Acme Corp is collapsed -- it should be open.
The ledger entries in Globex are out of order, newest should be first.
The contacts table in Initech isn't rendering -- can you check the base file?
Move the architecture diagram above the Salesforce Updates section in Acme Corp.
The ledger is calling him Jon, but he spells it with an H.
```

## Customizing and creating skills

These skills are a starting point -- you should customize them for your own workflow. Skills are just markdown files with instructions and optional frontmatter, and Claude Code is great at editing them for you.

### Updating existing skills

Just tell Claude what you want to change:

```
Update /sales-meeting to add a "## Prep Notes" section to the meeting template.
Update /sales-summarize-account so it also tracks security review status under MEDDPICC > Paper Process.
Change /sales-create-account to set deal_type to "Expansion" by default instead of "Net New".
```

### Creating new skills

To create a new skill, just ask Claude:

```
Create a new skill called /sales-prep that reads the account file and upcoming meeting agenda,
then generates a one-page prep doc with talking points, open questions, and recent news.
```

Claude will create a `SKILL.md` file in a new directory under `~/.claude/skills/` (or in your repo if you tell it to). Skills are just natural language instructions with optional YAML frontmatter -- no code required.

### Ideas for improvements

Here are some directions you could take this:

- **Gong API integration** -- Use an [MCP server](https://modelcontextprotocol.io/) or API calls to pull transcripts and briefings directly from Gong instead of copy-pasting
- **Google Calendar integration** -- Connect a [Google Calendar MCP server](https://github.com/anthropics/claude-code/blob/main/docs/mcp.md) to automatically fetch upcoming meetings and create meeting notes for calls matching an account name -- no manual `/sales-meeting` needed
- **Competitive intelligence** -- Add a skill that searches for competitor mentions across all account meetings and builds a comparison matrix
- **Pipeline dashboard** -- Create a skill that reads all account files and generates a summary table with deal stage, next call, and MEDDPICC completeness
- **POV tracking** -- Add a skill for managing proof-of-value timelines, success criteria, and milestone tracking
- **Email drafts** -- Generate follow-up emails or internal updates from the latest meeting summary and next steps
- **Email and Slack context** -- Pull in relevant email threads and Slack messages as additional context for account summaries, using MCP servers for [Gmail](https://github.com/anthropics/claude-code/blob/main/docs/mcp.md) and [Slack](https://github.com/anthropics/claude-code/blob/main/docs/mcp.md)
- **Static site hosting** -- Publish account files as static pages (e.g., via [Obsidian Publish](https://obsidian.md/publish), [Quartz](https://quartz.jzhao.xyz/), or GitHub Pages) so stakeholders can view live account summaries in a browser instead of receiving PDF exports

If you build something useful, consider contributing it back -- see [Contributing](#contributing) below.

## Contributing

Contributions are welcome! If you've built a new skill, improved an existing one, or fixed a bug, submit a pull request:

1. Make sure your fork is up to date:
   ```bash
   git fetch upstream
   git merge upstream/main
   ```
2. Create a feature branch:
   ```bash
   git checkout -b my-new-skill
   ```
3. Make your changes and commit
4. Push to your fork and open a PR against `main`:
   ```bash
   git push origin my-new-skill
   ```

**Guidelines:**
- Keep skill instructions clear and self-contained -- another user should be able to use your skill without extra context
- If your skill adds a new `sales-*` directory, `/sales-git` will automatically pick it up for the README
- Test your skill on at least one real account before submitting
- Don't include vault-specific paths, company names, or personal info -- use `{config.*}` references and `/sales-setup` handles personalization
- `/sales-git` will check for proprietary information before committing and auto-fix any leaks
```

### Step 5: Stage, Commit, and Push

1. Stage all changed files
2. Generate a concise commit message describing what changed
3. Commit and push to origin
4. If there were no changes before the README update and the README also didn't change, inform the user that everything is up to date

### Step 6: Sync to Public Repo

After successfully committing and pushing the private repo, sync changes to the public `sales-*` repo.

1. **Check if the public repo exists:**
   If `{config.public_repo_path}` is empty or not set, skip this step silently. Otherwise:
   ```bash
   test -d "{config.public_repo_path}/.git"
   ```
   If the directory doesn't exist, warn: "Public repo not found at {config.public_repo_path}. Skipping sync." and stop.

2. **Copy and rename each SKILL.md:**
   For each `ld-*/SKILL.md` in the private repo, copy it to the corresponding `sales-*/SKILL.md` in the public repo:
   ```bash
   for d in {config.repo_path}/sales-*/; do
     skill_name=$(basename "$d")
     sales_name="sales-${skill_name#ld-}"
     mkdir -p "{config.public_repo_path}/$sales_name"
     cp "$d/SKILL.md" "{config.public_repo_path}/$sales_name/SKILL.md"
   done
   ```

3. **Replace `ld-` references with `sales-` in all copied files:**
   ```bash
   cd {config.public_repo_path}
   # Replace /sales- skill references with /sales-
   sed -i '' 's|/sales-|/sales-|g' sales-*/SKILL.md
   # Replace ld-config.md with sales-config.md
   sed -i '' 's|ld-config\.md|sales-config.md|g' sales-*/SKILL.md
   # Replace ld-* directory patterns (in symlink loops, file scans, etc.)
   sed -i '' 's|/sales-\*/|/sales-*/|g' sales-*/SKILL.md
   sed -i '' 's|ld-\*\.md|sales-*.md|g' sales-*/SKILL.md
   ```

4. **Regenerate the public README.md** using the same logic as Step 4, but:
   - Use `sales-*` skill names throughout
   - Use `sales-config.md` instead of `ld-config.md`
   - Use `sales-setup` instead of `ld-setup`
   - Reference the public repo's GitHub URL as the upstream (derive from `git remote get-url origin` in the public repo)
   - Keep the same structure (table of contents, skills table, detailed subsections, prerequisites, vault setup, workflow, customization, contributing)

5. **Commit and push the public repo:**
   ```bash
   cd {config.public_repo_path}
   git add -A
   ```
   If there are changes:
   - Use the same commit message as the private repo, prefixed with "sync: "
   - Commit and push to origin

6. Report: "Public repo synced: {N} skill files updated."
