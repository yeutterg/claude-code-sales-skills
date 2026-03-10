---
description: Weekly review of all accounts with open Salesforce opportunities — pulls deal context, summarizes activity, updates ledgers and Salesforce
argument-hint:
---

# Weekly Account Review

Portfolio-wide sweep of all accounts with open Salesforce opportunities. Pulls current deal context, identifies unsummarized meetings, adds status ledger entries, and pushes updates to Salesforce. Designed to run autonomously at the end of the week — start it and walk away.

## Instructions

You are running a weekly account review for: $SE_NAME

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `name`, `initials`, `company`, `salesforce_username`, `salesforce_instance_url`, `salesforce_se_status_field`, `salesforce_deal_health_field`, `salesforce_custom_fields`. Use these values throughout the rest of this skill wherever `{config.*}` placeholders appear.

### Pre-check

```bash
test -d "$VAULT_PATH/{config.company_folder}/Accounts"
```
If the vault doesn't exist, stop: "Obsidian vault not found. Run `/sales-setup` to configure."

```bash
which sf && sf org list 2>&1
```
If `sf` is not installed or not authenticated, stop: "Salesforce CLI not ready. Run `/sales-setup salesforce`."

### Execution Strategy
Use subagents for all independent work — account scanning, Salesforce queries, and web searches should run in parallel via subagents whenever possible. Fan out for reads/extraction, fan in for writes.

---

### Phase 1: Discover Accounts with Open Opportunities

Scan all account directories under `$VAULT_PATH/{config.company_folder}/Accounts/`. For each account:

1. Read `{Account}.md` frontmatter
2. Check if at least one `salesforce_opportunity` or `salesforce_opportunity_*` field contains a non-empty URL (must start with `http` and contain `/Opportunity/` — skip Account URLs)
3. Check if `salesforce_account` is populated (non-empty, contains `http`)

Categorize each account into one of these lists:

- **Active (set up):** Has valid opportunity URL(s) AND `salesforce_account` is populated → these get processed in Phase 2
- **Needs setup:** Has valid opportunity URL(s) BUT `salesforce_account` is empty → flagged for the user at the end (NOT processed)
- **Bad opp URL:** Has a `salesforce_opportunity` field with a non-Opportunity URL (e.g., `/Account/` instead of `/Opportunity/`) → auto-fix before categorizing

**Auto-fixing bad opp URLs:**

For each account with a bad opp URL, extract the Account ID from the URL and query Salesforce for open opportunities on that account:

```sql
SELECT Id, Name FROM Opportunity WHERE AccountId = '{account_id}' AND IsClosed = false
```

- If exactly 1 open opp is found: automatically update the `salesforce_opportunity` field with the correct Opportunity URL and re-categorize the account as Active or Needs Setup
- If multiple open opps are found: update `salesforce_opportunity` with the first one and add additional opps as `salesforce_opportunity_2`, `salesforce_opportunity_3`, etc. Re-categorize accordingly.
- If no open opps are found: clear the `salesforce_opportunity` field, note the account has no open opportunities
- Also: if the bad URL was an Account URL and `salesforce_account` is empty, populate `salesforce_account` with that URL (it's the right value, just in the wrong field)

Report: "Found {N} set-up accounts to process, {M} accounts need setup first, fixed {K} bad opp URLs"

---

### Phase 2: Process Each Set-Up Account via Subagents

Launch a subagent for each **active (set up)** account only (`subagent_type: "general-purpose"`, `model: "sonnet"`). Run all account subagents **in parallel**. Do NOT process accounts from the "needs setup" list.

Each subagent handles one account end-to-end. Pass it:
- The account name and file path
- The vault path and SE name/initials
- Today's date
- The Salesforce access token and instance URL (obtain once in the main agent before launching subagents)

**Subagent prompt template:**

```
You are running a weekly review for the {config.company} account: {Account}

Account file: {path to Account.md}
Vault path: {vault_path}
SE Name: {se_name}
SE Initials: {se_initials}
Today: {YYYY-MM-DD}
Salesforce access token: {token}
Salesforce instance URL: {instance_url}

Perform these steps in order:

### Step 1: Pull Deal Context from Open Opportunities

For each salesforce_opportunity field in the account frontmatter, extract the Opportunity ID and query Salesforce for current deal context:

```sql
SELECT Id, Name, StageName, Amount, CloseDate, Type, Probability, ForecastCategoryName,
  NextStep, Description, LastActivityDate, LastStageChangeDate, IsClosed,
  {config.salesforce_custom_fields}
FROM Opportunity WHERE Id = '{opp_id}'
```

Use Python with urllib (not curl) to avoid shell escaping issues with the access token.

**If any opportunity is now closed (IsClosed = true):**
- Note it in your report
- Clear the corresponding salesforce_opportunity field in the frontmatter

**If all opportunities are now closed:**
- Clear all salesforce_opportunity fields
- Note this account no longer has open opportunities
- Skip remaining steps — return early with this status

### Step 2: Check for Unsummarized Meetings and Auto-Summarize

List ALL meeting files in {account_path}/meetings/. For each file:

1. Check if `## Summary` has content (not just the heading or `- [ ]`)
2. If Summary is empty, check if `## External Summary` or `## Transcript` has content
3. Categorize:
   - **Summarizable:** Has External Summary or Transcript content but no Summary → can be auto-summarized
   - **Needs input:** Has NO External Summary AND no Transcript content → truly needs user input (transcripts/briefs must be added first)

**Auto-summarize if possible:**

If there are ANY summarizable meetings (across all time, not just recent):
1. Run `/sales-summarize-account {Account}` — this will process all unsummarized meetings that have source material, update MEDDPICC/TECHMAPS/CoM, refresh the deal ledger, and update the Salesforce Updates section
2. Note which meetings were auto-summarized in your return data
3. After summarization completes, re-read the account file and Ledger.md (they will have been updated)

If there are meetings that need input (no source material at all), note them but continue processing — do not stop.

### Step 3: Add or Update Weekly Status Ledger Entry

Read Ledger.md for this account.

**Determine recent activity:**
- Check the most recent non-status ledger entry (any entry that does NOT contain "(status)")
- Check the Salesforce LastActivityDate and LastStageChangeDate from Step 1
- Check for any meetings in the last 7 days (regardless of summary status)
- Check AE/CSM notes from the deal context fields from config

**Build the status entry:**

Format: `- {M/D} {SE_INITIALS} (status): {update}`

**Keep it concise — one line, max ~20 words.** Include stage, key recent event, and what's next. Do NOT repeat deal amounts, close dates, days in stage, or forecast — those are visible in Salesforce already.

If there IS recent activity (last 7 days):
- Example: `- 3/7 {config.initials} (status): Tech Eval. Customer reviewing pricing proposal. Demo 3/12.`

If there is NO recent activity:
- Example: `- 3/7 {config.initials} (status): No activity since 2/4.`

**Updating vs adding:**
- Search for an existing `(status)` entry in the ledger (a line containing "(status)")
- If one exists: REPLACE it with the new entry (same line position)
- If none exists: ADD the new entry at the TOP of the ledger (after the `# Deal Ledger` heading)

This ensures there is only ever one (status) entry per account.

### Step 4: Update Salesforce Updates Section and Push to Salesforce

**4a. Update the `## Salesforce Updates` section in the account file:**

Read the existing `## Salesforce Updates` section from the account file. Look for the triple-backtick code block.

The status entry goes at the TOP of the code block, right before the most recent deal history entry (or before MEDDPICC if no deal history entry exists at the top). Use the same format as the ledger: `- M/D {config.initials} (status): {concise update}`

- If the code block has existing content: Add/replace the `(status)` line at the very top of the code block. Do NOT duplicate any existing deal history entries — the status line is separate from and in addition to the most recent meeting entry that's already there.
- If a previous `(status)` line already exists in the code block, replace it.
- If the code block is empty or the section doesn't exist: write a minimal code block with just the status line.

This ensures the SE Notes in Salesforce always reflect the latest weekly review status, even for accounts that haven't been fully summarized yet.

**4b. Push to Salesforce:**

Extract the full content of the (now-updated) code block from `## Salesforce Updates`.

1. Convert newlines to `<br>` tags
2. Bold section headers (MEDDPICC, TECHMAPS, TECH STACK, DEAL HISTORY)
3. For each open opportunity ID, PATCH via REST API:
   ```
   PATCH {instance_url}/services/data/v62.0/sobjects/Opportunity/{id}
   Authorization: Bearer {token}
   Content-Type: application/json
   {"{config.salesforce_se_status_field}": "{html_content}"}
   ```

### Step 5: Deal Health Assessment

Score each open opportunity as **Green**, **Yellow**, or **Red** based on deal signals. This is a holistic assessment, not a formula — use judgment informed by the data.

**Signals to evaluate:**

| Signal | Green | Yellow | Red |
|--------|-------|--------|-----|
| Days since last meeting | < 14 days | 14-30 days | 30+ days |
| Champion engagement | Active, responding | Slowing down, delayed responses | Dark, no-shows, unresponsive |
| MEDDPICC completeness | Most fields populated | Key gaps (EB, Decision Process) | Major gaps across multiple fields |
| Stage velocity | Progressing on schedule | Stalled but explainable | Stuck for 30+ days with no movement |
| Close date | On track or moved in | Pushed once | Pushed multiple times |
| Stakeholder breadth | Multi-threaded (3+ contacts) | 2 contacts | Single-threaded |
| Technical validation | POV complete or scheduled | POV delayed but planned | No technical validation path defined |
| Competitive pressure | No active competitor or we're preferred | Competitor in evaluation | Competitor is incumbent or preferred |
| Next steps clarity | Clear next step with date/owner | Vague next step | No next steps defined |

**Scoring logic:**
- **Green**: Deal is progressing well. Most signals are positive. Champion is engaged, timeline is on track.
- **Yellow**: Deal has 1-2 risk signals that need attention but is still viable. Typical: slowing momentum, a key gap in MEDDPICC, or a pushed close date.
- **Red**: Deal has multiple risk signals. Typical: champion gone dark, stalled 30+ days, single-threaded with no EB access, or competitor is winning.

**One-line justification**: Write a short explanation for the score (max ~15 words). This goes into Salesforce and the ledger.

Examples:
- Green: "Champion engaged, POV scheduled for 3/20, no blockers."
- Yellow: "Close date pushed from 3/15 to 4/30. Waiting on budget approval."
- Red: "No contact in 28 days. Champion left the company. Single-threaded."

**Push to Salesforce (if configured):**

If `{config.salesforce_deal_health_field}` is set in the config:
1. For each open opportunity, PATCH the health field via REST API:
   ```
   PATCH {instance_url}/services/data/v62.0/sobjects/Opportunity/{id}
   Authorization: Bearer {token}
   Content-Type: application/json
   {"{config.salesforce_deal_health_field}": "{Green|Yellow|Red}"}
   ```

If `salesforce_deal_health_field` is NOT set in config, skip the Salesforce push but still include the health score in the return data and the ledger status entry.

**Update ledger status entry**: Append the health color to the status entry from Step 3. Format: `- M/D {initials} (status): 🟢/🟡/🔴 {justification}`

### Step 6: Return Results

Return EXACTLY this format:

---BEGIN WEEKLY REVIEW---
ACCOUNT: {name}
STATUS: {processed|needs_input|no_open_opps|error}
OPEN_OPPS: {count}
OPP_DETAILS: {opp name | stage | amount | close date | forecast — one per line}
DEAL_HEALTH: {Green|Yellow|Red} — {justification}
DEAL_HEALTH_PUSHED: {yes|no|not configured}
AUTO_SUMMARIZED: {yes — N meetings | no}
UNSUMMARIZED_MEETINGS: {list of filenames that still need input, or "none"}
LEDGER_ENTRY: {the status entry that was added/updated, now including health color}
SF_PUSH: {success count}/{total count} or "skipped"
CLOSED_OPPS: {any opps that were found to be closed, or "none"}
NEW_COMPETITORS: {any new competitors found during auto-summarization, or "none"}
NEW_OBJECTIONS: {recurring objections or blockers across this account's meetings, or "none"}
FEATURE_REQUESTS: {product gaps or feature requests from this account, or "none"}
NOTES: {any issues, warnings, or notable changes}
---END WEEKLY REVIEW---
```

---

### Phase 3: Collect Results and Report

After all subagents complete, collect their results and build the final report.

#### Accounts Successfully Processed

For each account with STATUS=processed:

```
| Account | Health | Stage | Amount | Close | Forecast | Status Entry | SF Push |
|---------|--------|-------|--------|-------|----------|--------------|---------|
| Acme    | 🟢     | Tech Eval | $50K | 3/15 | Commit | In Tech Eval. Demo 3/12. | 1/1 |
| Globex  | 🔴     | Discovery | $100K | 3/30 | Pipeline | No contact in 28 days. | 1/1 |
```

#### Deal Risk Radar

Show the top risk accounts first (Red, then Yellow). This is the "what needs my attention" view:

```
## Deal Risk Radar

🔴 Red — Needs Immediate Attention
| Account | Stage | Amount | Close | Why |
|---------|-------|--------|-------|-----|
| Globex  | Discovery | $100K | 3/30 | No contact in 28 days. Champion left. |

🟡 Yellow — Watch Closely
| Account | Stage | Amount | Close | Why |
|---------|-------|--------|-------|-----|
| Initech | Tech Eval | $75K | 4/15 | Close date pushed twice. Waiting on budget. |

🟢 Green — On Track
Acme Corp, NewCo, BigBank (all progressing normally)
```

If `salesforce_deal_health_field` is configured, note: "Deal health scores pushed to Salesforce (`{field_name}`)."

#### Accounts Auto-Summarized

List any accounts where `/sales-summarize-account` was automatically run because meetings had External Summary or Transcript content but no Summary:

```
Auto-summarized {N} accounts (meetings had transcripts/briefs but no summaries):
- Globex: 8 meetings summarized
- Initech: 1 meeting summarized
```

#### Accounts Needing Input

For each account with STATUS=needs_input, list meetings that have NO source material (no External Summary, no Transcript):

```
These accounts have meetings without any source material (no transcripts or briefs):

**Acme Corp:**
- 2026-03-04 Discovery.md
- 2026-03-06 Demo.md

Add transcripts/briefs to these meetings, then run:
1. `/sales-summarize-account {Account}` for each
2. `/sales-weekly` again to complete the review
```

#### Accounts with Newly Closed Opportunities

List any accounts where opportunities were found to be closed:

```
Opportunities closed since last check:
- Acme Corp: "Acme - NB - 2026" moved to Closed Won
- Globex: "Globex - Expansion" moved to CL - Closed Lost
```

#### Accounts Needing Setup

List accounts that have open opportunities but are not fully set up (missing `salesforce_account`):

```
These accounts have open Salesforce opportunities but haven't been fully set up in Obsidian:
- Acme Corp
- Initech
- ...

Would you like me to set up these accounts? I'll run `/sales-create-account` for each
and then `/sales-salesforce scan` to link them to Salesforce.
```

**IMPORTANT:** This is an interactive prompt — wait for the user's response before proceeding. If the user says yes, run `/sales-create-account {Account}` and `/sales-salesforce scan {Account}` for each. If no, skip.

#### Summary

```
Weekly Review Complete

Processed: {N} set-up accounts
Auto-summarized: {N} accounts
Needs input: {N} accounts ({total} meetings need transcripts/briefs)
Newly closed: {N} opportunities
SF updates pushed: {N} accounts
Not set up: {N} accounts with open opps (prompted above)
Bad opp URLs fixed: {N} accounts

Next steps:
1. Add transcripts/briefs to flagged meetings
2. Re-run /sales-weekly after completing the above
```

---

### Phase 4: Weekly Retro (Self-Improvement)

After all subagents complete and the report is assembled, perform a self-review.

#### 4a: Analyze Run Quality

Read `~/.claude/skills/sales-config.md` and update it with this week's observations:

**Model Performance:** For each subagent, log success/failure by model and task type in the `## Model Performance` table. Common failure modes to watch for:
- Subagent returned empty or malformed structured output
- Salesforce push failed (auth, field name, network)
- Contact enrichment returned "not found" for most contacts
- Auto-summarization produced low-quality summaries

**Recurring Issues:** Look across ALL account results for patterns:
- Which accounts consistently have unsummarized meetings? (user may not be adding transcripts)
- Which accounts have stale data? (no activity in 30+ days)
- Are any Salesforce pushes consistently failing? (field name issue, auth expiry)
- Did any subagents take unusually long or use excessive tokens?

Add new observations under `## Recurring Issues` with format:
```
- [{date}] {observation} — {accounts affected}
```

#### 4b: Surface Discoveries for Daily Review

Read `## Discovered Patterns > ### Pending Review` in the learnings file. If there are pending items that haven't been surfaced yet, add a task to tomorrow's daily note:

1. Determine tomorrow's date
2. Check if `{config.vault_path}/Daily/{tomorrow}.md` exists
3. If it exists, add under `## {config.company}` (or create the section if missing):
   ```
   - [ ] Review skill learnings — {N} new patterns discovered (run `/sales-review-learnings`)
   ```
4. If it doesn't exist, the next `/today` run will pick it up — add a flag in the learnings file: `pending_daily_surface: true`

#### 4c: Portfolio-Level Insights

After processing all accounts, look for cross-account patterns:

- **Common competitors:** Which competitors appear most frequently? Are any new ones emerging?
- **Common objections:** Are multiple accounts raising the same concerns?
- **Common tech stacks:** Are there patterns in what customers use?
- **Deal velocity:** Which accounts moved stages this week vs. stalled?

Log any notable cross-account insights under `## Discovered Patterns > ### Pending Review` with tag `[portfolio]`.

#### 4d: Retro Summary

Add to the final report:

```
## Self-Improvement Notes

- Subagent success rate: {N}/{total} ({percentage}%)
- Model escalations: {any haiku→sonnet escalations this run}
- New patterns discovered: {count} (queued for daily review)
- Recurring issues: {any new issues identified}
- Stale accounts (30+ days no activity): {list}
- Portfolio trends: {1-2 sentence summary of cross-account patterns}
```

---

### Status Entry Lifecycle

The `(status)` ledger entry has a specific lifecycle that other skills must respect:

1. **`/sales-weekly` creates/updates it** — one `(status)` entry per account, always at the top of the ledger
2. **`/sales-summarize-account` clears it** — when a real meeting-based ledger entry is added, remove the `(status)` entry (it's superseded by actual activity)
3. **`/sales-salesforce` (push mode) clears it** — same reason; a push means the account was actively updated
4. **`/sales-weekly` replaces it** — next weekly run replaces the old `(status)` entry with a fresh one

This means if there are 3 weeks with no activity, there's still only ONE `(status)` entry showing the most recent weekly review date and when the last real activity was.
