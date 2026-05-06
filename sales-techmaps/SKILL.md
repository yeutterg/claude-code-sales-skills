---
name: ld-techmaps
description: Canonical TECHMAPS framework for LaunchDarkly SEs. Drafts, scores, gap-analyzes, or coaches on a per-account TECHMAPS assessment using the locked eight-dimension framework with explicit Status / Findings / Risks per dimension. Invoked by /sales-summarize-account during account refresh, or runnable standalone for a focused review.
---

# TECHMAPS Framework

Canonical reference for the LaunchDarkly TECHMAPS framework. Definitions below are LOCKED. Do not infer, paraphrase, or invent meanings for any letter. If a query implies a different definition, correct it before answering.

**Source of truth:** https://launchdarkly.atlassian.net/wiki/spaces/SE/pages/4543742321/TECHMAPS+Framework+for+Solutions+Engineers

If this skill conflicts with the Confluence page, the Confluence page wins. Flag the discrepancy.

## Arguments

- `<account>` (required): Account name (e.g., `Apple`, `Acme Corp`, `Globex`)
- `<mode>` (optional, default `draft`): one of:
  - `draft`: First-pass TECHMAPS from meeting notes / account file. Mark unknown fields as "Not yet captured." Do not extrapolate.
  - `score`: Per-dimension status with one-line justification. Flag wrong letter meanings, missed risks, or contradictions.
  - `gaps`: Ranked list of dimensions that most threaten the tech win, with concrete next actions per dimension.
  - `coach`: Dimension-by-dimension question prompts the SE can take into the next customer conversation.

Examples:
- `/sales-techmaps Apple` (defaults to `draft`)
- `/sales-techmaps Globex score`
- `/sales-techmaps Initech gaps`
- `/sales-techmaps Acme Corp coach`

When invoked by another skill (e.g., `/sales-summarize-account`), the parent passes already-extracted findings; this skill applies the framework rules and renders the eight-dimension assessment.

## What TECHMAPS is

TECHMAPS is the SE-specific framework for the technical evaluation stage of an opportunity. Its purpose is to help SEs secure the tech win against competitors, open source, homegrown solutions, and the status quo.

LaunchDarkly uses MEDDPICC as its company-wide qualification framework. AEs own it. **TECHMAPS does not replace MEDDPICC.** It gives SEs a structured way to cover the technical dimensions that MEDDPICC alone does not fully capture, and it maps cleanly back so SE and AE work stays connected.

## The eight dimensions (locked)

Use exactly these letters and exactly these names. Do not substitute synonyms.

| Letter | Name | Definition | Look for | MEDDPICC mapping |
|---|---|---|---|---|
| **T** | **Technical Requirements & Scalability** | Do we fully understand technical needs, constraints, and growth patterns? Can we scale reliably? | Documented technical fit, performance benchmarks and capacity planning, architectural validation, scalability risks identified early. | Decision Criteria |
| **E** | **Environment** | What does their current stack look like? How will we integrate? | Systems, APIs, identity, networking, data flows. Security, compliance, and ecosystem risks. | Decision Criteria |
| **C** | **Competitors** | Who are we up against, and how do we win technically? | Clear view of competitor capabilities and gaps. Credible counter-positioning with tradeoffs. | Competitors |
| **H** | **Hero (Technical Champion)** | Do we have a technical advocate who believes in us and can influence decisions? | Named person(s) with influence over the technical decision. Signal strength: confidence, access, and internal clout. | Champion, Economic Buyer |
| **M** | **Metrics** | How does the customer measure technical success? | POC/pilot success criteria that ladder to business impact. Quantitative preferred over pass/fail. Ambiguity identified early. | Metrics |
| **A** | **Alignment** | Are we solving the right problem in the right way? | Confirmed alignment between our capabilities and their stated and unstated goals. Validated at technical and business levels. Use cases mapped to goals and value narrative (BVA). Misalignments identified early. | Identified Pain |
| **P** | **Plan for Tech Validation** | Is there a structured, mutually agreed plan (POV, workshop, deep-dive demo)? | Documented plan with owners, scope, and success criteria. Timelines set. Scope creep and blockers flagged early. | Decision Criteria, Decision Process |
| **S** | **Support** | Have we shown them how we will support implementation and long-term success? | Introductions to post-sale teams (TAM, PS, Support). Enablement and onboarding path that reduces adoption risk. | Decision Criteria, Paper Process |

## Risk awareness is built in

TECHMAPS does not have a separate risk line item. Risk lives inside every dimension. For each one, ask:

> What could go wrong here, and how do we mitigate it before it becomes a blocker?

**Every TECHMAPS output you produce must include a Risks field for every dimension.** See the canonical output template below.

## Glossary of LD-specific terms

Quick reference for terms that appear in this framework. Use these meanings exactly. If a term appears in a TECHMAPS context that is not listed here, ask the SE for the definition rather than guessing.

- **BVA**: Business Value Analysis. The narrative and quantitative case tying technical capabilities to customer business outcomes.
- **POV / POC**: Proof of Value / Proof of Concept. A scoped, time-bound technical validation with agreed success criteria.
- **TAM**: Technical Account Manager. Post-sale role responsible for ongoing technical relationship and adoption.
- **PS**: Professional Services. Post-sale implementation and integration delivery team.
- **AE**: Account Executive. Owns the overall opportunity and MEDDPICC.
- **SE**: Solutions Engineer. Owns the technical evaluation and TECHMAPS.
- **EB**: Economic Buyer. The MEDDPICC role for the person who can authorize spend.
- **MEDDPICC**: LD's company-wide qualification framework. Metrics, Economic Buyer, Decision Criteria, Decision Process, Paper Process, Identified Pain, Champion, Competitors.

## Canonical output template

When generating, drafting, or scoring a TECHMAPS assessment, use this exact structure for every dimension. Do not omit fields. Do not skip a letter.

**Status color code.** Always pair the colored circle with the label, in this order: circle, then label. Use exactly one of the four values below. Do not invent intermediate states (no "almost strong," no "yellow-green").

- 🟢 Strong (green): well-covered, no immediate gap
- 🟡 Adequate (yellow): present but needs more depth or validation
- 🔴 Thin (red): material gap that threatens the tech win
- ⚫ Not yet captured (black): no information yet from the customer or source

**Template:**

```markdown
### [Letter] - [Name]
**Status:** [🟢 Strong | 🟡 Adequate | 🔴 Thin | ⚫ Not yet captured]
**Findings:** [Specifics. Names, systems, numbers, dates. Avoid generalities.]
**Risks:** [What could go wrong here and how we mitigate it. If none identified yet, write "None identified yet" rather than leaving blank.]
```

Repeat for all eight letters in order: T, E, C, H, M, A, P, S.

End with a one-line summary of overall tech-win readiness and the top two dimensions that need work next.

## Verification step (run before responding)

Before sending any TECHMAPS-related response, walk through this checklist. If any check fails, fix the response before sending.

- [ ] All eight letters are present and in order: T, E, C, H, M, A, P, S
- [ ] Each letter uses the exact name from the locked table above
- [ ] Each dimension includes Status, Findings, and Risks fields. Status uses exactly one of: 🟢 Strong, 🟡 Adequate, 🔴 Thin, ⚫ Not yet captured. The colored circle is always present.
- [ ] No letter has been substituted with a wrong meaning from the reject list in the anti-hallucination rules
- [ ] No glossary term has been silently expanded into a guess
- [ ] The summary line at the end is present
- [ ] (Metrics) Business KPIs only, with provenance: customer-confirmed (preferred), public earnings with source label, or explicit "discovery gap" flag. Never proxy from LD-side scope numbers.

## Ask vs. assume

If the source material does not contain enough information for a dimension, follow this rule:

- **Drafting from notes** (mode `draft`): mark unknown fields as ⚫ Not yet captured and continue. Do not invent.
- **Final/complete TECHMAPS** (mode `draft` invoked with intent of finality, or mode `score`): if a dimension is missing critical detail, stop and ask the SE for the specific information needed before producing that dimension. Do not fabricate to fill the gap.
- **Named entities** (people, systems, competitors, dollar amounts, dates): never guess. If a name is not in the source, write "Not specified" or ask.

## Mode-specific instructions

### Pre-check (all modes)

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `name`. Verify the account folder exists at `{vault_path}/{company_folder}/Accounts/{Account}/`. Stop if missing.

Read sources in this order:
1. **Account file** (`{Account}.md`): MEDDPICC, TECHMAPS (if present), CoM, Tech Stack, frontmatter (deal size, AE/CSM, Salesforce stage)
2. **Recent meetings**: last 45 days from `meetings/`, newest first
3. **Ledger.md**: most recent 10 entries
4. **Existing TECHMAPS section in account file**: read it to understand current state

### Mode: `draft`

Produce a first-pass TECHMAPS assessment using the canonical template. Mark unknown fields as ⚫ Not yet captured. Do not extrapolate beyond the source.

**Output destination:** Replace the `## TECHMAPS` section in `{Account}.md` with the new assessment. Preserve the section's position in the file (between `## Command of the Message` and `## Tech Stack` per the standard account file order). Keep the existing `> [!summary] Summary` callout at the top with one-line bullets per dimension; render the per-dimension `### [Letter] - [Name]` blocks below.

### Mode: `score`

Read the existing `## TECHMAPS` section. For each dimension, output:
- 🟢/🟡/🔴/⚫ Status
- One-line justification
- Flag any dimension where a wrong letter meaning was used, a risk was missed, or a finding contradicts another dimension

Output as a chat response, not a file write. Do not modify the account file.

### Mode: `gaps`

Read the existing `## TECHMAPS` section. Produce a ranked list (1, 2, 3...) of dimensions that most threaten the tech win, with concrete next actions per dimension. Base the ranking only on what is in the assessment. Do not invent buyer behavior or competitor moves.

Output as a chat response.

### Mode: `coach`

Read the existing `## TECHMAPS` section. For each dimension, produce 1-2 specific question prompts the SE can take into the next customer conversation. Keep questions specific and grounded in what is already captured. Do not produce generic discovery questions.

Output as a chat response.

## Anti-hallucination rules

When generating, summarizing, scoring, or critiquing a TECHMAPS assessment, you must:

**Use the exact letter mapping above. Do not substitute. The following are common wrong guesses. Reject them and correct the user:**

- **T** is not Timeline, Tools, Tech Stack, Team, or Trial.
- **E** is not Economic Buyer, Evaluation, Enterprise, or Engineering.
- **C** is not Champion, Customer, Criteria, or Compliance.
- **H** is not History, Hypothesis, or Hurdles.
- **M** is not Money, MEDDPICC, Motion, or Manager.
- **A** is not Authority, Adoption, Account, or Architecture.
- **P** is not Pain, Paper, Process, Pricing, or Procurement.
- **S** is not Stakeholders, Success, Strategy, Solution, or Sponsor.

**Hero is the LD term, not Champion.** They map to the same MEDDPICC element, but inside TECHMAPS the letter is **H** and the name is **Hero**.

**TECHMAPS has exactly eight letters.** Do not invent a ninth dimension. Do not collapse or merge dimensions.

**Do not conflate TECHMAPS with MEDDPICC.** Do not position one as replacing the other. LD uses MEDDPICC company-wide and AEs own it. TECHMAPS is the SE lens for the technical evaluation stage and the tech win. The two complement each other and map cleanly. Use TECHMAPS letters when capturing technical evaluation findings. Do not rewrite an AE's MEDDPICC notes into TECHMAPS letters.

If a user asks "what does X stand for in TECHMAPS" and X is not in the table above, say so explicitly. Do not guess. Do not extrapolate.

If a user supplies a TECHMAPS assessment with non-standard terms (for example, "T = Timeline"), correct them in your response and cite this skill.

Do not summarize TECHMAPS as "MEDDPICC for SEs" without naming the eight letters. A summary that omits the actual definitions is incomplete and risks propagating bad versions.

**Always include a Risks field for every dimension.** Risk is built into TECHMAPS, not a separate dimension. An assessment without explicit per-dimension risks is incomplete.

## Metrics special rule (NO HALLUCINATION)

TECHMAPS Metrics = business metrics, same as MEDDPICC Metrics. Revenue, conversion, MAU, NPS, time-to-market, churn : what the customer measures their business by. **NOT LaunchDarkly usage stats** like flag counts, environment counts, seat counts, or platform MAU; those go in Tech Stack or Environment.

Three valid sources for Metrics, in priority order:

1. **Customer-stated** (best): the prospect explicitly named this KPI in a meeting, transcript, Slack thread, or email. Render as plain bullets, no provenance suffix needed.
2. **Public-company earnings reports** (acceptable for public companies, but MUST be labeled): if the account is publicly traded and you have direct article links to specific earnings releases (BusinessWire, PRNewswire, investor.{company}.com, etc.), you may pull headline business KPIs (revenue, growth rate, RPO, EPS, customer count, segment revenue). Append `(from {Quarter FY} earnings, {short-source})` so the reader can never confuse it with prospect-confirmed signal.
3. **Discovery gap** (correct default when neither above applies): render as the explicit gap flag.

If no meeting subagent extracted customer-confirmed metrics AND no earnings data is available (private company, or no usable sources), the Metrics dimension MUST render Status as 🔴 Thin or ⚫ Not yet captured and Findings as the explicit discovery-gap flag, NOT filled in from anything else.

## Worked examples

### Example 1: Single dimension, wrong vs. right

**Wrong (do not produce output like this):**

```
T - Timeline
Status: 🟢 Strong
Findings: Customer wants to go live in Q3.
```

This is wrong on three counts. T does not stand for Timeline. "Go live in Q3" is a project schedule, not a technical requirement. There is no Risks field.

**Right:**

```
### T - Technical Requirements & Scalability
**Status:** 🟡 Adequate
**Findings:** Java and Go SDKs needed across ~200 microservices. Peak evaluation traffic ~50K flag evals/sec at production scale. Multi-region deployment required (US-East, EU-West). No documented latency SLA yet.
**Risks:** Latency SLA undefined. If customer expects sub-10ms p99 globally, we need to validate edge delivery early. Mitigation: schedule architecture review with their platform team in the next two weeks.
```

### Example 2: Full TECHMAPS for a fictional deal

Deal: Acme Corp, platform migration. Source: 60-minute discovery call with their Principal Platform Engineer.

```
### T - Technical Requirements & Scalability
**Status:** 🟡 Adequate
**Findings:** Java and Python microservices, ~150 services, 30K flag evals/sec peak. Multi-region (US-East, EU-West). SOC 2 Type II artifacts required.
**Risks:** Latency SLA undefined for EU traffic. Mitigation: validate edge delivery in POV.

### E - Environment
**Status:** 🟢 Strong
**Findings:** AWS-native, EKS in us-east-1 and eu-west-1. Okta SSO, Datadog observability, GitHub Enterprise. SCIM provisioning required.
**Risks:** Datadog logs ingestion already at budget cap. LD events stream needs sizing review. Mitigation: scope events volume estimate with platform team.

### C - Competitors
**Status:** 🔴 Thin
**Findings:** Customer mentioned evaluating Statsig in passing. Not formally in cycle.
**Risks:** Statsig may enter via experimentation team. Mitigation: ask Hero whether experimentation is in scope and prepare counter-positioning brief.

### H - Hero (Technical Champion)
**Status:** 🟡 Adequate
**Findings:** Priya Shah, Principal Platform Engineer. Strong technical clout, attended both demos, runs internal Slack channel for the eval. Reports to VP Eng who is the EB.
**Risks:** Priya is one-deep. No secondary advocate in security or SRE. Mitigation: get a 1:1 with their SRE lead in next two weeks.

### M - Metrics
**Status:** 🔴 Thin
**Findings:** Customer wants "fewer rollback incidents" and "faster feature delivery." No quantitative baselines yet.
**Risks:** Without baselines, POV success becomes subjective. Mitigation: get current rollback frequency and lead-time-to-prod numbers from Priya before POV starts.

### A - Alignment
**Status:** 🟡 Adequate
**Findings:** Stated goal is reducing release risk during platform migration. BVA mapped to deployment frequency and incident rate. Unstated: VP Eng wants a visible win to justify FY budget.
**Risks:** VP Eng's political need for a fast visible win may push timeline tighter than POV can support. Mitigation: align on POV scope with VP Eng directly, not just Priya.

### P - Plan for Tech Validation
**Status:** 🟡 Adequate
**Findings:** 4-week POV agreed. Scope: 2 services, EU and US, targeted rollback scenario. Success criteria drafted but not signed.
**Risks:** Success criteria not co-signed. Scope creep risk from SRE team. Mitigation: get success criteria signed by Priya and VP Eng before kickoff.

### S - Support
**Status:** ⚫ Not yet captured
**Findings:** TAM and PS not yet introduced.
**Risks:** Customer has been burned by a prior vendor's poor onboarding. Mitigation: introduce TAM and PS early, ideally during POV kickoff, with named owners on our side.

**Summary:** Tech-win readiness is moderate. Top two dimensions to advance: Metrics (need quantitative baselines before POV) and Support (post-sale introductions not yet made).
```

## How SEs should use this

- **Opportunity reviews:** walk all eight dimensions. Flag any dimension that is empty or thin.
- **Discovery notes:** tag findings with the relevant letter so reviewers can scan quickly.
- **Deal strategy docs and CRM:** use TECHMAPS to structure the technical evaluation portion of the deal. Do not overwrite the AE's MEDDPICC notes with TECHMAPS letters.
- **Living framework:** refine and evolve with the SE org. If you want to propose a change, take it to SE leadership before using it in customer-facing work. Do not improvise in the field.

## When you are unsure

Stop. Re-read this skill. If still unsure, ask in your SE leadership Slack channel or open the Confluence page linked above. Do not make it up.

## Account file integration

When invoked in `draft` mode, the skill writes the assessment into `{Account}.md` at the `## TECHMAPS` section. The section structure inside the account file:

```markdown
## TECHMAPS

> [!summary] Summary
> - **T - Technical Requirements & Scalability:** {one-line status + headline finding}
> - **E - Environment:** {one-line status + headline finding}
> - **C - Competitors:** {one-line status + headline finding}
> - **H - Hero (Technical Champion):** {one-line status + headline finding}
> - **M - Metrics:** {one-line status + headline finding}
> - **A - Alignment:** {one-line status + headline finding}
> - **P - Plan for Tech Validation:** {one-line status + headline finding}
> - **S - Support:** {one-line status + headline finding}

### T - Technical Requirements & Scalability
**Status:** ...
**Findings:** ...
**Risks:** ...

### E - Environment
...

(repeat for all 8 letters)

**Summary:** Tech-win readiness is {strong/moderate/weak}. Top two dimensions to advance: {X} and {Y}.
```

This matches the canonical output template above with the addition of the at-a-glance summary callout (consistent with the rest of the account file structure: MEDDPICC and CoM also use this callout pattern).

## Inheritance from /obsidian-format

Account files live in the Obsidian vault. The skill MUST follow `/obsidian-format` rules:
- No em-dashes (use colons or `:` instead) : BLOCKER
- No horizontal rule dividers (`---`)
- Standard wiki-link format `[[Name]]`
- Frontmatter only at the top of the file

The colored-circle status emojis (🟢🟡🔴⚫) are an explicit exception : they are required by the canonical TECHMAPS template per the LD framework, not decorative.
