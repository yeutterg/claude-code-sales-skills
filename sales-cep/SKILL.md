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

## CEP Stage Definitions (Pipeline Starts → Closing)

### Stage 1: Validate Fit

**Customer state:** Customer tells us problems and impacts.

**Account Team activities:**
- Deliver custom demo(s) aligned to use cases
- Validate technical feasibility and future-state alignment
- Identify success metrics tied to outcomes
- Identify and position against competition
- Prepare for potential co-sell motions with partners (AWS, SI/Consulting/ISV)
- AE + SE align on technical qualification
- Position deeper/tech value dives
- For Large Enterprises: start to identify governing bodies, change advisory board (CAB) or architecture review board (ARB)

**MEDDPICC focus:** M E D D P I **C C** (validating Champion and Competition)

**Exit Criteria:**
- Custom demo delivered
- Customer-validated alignment to future state with LD
- Next step set in SFDC

### Stage 2: Business Value

**Customer state:** Customer confirms business value.

**Account Team activities:**
- Validate pain and metrics tied to business outcomes via key meetings or workshops with Champion(s)
- Identify and engage EB: align on POV requirements, success criteria, scope, timelines, and (3 whys) or BVA for any deal over $125K
- Clarify decision process and approval path
- Strengthen Champion(s) and co-create MAP
- Align AE + SE on tech validation plan
- Set up AWS co-sell call
- Engage services for all deals over $30K for value acceleration
- Initiate SI/ISV joint pursuit as applicable

**MEDDPICC focus:** **M E** D D P **I** C C (validating Metrics, Economic Buyer, Identified Pain)

**Exit Criteria:**
- Economic buyer POV Go/No-Go meeting happened
- Business justification confirmed and POV planned and timed

### Stage 3: Tech Validation

**Customer state:** Customer verbally confirms tech fit.

**Account Team activities:**
- Execute technical validation against agreed success criteria
- Validate required capabilities, integrations, security, and architecture
- Align ROI narrative with POV outcomes
- Advance procurement, security, and legal workflows
- Prepare for and schedule EB Go/No go
- Assess change management requirements
- Start CPQ quoting ahead of pricing discussions: define and document the SI quote process

**MEDDPICC focus:** M E D D P **I** C C (full MEDDPICC validation)

**Exit Criteria:**
- Tech accept agreed upon by champion
- CoM complete with tech differentiation narrative
- Primary quote in approved status
- LD ID added to the opp

### Stage 4: EB Approval

**Customer state:** Customer decision and commercial approvals.

**Account Team activities:**
- Champion co-leads EB Go/No Go meeting
- Align on a Close Plan and agreed upon milestones
- Review services scope (PS, RSA), onboarding, and future-state delivery plan
- Finalize negotiation non-starters and trade-offs
- Align on exec sponsor involvement after signature
- Deal Desk confirms pricing/proposal structure, order form structure
- AE aligns with customer on proposal structure, pricing strategy, discounts, contract timing, reseller involvement
- Ensure AWS Co-Sell Call is complete
- Confirm if reseller/marketplace will be used
- AE secures confirmation from customer on commercials and sends order form and LSA
- AE secures confirmation that vendor onboarding and legal review begin

**MEDDPICC focus:** M E D D **P** I C C (Paper Process emphasis)

**Exit Criteria:**
- EB Go/No-Go meeting complete
- Primary quote in approved status
- LD ID added to the opp

### Stage 5: Paper Process

**Customer state:** Customer negotiations and signatures done.

**Account Team activities:**
- AE supports and facilitates all negotiations and legal discussions
- Legal and Deal Desk execute final pricing, order form, contracts, approvals and legal/commercial docs
- Confirm AWS marketplace/reseller internal routing, offer structure, and acceptance requirements
- Complete vendor setup and billing requirements
- Final architecture/security reviews
- Align services scope with signed quote
- Align internal teams for handoffs (CSM, SE, PS)

**MEDDPICC focus:** M E D D **P** I C C (Paper Process completion)

**Exit Criteria:**
- Negotiation complete
- Legal docs signed by all parties
- Deal ready for booking

### Stage 6: Booking Review

**Customer state:** Customer anticipates final approvals.

**Activities:**
- Finance confirms executed documents are complete and accurate
- Finance creates AWS Marketplace private offer link
- Attach completed documents to the account in SFDC
- Ensure account team have Success Plan and key account notes
- Finance validates CPQ fields, discounts, terms, and revenue recognition
- Finance reviews and approves deal for booking

**Exit Criteria:**
- Finance approves all required fields, data, and documentation
- Finance moves opp to Stage 7 (Booked)

### Stage 7: Closed/Won

**Customer state:** Customer purchase official.

**Activities:**
- AE leads internal handshake with post-sales team (TAM/CSM/SE)
- Ensure intros to post-sales team are complete and accurate
- Customer kickoff call scheduled
- Review Success Plan and begin activation prep

**Exit Criteria:**
- Internal docs shared across account team
- Customer kickoff scheduled
- Success Plan alignment in Salesforce
- Account provisioned

---

## Pre-Pipeline Stages (for reference)

### Targeting (No Open Opp)
Customer becomes discoverable to LD. ICP validation, PG plan, initial outreach.

### Engagement (No Open Opp)
Customer engages to validate problem(s). Multithreading, POV signal testing, persistent follow-up.

### Qualification (Opp Created)
Customer agrees to initial call. Lead Qualification call, validate/invalidate pain, identify early Champion signals, SDR Handshake, CSM Handshake.

**Exit Criteria:** Identified Pain validated in SFDC. Next step documented (Disco, Stage 1, DQ). SLA 48 hours.

### Discovery (Opp Created)
Customer is open to change and shares info. Structured discovery with Deal Deck, validate POV, validate technical/business Champion(s), schedule custom demo.

**Exit Criteria:** Deal Deck used, Discovery completed, iARR estimate, custom demo scheduled. SLA 30 days.
