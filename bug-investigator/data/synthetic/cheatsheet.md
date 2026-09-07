# ShopFlow — Incident Cheatsheet (synthetic)

Quick symptom → investigation ranking for War Room triage. All data is fictional.

## WR ranking (investigate in this order)

| Priority | Symptom | First signal | Key trace prefix | Escalate |
|----------|---------|--------------|------------------|----------|
| 1 | Orders missing | Payment OK, dashboard empty | `ORD-Ingest-*` | Order ingestion |
| 2 | Duplicate charge | Customer billed twice | `PAY-Trace-*`, `PAY-409` | Payments |
| 3 | Inventory stale | Admin in stock, storefront OOS | `INV-Sync-*`, `INV-lag` | Inventory sync |

## Demo tickets (for CLI / agent)

| Ticket | Use when testing… |
|--------|-------------------|
| `INC-1001` | Order ingestion / consumer / DLQ |
| `INC-1002` | Idempotency / duplicate payment |
| `INC-1003` | Cache vs sync lag (resolved RCA in comments) |

## Free-text queries (RAG smoke test)

- `merchant dashboard empty after checkout ORD-Ingest`
- `double charge PAY-409 idempotency retry`
- `WIDGET-42 out of stock cache INV-lag`

## What is NOT the root cause (common traps)

- Payment captured ≠ order visible (consumer may still fail)
- Single ERROR log without trace ID ≠ sufficient for RCA
- Admin UI and storefront may read different data sources
