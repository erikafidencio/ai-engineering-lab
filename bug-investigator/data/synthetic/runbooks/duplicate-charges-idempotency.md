# Runbook — Duplicate Charges on Client Retry

## When to use

Customer billed twice (or more) after checkout timeout and manual retry.

**Typical ticket labels:** `payments`, `duplicate`, `idempotency`  
**Symptom ID:** `duplicate_charge`

## Quick triage

| Check | Signal | Healthy |
|-------|--------|---------|
| Idempotency header | `Idempotency-Key` on retry request | Same key as first attempt |
| Error code | `PAY-409 IdempotencyKeyConflict` | Should return existing charge, not new |
| Trace linkage | `PAY-Trace-*` across attempts | Single charge ID |

## Investigation steps

1. Find both charge IDs and the shared `PAY-Trace-*` from the ticket.
2. Compare request headers between first attempt and client retry (mobile vs web).
3. Confirm whether the retry path omits `Idempotency-Key` (common on mobile SDK < 3.2).
4. Check payment-service logs for `IdempotencyKeyConflict` — was it handled as 409 or ignored?
5. Verify refund workflow if duplicate capture already settled.

## Common root causes

| Pattern | Likely cause |
|---------|--------------|
| Missing `Idempotency-Key` on retry | Client bug or gateway strip |
| New key generated per retry | Frontend regenerates UUID incorrectly |
| Timeout before 409 returned | User retries while first charge still processing |
| Webhook double delivery | Reconcile via charge ID, not order ID |

## Historical reference

- **INC-1002** — EU region, `PAY-409` on retry path without idempotency header.

## Escalation

**Team:** Payments platform  
**Include:** both charge IDs, trace, client version, region.
