# LaunchDarkly Product Learnings (Pending Review Queue)

*Append-only log of candidate updates to `knowledge.md`, extracted from customer calls by `/sales-summarize-account`. Reviewed via `/sales-review-learnings`. Promoted entries get edited into `knowledge.md`; rejected entries are marked but archived.*

## Entry Schema

Each candidate update is a structured block. Schema:

```markdown
### {YYYY-MM-DD-NNN} | {category} | {account}

- **category:** one of `capability-gap`, `competitor-encounter`, `pricing-pushback`, `customer-confusion`, `tradeoff-revelation`, `new-use-case`, `roadmap-mention`
- **product or competitor:** {canonical name; cross-ref to knowledge.md if existing}
- **observation:** {what was learned, in 1-3 sentences}
- **customer quote:** "{verbatim if captured; omit if not}"
- **LD-side response (if logged):** {what was said in the meeting; omit if not}
- **proposed update to knowledge.md:** {section + specific change}
- **source:** [[{account}]] / [[{meeting file}]]
- **status:** `pending-review` | `promoted` | `rejected`
- **status-date:** {when status changed}
```

## Categories

- **capability-gap:** customer asked for a feature LD doesn't have (e.g., prerequisite flag dependency visibility, .NET agent-graph SDK)
- **competitor-encounter:** customer mentioned a competitor by name; what they liked / disliked / their state of evaluation
- **pricing-pushback:** customer pushed back on price, PS hours, packaging tier, or licensing model
- **customer-confusion:** customer conflated two LD products or misunderstood a capability boundary; recurrent confusion patterns surface positioning issues
- **tradeoff-revelation:** customer surfaced a real-world tradeoff that isn't explicit in `knowledge.md`
- **new-use-case:** customer is using or planning to use a product in a way that isn't in `knowledge.md`
- **roadmap-mention:** customer asked about a future capability; LD-side response logged (e.g., "confirmed roadmap, no firm timeline")

## Promotion Rules

A learning is ready to promote when:

- The signal has been observed in 2+ accounts (one-off curiosities aren't canonical)
- Customer-confidential context (specific deal info, account state) is stripped; only the generalizable pattern merges
- The proposed update is specific to a `knowledge.md` section + a clear edit
- The change doesn't conflict with another pending or recently-promoted learning

`/sales-review-learnings` is where Greg walks the queue and decides per-entry: promote / reject / hold for more signal.

## Pending Queue

*(Empty. `/sales-summarize-account` populates this on each account refresh.)*

---

## Promoted History (Archive)

*(Promoted learnings get archived here with their original entry + the resulting knowledge.md change. Lets us audit canonical-knowledge evolution over time.)*

## Rejected History (Archive)

*(Rejected learnings stay archived for context if a similar signal recurs later.)*
