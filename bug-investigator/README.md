# AI Bug Investigator

An AI-assisted incident investigation system that combines **LLMs, Retrieval-Augmented Generation (RAG), vector search, and Model Context Protocol (MCP)** to accelerate root-cause analysis of software incidents.

The project explores how AI can help software engineers investigate complex incidents by combining historical engineering knowledge with information retrieved from multiple technical sources.

> **Portfolio project:** This repository uses synthetic data and public examples. No proprietary company data, credentials, or internal systems are included.

## Problem

Investigating production incidents in distributed systems can require engineers to manually correlate information across multiple sources:

- Incident descriptions and tickets
- Historical incidents
- Technical documentation
- Application logs
- Observability data
- Database records
- Message-processing information

This process can be time-consuming, especially when the same or similar problems have already been investigated in the past.

The goal of **AI Bug Investigator** is to reduce this manual effort by providing an AI-assisted workflow that retrieves relevant historical knowledge and helps engineers investigate a new incident.

## Solution

The system combines two complementary approaches:

### 1. RAG-based knowledge retrieval

Historical incidents and technical documentation are:

1. Collected from knowledge sources
2. Split into meaningful chunks
3. Converted into vector embeddings
4. Stored in a vector database
5. Retrieved using semantic similarity when a new incident is investigated

This allows the system to retrieve relevant historical incidents even when the wording of the new incident differs from the original one.

### 2. AI-assisted investigation

The retrieved knowledge is provided to an LLM together with the current incident context.

The investigation workflow can then:

- Identify potentially affected components
- Retrieve similar historical incidents
- Correlate technical information
- Generate investigation hypotheses
- Suggest relevant next steps
- Assist engineers during root-cause analysis

## Architecture

```text
                   ┌─────────────────────┐
                   │ Historical Incidents │
                   │   & Documentation   │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │     Ingestion       │
                   │ Chunking + Metadata │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │    Embeddings       │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │      ChromaDB       │
                   │    Vector Store     │
                   └──────────┬──────────┘
                              │
                    Semantic Retrieval
                              │
                              ▼
┌─────────────────┐   ┌─────────────────────┐
│ Current Incident│──▶│  Investigation      │
│     Context     │   │      Workflow       │
└─────────────────┘   └──────────┬──────────┘
                                 │
                         ┌───────┴────────┐
                         ▼                ▼
                  ┌─────────────┐  ┌─────────────┐
                  │     RAG     │  │     MCP     │
                  │ Retrieval   │  │    Tools    │
                  └──────┬──────┘  └──────┬──────┘
                         │                │
                         └───────┬────────┘
                                 ▼
                         ┌─────────────┐
                         │     LLM     │
                         └──────┬──────┘
                                ▼
                     Investigation Result

```

## Key Technologies

- **Python**
- **LLMs**
- **Retrieval-Augmented Generation (RAG)**
- **Embeddings**
- **ChromaDB**
- **MCP (Model Context Protocol)**
- **Cursor**
- **Vector Search**
- **Async LLM API calls**

## MCP Integration

The project also explores MCP as a way to give an AI-assisted investigation workflow structured access to engineering tools and information sources.

The original workflow was designed around sources such as:

- Jira
- Azure DevOps
- Observability platforms
- Databases

For the public version of this project, these integrations will be represented using **mock or local implementations** to keep the repository independent from proprietary systems.

## Engineering Workflow

A typical investigation follows a structured process:

1. Read and understand the incident description.
2. Identify potentially affected services or components.
3. Search historical incidents using semantic retrieval.
4. Retrieve relevant technical documentation.
5. Use available tools to gather additional technical context.
6. Correlate the retrieved information.
7. Generate investigation hypotheses.
8. Suggest the next steps for root-cause analysis.

## Why RAG?

Traditional keyword search can fail when two incidents describe the same underlying problem using different terminology.

RAG allows the system to search based on **semantic similarity**, making it possible to retrieve historically relevant incidents even when the vocabulary is different.

This project uses **ChromaDB** as the vector store for the initial implementation.

## Quick Start

```bash
cd bug-investigator
./scripts/index.sh
./scripts/investigate.sh INC-1001
```

RAG-only commands:

```bash
export PYTHONPATH=src
python -m bug_investigator search "order missing after checkout"
python -m bug_investigator diagnose "double charge PAY-409 idempotency"
python -m bug_investigator investigate "merchant dashboard empty"
```

Optional: set `OPENAI_API_KEY` in `.env` for LLM synthesis in `diagnose` (falls back to template without it).

Run tests:

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest tests/ -q
```

## Current Status

🚧 **Work in Progress**

| Part | Status |
|------|--------|
| 1 — Synthetic dataset (ShopFlow) | ✅ |
| 2 — RAG (ChromaDB + CLI) | ✅ |
| 3 — LangGraph agent + mock tools | ✅ |
| 4 — Mock MCP polish / import | ⏳ |
| 5 — End-to-end demo docs | ⏳ |
| 6 — Retrieval evaluation metrics | ⏳ |

## Future Improvements

The project will explore:

- Agentic investigation workflows
- Tool calling
- RAG evaluation
- Retrieval quality metrics
- Hallucination mitigation
- Prompt and response evaluation
- Observability for LLM applications
- Automated incident classification
- Root-cause analysis evaluation
- Production-oriented architecture

## Learning Goals

This project is part of my journey from **Senior Backend Engineering to AI Engineering**, combining my background in distributed systems with practical AI engineering.

My focus areas include:

- LLM application development
- RAG architectures
- Vector databases
- AI agents
- MCP
- LLM evaluation
- AI observability
- Production AI systems

## Author

**Érika Fidêncio**

Senior Software Engineer focused on **Java, Spring Boot, microservices, distributed systems, and Applied AI**.