---
name: ld-architecture-diagram
description: Generate a Mermaid architecture diagram for an account showing tools, services, and integration points
argument-hint: <account>
---

# Architecture Diagram

Generate or update a Mermaid architecture diagram for an account, focused on the actual tools, services, and interfaces between them.

## Arguments

- `account`: The account name (e.g., "Acme Corp")

## Instructions

### Pre-check: Read Config

Read `~/.claude/skills/sales-config.md` and extract: `vault_path`, `company_folder`, `company`, `products`

### Step 1: Gather Architecture Data

Read the account file at `{config.vault_path}/{config.company_folder}/Accounts/{Account}/{Account}.md` and extract:

1. **Tech Stack section** — languages, frameworks, cloud, infra, data, observability, CI/CD, feature flags
2. **TECHMAPS section** — environment, technical requirements, competitors
3. **Architecture Diagram section** — existing diagram content (ASCII or Mermaid)
4. **Meeting notes** — scan `meetings/` for ENVIRONMENT, TECH_STACK, and ARCHITECTURE_NOTES data in transcripts and summaries. Focus on concrete tools and services mentioned, not abstract concepts.

### Step 2: Build the Mermaid Diagram

Always use `graph TD` (top-down) for a vertical layout. This provides the most readable flow from client applications at the top through services, infrastructure, and data layers to observability and tooling at the bottom. Never use `graph LR`.

#### Node Categories

Organize nodes into subgraphs by layer. Use only the layers that have known components:

```
subgraph clients["Client Applications"]
```
- Web apps, mobile apps, SPAs, browser extensions
- Include framework (React, Angular, etc.) if known

```
subgraph services["Backend Services"]
```
- APIs, microservices, monoliths, serverless functions
- Include language/framework (Node.js, Python, Ruby, Go, etc.)

```
subgraph infra["Infrastructure"]
```
- Cloud provider services (AWS EKS, GCP GKE, Azure AKS, etc.)
- Container orchestration, serverless platforms
- CDN, load balancers, API gateways

```
subgraph data["Data & Storage"]
```
- Databases (Postgres, MySQL, DynamoDB, etc.)
- Data warehouses (Snowflake, BigQuery, Redshift)
- Message queues (Kafka, RabbitMQ, SQS)
- Cache (Redis, Memcached)

```
subgraph observability["Observability & Monitoring"]
```
- APM (Datadog, New Relic, Dynatrace)
- Logging (Splunk, ELK, CloudWatch)
- Error tracking (Sentry, Bugsnag)
- Session replay tools

```
subgraph devtools["Developer Tooling"]
```
- CI/CD (Jenkins, GitHub Actions, CircleCI)
- Source control (GitHub, GitLab, Bitbucket)
- Feature flags (current provider if not {config.company})
- Identity (Okta, Auth0)

```
subgraph ld["{config.company}"]
```
- {config.company} products in use or being evaluated
- Show SDK integration points

#### Styling

Use Mermaid styling to highlight key information:

```mermaid
%% Pain points: red border
style node_id stroke:#e74c3c,stroke-width:3px

%% LaunchDarkly targets: green border
style node_id stroke:#27ae60,stroke-width:3px

%% Existing LD integration: green fill
style node_id fill:#d5f5e3,stroke:#27ae60
```

- **Red border** (`stroke:#e74c3c`): Pain points, problems, bottlenecks
- **Green border** (`stroke:#27ae60`): Target integration points for {config.company}
- **Green fill** (`fill:#d5f5e3`): Already using {config.company}

#### Edges

Use arrows to show data flow and integration relationships:
- `-->` for data flow / API calls
- `-.->` for planned / future integrations
- `==>` for high-volume / critical paths
- Label edges with the integration type when relevant (e.g., `-->|"REST API"| `, `-->|"SDK"| `)

#### Legend

Add a comment block at the top of the diagram explaining the color coding:

```
%% RED border = pain point | GREEN border = LD target | GREEN fill = using LD
```

### Step 3: Write the Diagram

Replace the `## Architecture Diagram` section in the account file with the Mermaid diagram wrapped in a code fence:

````markdown
## Architecture Diagram

```mermaid
%% RED border = pain point | GREEN border = LD target | GREEN fill = using LD
graph TD
    subgraph clients["Client Applications"]
        web["React Web App"]
        mobile["React Native Mobile"]
    end
    
    subgraph services["Backend Services"]
        api["Node.js API"]
        worker["Python Workers"]
    end
    
    subgraph infra["Infrastructure"]
        eks["AWS EKS"]
        lambda["AWS Lambda"]
    end
    
    subgraph data["Data & Storage"]
        pg["PostgreSQL"]
        redis["Redis Cache"]
        kafka["Kafka"]
    end
    
    subgraph observability["Observability"]
        dd["Datadog"]
        sentry["Sentry"]
    end
    
    subgraph ld["LaunchDarkly"]
        ff["Feature Flags"]
        exp["Experimentation"]
    end
    
    web -->|"JS SDK"| ld
    api -->|"Node SDK"| ld
    worker -->|"Python SDK"| ld
    
    web --> api
    api --> pg
    api --> redis
    api --> kafka
    worker --> kafka
    
    api --> dd
    web --> sentry
    
    style worker stroke:#e74c3c,stroke-width:3px
    style exp stroke:#27ae60,stroke-width:3px
```
````

### Rules

1. **Only include components you have evidence for.** Do not guess or add generic components. If the tech stack section says "AWS" but doesn't specify which services, just show "AWS" as a single node.

2. **Keep it focused.** Max 15-20 nodes. Combine related tools into single nodes if the diagram gets too complex (e.g., "CI/CD: GitHub Actions + ArgoCD").

3. **Show integration points clearly.** The most valuable part of the diagram is showing WHERE {config.company} connects to the architecture via SDKs and how data flows.

4. **Preserve existing insights.** If the current ASCII diagram has pain points or target annotations, carry them forward into the Mermaid version.

5. **Use readable node IDs.** Node IDs should be short lowercase slugs, display labels should be the actual tool/service name.

6. **Subgraph labels in quotes.** Always use `subgraph id["Label"]` format for readable labels.

### Output

Report what was created/updated:
- Number of nodes and subgraphs
- Pain points highlighted
- {config.company} integration points shown
- Any components from the tech stack that couldn't be placed (unknown relationships)
