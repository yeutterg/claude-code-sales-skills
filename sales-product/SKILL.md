---
name: ld-product
description: Canonical LaunchDarkly product knowledge base. Per-product capability descriptions, doc URLs, common confusions, competitive positioning, and integrations. Read by /sales-pov, /sales-ps-prep, /sales-summarize-account, /sales-meeting prep, /sales-architecture-diagram, /sales-exec-summary, and any LD-specific skill that needs canonical product context. Auto-extends from customer call signal via /sales-summarize-account → learnings.md → review queue → promotion to knowledge.md.
---

# LaunchDarkly Product Knowledge

Canonical reference for LaunchDarkly product capabilities, competitive positioning, integrations, and customer-relevant tradeoffs. Two files:

- `knowledge.md` : Greg-curated canonical reference. Stable, intentionally maintained. Read by other skills.
- `learnings.md` : append-only queue of candidate updates extracted from customer calls by `/sales-summarize-account`. Reviewed and promoted to `knowledge.md` via `/sales-review-learnings`.

## Arguments

- (no arguments) : print summary of all products with one-line descriptions
- `<product name>` : print full canonical entry for a single product (e.g., `/sales-product Workflows`)
- `compare <product-a> <product-b>` : print explicit distinction between two products (e.g., `/sales-product compare Workflows GuardedReleases`). Useful when customer language conflates them.
- `competitor <name>` : print competitive positioning for a competitor across LD products
- `learnings` : print pending learnings queue (candidate updates not yet promoted)
- `learnings promote <entry-id>` : promote a learnings entry into knowledge.md
- `learnings reject <entry-id>` : remove a learnings entry without promoting

Examples:
- `/sales-product`
- `/sales-product Workflows`
- `/sales-product compare Workflows GuardedReleases`
- `/sales-product competitor Statsig`
- `/sales-product learnings`

## Usage by Other Skills

When another LD skill needs product context (POV writing, PS prep, exec summary generation, architecture diagram, customer migration plan), it reads `knowledge.md` directly. Common patterns:

- **`/sales-pov`**: when listing painful + deal-gating items, look up canonical product names + doc URLs from `knowledge.md`
- **`/sales-ps-prep`**: surface common confusions (e.g., Workflows vs Guarded Releases) so SAs are calibrated before customer calls
- **`/sales-summarize-account`**: extract product-related signal from meetings → write structured entries to `learnings.md`
- **`/sales-architecture-diagram`**: pull canonical product names + integration boundaries
- **`/sales-meeting`** prep: include Common Confusions warnings when relevant products surface in the agenda
- **`/sales-exec-summary`** (forthcoming): pull required-capability table mappings + inline doc URLs from `knowledge.md`

## Instructions

### Pre-check: Read Files

Read `knowledge.md` for canonical content. Read `learnings.md` if user is asking about pending learnings.

### Mode: print summary (no args)

List every product in `knowledge.md` with: name, one-line description, doc URL.

### Mode: print full product entry

Read the named product's section from `knowledge.md`. Output:
- name + one-line description
- What it solves (problem statement)
- When to use vs when NOT to use
- Common confusions (cross-references)
- Pricing tier (if known)
- Doc URL
- Related products
- Competitive positioning summary
- Customer use cases (real ones from learnings, if promoted)

### Mode: compare A B

Read both product sections. Output a table of distinctions:
- Purpose
- When to use
- Pairs with / replaces
- Common confusion pattern
- Doc URL each

### Mode: competitor lookup

Read the competitor's section in `knowledge.md` (or per-competitor file). Output:
- Where they're strong
- Where LD wins on capability
- Where LD wins on substrate (e.g., flag delivery network, per-fact ACL)
- Common deal scenarios
- Outcomes from past encounters (if logged)

### Mode: learnings queue

Read `learnings.md` and surface unreviewed entries grouped by:
- Capability gap candidates
- Competitor encounter signal
- Pricing pushback
- Customer confusion patterns
- Tradeoff revelations
- New use cases

For each entry: timestamp, account, meeting reference, candidate update, status (pending review).

### Mode: learnings promote / reject

`promote <entry-id>` : merge the entry into the appropriate section of `knowledge.md`, mark the learnings entry as promoted with a timestamp.

`reject <entry-id>` : mark the learnings entry as rejected; archive but don't merge.

## Auto-Extension Pattern

`/sales-summarize-account` writes to `learnings.md` autonomously during account refresh. The schema for entries is at the top of `learnings.md`. Extraction subagents look for:

- Customer asked for a feature LD doesn't have → capability gap candidate
- Customer mentioned competitor by name → competitor encounter
- Customer pushed back on pricing / PS hours → pricing pushback
- Customer confused two LD products → customer confusion pattern
- Customer surfaced a real-world tradeoff not in canonical knowledge → tradeoff revelation
- Customer used a product in an unexpected way → new use case

`/sales-review-learnings` is the human-in-the-loop review surface. Greg reviews the queue, accepts/rejects, accepted entries merge into `knowledge.md`.

## Rules

- `knowledge.md` is the canonical source; never let it drift from reality. Promotions from `learnings.md` should be reviewed for accuracy first.
- `learnings.md` is append-only; entries never delete, only mark status (pending / promoted / rejected).
- When an LD product or capability sunsets (deprecation), update its `status` field in `knowledge.md` and add a `successor` cross-reference. Don't delete the entry.
- When a doc URL changes (LD restructures docs), update `knowledge.md`. The skill is the source of truth for URLs that other skills cite.
- Customer-confidential signal (specific deal context, non-public account info) does NOT merge into `knowledge.md` even when promoted. Only generalizable patterns merge. Account-specific signal stays in the account file's MEDDPICC / Ledger.
- This skill is LD-only and lives in the private LD repo (`claude-code-obsidian-commands`). It does NOT mirror to the public `claude-code-sales-skills` repo.
