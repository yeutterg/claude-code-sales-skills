---
description: Export account files to PDF with clean formatting via pandoc and Playwright
argument-hint: [account | all | today]
---

# Export Account PDFs

Exports account markdown files to professionally formatted PDFs. Preprocesses Obsidian-specific syntax, converts to HTML via pandoc, and prints to PDF via Playwright MCP. The public version of this skill is `/sales-pdf`.

## Arguments
- No arguments: Export accounts that were summarized today (same as `today`)
- `today`: Export accounts summarized during this run or today
- `{account}`: Export a specific account
- `all`: Export all accounts that have real content

## Instructions

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract all config values from the YAML frontmatter, including:
- `vault_path`
- `company_folder`
- `pdf_export`
- `pdf_path`
- `playwright_configured`

If `pdf_export` is not `true`, tell the user: "PDF export is not enabled. Run `/sales-setup` to configure it." and stop.

### Pre-check: Verify Dependencies

**pandoc:**
```bash
which pandoc
```
If not installed, tell the user: "pandoc is required. Install with `brew install pandoc`." and stop.

**Playwright MCP:**
If `playwright_configured` is not `true` in config, tell the user: "Playwright is required for PDF export. Run `/sales-setup playwright` to configure." and stop.

### Step 1: Determine Which Accounts to Export

Based on `$ARGUMENTS`:

- **No arguments / `today`:** Read today's daily note at `{config.vault_path}/Daily/{YYYY-MM-DD}.md`. Find accounts that have `[x] Run /sales-summarize-account` checked. These are accounts that were summarized today. If none found, report "No accounts were summarized today. Nothing to export." and stop.

- **`{account}`:** Verify the account folder exists at `{config.vault_path}/{config.company_folder}/Accounts/{account}/`. If not, report the error and stop.

- **`all`:** List all account folders in `{config.vault_path}/{config.company_folder}/Accounts/`. Filter out accounts with no real content (see content check below).

**Content check:** Skip any account whose main file (`{Account}.md`) has no substantive content beyond the template. Check if the file has any MEDDPICC content filled in (not just empty headers) OR has ledger entries in `Ledger.md`. If both are empty/template-only, skip the account.

### Step 2: Preprocess Markdown (for each account)

Read the account file at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/{Account}.md`.

Apply these transformations in order:

1. **Remove YAML frontmatter:** Strip everything between the opening `---` and closing `---` at the top of the file.

2. **Resolve transclusion embeds (`![[...]]`):** When the file contains `![[filename]]`, read the referenced file and inline its content in place of the embed. Look for the file in the account folder first, then the vault root.
   - `![[Ledger]]` → Read `{account_folder}/Ledger.md` and inline its full content (this is plain markdown with bullet-point entries)
   - `![[contacts.base]]` → This is an Obsidian Database plugin config, NOT markdown. Replace it with a **generated contacts table** (see Step 2b below)
   - `![[meetings.base]]` → This is an Obsidian Database plugin config, NOT markdown. Replace it with a **generated meetings table** (see Step 2c below)
   - For any other `![[file]]` embeds, attempt to find and inline the file. If not found, remove the line.

3. **Generate contacts table (for `![[contacts.base]]` replacement):**
   Read all `.md` files in `{account_folder}/contacts/`. For each contact file, extract frontmatter fields: `name` (or filename), `company`, `role`, `influence`, `email`, `linkedin`, `notes`. Build a markdown table:
   ```
   | Name | Company | Role | Influence | Email | LinkedIn | Notes |
   |------|---------|------|-----------|-------|----------|-------|
   | Cooper Watts | Acme Corp | Principal Architect | Champion | ... | [LinkedIn](...) | ... |
   ```
   Sort by influence (Champion > Coach > Detractor > empty), then alphabetically by name.

4. **Generate meetings table (for `![[meetings.base]]` replacement):**
   Read all `.md` files in `{account_folder}/meetings/`. For each meeting file, extract frontmatter fields: `date`, `meeting_type`, `attendees`. Build a markdown table sorted by date descending:
   ```
   | Meeting | Date | Type | Attendees |
   |---------|------|------|-----------|
   | 2026-03-11 Internal Prep | 2026-03-11 | Internal Sync | Jane Smith, Bob Chen |
   ```
   Strip wiki-link syntax from attendee names (convert `"[[Person Name]]"` to just `Person Name`).

5. **Remove dataview code blocks:** Remove entire fenced code blocks with language `dataview`:
   ````
   ```dataview
   ...
   ```
   ````

6. **Remove inline dataview expressions:** Remove patterns like `` `= this.field` `` or `` `= this.anything` ``. BUT first, resolve common inline field references if the value is available from the frontmatter that was stripped in step 1:
   - `` `= this.ae` `` → Replace with the `ae` value from the original frontmatter
   - `` `= this.se` `` → Replace with the `se` value
   - `` `= this.csm` `` → Replace with the `csm` value
   - `` `= this.deal_type` `` → Replace with the `deal_type` value
   - `` `= this.next_call` `` → Replace with the `next_call` value
   - `` `= this.next_call_agenda` `` → Replace with the `next_call_agenda` value (format as comma-separated if it's a YAML list)
   - For any other `` `= this.*` `` expressions where the field exists in frontmatter, substitute the value. If the field is empty or not found, remove the expression.

7. **Convert wiki-links with display text:** Replace `[[path/to/file|Display Text]]` with just `Display Text`.

8. **Convert simple wiki-links:** Replace `[[simple link]]` with just `simple link`.

9. **Convert Obsidian callouts:** Transform `> [!type] Title` into a blockquote with bold title:
   ```
   > **Title**
   ```
   Preserve the rest of the callout content as regular blockquote lines.

10. **Remove empty table rows:** Remove table rows where all cells (after the header separator) are empty or contain only whitespace.

11. **Remove empty field labels:** Remove lines that are just a bold label with nothing after it, like `**AE:** ` or `**Champion:** ` (bold text followed by colon, optional space, and nothing else).

12. **Add H1 title:** Prepend `# {Account Name}` as the first line.

13. **Add generation date:** Add `*Generated {YYYY-MM-DD}*` on the line after the title, followed by a blank line.

Save the preprocessed markdown to a temp file (e.g., `/tmp/sales-pdf-{Account}.md`).

### Step 3: Convert to HTML via pandoc (for each account)

Create a temporary CSS file at `/tmp/sales-pdf-style.css` with the stylesheet below (create once, reuse for all accounts).

Run pandoc:
```bash
pandoc "/tmp/sales-pdf-{Account}.md" \
  -f markdown -t html5 \
  --standalone --embed-resources \
  --css /tmp/sales-pdf-style.css \
  --metadata title="{Account}" \
  -o "/tmp/sales-pdf-{Account}.html"
```

**Process all accounts through Steps 2-3 before moving to Step 4.** The preprocessing and pandoc conversion can run in parallel across accounts.

### Step 4: Start Temp HTTP Server

Start a temporary HTTP server to serve the HTML files (Playwright MCP blocks `file://` URLs):

```bash
cd /tmp && python3 -m http.server 18765 &
HTTP_PID=$!
echo $HTTP_PID
```

Save the PID for cleanup.

### Step 5: Print to PDF via Playwright MCP (sequential)

For each account HTML file, use Playwright MCP to print to PDF:

1. Navigate to `http://localhost:18765/sales-pdf-{Account}.html`
2. Use `browser_run_code` to execute:
   ```javascript
   await page.pdf({
     path: '{pdf_output_path}',
     format: 'Letter',
     margin: { top: '0.5in', right: '0.5in', bottom: '0.5in', left: '0.5in' },
     printBackground: true
   });
   ```

Save each PDF to `{config.pdf_path}/{YYYY-MM-DD} {Account}.pdf`.

Create the `{config.pdf_path}` directory if it doesn't exist:
```bash
mkdir -p "{config.pdf_path}"
```

Process accounts **sequentially** in this step (each needs the Playwright browser).

### Step 6: Clean Up

Always run cleanup, even if earlier steps failed:

```bash
# Kill the HTTP server
kill $HTTP_PID 2>/dev/null

# Remove temp files
rm -f /tmp/sales-pdf-*.md /tmp/sales-pdf-*.html /tmp/sales-pdf-style.css
```

### Step 7: Report

```
PDF export complete.

Exported {N} accounts:
- {pdf_path}/{YYYY-MM-DD} {Account1}.pdf
- {pdf_path}/{YYYY-MM-DD} {Account2}.pdf
...
```

If any accounts were skipped (no content), list them:
```
Skipped (no content):
- {Account}
```

## CSS Stylesheet

Use this for `/tmp/sales-pdf-style.css`:

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  line-height: 1.6;
  max-width: 900px;
  margin: 0 auto;
  padding: 20px 40px;
  color: #1a1a1a;
  font-size: 13px;
}
h1 { font-size: 24px; border-bottom: 2px solid #333; padding-bottom: 8px; margin-top: 0; }
h2 { font-size: 18px; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 24px; }
h3 { font-size: 15px; margin-top: 16px; }
blockquote {
  background: #f5f7fa;
  border-left: 4px solid #4a90d9;
  padding: 12px 16px;
  margin: 12px 0;
  font-size: 12px;
}
blockquote p { margin: 4px 0; }
pre, code {
  background: #f5f5f5;
  font-size: 11px;
  border-radius: 3px;
}
pre {
  padding: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}
code { padding: 2px 4px; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 12px; }
th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; }
th { background: #f0f0f0; }
ul, ol { padding-left: 20px; }
li { margin: 2px 0; }
hr { border: none; border-top: 1px solid #ddd; margin: 20px 0; }
strong { color: #111; }
a { color: #4a90d9; }
@media print {
  body { max-width: none; padding: 0; }
  pre { white-space: pre-wrap; }
}
```

## Rules
- Requires `pandoc`. If not installed, tell user: "pandoc is required. Install with `brew install pandoc`."
- Requires Playwright MCP. If not configured (`playwright_configured` is not `true`), tell user: "Playwright is required for PDF export. Run `/sales-setup playwright` to configure."
- Kill the temp HTTP server in a finally/cleanup step, even if PDF generation fails partway through
- Don't export accounts that have no content beyond the template (check if the file has MEDDPICC content or ledger entries)
- Use port 18765 for the temp server to avoid conflicts
- Never hardcode vault paths, company names, or account names. Use `{config.*}` references throughout.
