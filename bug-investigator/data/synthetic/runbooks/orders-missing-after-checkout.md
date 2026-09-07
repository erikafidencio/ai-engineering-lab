# Runbook — Orders Missing After Checkout

## When to use

Merchant or support reports: payment went through, but the order does not appear in the dashboard or admin UI.

**Typical ticket labels:** `orders`, `ingestion`, `consumer`  
**Symptom ID:** `orders_missing`

## Quick triage

| Check | Command / signal | Healthy |
|-------|------------------|---------|
| Payment captured | Trace `ORD-Ingest-*` in payment-service | `status=captured` |
| Consumer lag | `order-consumer` queue depth | < 1 min lag |
| DLQ | `order-ingestion-dlq` message count | 0 or stable |
| Dashboard API | `GET /merchants/{id}/orders?since=...` | Returns new rows |

## Investigation steps

1. Copy the checkout trace from the ticket (`ORD-Ingest-<uuid>`).
2. Search observability for that trace across `checkout-service`, `order-consumer`, `order-api`.
3. If payment succeeded but consumer shows `affected=0`, inspect payload validation errors.
4. Compare `storeId` and `region` in the payload with merchant configuration.
5. Check DLQ for poison messages with the same trace ID.

## Common root causes

| Log pattern | Likely cause | Fix direction |
|-------------|--------------|---------------|
| `SchemaValidationException: storeId` | Wrong store mapping | Fix merchant config |
| `affected=0` after ingest | Silent reject in consumer | Patch validation / mapping |
| Consumer lag > 5 min | DB write bottleneck | Scale consumer, check DB locks |
| Message in DLQ, duplicate trace | Retry without idempotency | Replay after fix |

## Historical reference

- **INC-1001** — ORD-Ingest trace present, payment OK, consumer DLQ spike after 14:00 UTC.

## Escalation

**Team:** Order ingestion / consumer  
**Include:** trace ID, store ID, region, DLQ sample message (redacted).
