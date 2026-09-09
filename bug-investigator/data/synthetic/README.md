# Synthetic dataset — Part 1

Fictional **ShopFlow** e-commerce incidents for the public MVP. No proprietary data, credentials, or real service names from production systems.

## Layout

```text
data/synthetic/
├── manifest.json          # Index: incidents ↔ symptoms ↔ runbooks ↔ logs
├── cheatsheet.md          # Symptom ranking + demo queries
├── incidents/             # Mock Jira tickets (JSON)
│   ├── INC-1001.json
│   ├── INC-1002.json
│   └── INC-1003.json
├── runbooks/              # Investigation playbooks (Markdown)
│   ├── orders-missing-after-checkout.md
│   ├── duplicate-charges-idempotency.md
│   └── inventory-stale-cache.md
└── logs/                  # Mock observability (JSON)
    ├── INC-1001.json
    ├── INC-1002.json
    └── INC-1003.json
```

## Incident JSON schema

| Field | Type | Description |
|-------|------|-------------|
| `key` | string | Ticket ID (`INC-1001`) |
| `summary` | string | One-line title |
| `status` | string | `Open`, `In Progress`, `Resolved` |
| `priority` | string | `Low` … `Critical` |
| `labels` | string[] | Tags for routing |
| `description` | string | Full body (includes trace IDs, IDs) |
| `comments` | object[] | `{ "author", "body" }` |
| `url` | string | Fictional Jira URL |

## Log JSON schema

| Field | Type | Description |
|-------|------|-------------|
| `incident_key` | string | Links to incident |
| `trace_id` | string | Primary trace for search |
| `environment` | string | `prod` / `staging` |
| `region` | string | e.g. `US`, `EU` |
| `services` | string[] | Services involved |
| `entries` | object[] | Log lines (see below) |

Each **entry**:

| Field | Description |
|-------|-------------|
| `timestamp` | ISO-8601 UTC |
| `level` | `INFO`, `WARN`, `ERROR` |
| `entity.name` | Service name (observability-style) |
| `message` | Log message |
| `trace_id` | Optional per-line trace |

## Symptom mapping

Defined in `manifest.json` and mirrored in root `config.yaml` → `symptoms:`.

| symptom_id | Ticket | Trace |
|------------|--------|-------|
| `orders_missing` | INC-1001 | `ORD-Ingest-*` |
| `duplicate_charge` | INC-1002 | `PAY-Trace-*` |
| `inventory_stale` | INC-1003 | `INV-Sync-*` |

## Part 2 — RAG (done)

Index and query from project root:

```bash
./scripts/index.sh
export PYTHONPATH=src
python -m bug_investigator search "ORD-Ingest order missing"
python -m bug_investigator diagnose "double charge PAY-409"
```

## Next parts

- **Part 3 — Agent:** LangGraph workflow
- **Part 4 — Mock tools:** read tickets/logs from these files
- **Part 5 — CLI:** `investigate.sh INC-1001`

## Validate files manually

```bash
# All JSON parses
for f in incidents/*.json logs/*.json manifest.json; do
  python3 -m json.tool "data/synthetic/$f" > /dev/null && echo "OK $f"
done
```
