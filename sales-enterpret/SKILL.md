---
description: Import Gong call transcripts from Enterpret (via wisdom MCP) into Obsidian meeting notes. Faster than /sales-gong — no browser needed.
argument-hint: <account name> [date range]
---

# Import Gong Transcripts via Enterpret

Search and import Gong call transcripts from Enterpret's knowledge graph (via the wisdom MCP server) into Obsidian meeting notes. This is the preferred method — it's faster and doesn't require a browser. Falls back to `/sales-gong` when transcripts aren't found in Enterpret.

## Arguments

- `account`: The account name (e.g., "Acme Corp", "Globex")
- `date` (optional): Date or date range to search. Defaults to today.
  - Single date: `2026-04-15`
  - Date range: `2026-04-14 to 2026-04-15`
  - Relative: `today`, `yesterday`, `this week`, `last 7 days`

Examples:
- `/sales-enterpret Arlo` (today's calls)
- `/sales-enterpret Arlo yesterday` (yesterday's calls)
- `/sales-enterpret Arlo 2026-04-10 to 2026-04-15` (date range)
- `/sales-enterpret Arlo this week` (current week)

## Prerequisites

### Wisdom MCP Server

This skill requires the wisdom MCP server (Enterpret knowledge graph) to be connected. Run `/mcp` at the start of the session to authenticate. The wisdom server token expires between sessions, so this must be done every time.

**If the wisdom MCP tools are not available or return auth errors:**
1. Warn the user: "Wisdom MCP not connected — run `/mcp` to authenticate. Skipping Enterpret import."
2. Return immediately so the caller (e.g., `/sales-today`) can fall back to `/sales-gong`.

## Instructions

You are helping a Solutions Engineer import Gong call transcripts for the account: $ARGUMENTS

### CRITICAL: Autonomous Execution

This skill runs fully autonomously — **never ask for confirmation**. Import everything that matches, skip what doesn't, and report results at the end. This mirrors `/sales-gong` behavior:
- Never skip an import because the meeting file already has notes
- Never ask "should I proceed?" — just proceed
- If no transcripts found, warn and continue (do not block)
- If the wisdom MCP is not connected (auth issue), warn and return immediately (do not block)

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `name`, `initials`, `company`, `gong_workspace_id`. Use these values throughout.

### Pre-check: Verify Vault Path

Check that the accounts directory exists:
```bash
test -d "{config.vault_path}/{config.company_folder}/Accounts"
```
If not found, stop: "Obsidian vault not found. Run `/sales-setup` to configure."

### Pre-check: Verify Wisdom MCP

Before querying, confirm the wisdom MCP tools are available by calling `mcp__wisdom__get_organization_details`. If this fails with an auth error, warn: "Wisdom MCP not connected — run `/mcp` to authenticate. Skipping Enterpret import." Then return immediately (do not block the workflow).

### Step 1: Parse Arguments

1. Extract the account name from arguments
2. Verify the account directory exists at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/`
3. Parse the date/range argument:
   - `today` or no date → today's date
   - `yesterday` → yesterday's date
   - `this week` → Monday through today
   - `last N days` → N days back through today
   - `YYYY-MM-DD` → single date
   - `YYYY-MM-DD to YYYY-MM-DD` → explicit range
4. Convert to ISO 8601 timestamps for Cypher queries (start of first day `T00:00:00Z` through end of last day `T23:59:59Z`)

### Step 2: Search Enterpret for Gong Transcripts

Query the Enterpret knowledge graph for Gong-sourced NaturalLanguageInteraction records that match the account and date range.

**Strategy:** Enterpret stores Gong transcripts as flat text in `NaturalLanguageInteraction` nodes. There's no structured account field linking NLIs to specific accounts. Instead, search by:
1. Source = 'Gong'
2. Date within range
3. Content contains the account name (or key people/terms associated with the account)

**Step 2a: Get account context**

Read the account file at `{Account}.md` to extract:
- Key contact names (from `attendees` in recent meeting files)
- Account aliases or alternate names
- Any distinguishing terms that would appear in call transcripts

**Step 2b: Query for candidate transcripts**

```cypher
MATCH (n:NaturalLanguageInteraction)
WHERE n.source = 'Gong'
  AND n.record_timestamp >= '{start_iso}'
  AND n.record_timestamp <= '{end_iso}'
RETURN n.record_id, n.record_timestamp
ORDER BY n.record_timestamp DESC
LIMIT 50
```

Then for each candidate, fetch content and check if it matches the account:

```cypher
MATCH (n:NaturalLanguageInteraction)
WHERE n.record_id = '{record_id}'
RETURN n.content, n.record_timestamp
```

**Step 2c: Match transcripts to account**

For each transcript, check if the content mentions:
- The account name (or common variations)
- Known contact names from the account
- Distinctive product names, project names, or deal terms specific to this account

Score each transcript by relevance. A transcript matches if it contains the account name OR 2+ known contact names from the account.

**Important:** Gong transcripts in Enterpret use `agent:` for the seller side and `user:` for the customer side. The speaker labels are not actual names — you'll need to infer who is speaking from context and known contacts.

### Step 3: Present Matches

Show the user what was found:

```
Enterpret search for {Account} ({date range}):

Found {N} Gong transcripts:

| # | Date/Time | Duration (est.) | Match Confidence | Preview |
|---|-----------|-----------------|------------------|---------|
| 1 | 2026-04-15 10:03 | ~45m | High (account name + 3 contacts) | Contract review with Charlotte... |
| 2 | 2026-04-14 14:00 | ~30m | Medium (2 contacts matched) | SDK setup discussion... |

{If 0 found: "No matching transcripts found in Enterpret for this date range."}
```

**If no transcripts found:**
- Warn the user but do NOT block: "No Gong transcripts found in Enterpret for {Account} in {date range}. Possible reasons: no recording, not yet ingested (Enterpret can lag hours/days), or account name not in transcript."
- **Skip and continue** — do not ask the user what to do. This mirrors `/sales-gong` behavior where calls without recordings are skipped with a warning.
- Include the skip in the final report under a "Skipped" or "Warnings" section.

### Step 4: Match to Meeting Files

For each matched transcript:

1. Parse the date from `record_timestamp`
2. List existing meeting files for that date: `{Account}/meetings/YYYY-MM-DD*.md`
3. If a meeting file exists for that date:
   - **Never skip because the meeting already has notes.** User-pasted notes, Granola summaries, and manually typed content do NOT replace Enterpret/Gong data. Always append using the Append Rules.
   - If it already has Enterpret or Gong transcript content (check for `enterpret:` or `gong.io` in `gong_url` frontmatter), skip to avoid duplicates.
4. If no meeting file exists for that date:
   - Infer a topic from the transcript content (first few exchanges, key themes)
   - Create one with `/sales-meeting {Account} {Topic} {YYYY-MM-DD}`

### Step 5: Write Transcripts to Meeting Files

For each matched transcript and its target meeting file:

**5a: Parse the transcript**

The raw Enterpret transcript is formatted as:
```
agent: text here
agent: more text
user: response text
```

Convert to a more readable format:
```
**Agent:** text here. more text
**Customer:** response text
```

Group consecutive lines from the same speaker into paragraphs. Where possible, replace `agent`/`user` with actual names inferred from context and known contacts.

**5b: Generate a brief summary**

From the transcript content, generate:
- **Recap**: 2-3 sentence overview of the call
- **Key Points**: 3-5 bullet points
- **Next Steps**: Action items mentioned in the call

**5c: Update the meeting file**

Follow the same Append Rules as `/sales-gong`:

1. Update frontmatter:
   - Set `gong_url` to `enterpret:{record_id}` (to track the source)
   - Set `attendees` as `"[[Name]]"` links (inferred from transcript + known contacts)

2. Write to `## External Summary`:
   - If section is empty: write the brief directly
   - If section has content: add under `### Enterpret Brief` subheading

3. Write to `## Transcript`:
   - If section is empty: write the formatted transcript directly
   - If section has content: add under `### Enterpret Transcript` subheading

**5d: Formatting**

The External Summary should follow this structure:
```markdown
**Recap**
{2-3 sentence overview}

**Key points**
1. {point 1}
2. {point 2}
3. {point 3}

**Next steps**
- {action 1}
- {action 2}
```

### Step 6: Report Results

```
Enterpret Import for {Account} ({date range})

Imported: {N} transcripts
Skipped: {M} (already had content / no match)

{If N > 0:}
Files updated:
- meetings/2026-04-15 BVA.md (summary + transcript)
- meetings/2026-04-14 Internal War Room.md (summary + transcript)

{If any transcripts couldn't be matched to meetings:}
Unmatched transcripts (couldn't determine account match):
- {record_id} at {timestamp} — preview: "{first 100 chars}"

{If N > 0:}
Next steps:
- Run `/sales-summarize-account {Account}` to process the new transcripts

## Warnings
{If no transcripts found:}
- No Gong transcripts found in Enterpret for {Account}. Possible reasons: no recording exists, not yet ingested, or account name not in transcript content.
{If specific dates had meetings but no transcripts:}
- {YYYY-MM-DD} {Topic}: No matching transcript found
```

### Error Handling

- **Wisdom MCP not connected:** Warn: "Wisdom MCP not connected — run `/mcp` to authenticate. Skipping Enterpret import." Return immediately so caller can fall back to `/sales-gong`.
- **Wisdom MCP auth expired mid-query:** Warn: "Wisdom MCP token expired — run `/mcp` to re-authenticate. Skipping Enterpret import." Return with partial results (anything already extracted) and let caller fall back.
- **No results for account:** Warn and skip, just like `/sales-gong` skips calls without recordings. Include in final report warnings. Do NOT block or ask the user what to do.
- **Ambiguous matches:** When a transcript could belong to multiple accounts, use the best match based on contact name overlap. Do NOT ask for confirmation — process autonomously like `/sales-gong`.
- **Large result sets:** If >20 transcripts match the date range, process in batches of 5 and use subagents for file writes.

### Notes

- Enterpret ingests Gong transcripts with some delay (hours to days). For same-day calls, the transcript may not be available yet.
- The `NaturalLanguageInteraction` node in Enterpret contains the full transcript as a flat text blob — no structured metadata like call title, duration, or participant list.
- Speaker labels are generic (`agent:`/`user:`) — names must be inferred from context and known contacts.
- This skill does NOT require Playwright CLI or a browser session, making it much faster than `/sales-gong`.
- The `enterpret:{record_id}` value in `gong_url` distinguishes Enterpret-sourced transcripts from direct Gong imports. This prevents `/sales-gong` scan mode from re-importing the same call.
- Enterpret may have transcripts that Gong's activity page doesn't surface easily (e.g., calls from other team members' Gong accounts).
