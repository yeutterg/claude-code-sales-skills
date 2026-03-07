---
description: Summarize all meeting notes, update MEDDPICC/TECHMAPS/CoM, enrich contacts, refresh business context
argument-hint: <account name>
---

# Summarize Account

Summarize all meeting notes for an account and update the account page.

## Arguments

- `account`: The account name (e.g., "Acme Corp", "Globex")

## Instructions

You are helping a Solutions Engineer maintain their sales notes for the account: $ARGUMENTS

### Pre-check: Verify Vault Path

Check that the Obsidian vault directory exists:
```bash
test -d "{config.vault_path}/{config.company_folder}/Accounts"
```
If the directory does not exist, stop and tell the user: "Obsidian vault not found at the configured path. Run `/sales-setup` to configure your vault path."

### Pre-check: Read Config

Read the config file at `~/.claude/skills/sales-config.md` and extract:
- `vault_path`, `company_folder`, `name`, `initials`, `company`, `products`, `competitors`

These values are used throughout this skill as `{config.*}` references.

**Product Naming:**
Read the `products` array from `~/.claude/skills/sales-config.md`. Each product has a `name`, `description`, and optional `aliases`. Always use the canonical product name. If a product has aliases, those are acceptable alternatives but the canonical name is preferred.

**Competitor Spellings:**
Read the `competitors` array from `~/.claude/skills/sales-config.md`. Each competitor has a `name`, `description`, and optional `misspellings`. Transcription tools frequently misspell competitor names — always use the canonical spelling from config.

**Auto-grow competitors:** If a meeting transcript mentions a competitor not yet in the config, add it to `~/.claude/skills/sales-config.md` with the name, a brief description (inferred from context), and any observed misspellings.

---

### Phase 1: Discovery

1. Find the account directory at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/`
2. Read the main account file `{Account}.md`
3. **Migrate legacy frontmatter:** If the account file has a `salesforce_url` field, rename it to `salesforce_opportunity` (update the key name in the frontmatter, preserving the value). This is a one-time migration from the old field name.
4. Read `Ledger.md` to see which meetings already have ledger entries
5. List all meeting files in the `meetings/` subdirectory (files are `.md`)
6. List all contact files in the `contacts/` subdirectory — save the list of contact names (filenames without `.md`) for use in Phase 2 subagent prompts

---

### Phase 2: Process Each Meeting Note via Subagents

**Pre-check: Adaptive model selection.** Read `~/.claude/skills/sales-config.md` and check the `## Model Performance` table. If "meeting-summary" has >30% failure rate on the current model, escalate to the next tier (haiku→sonnet). Default is sonnet for meeting subagents and haiku for contact enrichment subagents.

**Pre-check: Skip already-summarized meetings.** Before launching subagents, read the first ~30 lines of each meeting file to check if the `## Summary` section has content (not just the heading). Only launch subagents for meetings where the Summary section is empty or missing — these are the meetings that haven't been processed yet. Previously summarized meetings already had their data incorporated into the account file during prior runs, so re-processing them is wasteful.

For each **unsummarized** meeting file, launch a subagent using the Task tool (`subagent_type: "general-purpose"`). Run all meeting subagents **in parallel** (send all Task tool calls in a single message).

If ALL meetings are already summarized, skip directly to Phase 3 — you can still update the account file based on any new information from the Ledger or other sources.

For each meeting subagent, use this prompt template (fill in the variables):

```
You are processing a single {config.company} meeting note for the account "{Account}".

Read the meeting file at: {full path to meeting file}

**Known contacts and team members for name resolution:**
- Account contacts: {comma-separated list of contact file names from contacts/ folder, e.g., "Jane Doe, Bob Chen, Sarah Miller"}
- {config.company} team: SE: {se from account frontmatter}, AE: {ae from account frontmatter}, CSM: {csm from account frontmatter}

Then perform these tasks:

**1. Summarize (if needed)**
If the `## Summary` section is empty, write a 2-4 sentence summary based on the Notes, External Summary, and Transcript sections covering:
- What was discussed
- Key learnings or discoveries
- Any decisions made or next steps mentioned
Update the meeting file's `## Summary` section with this content.

**2. DO NOT TOUCH THE TASKS SECTION**
Do NOT create, modify, populate, or add anything to the `## Tasks` section. The user manages tasks manually. This means:
- Do NOT extract action items, next steps, or follow-ups into tasks
- If `## Tasks` has an empty `- [ ]` placeholder, leave it exactly as-is
- If `## Tasks` already has content, do not add, remove, or change anything
- Never write to this section under any circumstances

**3. Ensure Frontmatter is Complete**
The frontmatter should have:
- account: "[[{Account}]]"
- date: YYYY-MM-DD
- meeting_type: (if missing, infer from content/filename. **MUST be Title Case.** Values: Discovery, Demo, Technical Deep-Dive, POV Kickoff, POV Check-in, Implementation, Troubleshooting, Renewal, Expansion, CSM Check-in, Internal Sync, Procurement, Pricing, Partnership, Outreach)
- gong_url:
- attendees: array of "[[Person Name]]" links

**CRITICAL: Every name in the attendees array MUST use wiki-link format: `"[[Person Name]]"`.** If any existing attendees are listed as plain text (e.g., `"Person Name"`, `Person Name`, or `[Person Name]`), convert them to `"[[Person Name]]"`. This is required for Obsidian's dataview queries to work.

Populate the attendees array with links for every person who actually PARTICIPATED in the call — both customer/account contacts AND {config.company} team members (AEs, SEs, CSMs, leadership, etc.). Use the transcript's participant/speaker list and the Notes section's people list as the source of truth for who was on the call. Do NOT add people who are merely mentioned or discussed during the call but were not actually present as participants. Update the meeting file if changes were made.

**CRITICAL: Resolve first-name-only or ambiguous attendees to full names.** Transcripts and notes often refer to people by first name only (e.g., "Greg", "Cooper", "Dylan"). You MUST resolve these to full names before writing the attendees array:
1. Check existing contact files in the account's `contacts/` folder for matches
2. Check the account file frontmatter (`ae`, `se`, `csm` fields) for {config.company} team members
3. Check attendees from other meeting files in the same account for name patterns
4. Use context from the transcript itself (e.g., "Kathy Tang" mentioned later resolves "Kathy")
5. If a name cannot be resolved to a full name with reasonable confidence, keep it as-is but flag it in the extraction output

**CRITICAL: Prefer existing name spellings over transcript spellings.** Transcription tools frequently misspell names (e.g., "Kathy" vs "Cathy", "Shawn" vs "Sean"). When a name from the transcript is phonetically similar to an existing contact or known team member, ALWAYS use the spelling from the existing contact file or frontmatter. The contact files and frontmatter are the source of truth for how names are spelled — transcripts are not.

**4. Suggest Better Title (if needed)**
If the meeting filename has a generic topic like "Call", "Check-in", or "Meeting", suggest a more descriptive title based on the actual content discussed. The title should be 1-3 words in Title Case that capture the primary topic (e.g., "Pricing Discussion", "Experimentation Demo", "Renewal Negotiation", "POV Kickoff"). If the existing title is already descriptive, return "unchanged".

**5. Extract and Return Structured Data**
After processing, return EXACTLY this structured output (fill in all fields):

---BEGIN EXTRACTION---
MEETING_FILE: {filename}
DATE: {YYYY-MM-DD}
MEETING_TYPE: {type}
SUGGESTED_TITLE: {better topic name in Title Case, or "unchanged" if already descriptive}
ATTENDEES: {comma-separated list of names}
SUMMARY: {2-4 sentence summary}
LEDGER_ENTRY: {Format: "M/D {config.initials}: {concise ~15-25 word summary}. Next call: M/D {type}" or "Next call: TBD". Use M/D/YY if different year.}
NEXT_CALL: {date and type if mentioned, or "none"}
METRICS: {any business metrics, KPIs, success criteria mentioned}
ECONOMIC_BUYER: {budget holder info if mentioned}
DECISION_CRITERIA: {technical requirements, must-haves mentioned}
DECISION_PROCESS: {how they make decisions, approval chain}
PAPER_PROCESS: {procurement, legal, security review info}
IDENTIFIED_PAIN: {problems, pain points, challenges}
CHAMPION: {internal advocate info}
COMPETITION: {other solutions mentioned}
REQUIRED_CAPABILITIES: {what solution must do}
BUSINESS_VALUE: {ROI, cost savings, revenue impact}
POSITIVE_OUTCOMES: {what improves with {config.company}'s solution}
NEGATIVE_CONSEQUENCES: {risk of status quo}
BEFORE_AFTER: {current pain vs future state}
TECH_REQUIREMENTS: {technical needs, performance requirements}
ENVIRONMENT: {tech stack, systems, integrations}
TECH_COMPETITORS: {competitors' capabilities and gaps}
HERO: {technical champion name and influence}
TECH_METRICS: {how they measure technical success}
ALIGNMENT: {connection to business value}
TECH_VALIDATION_PLAN: {POV, workshop, demo plans}
SUPPORT: {post-sale needs}
TECH_STACK: {languages, frameworks, cloud, infra, AI/ML, data, observability, CI/CD, feature flags, other tools}
ARCHITECTURE_NOTES: {client apps, platforms, infrastructure, data flows}
NEW_COMPETITORS: {any competitors or alternative solutions mentioned that are NOT in the known competitors list, with context — or "none"}
NEW_OBJECTIONS: {recurring objections, blockers, or concerns raised by the customer — or "none"}
FEATURE_REQUESTS: {product gaps or feature requests mentioned by the customer — or "none"}
---END EXTRACTION---

For any field where no relevant information was found, write "none".

REMINDER: Do NOT write anything to the `## Tasks` section. Leave it untouched.
```

**IMPORTANT:**
- Launch ALL meeting subagents in a SINGLE message (parallel execution)
- Use `model: "sonnet"` for each subagent to optimize cost/speed
- Each subagent handles its own file reads and writes independently
- The structured extraction format lets you collect results without re-reading transcripts

---

### Phase 3: Collect Results and Update Account

After all meeting subagents complete, collect their structured extractions and proceed with the following steps. You now have all meeting data in compact form without needing to read any transcripts.

#### Step 3a: Rename Generic Meeting Files

Check each subagent's SUGGESTED_TITLE field. If a meeting has a suggested title (not "unchanged"), rename the file:

1. **Rename the file** from `YYYY-MM-DD {Old Topic}.md` to `YYYY-MM-DD {Suggested Title}.md` using `mv`
2. **Update daily notes** that reference the old filename:
   - Search daily notes around the meeting date: `grep -rl "YYYY-MM-DD {Old Topic}" "{config.vault_path}/Daily/"`
   - Replace ALL occurrences of the old link text with the new one (both the path and display text)
   - Example: `[[{config.company_folder}/Accounts/Acme Corp/meetings/2026-03-04 Call|2026-03-04 Call]]` → `[[{config.company_folder}/Accounts/Acme Corp/meetings/2026-03-04 Pricing Discussion|2026-03-04 Pricing Discussion]]`
3. **Update any other references** in the account's Ledger or account file that link to the old filename

Only rename files where the current topic is generic (e.g., "Call", "Check-in", "Meeting", "Sync"). Do NOT rename files that already have descriptive topics.

#### Step 3b: Update Next Call Information

From the subagent results, find the **most recent** meeting (by date) that mentions a next call.

**ALWAYS update the frontmatter in the main account file:**
- `next_call:` with format `YYYY-MM-DD - {type of call}` OR `TBD - {reason/pending action}` if not yet scheduled
- `next_call_agenda:` as a YAML list of bullet points (leave empty if TBD)

#### Step 3c: Update Ledger

The Ledger file should ONLY contain meeting entries — no analysis, pain points, outage examples, or other prose. That content belongs in the MEDDPICC sections of the account file.

For each meeting, ensure there is a corresponding entry in `Ledger.md` using the LEDGER_ENTRY from each subagent.

Format: `- M/D {config.initials}: {concise summary}. Next call: M/D {type}`

**Keep entries concise — aim for one line (~15-25 words before "Next call").** Focus on what happened and what was decided, not details. Omit attendee names, product descriptions, and technical details that are captured elsewhere (MEDDPICC, account file).

**Date format:** M/D (no leading zeros, no year) for the current year. Use M/D/YY for meetings from a different year (e.g., 11/3/25).

**CRITICAL: Every ledger entry MUST end with "Next call: M/D {type}" or "Next call: TBD" if not scheduled.**

Good: `- 3/3 {config.initials}: Internal checkpoint. Contact no-showed. Vendor onboarding form in progress. Next call: TBD`
Bad: `- 3/3 {config.initials}: Internal checkpoint call with Alex Rivera (AE) and Pat Lee (CSM). Dana Wells no-showed the call (didn't accept or decline invite). Vendor onboarding form in progress — needs finance and supplier diversification sections. PDF-to-Google-Sheet conversion distorted the form. Pat pinged both contacts in Slack. SE working on security questionnaire separately. Next call: TBD`

Most recent entries at the top. If the Ledger contains non-meeting content, move it to the appropriate MEDDPICC section.

**Clear `(status)` entries:** If the ledger contains a line with `(status)` (added by `/sales-weekly`), remove it — real meeting-based entries supersede weekly status updates.

#### Step 3d: Update Business Context

Check if the `## Business Context` section exists and is populated:

**If the section doesn't exist or is empty:**
1. Add the section below `## Meetings` and above `## MEDDPICC`
2. Use web search to populate:
   - **About the Company**: Search for "{Account} company" - add 1-2 bullets on their line of business
   - **Recent News**: Search for "{Account} news {current year}" - add relevant headlines:
     - Leadership changes, acquisitions, layoffs, data breaches, funding, partnerships, financial results

**If the section exists and has content:**
1. If the newest headline is more than 2 weeks old, search for "{Account} news" for updates
2. Add any new headlines at the top of the Recent News list

Format for news items: `- **M/DD/YYYY**: [Headline summary](URL)`

**CRITICAL: Only include news items where you have a direct URL to the actual article.**
- Link to specific articles (BusinessWire, PRNewswire, TechCrunch, news outlets)
- Do NOT link to company profile pages (Tracxn, Crunchbase, ZoomInfo)
- Do NOT link to generic newsroom landing pages
- No source = don't include it

#### Step 3e: Update MEDDPICC, Command of the Message, TECHMAPS, and Tech Stack

Aggregate the extracted data from ALL meeting subagents to update the main account page.

**IMPORTANT: Section Formatting Rules**

All major sections must use this format:
1. A SINGLE `> [!summary] Summary` callout (NOT collapsed with `-`) containing ALL fields as one-line bullet points
2. Followed by detailed `### Field` subsections with expanded information

**DO NOT use individual collapsed callouts like `> [!summary]- Metrics`** — this is incorrect formatting.

Example correct format for MEDDPICC:

```markdown
## MEDDPICC

> [!summary] Summary
> - **Metrics:** 500+ flags, 2M MAU, targeting 10M experiment keys
> - **Economic Buyer:** John Smith (VP Eng), prefers usage-based pricing
> - **Decision Criteria:** Mobile-first, Datadog integration required
> - **Decision Process:** Technical POV → business case → procurement
> - **Paper Process:** 60-day procurement cycle, security review required
> - **Identified Pain:** Slow releases, no targeting, manual rollbacks
> - **Champion:** Jane Doe (Sr Eng Manager) - runs experimentation program
> - **Competition:** Firebase (legacy), Split.io (evaluated)

### Metrics
- 500+ feature flags in production
- 2M monthly active users
- etc.

### Economic Buyer
- **John Smith** - VP Engineering, budget holder
- etc.
```

**MEDDPICC sections** - Fill in from extracted METRICS, ECONOMIC_BUYER, DECISION_CRITERIA, DECISION_PROCESS, PAPER_PROCESS, IDENTIFIED_PAIN, CHAMPION, COMPETITION fields.

**Command of the Message sections** - Fill in from extracted REQUIRED_CAPABILITIES, BUSINESS_VALUE, POSITIVE_OUTCOMES, NEGATIVE_CONSEQUENCES, BEFORE_AFTER fields:
- Required Capabilities, Business Value, Positive Business Outcomes, Negative Consequences, Before/After Scenarios

**TECHMAPS sections** - Fill in from extracted TECH_REQUIREMENTS, ENVIRONMENT, TECH_COMPETITORS, HERO, TECH_METRICS, ALIGNMENT, TECH_VALIDATION_PLAN, SUPPORT fields:
- Technical Requirements & Scalability, Environment, Competitors, Hero, Metrics, Alignment, Plan for Tech Validation, Support

**Tech Stack section** - Aggregate from extracted TECH_STACK fields. Use categories:
- Languages, Frameworks, Cloud, Infrastructure, AI/ML, Data, Observability, CI/CD, Feature Flags, Other Tools
- Only include categories with relevant information

**Section Order Reminder:** The account file sections should be in this order:
1. Deal Ledger
2. Open Tasks
3. Stakeholders
4. Meetings
5. Business Context
6. MEDDPICC
7. Command of the Message
8. TECHMAPS
9. Tech Stack
10. Architecture Diagram
11. Salesforce Updates

#### Step 3f: Create/Update Architecture Diagram

Using aggregated ARCHITECTURE_NOTES and ENVIRONMENT data, create or update an ASCII architecture diagram showing:
- Client applications and platforms
- Infrastructure (cloud providers, services)
- Data flows and integrations
- Current pain points (mark with "PAIN:")
- Target areas for {config.company} (mark with "TARGET:")
- Key stakeholders

Use the format:
```
+---------------------------------------------------------------------------+
|                      {ACCOUNT} ARCHITECTURE                                |
+---------------------------------------------------------------------------+
...
```

#### Step 3g: Create/Update Salesforce Updates Section

At the bottom of the account file, create or update a `## Salesforce Updates` section.

**IMPORTANT FORMAT RULES:**
- Only the LATEST meeting entry appears at the top (above MEDDPICC)
- MEDDPICC must be structured with `- Field: value` on separate lines
- TECHMAPS must be structured with `- Field: value` on separate lines
- TECH STACK is one comma-separated line
- DEAL HISTORY at the bottom contains all OLDER meeting entries (not the latest)
- All entries must be from {config.name}'s ({config.initials}) perspective
- **DATE FORMAT: Use M/D format (no leading zeros, no year) for the current year. Use M/D/YY for meetings from a different year (e.g., 11/3/25).** Same as Ledger format.
- **CONCISENESS: Keep deal history entries short (~15-25 words each).** Same conciseness rules as ledger entries. Focus on what happened, not details.

```markdown
## Salesforce Updates

\`\`\`
- M/D {config.initials}: [Most recent meeting update only]

MEDDPICC:
- Metrics: [value]
- Economic Buyer: [value]
- Decision Criteria: [value]
- Decision Process: [value]
- Paper Process: [value]
- Identified Pain: [value]
- Champion: [value]
- Competition: [value]

TECHMAPS:
- Technical Requirements: [value]
- Environment: [value]
- Competitors: [value]
- Hero: [value]
- Metrics: [value]
- Alignment: [value]
- Plan: [value]
- Support: [value]

TECH STACK:
[One-line comma-separated list]

DEAL HISTORY:
- [All older ledger entries, newest first]
\`\`\`
```

---

### Phase 4: Contact Reconciliation and Enrichment via Subagents

#### Step 4a: Reconcile Attendees

1. **Collect ALL attendees** from the subagent extraction results (ATTENDEES fields)
2. **List existing contacts** in the `contacts/` folder
3. **Identify missing contacts** — attendees without a matching contact file

For each **missing** contact, create a new file at `contacts/{Person Name}.md`:

```markdown
---
name: {Person Name}
company: {company — see below}
role: {Role if known from meeting extractions}
influence:
email:
linkedin:
notes:
---

# {Person Name}

## Meeting History

```dataview
LIST
FROM "{config.company_folder}/Accounts/{Account}/meetings"
WHERE contains(attendees, this.file.link)
SORT date DESC
```
```

**Company field rules:**
- Default to `{Account}` for most attendees (they work at the account company)
- Set to '{config.company}' for {config.company} team members (SE, AE, CSM, etc.)
- For third parties (lawyers, consultants, implementation partners, integration vendors), infer the company from context — e.g., if someone is introduced as "from Deloitte" or their email domain differs, use that company name
- If the company can't be determined for a non-obvious attendee, leave it as `{Account}` (safe default)

**Also update existing contacts:** After creating missing contacts, scan ALL existing contact files in the `contacts/` folder. If any contact has an empty `company:` field, fill it in using the same rules above. Check meeting transcripts and notes for context clues about each person's company affiliation.

#### Step 4b: Enrich Contacts via Subagents

After reconciliation, list ALL contact files again. For each contact that has an empty `role:` or `linkedin:` field, launch a subagent (`subagent_type: "general-purpose"`, `model: "haiku"`) to search for and enrich that contact.

Run all contact enrichment subagents **in parallel**. Use this prompt template:

```
You are enriching a contact profile for a {config.company} sales account.

Contact: {Person Name}
Company: {Account}
Current role (if any): {existing role value}
Current LinkedIn (if any): {existing linkedin value}

Tasks:
1. If role is empty: Search the web for "{Person Name} {Account} LinkedIn" to find their job title. If not found, return "not found".
2. If linkedin is empty: Search for their LinkedIn profile URL. Format: https://www.linkedin.com/in/{slug}/
3. Do NOT overwrite existing values — only fill in empty fields.

Return EXACTLY this format:
---BEGIN CONTACT---
NAME: {Person Name}
ROLE: {job title or "unchanged" if already set or "not found"}
LINKEDIN: {URL or "unchanged" if already set or "not found"}
---END CONTACT---
```

After all contact subagents return, update the contact files with any enrichment data found.

#### Step 4c: Output Contact Table

Output a reconciliation table:

| Attendee | Contact File Exists? | Action Taken |
|----------|---------------------|--------------|
| Person A | Yes | - |
| Person B | No | Created |

And a full contact roster:

| Name | Role | LinkedIn | Status |
|------|------|----------|--------|
| Person A | VP Eng | linkedin.com/in/... | already complete |
| Person B | Sr Dev | linkedin.com/in/... | enriched |
| Person C | | | not found |

---

### Phase 5: Update Daily Note

After completing all account updates:

1. **Find today's daily note** at `{config.vault_path}/Daily/YYYY-MM-DD.md` (use today's date)

2. **Search for the account summarization checkbox** across all meeting subsections (Today, Upcoming, Past) - look for a line like:
   ```
   - [ ] Run `/sales-summarize-account {Account}`
   ```

   The daily note now organizes meetings into subsections:
   ```
   ## Meetings
   ### Today
   - [meetings for today's date]
   ### Upcoming
   - [meetings after today]
   ### Past
   - [meetings before today]
   ```

3. **Mark it complete** by changing `- [ ]` to `- [x]` and adding a completion timestamp:
   ```
   - [x] Run `/sales-summarize-account {Account}`  [completion:: YYYY-MM-DD]
   ```

---

### Formatting

- No blank line between heading and first bullet
- No blank line between last bullet and next heading
- Sections flow directly into each other

### Phase 6: Self-Improvement

After completing all account updates, perform these learning steps:

#### 6a: Log Run Diagnostics

Read `~/.claude/skills/sales-config.md`. Append observations to the appropriate sections:

**Model Performance:** For each subagent that ran, log whether it succeeded or failed and what model was used. Update the `## Model Performance` table — increment success/failure counts for the task type + model combination. If a haiku subagent failed (produced garbled output, missed critical fields, or had to be retried), note the failure reason. If a task type has >30% failure rate on haiku, add a note under `## Recurring Issues` recommending sonnet for that task.

**Discovered Patterns:** Check the meeting extractions for:
- **New competitors** not in `~/.claude/skills/sales-config.md` — if found, add them to the config (existing behavior) AND log under `## Discovered Patterns > ### Pending Review` with format: `- [competitor] {Name}: {context from meeting} ({Account}, {date})`
- **New objections or blockers** that appear across multiple accounts — log as: `- [objection] {pattern}: {details} ({Account}, {date})`
- **Technical patterns** (common tech stacks, integration requests, architecture patterns) — log as: `- [tech] {pattern}: {details} ({Account}, {date})`
- **Product gaps or feature requests** mentioned by customers — log as: `- [feature] {request}: {context} ({Account}, {date})`

These pending items will be surfaced in the daily note for review.

#### 6b: Detect Template Drift

After writing the account file, compare what you wrote against what was there before (if this is a re-run, not a first run):

1. Read the account file one more time
2. Check if the user has manually edited any sections since the LAST run by looking for content that doesn't match the expected template patterns:
   - MEDDPICC fields reworded or restructured
   - Salesforce Updates reformatted
   - Sections reordered
   - Summary style changed (e.g., user consistently writes shorter/longer summaries)

3. If edits are detected, log under `## Template Feedback`:
   - Which section was edited
   - What kind of change (rewording, restructuring, removing content, adding content)
   - The account name

This helps identify when the skill's output style doesn't match user preferences.

#### 6c: Adaptive Model Selection

Before launching subagents at the START of Phase 2, read `~/.claude/skills/sales-config.md` and check the `## Model Performance` table:

- If "meeting-summary" task type has >30% failure rate on haiku → use sonnet instead
- If "contact-enrichment" task type has >50% failure rate on haiku → use sonnet instead
- Log which model was selected and why in the run output

---

### Output

After completing all phases, provide a summary of:
1. Which meeting files were updated with summaries (and any that were renamed)
2. What was added to the ledger
3. Business Context updates (company info, new headlines)
4. What MEDDPICC fields were populated
5. What TECHMAPS fields were populated
6. What Command of the Message fields were populated
7. Architecture diagram created/updated
8. Salesforce Updates section created/updated
9. Any new contact files created
10. **Full contact roster table** showing ALL contacts with: Name | Role | LinkedIn | Status
11. Next call information (if any)
12. **Daily note checkbox marked complete**
13. **Learnings logged** — new patterns discovered, model performance, template drift detected
