---
description: Post deal prep or recap messages to deal-specific Slack channels. Posts to the channel listed in the account's `slack_channel` frontmatter, attaches the latest account PDF to recaps, and skips silently when no channel is configured.
argument-hint: <account> <prep|recap>
---

# Post Deal Update to Slack

Post prep or recap messages to deal-specific Slack channels. Designed to be called automatically by `/sales-today` after generating deal prep and recap content.

## Arguments

- `account` (required): The account name
- `mode` (required): `prep` or `recap`
- `content` (optional): Pre-generated content to post. If not provided, reads from the account file and meeting notes.

## Instructions

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `name`, `initials`

### Pre-check: Get Slack Channel

Read the account file at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/{Account}.md` and extract the `slack_channel` field from frontmatter.

If `slack_channel` is empty or missing, skip silently and return `{"skipped": true, "reason": "no slack_channel"}`. Do not ask the user.

### Step 1: Build the Message

#### Prep Messages

Format:
```
@{stakeholder1} @{stakeholder2} Prep for {Account} {Meeting Topic}

- Agenda: {1-2 line summary of what the call is about}
- Discover: {2-3 bullets of what we want to learn}
- Questions:
  - {Discovery question 1}
  - {Discovery question 2}
  - {Discovery question 3}
```

Source the content from:
1. The meeting file's `## Prep` section (objective, attendees, context)
2. The meeting file's `## Agenda` section
3. The account file's MEDDPICC gaps relevant to the attendees
4. The meeting file's `### Questions to Ask` section

Rules:
- **Stakeholders** = the AE (always) + any other internal team members on the call. Use their Slack handles if known (check contact files for `slack` field), otherwise use their full name
- Keep bullets extremely short (5-10 words each)
- Questions should be open-ended discovery questions, not yes/no
- Max 3-4 discovery questions
- No markdown formatting (Slack doesn't render it well in bot messages). Use plain dashes for bullets
- No em dashes

#### Recap Messages

Format (Slack-native — header is one line, Gong as Markdown link at top, three top-level sections in fixed order: Business updates → Feature requests → Next):

```
Recap: {Account} | {Meeting Topic} ({Day}, {Mon} {Date})
[Gong]({gong_url})

- Business updates
   - {bullet 1: what changed in the deal}
   - {bullet 2: new stakeholder, risk, decision}
   - {bullet 3: outcome or learning}
- Feature requests
   - {Request 1, ≤12 words}
   - {Request 2}
- *CEP recommendation: Stage X {name}* (include only if changed or differs from current SF stage)
- Next: {specific next step with date if known}
```

**Top-level structure is fixed:**
1. `Business updates` — always present; sub-bullets carry the substance
2. `Feature requests` — only when feature asks surfaced; omit the whole parent bullet otherwise (don't write "none")
3. `*CEP recommendation: Stage X*` — only when stage changed or differs from SF; otherwise skip
4. `Next:` — single line, always present

Don't introduce other top-level categories (no "MEDDPICC update," no "CoM update"). Those updates already land in the account file's MEDDPICC / TECHMAPS / CoM blocks via `/sales-summarize-account`; duplicating them in Slack is noise.

**Terminology:** use **PoV Plan** (capital-P, lowercase-o, capital-V) for the deal-stage artifact — never "eval success criteria," "POV scope doc," "evaluation plan," or other variants. The PoV Plan is the canonical name across the team.

**Stakeholder mention line:** prepend `@{stakeholder1} @{stakeholder2}` ABOVE the recap header when posting via the Slack API. Omit the @ line in copy/paste-ready blocks since Slack's user-mention syntax (`<@U123>`) only works through the API — let the user @ them by hand if pasting.

Source the content from:
1. The meeting file's `## Summary` section
2. The meeting file's `## External Summary` and `## Notes` sections
3. The account's latest ledger entry
4. The account file's `gong_url` frontmatter (for the `Gong:` line at top)
5. Feature requests captured in either the meeting file's `## Notes` or the account-level feature-requests log (when present). If no feature requests came up on the call, omit the `Feature requests` parent bullet entirely — don't write "none".

Rules:
- **Slack-native formatting:**
  - `*single-asterisk bold*` for date header, account name, and CEP-stage callout
  - Plain `-` bullets at top level
  - 3-space indent + `-` for nested sub-bullets (Slack renders them as a second indent level)
  - Blank lines between major blocks (between header and bullets, and around `Gong:` line) for breathing room when read on mobile
  - No markdown headers (`#`), no double-asterisk bold, no em dashes (—). Use single `*bold*`, plain dashes, parentheses, periods, colons.
- **Gong link at top, not bottom.** Sits on the line immediately after the account/topic header. Recipients clicking through to listen want it findable; bottom-of-message is bad real estate on mobile.
  - Always include `Gong:` line when one is available in the account's `gong_url` field. Fall back to the meeting file's transcript URL (Granola or Gong) when account-level URL isn't set.
  - When neither is available, write a one-line note instead (`Gong: not captured on Greg's account this call`) so the structure stays consistent.
- **Always include feature requests** when they surfaced on the call (1-3 max, paraphrased ≤12 words each). Group under a `Feature requests` parent bullet with each request as a nested bullet — don't smush them onto one line.
- Focus on *what changed* and *what we learned*, not a rehash of the agenda
- Call out MEDDPICC field updates explicitly when they happen (new champion identified, EB confirmed, pain validated, competition surfaced, etc.) — group under a `MEDDPICC update` parent bullet with the specific changes nested
- Call out Command of Message updates similarly (new before/after, new pain, new required capability) — under a `CoM` parent bullet OR rolled into the MEDDPICC block when they're tightly related
- Include the CEP-stage callout as a bolded line when the recommendation differs from current SF stage, or when the call moved the recommended stage
- End with `Next:` step
- 4-8 top-level bullets total. Be concise — sub-bullets are for evidence, not padding.

### Step 2: Post Message to Slack

Read `slack_bot_token` from `~/.claude/skills/sales-config.md`. If not set, output the message to stdout for manual copy-paste and warn: "Slack bot token not configured. Add `slack_bot_token` to sales-config.md."

Post using the Slack Web API via Python:

```python
import requests, json

token = "{slack_bot_token from config}"
channel = "{slack_channel from account frontmatter}"

# Post the message
resp = requests.post("https://slack.com/api/chat.postMessage",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"channel": channel, "text": message, "unfurl_links": False})
result = resp.json()
if not result.get("ok"):
    print(f"Slack error: {result.get('error')}")
```

### Step 2b: Attach Deal PDF (recap mode only)

For recap messages, after posting the text message, upload the account's latest PDF as a file attachment to the same channel.

The PDF path is: `{config.pdf_path}/{YYYY-MM-DD}/{YYYY-MM-DD} {Account}.pdf`

```python
# Upload PDF to the channel
pdf_path = f"{config.pdf_path}/{date}/{date} {account}.pdf"
if os.path.exists(pdf_path):
    # Step 1: Get upload URL
    resp = requests.post("https://slack.com/api/files.getUploadURLExternal",
        headers={"Authorization": f"Bearer {token}"},
        data={"filename": os.path.basename(pdf_path), "length": os.path.getsize(pdf_path)})
    upload_info = resp.json()
    
    # Step 2: Upload the file
    with open(pdf_path, "rb") as f:
        requests.post(upload_info["upload_url"], files={"file": f})
    
    # Step 3: Complete upload and share to channel
    requests.post("https://slack.com/api/files.completeUploadExternal",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"files": [{"id": upload_info["file_id"]}], "channel_id": channel})
```

If the PDF doesn't exist (e.g., `/sales-pdf` hasn't run yet), skip the attachment silently.

### Step 3: Report

Return:
```json
{
  "posted": true/false,
  "channel": "#deal-acme-corp",
  "mode": "prep/recap",
  "account": "Acme Corp",
  "pdf_attached": true/false,
  "message_preview": "first 100 chars..."
}
```

## Integration with /sales-today

`/sales-today` should call this skill automatically at the END of the workflow, after `/sales-summarize-account` and `/sales-pdf` have run:

1. **After generating Deal Prep** (morning or evening mode): For each deal meeting in the prep section, call `/sales-slack {Account} prep`
2. **After generating Deal Recap** (morning or evening mode): For each deal meeting in the recap section, call `/sales-slack {Account} recap` (this attaches the freshly generated PDF)

Timing is critical: Slack posts happen LAST because:
- Summarization must complete first (recap content depends on it)
- PDFs must be generated first (recap attaches them)
- The message content is finalized only after all processing

Only post if the account has a `slack_channel` configured. Skip silently otherwise.

## Account File Integration

The `slack_channel` field should be added to account frontmatter:

```yaml
slack_channel: "#deal-acme-corp"
```

This field is:
- Set manually by the user when creating a deal channel
- Read by this skill to determine where to post
- Optional: accounts without it are silently skipped
