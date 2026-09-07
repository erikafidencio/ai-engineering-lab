# Runbook — Inventory Stale (Admin vs Storefront)

## When to use

Admin panel shows stock available, but storefront or checkout reports out of stock.

**Typical ticket labels:** `inventory`, `cache`, `sync`  
**Symptom ID:** `inventory_stale`

## Quick triage

| Check | Signal | Healthy |
|-------|--------|---------|
| Source of truth | `inventory-api` SKU count | Matches warehouse feed |
| Edge cache | Redis key `inv:{storeId}:{sku}` | TTL aligned with sync job |
| Sync job | `INV-Sync-*` last success | < 15 min ago |
| Checkout | `GET /availability` response | Consistent with API |

## Investigation steps

1. Note SKU, store ID, and last sync timestamp from the ticket.
2. Query `inventory-api` directly for the SKU — compare with admin UI.
3. Check Redis/cache layer for stale value and TTL.
4. Find last successful `INV-Sync-*` job and any failed runs.
5. If resolved historically, read ticket comments for RCA pattern (TTL vs sync interval).

## Common root causes

| Pattern | Likely cause |
|---------|--------------|
| Admin reads DB, storefront reads cache | Cache invalidation gap |
| `INV-lag` metric spike | Sync job delayed or failed |
| TTL 5m, sync every 15m | Misaligned refresh (see INC-1003) |
| Partial store rollout | Wrong store ID in cache key |

## Historical reference

- **INC-1003** — WIDGET-42, Redis TTL 5m vs warehouse feed every 15m. Fixed via sync webhook invalidation.

## Escalation

**Team:** Inventory sync  
**Include:** SKU, store ID, cache key, last sync job ID.
