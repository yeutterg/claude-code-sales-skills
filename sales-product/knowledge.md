# LaunchDarkly Product Knowledge (Canonical)

*Greg-curated reference. Other skills read this file. Promotions from `learnings.md` are reviewed by `/sales-review-learnings` before merging here.*

Last reviewed: 2026-05-06.

## Products

### Feature Flags

- **One-line:** Core feature flag platform; flag delivery network + SDK + targeting + segment-based rules.
- **What it solves:** Decouple deploy from release; targeted rollouts; instant rollback without redeploy; per-user / per-segment / per-environment flag state.
- **When to use:** Always. The substrate. Every other LD product depends on it.
- **When NOT to use:** When the customer wants config-management for non-runtime values (use feature flags only for behavior that varies at runtime).
- **Docs:** https://launchdarkly.com/docs/home/flags
- **Pricing tier:** Foundation (always included).
- **Common confusions:** Flags ≠ feature toggles in code. LD flags are runtime-evaluated against user context, not compiled-in constants. Customers with homegrown systems often have toggles, not flags.
- **Related products:** Contexts, Segments, SDKs (all dependencies).
- **Competitive positioning:**
    - vs Statsig / Eppo / GrowthBook / Optimizely / Harness.io / homegrown: LD wins on flag delivery network (200ms global, multi-layer redundancy, no null states), per-fact ACL maturity, mature enterprise compliance (SOC 2, FedRAMP), and breadth of advanced features (Guarded Releases, AI Configs, Experimentation, Workflows).
- **Customer use cases:** universal; every LD customer uses Feature Flags.

### SDKs

- **One-line:** Server-side and client-side SDKs in 30+ languages; streaming connection to LD's flag delivery network.
- **What it solves:** Application-side integration. SDKs maintain a streaming connection to LD, evaluate flags against user context, stream metrics back, support advanced features (Guarded Releases, Experimentation, AI Configs).
- **When to use:** Required for any LD deployment. Without the SDK, customer is using LD as a flag database only and forfeits the delivery network, user context, metrics, and advanced features.
- **Docs:** https://launchdarkly.com/docs/sdk
- **Common confusions:** Hybrid models (customer's backend + LD UI) skip the SDK. LD does not support that long-term: it loses delivery network reliability, user context, metrics tie-in, and advanced features.
- **Related products:** Contexts (SDK passes contexts at evaluation), Guarded Releases (SDK streams metrics back), Experimentation (SDK reports variant exposure).
- **Tradeoffs:** SDK integration is the migration cost of moving from a homegrown system to LD. Standard sales objection. Mitigation: gradual SDK-first migration starting with one new high-value initiative.

### Contexts

- **One-line:** Multi-attribute user / device / org / custom context model passed at flag evaluation.
- **What it solves:** Flag targeting against rich user attributes (role, plan, tenant, device, custom kinds). Replaces the legacy "user" model with multi-kind contexts.
- **When to use:** Always. Every flag evaluation runs against a context.
- **Docs:** https://launchdarkly.com/docs/home/flags/contexts
- **Common confusions:** "Context" is the modern term replacing "user." Old documentation may say "user"; same idea, multi-kind expansion.
- **Related products:** Segments (segment definitions match against contexts), SDKs (SDK passes contexts at evaluation).
- **Pricing tier:** Foundation (included).

### Segments

- **One-line:** Reusable named groups of contexts; segment definitions evaluated at flag-eval time.
- **What it solves:** Author a customer cohort once (e.g., "Beta users in EU"), reuse across many flags and rules. Segments support inclusion lists, rule-based criteria, AND-OR logic, and integration-driven definitions (e.g., from Salesforce or Snowflake data).
- **When to use:** Whenever the same group of users / accounts / devices is targeted by more than one flag.
- **Docs:** https://launchdarkly.com/docs/home/flags/segments
- **Common confusions:** Segments are reusable named cohorts; ad-hoc targeting rules in a single flag are NOT segments.
- **Related products:** Contexts (segments match against context attributes), Salesforce + Snowflake integrations (data sources for segment definitions).
- **Pricing tier:** Foundation (included).

### Workflows

- **One-line:** Schedule-based multi-stage flag rollout templates.
- **What it solves:** Author a calendar-driven rollout cadence once and let the system progress flags through stages without manual PM intervention. Each stage can change targeting rules, percentages, or segment assignments. Templates can be reused across flags.
- **When to use:** When a rollout cadence is calendar-driven and predictable (e.g., "5% Day 1, 10% Day 3, 25% Day 7, 100% Day 14"). Common for multi-cohort customer rollouts (e.g., 8 batches by payment type with scheduled gates).
- **When NOT to use:** When the rollout should be metric-driven rather than calendar-driven (use Guarded Releases). When you only need a single one-time targeting change (use a direct rule edit).
- **Docs:** https://launchdarkly.com/docs/home/releases/workflows
- **Common confusions:** **Workflows ≠ Guarded Releases.** Workflows is calendar-driven scheduled progression. Guarded Releases is metric-driven auto-rollback. They are complementary (often paired: Workflows handles the schedule, Guarded Releases handles the safety gate per stage). Workflows is NOT in maintenance mode.
- **Related products:** Guarded Releases (often paired), Approvals (per-stage gates), Release Pipelines, Segments.
- **Pricing tier:** Pro / Enterprise (check current pricing).

### Guarded Releases

- **One-line:** Metric-driven auto-rollback for progressive rollouts; statistical-significance testing per stage.
- **What it solves:** Catch regressions in production based on real-time metrics (latency, error rate, custom KPIs). Compare new-version users vs old-version users in real time; auto-rollback when threshold exceeded. Eliminates the multi-day env-misalignment-bug remediation pattern in homegrown systems.
- **When to use:** Whenever a feature has measurable production metrics and you want safety gates. Especially valuable for AI feature rollouts (where regressions can be subtle and metric-driven detection beats human review).
- **When NOT to use:** When the rollout is a pure binary cutover with no measurable metric, or when the metric isn't reliable enough for auto-decision (then use notify-only mode, no auto-rollback).
- **Docs:** https://launchdarkly.com/docs/home/releases/guarded-rollouts
- **Common confusions:** **Guarded Releases ≠ Workflows.** Guarded Releases = metric-driven safety. Workflows = scheduled calendar progression. They pair often: Workflows for the cadence, Guarded Releases for the gate per stage. Customers often confuse the two; the canonical pattern is "Workflows + Guarded Releases together."
- **Related products:** Workflows, Experimentation (Guarded Releases is a simpler metric-comparison; Experimentation is full statistical experimentation), Contexts, SDKs (metrics streamed back via SDK).
- **Pricing tier:** Pro / Enterprise (check current pricing).
- **Customer demonstration:** Acme Corp April 29 demo example: API v1 to v2 rollout, latency spiked 4-5x for new-version users, auto-rolled back at 18 users instead of 200. Canonical small-blast-radius story.

### Experimentation

- **One-line:** A/B and multivariate testing with Bayesian / Frequentist / Multi-Armed Bandit allocation.
- **What it solves:** Statistical experimentation tied to product metrics (conversion, revenue, NPS). Run controlled experiments on flag variations, get statistically-significant results before broad rollout, support multiple allocation strategies including MAB for real-time optimization.
- **When to use:** Customer wants to test variant impact statistically (not just gradual rollout). Common for AI feature variant testing (which prompt / which model produces better outcomes).
- **When NOT to use:** Customer is doing pure sequential rollouts ("first beta, then VIPs, then everyone"); they need Workflows + Guarded Releases, not Experimentation. (Acme Corp is this case: they want sequential not A/B.)
- **Docs:** https://launchdarkly.com/docs/home/experimentation
- **Common confusions:** Experimentation is statistical (variance, significance, power); Guarded Releases is operational (auto-rollback on metric regression). Different problem shapes.
- **Related products:** Contexts (experiment assignment), AI Configs (experiment on prompt/model variants), SDKs (variant exposure reporting), Snowflake / Datadog integrations (metric sources).
- **Pricing tier:** Pro / Enterprise (check current pricing).

### AI Configs

- **One-line:** Prompt + model versioning with runtime swap; evals + A/B testing for AI features.
- **What it solves:** Decouple prompt and model from application code. Update prompts and switch models in production without redeploy. Run evals against golden sets. A/B test prompt variants. Instant rollback when an AI feature regresses.
- **When to use:** Customer is shipping AI features to production. Especially valuable when AI rollouts are currently manual (e.g., 2-3 weeks per release with no eval infrastructure).
- **Docs:** https://launchdarkly.com/docs/home/ai-configs
- **Common confusions:** AI Configs is purpose-built for AI feature delivery; it is NOT a generic config-management product. Customers sometimes assume "AI Configs" means "configs for AI use cases" generically; it specifically means runtime prompt + model versioning and AI eval infrastructure.
- **Related products:** Experimentation (A/B test prompt variants), Guarded Releases (auto-rollback on metric regression for AI features), Contexts, SDKs.
- **Pricing tier:** AI add-on (check current pricing).
- **Customer landscape:** Compelling fit for customers running AI features manually with no eval infrastructure (Acme Corp invoice OCR / agentic AP, Globex AI chatbot, Initech AI rollouts). Common ask: "I have 70+ CSV files for manual prompt rollouts" or "AI rollouts take 2-3 weeks manual."

### Approvals

- **One-line:** Role-based approval gates for flag changes; per-environment policies.
- **What it solves:** Govern flag changes via review queues. Restrict who can change what in which environment. Audit trail per change. Common for orgs where PMs author flag intent but engineers / SREs gate production.
- **When to use:** Customer needs PM-vs-engineer access separation, or per-environment governance (production requires approval, dev does not), or compliance audit trail.
- **Docs:** https://launchdarkly.com/docs/home/releases/approvals
- **Common confusions:** Approvals govern flag-change workflows; Custom Roles govern user-permission RBAC. They pair: Custom Roles defines who can request, Approvals defines who must approve.
- **Related products:** Custom Roles, Workflows (Workflows can include approval gates per stage).
- **Pricing tier:** Pro / Enterprise.

### Custom Roles (RBAC)

- **One-line:** Granular role-based access control; per-resource and per-action permissions.
- **What it solves:** Move beyond LD's built-in roles (Admin / Writer / Reader) to define custom roles for specific personas (e.g., "PM with read-write on feature flags but read-only on segments and no production approval rights"). Common requirement for orgs with mixed PM-engineer-CSM access.
- **When to use:** Customer requires non-technical PM experience, CSM view-only access, or eng-only production write access. Standard for any 50+ person org buying LD.
- **Docs:** https://launchdarkly.com/docs/home/account/custom-roles
- **Common confusions:** Custom Roles is granular permissions; Approvals is workflow-level review gates. They complement each other.
- **Related products:** Approvals.
- **Pricing tier:** Enterprise.

### Release Pipelines

- **One-line:** End-to-end release management combining Workflows, Guarded Releases, Approvals, and progressive rollouts into a structured process.
- **What it solves:** Author a complete release process once (per-stage targeting + metric gates + approvals + Slack notifications + cohort schedules) and reuse it across flags. The "end-to-end rollout management in one platform" surface.
- **When to use:** Customer wants templated release governance across many flags. Especially valuable when current state is "manual PM intervention per phase per flag" (Acme Corp pattern).
- **Docs:** https://launchdarkly.com/docs/home/releases (umbrella page; combines the above)
- **Related products:** Workflows, Guarded Releases, Approvals, Custom Roles.

### o11y (Observability)

- **One-line:** Native observability suite: error monitoring, logs, traces, session replay.
- **What it solves:** Tie production observability directly to flag changes. See errors, traces, logs filtered by which flag variation a user received. Session replay scoped to flag-targeted users.
- **When to use:** Customer doesn't have separate observability tooling, or wants flag-aware observability that bolts cleanly to LD.
- **When NOT to use:** Customer is heavily invested in Datadog / New Relic / Grafana already; layer LD on top via integration rather than displace.
- **Docs:** (Check current LD docs URL for o11y.)
- **Common confusions:** LD's o11y is flag-aware observability; not a Datadog replacement.
- **Related products:** Datadog integration, Guarded Releases (metrics surface).

## Integrations

### Slack

- **What it does:** Notifications on flag state changes, approval requests, Guarded Release auto-rollback events, segment changes.
- **Docs:** https://launchdarkly.com/docs/integrations/slack/notifications
- **Customer use:** CSM / GTM teams gain visibility on rollout transitions; PMs notified on approval requests; SREs notified on auto-rollback events.

### Datadog

- **What it does:** Bidirectional integration. LD events flow to Datadog (correlate flag changes with incidents in their existing observability). Datadog metrics flow to LD (Guarded Releases can use Datadog metrics for auto-rollback decisions).
- **Customer use:** Acme Corp is Datadog-instrumented; Globex is Datadog APM + LLM o11y; integration positioning matters when customer is Datadog-heavy.

### Salesforce

- **What it does:** Customer / account / opportunity data flows from Salesforce into LD; segment definitions can be authored against Salesforce attributes (account tier, plan, region, owner).
- **Customer use:** Acme Corp example: 8 customer cohorts based on payment type sourced from Salesforce.

### Snowflake

- **What it does:** Product usage data and customer attribute warehouse data flow into LD; segments can be authored against Snowflake-derived attributes.
- **Customer use:** Acme Corp uses Snowflake for product usage data; segments derived from Snowflake.

### GainSight

- **What it does:** CSM context (account health, customer success metrics) flows into LD for flag targeting and segment definition.
- **Customer use:** Mid-market and enterprise customers with mature CS function.

### Native MCP Server

- **What it does:** LaunchDarkly MCP server enables Claude / agentic AI to query LD state and propose flag changes via the natural-language interface.
- **Customer use:** Customers building agentic workflows want LD as a reachable tool for AI orchestrators.

## Competitive Positioning Summary

(Detailed competitor entries can grow over time as `/sales-summarize-account` extracts encounter signal. Current high-level shapes:)

### Statsig
- **Where they're strong:** Modern UX, native experimentation depth, fast shipping velocity, founder-momentum brand.
- **Where LD wins:** Flag delivery network at enterprise scale, per-fact ACL, mature enterprise compliance (SOC 2, FedRAMP), breadth of release-management capabilities (Workflows, Guarded Releases, Approvals).
- **Common deal scenarios:** Statsig often surfaces in early-stage / engineering-led evaluations. Larger orgs evaluating both typically pick LD on substrate / compliance.

### Eppo
- **Where they're strong:** Warehouse-native experimentation (Snowflake-first), data-team-friendly model.
- **Where LD wins:** Native flag platform with SDK-based delivery; Eppo is experimentation-only and requires a separate flag system.
- **Common deal scenarios:** Eppo competes in experimentation evaluations specifically. Often Globex-shape orgs surface Eppo as the data-team's preferred experimentation tool.

### GrowthBook
- **Where they're strong:** Open-source story, low-friction adoption, free tier.
- **Where LD wins:** Enterprise compliance, SDK delivery network maturity, breadth of advanced features.

### Optimizely
- **Where they're strong:** Long-tenured market presence, marketing-team UX, content + experimentation suite.
- **Where LD wins:** Engineering-grade flag delivery, modern API, AI Configs.
- **Common deal scenarios:** Customers migrating off Optimizely after marketing-tool focus didn't fit engineering needs.

### Harness.io
- **Where they're strong:** Combined CI/CD + feature flags story, single-vendor consolidation pitch.
- **Where LD wins:** Specialized flag platform (deeper feature surface), better SDK breadth, more mature enterprise.

### Homegrown systems
- **Where they're strong:** Already exists; sunk cost. Tailored to customer's exact patterns. No procurement or vendor-management overhead.
- **Where LD wins:** Flag delivery network reliability, user context streaming, real-time metrics for auto-rollback, advanced release management (Workflows, Guarded Releases, Approvals), ongoing investment vs maintenance burden.
- **Common deal scenarios:** Acme Corp, Wayne Enterprises, Massive Dynamic — all homegrown FF systems with the same gating concern: migration effort. Counter-pattern: SDK-first gradual migration starting with one new high-value initiative.

### LangFuse / LangSmith / Braintrust / Arize / Azure Foundry Evals
- **Where they're strong:** AI-eval-native, deep prompt management depth, integrated with various foundation labs.
- **Where LD wins:** AI Configs ties prompt + model versioning to LD's flag delivery + Guarded Releases auto-rollback, so AI feature delivery sits on the same substrate as feature delivery generally. Customers running both feature flags and AI features can consolidate.
- **Common deal scenarios:** Globex is evaluating Azure Foundry evals + Datadog LLM o11y as alternatives to AI Configs. Initech is evaluating AI Configs against existing in-house options.

## Common Confusions Index (Cross-Product)

Quick lookup for customer-confusion patterns. Used by `/sales-pov`, `/sales-meeting` prep, `/sales-exec-summary`.

| Customer phrase | Likely meaning | What to clarify |
|---|---|---|
| "We want workflows for our rollouts" | Likely Workflows (scheduled progression) AND Guarded Releases (metric gate per stage) together. Customers often conflate. | Walk through both; explicit "Workflows handles cadence; Guarded Releases handles safety per stage." |
| "We want auto-rollback" | Guarded Releases. | Confirm whether metric-driven (Guarded Releases) or human-triggered (Approvals workflow). |
| "We want experimentation" | Could be Experimentation (statistical) or just Guarded Releases (metric comparison). | Probe: do they want statistical significance + variant testing, or just rollout safety? |
| "We want AI Configs" | AI Configs (prompt + model versioning + AI evals). NOT generic config management. | Confirm AI feature delivery is the use case, not generic feature flags. |
| "Prerequisite flag dependencies" | Currently a roadmap-confirmed gap in LD UI. | Acknowledge, surface roadmap timeline, position as confirmed future work. |
| "We want a hybrid model: keep our flag backend, use LD for management" | Acme Corp-shape proposal. LD does not support this long-term. | Walk through SDK-first migration alternative; preserve customer's low-risk on-ramp without forfeiting delivery network + advanced features. |

## Maintenance

- This file is the canonical source. Other skills read it; they do not mutate it.
- `/sales-summarize-account` writes candidate updates to `learnings.md`, NOT here.
- `/sales-review-learnings` is the human-in-the-loop promotion surface; promoted entries get edited into this file.
- When a product or capability sunsets, update its `status` field and add a `successor` cross-reference; do not delete entries.
- Quarterly review recommended: walk through each product, verify doc URLs still resolve, confirm pricing tiers, refresh competitive positioning if any competitor has shifted.
