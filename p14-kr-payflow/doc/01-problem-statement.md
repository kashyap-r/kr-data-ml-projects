# 01 — Problem Statement: Payments Event & Settlement Ingestion Service

| | |
|---|---|
| **Project** | `payflow-ingest` (working name) |
| **Doc status** | Draft v0.1, for review |
| **Author** | (you) |
| **Next doc** | 02 — Requirements |

---

## 1. Context

**Fictional company:** *OrbitPay* is a payment orchestration platform. Merchants integrate with OrbitPay once, and OrbitPay routes each payment to one of several Payment Service Providers (PSPs), such as an Adyen-like, a Stripe-like and a Checkout-like provider. Routing depends on cost, country and success rate.

A card payment produces data in **two independent places**, and they reach us at different times:

```
 Merchant ──► OrbitPay ──► PSP ──► Card scheme / acquirer ──► Bank
                 ▲            │
                 │            ├── (A) Real-time webhooks: AUTHORISED, CAPTURED,
                 │            │       REFUNDED, CHARGEBACK, ... (seconds to days)
                 │            │
                 │            └── (B) Settlement report files: what the PSP actually
                 │                    paid out, net of fees (T+1 … T+3, daily batch)
                 └── Finance, Ops and Merchants need (A) and (B) to agree
```

- **(A) Payment events** say what *should* happen to the money. They arrive through webhooks, **at least once**, often out of order and sometimes days late. Chargebacks can arrive months later.
- **(B) Settlement files** say what *actually* happened to the money: gross amount, interchange and scheme fees, PSP markup, net payout and batch/payout reference. Every PSP uses a different format (CSV with different column sets, sometimes XLSX or JSON), and PSPs change these formats without warning.

**Reconciliation** is the process of proving that (A) and (B) agree, transaction by transaction and payout by payout.

## 2. The Problem

Today, OrbitPay's finance and operations teams reconcile PSP settlements against internal payment records **manually**, using spreadsheets and ad-hoc SQL. This causes the following problems:

1. **Duplicate and missing data.** Webhook retries create duplicate events, and failed processing silently drops others. Nobody can say with confidence: *"every event we received is stored exactly once."*
2. **Late and out-of-order events corrupt state.** A `REFUNDED` event processed before its `CAPTURED` event, or a chargeback arriving 60 days later, leaves payments in the wrong status and makes reports incorrect.
3. **Schema changes break ingestion.** When a PSP adds, renames or reorders a column in its settlement file, the loader either fails (and finance is blocked) or, worse, loads the wrong values into the wrong columns without anyone noticing.
4. **Reconciliation is slow and incomplete.** Mismatches such as missing settlements, amount differences, unexpected fees, FX differences and settled-but-never-captured payments are found days or weeks late, if they are found at all. Unexplained differences become **financial losses and audit findings**.
5. **No data-quality visibility.** No one measures freshness, completeness or validity, so problems are found by customers or by finance at month-end close.

## 3. Problem Statement (one paragraph, for the interview)

> OrbitPay receives payment events from multiple PSPs as at-least-once, out-of-order webhooks, and receives settlement files in PSP-specific, evolving formats. Because there is no reliable ingestion layer, data is duplicated, lost or misinterpreted, and finance cannot reconcile what we *expected* to be paid with what we *were* paid. We need an ingestion service that lands both sources into PostgreSQL **exactly once in effect** (idempotent), tolerates late arrivals and schema changes without losing or corrupting data, and produces daily reconciliation and data-quality results that finance and engineering can trust and audit.

## 4. Stakeholders

| Stakeholder | What they need |
|---|---|
| **Finance / Treasury** | Daily reconciliation: matched, unmatched and mismatched transactions, plus fees, with an audit trail |
| **Payment Operations** | Fast detection of missing settlements, stuck payments and PSP incidents |
| **Merchants (indirectly)** | Correct payout and fee reporting |
| **Data / Analytics** | A clean, deduplicated, well-modelled payments dataset |
| **Engineering / On-call** | Observable, replayable pipelines with clear failure modes |
| **Compliance / Audit** | Immutable raw data, lineage, and no storage of sensitive card data (PCI DSS scope) |

## 5. Goals

- **G1. Reliable ingestion of payment events.** Every received event is stored durably once, even when it is delivered several times.
- **G2. Reliable ingestion of settlement files.** Every file is processed once, re-processable on demand, and resilient to schema drift.
- **G3. Correct state despite disorder.** Late and out-of-order events produce the same final payment state as in-order delivery.
- **G4. Automated reconciliation.** Classify every captured payment and every settlement line as matched, mismatched (and why), or unmatched.
- **G5. Data-quality checks.** Automated freshness, completeness, validity and uniqueness checks, with alerts.
- **G6. Operability.** Structured logs, metrics, retries with backoff, a dead-letter path, safe replays and CI/CD.

## 6. Non-Goals (explicitly out of scope)

- Processing payments, holding funds or calling PSP payment APIs. We only **consume** what PSPs send.
- Storing PANs or other card data. We use only tokens and PSP references, which keeps the service out of PCI DSS cardholder-data scope.
- A full double-entry general ledger or accounting system. Reconciliation outputs *feed* finance; they don't replace the ERP.
- Real-time fraud detection.
- BI dashboards for business users. We expose tables and views plus operational Grafana/CloudWatch dashboards only.
- Multi-region active-active deployment.

## 7. Success Metrics

| # | Metric | Target |
|---|---|---|
| M1 | Duplicate rows in canonical event table | **0** (enforced by constraint, not hope) |
| M2 | Record accounting: `received = loaded + quarantined` per batch/file | **100%**, no silent drops |
| M3 | Event ingestion latency (receipt → queryable), p95 | **< 60 s** |
| M4 | Settlement file processed after landing | **< 15 min** |
| M5 | Reconciliation results available | **Daily by 08:00 UTC** for all files received |
| M6 | Auto-match rate (captures ↔ settlement lines, within T+3) | **≥ 98%**, and the rest is classified with a reason |
| M7 | Replay determinism | Re-ingesting the same inputs gives **identical** final state |
| M8 | Unknown schema change detected before bad data reaches canonical tables | **100%** |

## 8. Constraints & Assumptions

- **Volume (sized for a portfolio project, designed to scale):** about 50k events/day and 3 PSPs × 1 settlement file/day, with peaks of 20 events/s. The design should explain what changes at 100× this volume.
- **Delivery semantics:** PSP webhooks are **at least once**. Settlement files may be **re-issued/corrected** with the same business date.
- **Lateness:** most events arrive within minutes. Captures and refunds can arrive up to 7 days late, and chargebacks up to 120 days late.
- **Money:** stored as **integer minor units + ISO-4217 currency code**. No floats. Settlement currency can differ from the payment currency (FX).
- **Identity:** each event has a PSP event ID. Payments link to the PSP through a PSP reference and to OrbitPay through a merchant reference.
- **Data is synthetic:** a generator will produce realistic events and settlement files, including duplicates, late events and drifted schemas.
- **Phase 1** runs on AWS (RDS PostgreSQL, S3, SQS/Kinesis, Lambda/ECS, Step Functions, CloudFormation, CloudWatch). **Phase 2** re-platforms on open source (Docker Compose, Kafka + Debezium, Airflow, Terraform/LocalStack, Prometheus + Grafana). The **core Python domain logic should be shared** between phases. Only the adapters change.

## 9. Key Risks & Open Questions (to resolve in Requirements/Design)

1. **Which status transitions are legal?** For example, can a payment go from `REFUNDED` back to `CAPTURED`? We need a state machine that tolerates any arrival order.
2. **Matching keys:** do all PSPs include our merchant reference in settlement lines, or only the PSP reference? What about partial captures and split settlements?
3. **Tolerance rules:** what amount difference counts as a "mismatch" versus FX rounding?
4. **Corrected settlement files:** should a corrected file replace the original or be versioned alongside it?
5. **Schema drift policy:** for each kind of change, should we auto-accept (new optional column), quarantine (missing required column) or fail (type change)?
6. **Phase 1 transport:** SQS or Kinesis? This depends on ordering, replay and fan-out needs, and will be decided in the technical design.

## 10. Glossary

| Term | Meaning |
|---|---|
| **PSP** | Payment Service Provider (e.g. Adyen, Stripe), which processes the card payment |
| **Authorisation** | Issuer approves and reserves funds. No money moves yet |
| **Capture** | Merchant claims the authorised funds |
| **Settlement** | PSP pays out captured funds minus fees, in batches |
| **Interchange / scheme fees** | Fees from the issuer and card network (Visa/Mastercard), passed through by the PSP |
| **Chargeback** | Cardholder disputes a payment, and funds are reversed, often weeks later |
| **Reconciliation** | Matching internal records with external statements and explaining every difference |
| **Idempotency** | Processing the same input N times gives the same result as processing it once |
| **Late-arriving data** | Data whose event time is much earlier than its processing time |
| **Schema drift** | Unannounced changes to the structure of a source's data |
