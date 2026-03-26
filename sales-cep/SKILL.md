---
name: ld-cep
description: Analyze deal stage based on LaunchDarkly's Customer Engagement Process (CEP). Compares completed and missing activities against stage criteria to recommend the correct opportunity stage.
---

# CEP Stage Analysis

Analyze a deal's actual stage based on what has and hasn't happened, using LaunchDarkly's Customer Engagement Process (CEP). Outputs a stage recommendation with evidence.

## Arguments

- `account`: Account name to analyze (required)

## Instructions

### Step 1: Read Account Data

Read the account file at `{vault_path}/{company_folder}/Accounts/{account}/{account}.md`.

Extract:
- Current Salesforce stage (from SF Updates or frontmatter)
- MEDDPICC section (all fields)
- Deal Ledger (chronological history)
- Meeting notes list (scan meetings/ folder)
- Business Context
- Next call info

Also read the most recent 3-5 meeting summaries to understand what has actually happened.

### Step 2: Evaluate Against CEP Stages

Compare the account's actual activities and evidence against each stage's requirements below. A deal belongs in the **highest stage where all prior exit criteria are met**. Specifically: if Stage 1 exit criteria are all met, the deal is in Stage 2 (working toward Stage 2 exit criteria). If Stage 2 exit criteria are also met, the deal is in Stage 3, and so on. The recommended stage is where the deal currently lives and is working, not the stage it has already completed. If Salesforce shows a higher stage than evidence supports, the deal is overstaged.

### Step 3: Write the Stage Analysis

Add or update a `## CEP Stage Analysis` section in the account file, positioned **above** `## MEDDPICC`. Keep it concise.

Format:

```
## CEP Stage Analysis

**Recommended: Stage {N} - {Name}** | SF: Stage {N} - {Name} | {date}
Tech Validation: {Type} / {Status}

**Key Risks:**
- {Risk} (Stage {N})

**Completed:**
- {Short activity} (S{N})
- {Short activity} (S{N})

**Not yet completed:**
- {Short activity} (S{N})
- {Short activity} (S{N})
```

Rules:
- **Bullet points must be short**: 5-10 words max per bullet. Use fragments, not full sentences. "Custom demos delivered (S1)" not "Delivered custom demo(s) aligned to multiple use cases across platform, experimentation, and guarded releases (Stage 1)"
- Use "S1", "S2", etc. as shorthand for stage numbers
- **Key Risks** section goes first, before Completed and Not yet completed. This is the most important section. Risks are especially critical when the deal is overstaged (SF stage ahead of CEP recommendation). Include: missing exit criteria for the current SF stage, stalled activities, missing stakeholder engagement, timeline risks.
- If correctly staged with no major risks, Key Risks can be omitted
- List 4-6 completed items, 3-5 not-yet-completed items
- Focus on SE-relevant activities but include visible AE activities

### Critical: POV Gate for Stage 3

**A deal CANNOT be in Stage 3 (Tech Validation) unless a POV/trial has actually started.** If the deal is still scoping the POV, planning success criteria, or waiting for the customer to begin, it belongs in Stage 2 regardless of what Salesforce says.

The only exception is a deal that **skipped POV entirely** and moved directly to Stage 4 (EB Approval). This is valid when the customer commits to purchase based on demos and business value alone, without requiring technical validation. In this case, the Tech Validation Type in Salesforce should be "Skipped."

If a deal is in Stage 3+ in Salesforce but has NOT started a POV and has NOT skipped POV, flag this as **overstaged (RED)** in the assessment. The assessment should explicitly state: "Deal is overstaged: Stage 3 requires an active POV. Current status is still POV scoping/planning, which is Stage 2."

### Tech Validation Fields

When writing the CEP Stage Analysis, also recommend values for these Salesforce fields (include in the output):

**Tech Validation Type** (`Evaluation_Type__c`): Allowed values:
- `Deep Dive Demo`: Technical deep-dive demos beyond initial custom demo
- `Guided POV`: Structured proof of value with defined success criteria and SE involvement
- `Self-Guided Trial`: Customer-led evaluation with minimal SE support
- `Skipped`: No formal technical validation, moved to commercial based on demos/value alone
- `Workshop`: Hands-on technical workshop (implementation planning, architecture review)
- `Stalled`: POV/evaluation started but stalled or went inactive

**Tech Validation Status** (`POV_Status__c`): Allowed values:
- `Planning`: POV scoped but not started
- `In-Progress`: POV actively running
- `Extended`: POV ran past original timeline
- `Completed`: POV finished (passed or failed)

Add these to the output format:

```
**Tech Validation:** {Type} / {Status}
```

---

## CEM + CEP Overview

The CEP (Customer Engagement Process) is the visual guide the field uses day-to-day: clear stages, clear ownership, clear outcomes, an end-to-end guide for how pipeline is created, advanced, and closed. The CEM (Customer Engagement Model) is the operating manual behind it: how teams coordinate across marketing, PLG, sales, and post-sales; how handoffs, signals, and systems fit together; why roles change at certain moments; what "good" looks like across the full customer lifecycle.

---

## Pre-Pipeline Stages

### Lead Gen: Targeting

**Customer state:** Customer may not yet know they have a problem LaunchDarkly solves. The account is identified as ICP-aligned, shows relevant signals, and fits a value hypothesis worth pursuing.

**Entrance Criteria for Productivity:**
Do not pursue deeper account research until rep has checked: employee size, engineering maturity, industry relevance, relevant partner technology stack. Do not proceed unless the account is being intentionally prioritized (by marketing, sales opps, territory logic, etc).

**Account Research Priorities:**
- Validate account ownership (segment, geo, territory, parent/child hierarchy) using ROE logic
- Review historical inbound/outbound activity to avoid ROE violations
- Identify intent or behavior signals (6sense intent stage, Zoominfo intent, Pocus ICP scoring, website activity, previous Marketo engagement like MQLs/PQLs)
- Tier the account appropriately and determine prioritization within the PG plan
- Develop initial POV hypothesis linked to a Value Driver
- Map likely buying teams and early personas (Engineering → Platform → DevOps → Product)
- Use existing relationships in AWS, ISV Partners or Consulting Partners to validate ICP fit and test for pain
- Identify potential networking opportunities (executive connections, partner-known contacts)

**Handoffs:**
- SDR to SDR handoff due to ROE with inbound before outreach (e.g., ROE GEO or if another rep already had activity in the last 30 days)

**Critical Handshakes:**
- AE, SDR, and CSM/TAM align on priority accounts, account tiering, target personas, value hypotheses, relevant signals, and known risks/expansion indicators
- CSM/TAM provides insights for existing customers (usage patterns, activation gaps, known challenges, historical context)

**Exit Criteria:**
- ICP fit confirmed (segment, territory, engineering profile, hierarchy validated, partner technology)
- SFDC account hygiene complete (domain, hierarchy, address, territory, engineering count)
- ROE validations complete (proper ownership, no open opportunity conflicts)
- For outbound: initial POV hypothesis documented, account added to PG plan and tiered appropriately
- Customer provides any form of engagement (response to outreach, inbound form fill, chatbot interaction, cold call dialogue)

**Internal References:** Tiering documentation, Value Framework + Proof Matrix, account hierarchy + Ultimate Parent, 6sense signals / Pocus ICP scoring, existing CSM/TAM insights, product usage data and contract data (if expansion), partner data, PLG trial intel from Vital Statistics, historical inbound/outbound activity logs.

**External Assets:** Customer stories, light POV-oriented marketing assets (from PG Deck), industry-specific one-pagers, relevant case studies aligned to value driver hypothesis.

### Lead Gen: Engagement

**Customer state:** Customer has provided some form of engagement (reply to outreach, inbound submission, chatbot interaction, cold call response). Goal is for customer to become aware of LaunchDarkly and begin exploring whether the identified problem is worth a meeting.

**Account Research Priorities:**
- Validate and refine POV hypothesis based on early interactions and signal data (Pocus, Marketo, 6sense)
- Test and adjust messaging based on what resonates; create Outreach sequences/templates as needed
- Identify likely champion pathways and assess persona influence
- Determine which teams or business units show interest or alignment
- Review customer health and usage patterns for expansion motions
- Continue mapping additional relevant personas surfaced through early interactions

**Handoffs:**
- Marketing → SDR: For MQLs, Direct Requests, webinar leads, event follow-up (agreed-to-engage threshold dependent on DR/MQL/PQL)
- SDR → AE: When meeting with AE is booked, ownership of progression transfers. SDR also transfers calendar ownership, opp ownership, and connects lead to AE via email
- CSM → AE: When CSM uncovers new customer pain during a call that warrants pre-sales qualification

**Critical Handshakes:**
- SDR + AE co-own engagement until opportunity is created and meeting accepted
- Marketing, SDR, and AE align on campaign messaging, target personas, and lead context for inbound
- CSM and AE align on expansion targeting, customer usage trends, risks, and relevant stakeholders

**Exit Criteria:**
- Correct AE assigned per ROE (territory, segment, hierarchy)
- SDR has dispositioned lead correctly (Working, Recycled, Current Customer) and followed inbound SLAs
- POV direction + target persona confirmed by AE based on early engagement
- Opportunity created only when: first meeting with AE booked and calendar invite accepted by prospect, OR CSM identifies real and actionable pain on a customer call
- First Meeting Plan drafted by AE

**Internal References:** Tiering documentation, ROE rules, lead/contact dispositioning guidelines, signal dashboards, CSM/TAM notes, account history.

**External Assets:** Discovery (First Meeting) Deck, relevant customer stories, high-level platform overviews, industry/value-driver one-pagers.

### PG: Qualification

**Customer state:** Customer participates in a first live conversation and validates that they have a meaningful problem worth evaluating. Customer should leave aligned to next steps in Discovery or Stage 1.

**Account Research Priorities:**
- Validate and refine the POV built in Targeting and tested during Engagement
- Understand the organizational context behind the problem (roles, workflows, ownership, interdependencies)
- Confirm which teams or business units are directly impacted by the pain
- Assess urgency and readiness: why this matters now
- For expansion: analyze product usage, health, risks, and activation gaps
- Leverage SDR and CSM research inputs

**MEDDPICC Priorities:**
- Identified Pain (REQUIRED): Move from initiative value hypothesis to improved hypothesis with pain context
- Champion (Optional): Identify early indicators of who cares and has influence
- Optional (only if surfaced): Metrics, Decision Process, Competition
- Not required: Economic Buyer, Decision Criteria, Paper Process

**Handoffs:**
- SDR → AE: Triggered when meeting with AE is booked and ROE/territory validation is complete. SDR converts lead to contact, opens opportunity, attaches notes, confirms ICP fit. AE must move to disco or DQ within 24 hours
- CSM → AE (Expansion): Triggered when CSM uncovers new pain. CSM logs context and First Meeting Date; AE assumes ownership

**Critical Handshakes:**
- SDR ↔ AE: Continue coordinated multithreading until Stage 1. SDR should attend the call. Post-call, align on identified area and team to multithread into
- CSM ↔ AE: CSM provides usage insights, risks, account history, stakeholder intel
- AE ↔ SE (as needed): Align early if technical validation will influence Discovery or demo plan

**Exit Criteria:**
- Identified Pain validated and documented in SFDC
- Potential Champion identified (early signals) and captured in SFDC
- AE documents qualification outcome within 48 hours: Move to Discovery, Disqualify, or Mark as Duplicate
- Next Step confirmed with customer and logged in SFDC
- Contact Roles updated for all attendees and known influencers

**Internal References:** Sales Asset Folder, First Meeting Plan, Value Framework, Proof Matrix, Deal Deck, org chart and historical activity, MEDDPICC hygiene guidelines, usage and health insights (expansion).

**External Assets:** Call recap email, security/compliance docs (only when requested), early customer stories or POV summaries, Deal Deck with Platform Narrative, one-pagers by pain/use case, short explainer videos (~90 sec), use-case-aligned case studies and proof points.

### PG: Discovery

**Customer state:** Customer works with LaunchDarkly to validate the problem, clarify desired outcomes, and align on the need for a custom demo. Customer should leave confident that LD understands their situation and has a relevant, differentiated approach.

**Account Research Priorities:**
- Clarify desired outcomes and what "better" looks like
- Validate the Before Scenario and Negative Consequences (pain tied to measurable or experiential impact)
- Understand technical landscape: repos, governance, deployment workflows, partner technology and integration points
- Determine use-case scope for custom demo and/or technical validation
- Identify cross-functional stakeholders (technical + business) for demo, validation, or decision making
- Understand if customer uses DevOps consultancies, SIs, or contractors for development and centralized procurement (resellers)
- Research if expansion was through a reseller for early involvement and pricing wariness
- Refine org chart based on new Discovery insights
- For expansion: gather precise usage context, gaps, and cross-team dependencies

**MEDDPICC Priorities:**
- Identified Pain (REQUIRED): Validated, clarified, and when possible quantified (progression from Qualification)
- Champion (REQUIRED): Confirm potential technical champion(s), their influence, and engagement in shaping use cases or demo criteria. Continue to test and keep updated through deal cycle
- Metrics (REQUIRED IF KNOWN): Early indicators of success metrics (release velocity, error budget risk, experiment throughput, operational consistency). Formal modeling occurs later in Stage 2 with BVA
- Competition (OPTIONAL IF SURFACED): Known competitors or homegrown approaches
- Initial Decision Process (OPTIONAL): Early signals of evaluation process
- Not required: Economic Buyer, formal Decision Criteria, Paper Process

**Handoffs:** None. AE remains primary owner.

**Critical Handshakes:**
- AE ↔ SE: SE Assignment Request initiated after Identified Pain, Before Scenario, and Negative Consequences are completed in SFDC. AE + SE co-build demo plan. Early technical validation questions aligned prior to custom demo
- SDR ↔ AE: SDR continues multithreading until Stage 1. AE validates personas surfaced by SDR
- CSM ↔ AE (Expansion): CSM provides customer context (usage patterns, adoption, risks, stakeholder dynamics)

**Exit Criteria:**
- Discovery completed and documented in SFDC
- Custom demo scheduled and on calendar
- MEDDPICC updated: Identified Pain (validated and quantified), Champion (potential)
- Primary Product Line selected in SFDC
- iARR estimate added
- Contact Roles updated for all attendees and known influencers

**Internal References:** Pre-call planner, Sales Asset Folder, org chart, prior Qualification notes, Discovery notes and technical notes, SE technical validation checklist, MEDDPICC hygiene, customer product usage/health metrics (expansion).

**External Assets:** Deal Deck with Platform Narrative, POV hypothesis (refined), best practices and enablement materials, demo preparation materials, technical guidance documents, one-pagers by pain/use case, short explainer videos (~90 sec), use-case-aligned case studies and proof points.

---

## CEP Stage Definitions (Pipeline Starts → Closing)

### Stage 1: Validate Fit

**Customer state:** Customer confirms that LaunchDarkly is a credible solution to their problem and agrees to move into deeper value validation and technical exploration. Customer leaves aligned on proposed future state and confident LD can support their use cases.

**Account Team activities:**
- Deliver custom demo(s) aligned to use cases
- Confirm future-state alignment: ensure customer understands how LD addresses pain and delivers outcomes
- Understand technical fit: validate repo structure, deployment workflows, governance model, integration expectations
- Refine org chart with technical leaders, architects, operational stakeholders and potential external consultancies
- Identify dependencies (DevOps ownership, platform constraints, release workflows)
- Assess scaling implications and Phase 1 vs Phase 2 rollout
- Confirm ARR estimate accuracy, refining CPQ draft from Discovery
- Identify and position against competition
- Prepare for potential co-sell motions with partners (AWS, SI/Consulting/ISV)
- Check reseller status: if expansion with current customer or renewal, check past history for reseller pricing structure. Resellers own pricing and there are legal implications (do not discuss pricing directly)
- If opp is reseller-sourced (NB or expansion), pricing may only be shared through a partner
- AE + SE align on technical qualification
- Position deeper/tech value dives
- For Large Enterprises: start to identify governing bodies, CAB or ARB

**MEDDPICC Priorities:**
- Metrics (REQUIRED): Validate customer's measurable success criteria (velocity targets, error budget improvements, performance requirements)
- Identified Pain (REQUIRED): Reconfirm pain from Discovery is tied directly to POV criteria and future-state solution. Validate pain is aligned to real business outcome with compelling timeline
- Champion (REQUIRED): Confirm technical champion(s), influence, and involvement in demo follow-up and validation
- Competition (REQUIRED IF PRESENT): Position against homegrown or competing tools with clear differentiation
- Not required: Economic Buyer, Decision Criteria, Paper Process (appear in Stage 2)

**Handoffs:** None. AE retains full ownership.

**Critical Handshakes:**
- AE ↔ SE: AE shares all previous knowledge needed for effective custom demo (Command of Message must be filled out). Deliver custom demo, validate technical feasibility and use-case viability, align on technical risks and success criteria
- AE ↔ Partner (SI/ISV): Validate or strengthen Champion alignment, gather competitive and technical insights, confirm partner-led use cases (e.g., Snowflake for experimentation), understand SI/consulting partner roles in SDLC
- AE ↔ CSM: Gather context for onboarding assumptions based on demo outcomes, align on expected customer constraints or implementation resources
- AE ↔ BVC (as needed): Engage early business value modeling if required for Stage 2 planning

**Exit Criteria:**
- Custom demo delivered to relevant stakeholders
- Customer confirms alignment with proposed future state
- ARR added to opportunity (must be completed when entering Stage 1), factoring in reseller margin if applicable
- MEDDPICC updated: Metrics, Champion, Competition (if surfaced)
- Contact Roles updated for all attendees and known influencers
- iARR estimate refined

**Internal References:** CoM (Mantra) and POV criteria, competitive positioning, technical validation checklists, prior Discovery notes, org chart and stakeholder map, Sales Asset Folder, persona cheat sheets (EB, Dev, Security).

**External Assets:** Simplified platform overview (deck or one-pager), technical architecture diagrams, demo summary material, product/use-case one-pagers, "What is LaunchDarkly" with high-level architecture, best practices for future-state release model (flag structure, lifecycle, targeting).

### Stage 2: Business Value

**Customer state:** Customer seeks to validate the business value and confirm the solution is worth advancing toward an EB Go/No-Go decision. Customer leaves with clear understanding of expected ROI, business justification, and evaluation plan.

**Account Team activities:**
- Validate pain and metrics tied to business outcomes via key meetings or workshops with Champion(s)
- Assess business pain severity and validate alignment with LD's value drivers (velocity, risk reduction, performance, experimentation) using 3 Whys from Command of the Message or a BVA
- Further map stakeholder roles: EB, Champion, Architect, procurement, finance
- Identify constraints impacting business justification (compliance, budget cycles, procurement gates)
- Prepare early onboarding considerations to shape timeline and value realization expectations
- Co-sell with AWS to gain account intelligence, Marketplace preferences, insight on strategic initiatives
- Identify and engage EB: align on POV requirements, success criteria, scope, timelines, and BVA (or 3 Whys)
- Clarify decision process and approval path
- Strengthen Champion(s) and co-create MAP
- Align AE + SE on tech validation plan: POV scope, environments, access requirements, test data, success criteria, timeline
- Agree on what "technical win" looks like and how it will be demonstrated
- Address security, compliance, and architectural concerns in advance
- Set up AWS co-sell call (for opps >$30K with High AWS Engagement score, triggered automatically)
- Engage services for all deals over $30K for value acceleration
- Initiate SI/ISV joint pursuit as applicable
- Engage BVA consultants for formal process on deals above $150K
- Understand strategic priorities (AI initiatives, modernization, cloud migration, governance)

**The 3 Whys:**
1. **Why Change:** Why should the customer do anything at all? Focuses on business problem, pain, or missed opportunity. Quantifies the cost of the status quo.
2. **Why Now:** Why does this need to be addressed now vs later? Introduces urgency using business impact over time, risk, market changes, competitive pressure, or internal initiatives. Highlights cost of delay.
3. **Why You:** Why should they solve this with LaunchDarkly specifically? Differentiates based on unique capabilities, proof points, expertise, and outcomes tied to their priorities.

**MEDDPICC Priorities:**
- Metrics (REQUIRED): Validate and quantify success metrics tied to rollout (velocity, error budgets, performance KPIs, experimentation pace). Informs BVA
- Economic Buyer (REQUIRED): Identify EB, understand priorities, secure alignment on what they need for Go/No-Go
- Decision Process (REQUIRED): Clarify what must happen before EB or Finance approves (security, architecture review, procurement, legal milestones)
- Identified Pain (REQUIRED): Reconfirm pain in business context, connect to ROI levers
- Champion (REQUIRED): Empower champion to co-deliver value narrative and influence EB evaluation
- Competition (REQUIRED): Position against internal tooling or external vendors; reinforce differentiation through POV alignment and champion insights
- Not required: Paper Process (belongs in Stage 4-5)

**Handoffs:** None. AE retains ownership.

**Critical Handshakes:**
- AE ↔ BVC: Co-build BVA (ROI modeling, before/after analysis), refine business justification narrative for EB consumption
- AE ↔ SE: Align on POV scope, environments, access requirements, test data, success criteria, and timeline. Agree on what "technical win" looks like. Address security, compliance, and architectural concerns. Finalize technical evaluation sequence and timeline, confirm with champion who should be involved
- AE ↔ PS: Services positioned for opportunities >$30K
- AE ↔ AWS: For opportunities >$30K with High AWS Engagement score, prep co-sell call slide and align on opportunity
- AE ↔ CSM: High Touch CSMs attend all calls with current customers in direct partnership with current state and related prior success plans
- AE ↔ Exec Sponsor: Prepare internal LD executive for EB meeting, validate message alignment for strategic influence

**Exit Criteria:**
- Economic buyer POV Go/No-Go meeting happened
- Business justification confirmed and POV planned and timed
- Key stakeholders documented in SFDC (Champion, EB, Architect)
- MAP (Mutual Action Plan) drafted with aligned milestones
- iARR estimate refined

**Internal References:** BVA modeling, technical validation plan (POV plan), MEDDPICC notes, competitive traps and positioning tools, internal exec briefing templates, Success Plan framework, partner (AWS, SI/ISV) guidance (co-sell deck).

**External Assets:** Exec Buy-In deck, POV Plan and Success Criteria, BVA/ROI tooling (calculator, value summary template), "Three Whys" / challenge definition framework, value workshop materials and champion-facing value slides.

### Stage 3: Technical Validation

**Customer state:** Customer technically validates the LaunchDarkly solution. Customer verbally confirms tech fit.

**Account Team activities:**
- Execute technical validation against agreed success criteria
- Validate required capabilities, integrations, security, and architecture
- SE takes the lead on running technical validation: access, test data, environments, SDKs, integrations, POV execution, reverse demos, validation check-ins, until clear "technical win" against agreed success criteria (standard is 2 weeks)
- AE retains commercial ownership and coordinates business-side stakeholders
- Validate security, compliance, and architectural requirements in customer's environment
- Complete required reviews and approvals (security questionnaires, data flow reviews, architecture sign-off)
- SE provides clear technical recommendation and status (Win, Gaps, Risks) for AE to carry into Stage 4+
- Align ROI narrative with POV outcomes
- AE conducts business value justification discussions with supporting resources (e.g. BVA) and integrates technical wins into BVA review with Champion
- Advance procurement, security, and legal workflows
- Prepare for and schedule EB Go/No-Go
- Assess change management requirements
- Start CPQ quoting ahead of pricing discussions: define and document SI quote process
- Align with CSM/PS on implementation assumptions, realistic pilot implementation plan, scaled onboarding approach and success milestones (especially for multi-team or global rollouts)
- Engage Deal Management early on non-standard deals; avoid giving pricing info not validated by Deal Management
- Begin quoting preparation process in CPQ; review pricing and deal structure on all non-standard + complex deals
- Request customer references via Salesforce workflow (submit form with prospect details, timeline, use case)
- Identify EB; align on POV requirements, success criteria, scope, timelines, and BVA (or 3 Whys)

**Trial Notes:**
- SEs initiate trial accounts for NB customers (via Re-tool; customer receives email and must accept)
- AEs initiate expansion trials (via SFDC)
- AEs request trial extensions beyond initial 14 days via SFDC workflow (up to 14 days = manager approval; past 14 days = SE manager approval)
- Support: #ask-trials in Slack

**MEDDPICC Priorities:**
- Metrics (REQUIRED): Validate success metrics tied to rollout, error budgets, performance
- Economic Buyer (REQUIRED): Identify EB and their POV requirements
- Decision Criteria (REQUIRED): Technical fit, compliance, architecture validation
- Decision Process (REQUIRED): What needs to happen before EB/finance buys in
- Paperwork (REQUIRED): Document requirements surfaced early (security, contracting implications, resellers and margin, marketplace)
- Identified Pain (REQUIRED): Validate and connect to POV criteria
- Champion (REQUIRED): Confirm technical champion(s) and their ability to influence
- Competition (REQUIRED): Position against homegrown or other tools

**Handoffs:** None. AE retains ownership.

**Critical Handshakes:**
- AE ↔ SE: SE leads technical validation end-to-end. AE retains commercial ownership
- AE ↔ Business Value: Integrate technical wins into BVA review with Champion
- AE ↔ CSM/PS: For complex implementations or expansions, align on implementation assumptions, pilot plan, success milestones
- AE ↔ Partner/AWS: Align on technical and joint use cases if partner involved. Account for reseller margin. Denote if deal via AWS Marketplace using checkbox on Opp
- AE ↔ Champion/EB: Stay aligned through email and live check-ins. Clear recap emails summarizing what was tested, what passed, open issues, next milestones. Key agreements in MAP
- AE ↔ Deal Management: Engage early on non-standard deals. Begin CPQ quoting. Review pricing and deal structure
- AE ↔ Customer Reference Manager: Request via Salesforce form. Customer Marketing matches, CSM notified, call scheduled

**Exit Criteria:**
- Tech accept agreed upon by champion
- CoM complete with tech differentiation narrative
- Primary quote in approved status
- LD ID added to the opp

**Internal References:** Prior discovery notes (pain, metrics), full MEDDPICC hygiene, customer architecture/SDK landscape/governance requirements, expansion or risk signals from TAM/CSM, competitive posture, champion reference request, BVA summary, quote and pricing structure.

**External Assets:** POV kit (POV deck, planning template, tracker, success criteria), architecture diagrams and SDK guidance, security and compliance documents, best practices (flag structure, lifecycle, targeting), CoE and scaling frameworks, architecture/SDK/data-flow diagrams (incl. reference architectures), realistic demos/sample apps/GitHub repos, technical workshops/best-practice guides/validation playbooks.

### Stage 4: Executive Buyer Approval

**Customer state:** Customer decision and commercial approvals. EB provides final approval and the customer gains commercial acceptance.

**Account Team activities:**
- Champion co-leads EB Go/No-Go meeting
- Align on Close Plan and agreed-upon milestones
- Review services scope (PS, RSA), onboarding, and future-state delivery plan
- Finalize negotiation non-starters and trade-offs
- Align on exec sponsor involvement after signature
- Deal Desk confirms pricing/proposal structure, order form structure
- AE aligns with customer on proposal structure, pricing strategy, discounts, contract timing, reseller involvement
- Ensure AWS Co-Sell Call is complete
- Confirm if reseller/marketplace will be used; check previous deals for reseller involvement and engage partner team for reseller margin
- AE secures confirmation from customer on commercials and sends order form and LSA
- AE secures confirmation that vendor onboarding and legal review begin
- AE reviews commercials with Champion in prep for EB alignment and sign off on pricing
- AE coordinates sending and reviewing order form, pricing, discounts, and approvals before executing final OF
- After EB alignment and order form sent, AE coordinates with champion and procurement to kick off vendor onboarding and legal review
- Work plan built into a close plan (path to close)
- AE submits and manages Deal Management and Legal requests via SFDC Cases (Case Chatter is primary internal communication channel)
- AE aligns early with Legal on fallback positions, negotiation thresholds, and redline strategy
- Partner with Legal to position LSA as purpose-built for SaaS, multi-tenant model
- AEs should consult deal management on reseller agreements and pricing before sharing externally
- CSM assignment triggered via #feed-csm-account-assignment-stage4 channel

**MEDDPICC Priorities:**
- Metrics (REQUIRED): Quantified business case (BVA, before/after, risk reduction)
- Economic Buyer (REQUIRED): Live in this stage; EB must echo value narrative
- Decision Criteria (REQUIRED): Strategic, financial, operational criteria validated
- Decision Process (REQUIRED): Defined steps to procurement and finance approval
- Paperwork (REQUIRED): Understand contract expectations before entering Stage 5
- Identified Pain (REQUIRED): Tie all messaging back to original pain → champion POV
- Champion (REQUIRED): Activated to co-deliver EB story
- Competition (REQUIRED): Trap-setting complete; clear differentiation established

**Handoffs:** None. AE retains ownership.

**Critical Handshakes:**
- AE ↔ CS/TAM: Early onboarding expectations, success criteria, and rollout assumptions scoped to validate feasibility and prepare for post-signature
- AE ↔ PS/RSA: Scoping services support and timeline agreed upon; RSAs introduced to customer
- AE ↔ Exec Sponsor: Align on EB personas, decision dynamics, value levers, messaging tone. Exec Sponsor briefed on talking points
- AE ↔ SE: Confirm final technical validation details needed for EB conversations (performance, governance, compliance, integrations). Champion supports via prep. SE documents any remaining risks
- AE ↔ Deal Management: Align on proposal structure, pricing strategy, commercial requirements, discounts, timing. Check previous deals for reseller involvement. Ensure DM aware of pending redlines on LSA/DPA/BAA. Confirm final pricing, discounts, CPQ configuration, OF structure. Coordinate OF and SoW changes via SFDC Cases only when required
- AE ↔ Legal: Align early on fallback positions, negotiation thresholds, redline strategy
- AE ↔ AWS/Partner: Align on deal, share account intelligence, work toward joint win. Confirm existing partner framework or net-new agreement. If working through reseller, all pricing routed through them directly
- AE ↔ Business Value: BVC provides BVA materials to LD Exec Sponsor or prep coach/champion at customer

**Exit Criteria:**
- EB Go/No-Go meeting complete
- Primary quote in approved status
- LD ID added to the opp

**Internal References:** BVA results/ROI modeling/CoM summary, tech validation success evidence, competitive traps and narrative, internal approval thresholds (discount, term, PS scope), Mutual Action Plan (Close Plan), final POV summary and success criteria recap, feature/function gaps noted during POV, booking checklist.

**External Assets:** Executive Buy-In deck, POV playback/executive readout deck, BVA summary (business justification), future state architecture, MAP and Close Plan, services scope documentation (PS/RSA), quantified POV results and business value summary, "Why LD vs homegrown/competitors" executive comparison, executive-ready case studies and proof matrices, Service Connection sizing and pricing explanation docs, pricing plug-n-play template (incl. services).

### Stage 5: Paper Process

**Customer state:** Customer completes legal, procurement, security, and financial steps to confidently sign the agreement. Negotiations and signatures done.

**Account Team activities:**
- AE supports and facilitates all negotiations and legal discussions
- Legal and Deal Desk execute final pricing, order form, contracts, approvals and legal/commercial docs
- AE submits and manages Deal Management and Legal requests via SFDC Cases (Case Chatter is primary internal communication)
- Ironclad comments used for legal workflow updates and version tracking (not Slack for deal execution/approvals)
- AE initiates and manages legal workflows in Ironclad for NDA, LSA, DPA, and BAA
- Confirm AWS marketplace/reseller internal routing, offer structure, and acceptance requirements
- Complete vendor setup and billing requirements
- Final architecture/security reviews
- Align services scope with signed quote
- Align internal teams for handoffs (CSM, SE, PS)
- AE exchanges contract drafts and redlines with customer legal primarily via email
- LaunchDarkly LSA shared as early as possible to accelerate customer review
- SE shares security and compliance documentation (SOC 2, ISO, DPA/BAA) via email once NDA is signed and Security Questionnaire is complete through HyperComply
- AE confirms billing entity, address, terms, start date are captured in SFDC Opp and Account fields and accurate on OF before sending to customer
- AE positions LaunchDarkly paper as default starting point

**MEDDPICC Priorities:**
- Metrics: Locked inside approved BVA; now supporting procurement justification
- Economic Buyer: Confirms contract terms align to approved scope and implementation plan
- Decision Criteria: Fully satisfied; now converting into contract requirements
- Decision Process: Procurement → Legal → Security → Finance chain confirmed
- Paperwork (PRIMARY FOCUS): Order Form, LSA, DPA/BAA (as applicable), billing, PS SoW, resellers or AWS Marketplace
- Identified Pain: Included in business case justifying spend
- Champion: Keeps procurement and legal moving; removes internal blockers
- Competition: Neutralized; focus is purely contracting

**Handshakes:**
- AE ↔ Deal Management: Confirm final pricing, discounts, CPQ configuration, OF structure. Coordinate and approve OF and SoW changes via SFDC Cases only when required. Validate reseller or AWS Marketplace routing and structure
- AE ↔ Legal: Initiate and manage legal workflows in Ironclad. Balance risk management with speed to signature
- AE ↔ Finance: Validate billing entity, invoicing requirements, term, start date, customer PO/payment portal requirements, regional compliance. Ensure paper-first execution preserves approved pricing and discounts. Confirm readiness for booking
- AE ↔ CS/TAM: Share onboarding readiness context prior to close. Validate contracted services align to onboarding assumptions and implementation readiness. Draft success plan
- AE ↔ AWS Marketplace/Reseller Partner: Confirm internal routing, offer structure, and acceptance requirements. Ensure partner path doesn't introduce avoidable contracting delays

**Documentation System of Record:**
- Ironclad: NDA, LSA, DPA, BAA workflows and version control
- SFDC: Opportunity and Stage 5 fields, all legal/contracting docs on account, OF and SoW changes via Cases, next steps tracking
- DocuSign: Final contract execution
- Vanta Trust Center: Approved legal templates and compliance documents

**Exit Criteria:**
- Negotiation complete
- Legal docs + OF signed by all parties
- AWS Marketplace, reseller, and compliance requirements validated (if applicable)
- Deal ready for booking

**Internal References:** Final BVA and EB approval, pricing approvals and CPQ configuration, partner involvement (AWS Marketplace, SI, reseller), compliance requirements, prior account legal docs/OF, Ironclad Best Practices, Case Management One-Sheeter, Booking Checklist.

**External Assets:** Executable Order Form/LSA/SoW, security and compliance documentation (SOC 2, ISO, Legal Docs, DORA Addendum), AWS Marketplace offer, procurement summary email (timeline and required actions), implementation readiness summary, value-based Pro vs Enterprise comparison, security/compliance/RBAC materials.

### Stage 6: Booking Review

**Customer state:** Customer is waiting for confirmation that all internal LD processes (finance validation, compliance readiness, provisioning readiness) are completed so the deal can be officially booked.

**Account Team activities:**
- Finance confirms executed documents are complete and accurate
- Finance creates AWS Marketplace private offer link
- Attach completed documents to the account in SFDC
- Ensure account team has Success Plan and key account notes
- Finance validates CPQ fields, discounts, terms, and revenue recognition
- Finance reviews and approves deal for booking
- Finance validates: required documents are signed and attached, required SFDC/CPQ fields and inputs are complete and accurate, term start date is invoiceable, SFDC/CPQ aligns to executed OF (billing entity, billing schedule, product detail, term dates)
- Validate requirements for provisioning; #feed-account-provisioning-log channel monitored for completion
- Provisioning complete on term start date or within 72-hour window of OF execution
- Once deal is CW, rev-rec can provision
- AE uploads contract and ancillary documents to account for account team reference

**MEDDPICC Priorities:**
- Metrics: Contract values, term, and financial impact validated by Finance
- Economic Buyer: Alignment already secured; confirm no commercial drift between executed paperwork and SFDC/CPQ
- Decision Criteria: Finance ensures all criteria met for compliant booking
- Decision Process: Finance review → resolve discrepancies (may require corrections before booking)
- Paperwork: Confirm all final documents correct, complete, and uploaded; verify SFDC/CPQ matches executed documents
- Champion: Ensures customer-side stakeholders expect start date and (if applicable) AWS Marketplace acceptance timing

**Handoffs:**
- AE → Finance: Move Opportunity into Stage 6 with executed doc set attached and required SFDC/CPQ inputs accurate
- Finance → AE: If discrepancies found, Finance flags what must be corrected (may require rework prior to booking)

**Critical Handshakes:**
- AE ↔ Finance: Finance validates all booking requirements are met
- Finance ↔ Deal Management: When discrepancies trace back to OF/quote structure, Finance partners with DM to resolve (may result in temporary stage change back to Stage 5)
- Finance ↔ Internal Tools/Biz Ops: When CPQ/SKU/provisioning constraints require system changes
- Finance ↔ AE/Partner (AWS Marketplace): Finance generates private offer link and shares with AE. Booking cannot occur until customer accepts the offer
- AE ↔ CSM/TAM: Confirm onboarding readiness assumptions and kickoff timing based on start date

**Communication:**
- Finance questions and status checks route to #ask-finance-booking (avoid 1:1 Slacks to individual Finance team members)
- If deal is ready with no discrepancies, Finance books and downstream systems trigger automatically; posted in #newrevenue channel
- For AWS Marketplace: AE sends private offer link to customer and drives acceptance timing

**Exit Criteria:**
- Finance approves all required fields, data, and documentation
- Finance moves opp to Stage 7 (Booked)

**Internal References:** Executed doc set (OF in SFDC + legal docs in Ironclad), SOW as attachment on OF when needed, CPQ configuration + Opportunity product detail, approvals/exceptions, AWS Marketplace or reseller routing details, known nuance flags (SKU/provisioning constraints), booking checklist.

**External Assets:** SOW and PS scope in OF/Quote, booking confirmation / "what happens next" update, for AWS Marketplace: private offer link + acceptance instructions, kickoff scheduling intro and start-date expectations, post-signature vendor onboarding documentation, internal handoff documentation (sales → post-sales), final architecture summary, Champion handoff / "Why We Chose LD" internal recap.

### Stage 7: Closed/Won

**Customer state:** Customer purchase official. Smooth transition into onboarding with clear expectations for provisioning, kickoff, roles, and implementation steps.

**Account Team activities:**
- AE leads internal handshake with post-sales team (TAM/CSM/SE)
- Ensure intros to post-sales team are complete and accurate
- Customer kickoff call scheduled
- Review Success Plan and begin activation prep
- AE remains engaged through kickoff to reinforce continuity and executive alignment
- Walk through Success Plan goals, onboarding milestones, and "what good looks like" with Champion
- Confirm roles, responsibilities, and communication cadence across both organizations
- Establish Champion as day-to-day implementation leader
- Validate technical context: environments, flag strategy, SDK expectations, rollout constraints
- Confirm PS scope, delivery expectations, and readiness to execute against SoW
- Validate internal dependencies required to support onboarding (provisioning, billing details, etc.)
- AE logs final Closed/Won summary in SFDC Opportunity Notes
- Success Plan ownership transitions to CSM/TAM in Catalyst
- Introduction email sent with kickoff scheduling details
- Kickoff invite includes AE, CSM/TAM, SE/PS (if applicable), Champion, and key customer stakeholders

**MEDDPICC Priorities:**
- Metrics: Confirm value outcomes that will drive onboarding and early adoption
- Economic Buyer: Awareness of onboarding and implementation plan reaffirmed
- Decision Criteria: "Successful onboarding" expectations clearly defined
- Decision Process: Customer confirms who will participate in kickoff and technical onboarding
- Paperwork: Fully executed; onboarding and provisioning workflows initiated
- Identified Pain: Mapped into Success Plan to shape implementation priorities
- Champion: Transitions into implementation leader alongside TAM/CSM

**Critical Handshakes:**
- AE ↔ CSM/TAM: Align on Success Plan, onboarding milestones, customer readiness signals. Confirm kickoff attendees
- AE ↔ SE/PS: Validate technical context, confirm PS scope and delivery expectations
- AE/CSM/TAM ↔ Finance/Provisioning: Validate internal dependencies for onboarding
- AE ↔ Executive Sponsor: Reinforce executive alignment during kickoff

**Exit Criteria:**
- Internal docs shared across account team
- Customer kickoff scheduled
- Success Plan alignment
- Account provisioned

**Internal References:** Success Plan from discovery and EB approval; BVA/POV outcomes, technical validation notes (architecture, environments, integrations), PS SOW, rollout constraints and assumptions, renewal and expansion signals identified during sales cycle.

**External Assets:** Kickoff deck, Success Plan, implementation timeline and roles, use-case-specific implementation examples, provisioning and setup instructions, security and compliance documentation for onboarding, best-practice and onboarding playbooks, Instruqt onboarding/enablement workshops, visual aids and "art of the possible" content.

---

## Post-Sale Stages

### Kickoff

**Customer state:** Establish shared expectations for onboarding, confirm provisioning and access, align on Success Plan, understand roles, milestones, and "what good looks like."

Kickoff is a continuity stage, not a handoff. Ownership evolves collaboratively: Sales remains engaged for context and reinforcement while CS/TAM leads execution.

**MEDDPICC Priorities:**
- Metrics: Success outcomes confirmed and translated into onboarding milestones in Success Plan
- Economic Buyer: Visibility maintained; attendance at Kickoff strongly encouraged. Goals reflected in onboarding
- Decision Criteria: Onboarding success criteria explicitly align to what was sold and approved
- Decision Process: Customer confirms who approves onboarding milestones and participates in kickoff
- Paperwork: OF, PS scope, entitlements, and provisioning inputs confirmed
- Identified Pain: Original pain and priority use cases reaffirmed and mapped into onboarding milestones
- Champion: Confirmed as day-to-day implementation leader and internal coordinator

**Internal Handshakes (No Formal Handoffs):**
- AE ↔ CSM/TAM/SE: Align on Success Plan, milestones, customer readiness. Confirm AE role through kickoff. Validate shared understanding of pain, value narrative, EB priorities
- AE/SE ↔ CSM/TAM/SA: Align on technical context (environments, SDK expectations, flag strategy). Surface known risks, gaps, or follow-ups from validation
- CSM/TAM ↔ SA/SE: Confirm architecture, environments, dependencies, onboarding sequence. Validate technical readiness

**Exit Criteria:**
- Kickoff Call delivered with JSP overview and enablement plan
- Kickoff Call/JSP logged in Catalyst

### Activation (Implements First Use Case)

**Customer state:** Successfully deploy first LaunchDarkly use case in production, establish operational confidence, prepare to validate value.

Activation is about making the product work in the customer's environment, not proving business value or scaling adoption. CS/TAM leads execution, with SA/SE support and Sales informed.

**MEDDPICC Priorities:**
- Metrics: Track activation milestones (flags live in production, SDKs implemented, environments configured)
- Identified Pain: Original pain remains mapped to first use case being implemented
- Champion: Actively coordinates customer-side teams and validates readiness

**Internal Handshakes:**
- AE ↔ CSM/TAM/SE/SA: Align on activation sequencing, environments, dependencies. Teams enabled on 101 LaunchDarkly ("Bronze Certified"). Validate SDK setup, flag configuration, governance patterns, observability. Address blockers and confirm readiness for first production deployment
- CSM/TAM ↔ AE: Share visibility into progress, risks, or notable signals. AE maintains context for future executive conversations. Align on potential expansion signals or risks
- SE ↔ AE: Monitor customer usage closely for signal on high-value applications or features driving growth. Partner on identifying new apps/teams that could use LaunchDarkly

**Exit Criteria:**
- Customer activated on their purchased product
- SLA: 90 days from Closed Won to Activated

### Wrap Up (See First Use Case in Action)

**Customer state:** Confirm first use case delivered meaningful value, align on outcomes achieved, understand go-forward plan for adoption.

Wrap Up is a decision and alignment stage. It confirms whether the first use case mattered and what should happen next.

**MEDDPICC Priorities:**
- Metrics: Document outcomes from first use case (qualitative and early quantitative indicators)
- Economic Buyer: Visibility reinforced through onboarding summary and value narrative
- Decision Criteria: Customer confirms whether first use case met expectations and justifies continued adoption
- Identified Pain: Validate that original pain was meaningfully addressed
- Champion: Communicates internal go-forward story within customer organization

**Internal Handshakes:**
- CSM/TAM ↔ AE: Share summarized outcomes, risks, expansion signals. AE regains context for future executive or commercial conversations. No active selling in this stage
- CSM/TAM ↔ Marketing/Advocacy: Surface potential advocacy readiness signals. No external advocacy commitments made

**Exit Criteria:**
- Onboarding lookback completed with recap sent to EB and Manager CC'd
- Customer categorized as Expansion or Risk with corresponding plan built (including org chart)

### Initial Value (Initial Value Realization)

**Customer state:** Demonstrate measurable business value, build internal credibility with leadership, establish confidence in continued investment and expansion.

**MEDDPICC Priorities:**
- Metrics: Baseline and track agreed success metrics (velocity, MTTR, incident reduction, experimentation impact)
- Economic Buyer: Re-engaged through structured value conversations (QBRs/EBRs)
- Decision Criteria: Customer leadership agrees value is real, measurable, and worth sustaining or expanding
- Identified Pain: Reframed as quantified outcomes (before/after narrative)
- Champion: Enabled to communicate outcomes internally with confidence

Note: Every customer review should clearly connect customer priorities to work delivered and measurable business outcomes. This reinforces LD's value beyond feature management, increases adoption across SKUs (including Experimentation), and reduces renewal risk tied to underutilization.

**Internal Handshakes:**
- CSM/TAM ↔ AE: Align on outcome narrative, customer health, expansion or risk signals quarterly. Reference metrics with QBRs. Review success plans regularly. Confirm roles in executive-level conversations
- CSM/TAM ↔ Business Value ↔ AE: Engage to quantify outcomes and assign business value. Educate on DORA metrics and tracking best practices. Support ROI framing
- AE ↔ CSM/TAM ↔ Marketing/Advocacy: Surface potential advocacy readiness signals once outcomes validated

**Exit Criteria:**
- Value check delivered
- Customer can verbalize value from first use case through adoption signals
- Customer expresses desire to proceed with new teams and/or use cases

### Scale (Enterprise-Wide Adoption)

**Customer state:** Scale LaunchDarkly across teams and initiatives, standardize usage patterns, implement governance (including CoE concepts) for enterprise-wide adoption.

Scale is about standardization and repeatability. Customers typically arrive here in one of two modes: scaling from a strong initial standard, or cleaning up fragmented usage and standardizing.

**MEDDPICC Priorities:**
- Metrics: Enterprise-scale KPIs and adoption signals (adoption depth/breadth, release frequency, MTTR, operational efficiency)
- Economic Buyer: Re-engaged as outcomes and standardization create case for broader investment and multi-year commitments
- Decision Criteria: Enterprise readiness (governance, compliance, operating model, sustainable adoption)
- Identified Pain: Shifts from "first use case value" to "enterprise inconsistency/lack of standardization" and scaling bottlenecks
- Champion: Customer-side leadership and enablement owners may emerge (platform team, DevOps, architecture leaders)

**Internal Handshakes:**
- CSM/TAM ↔ SA/PS: Evaluate current maturity and best-practice consistency. Determine customer mode (scaling from standard vs. standardizing fragmented usage). Align on governance path
- CSM/TAM ↔ AE: Align on outcomes from value cadence and where standardization creates expansion paths. Determine whether executive alignment should be re-engaged. Coordinate timing if commercial motion becomes relevant
- AE ↔ Partners: Re-engage strategic integrations and partner ecosystem where it accelerates scale
- CSM/TAM ↔ Marketing/Enablement: Align on reusable enablement assets (academy, office hours, certifications, governance toolkits)

**Signals and Notifications:** Thena for Slack (integration in customer channels), Marketing Newsletter with Product Log, access to support tickets, usage and user-growth signal alerts.

**Exit Criteria:**
- Outcomes documented and presented to exec sponsor
- Enterprise-wide adoption plan (BUs, apps, geos) entered in SFDC
- EBR with BV completed on 6-month cycle

### Evangelize (Customer Advocacy)

**Customer state:** Sustain transformation, confidently renew, and participate in advocacy activities that reflect value realized.

Evangelize is about making value visible and reusable (renewal justification + advocacy). It often runs in parallel with ongoing Scale motions.

**MEDDPICC Priorities:**
- Metrics: Outcomes used to justify renewal/expansion; ongoing outcome cadence tied to success plan
- Economic Buyer: Re-engaged as needed for multi-year partnership and renewal decisions
- Paperwork: Renewal/expansion paperwork readiness (commercial path, marketplace/reseller as applicable)
- Champion: Customer advocate(s) enabled and activated through clear mutual value exchange

**Internal Handshakes:**
- CSM/TAM ↔ AE ↔ SE ↔ PS: Align renewal strategy, multi-year account plan, expansion readiness. Use technical + services context to shape feasible expansion paths
- CSM/TAM ↔ Partner/SI Team: Re-assess partner paths for org-wide transformation and renewal packaging. Re-evaluate marketplace/reseller routes
- CSM/TAM ↔ Lifecycle/Customer Marketing ↔ ABM: Coordinate advocacy pathways and lifecycle programs. Align ABM campaigns for expansion. Avoid ad hoc asks by routing through defined plays and criteria
- CSM/TAM ↔ Product/Enablement: Curate shareable product updates and enablement

**Advocacy Activities (Customer-Facing):**
Position advocacy as mutual value exchange (visibility, leadership narrative, recruiting/brand, peer connection, roadmap influence). Offer a menu of activities, then select one right-fit activity to start:

Internal advocacy: Reference call, third-party review (anonymous), analyst interview, NPS/CSAT promoter, survey response, positive Gong call, email feedback, accepted request to join reference pool, product feedback session, feature request submitted/implemented, EAP participation, product advisory council membership.

External advocacy: Third-party review (public), case study participation, webinar speaker, LaunchDarkly event speaker, event co-presenter at non-LD event, press participation, CAB membership, community engagement (Discord), video testimonial, social media advocacy, blog post, written testimonial, customer-led user group/meetup, customer-owned blog/podcast mention, on-site workshop participation, industry awards submissions, involvement in purchase or expansion, refresh old case study, customer education (Academy attendance).

**Managed reference calls by Customer Marketing.** Common motions include reference calls, speaking opportunities, case studies, automated review collection (G2), surveys and structured feedback.

**Currently Running Automated Programs:**
- New users (<6 months, higher than average activity, high-maturity accounts) receive review asks
- Users with resolved support tickets receive one email asking for review (no repeat)
- Users completing UserEvidence survey with NPS 7+ receive review ask on confirmation page
- Planned: Review asks for strategic categories (Observability, Product Analytics, A/B Testing) based on product activity

**Exit Criteria:**
- Renewal contractually executed
- Champion agrees to at least one advocacy activity (reference opt-in, published blog post, event speaker, G2 review, etc.)
