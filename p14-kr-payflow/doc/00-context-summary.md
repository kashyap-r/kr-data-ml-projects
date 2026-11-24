# Running Context Summary — payflow-ingest (paste into a new chat)

**Who I am:** Data engineer, 20+ yrs (Python, SQL, Snowflake, AWS). Preparing for a Data Engineering role. 

Gaps to close: Docker/K8s, Airflow, Kafka streaming, Terraform, observability, CI/CD, payments-domain data.

**Project:** `payflow-ingest`. Ingest PSP payment events (webhooks) and PSP settlement files into PostgreSQL, handling duplicates, late/out-of-order events and schema drift, then expose reconciliation and data-quality checks. Fictional company: *OrbitPay*, a payment orchestrator using 3 PSPs.

**Stacks:**
- Phase 1 (AWS): Python, RDS PostgreSQL, Docker, S3, SQS or Kinesis, Lambda or ECS, CloudFormation, Step Functions, CloudWatch.

- Phase 2 (OSS): Python, PostgreSQL, Docker Compose, Kafka + Debezium, Airflow, Terraform (local/LocalStack), Prometheus + Grafana.
- Core domain logic is shared across phases; only the adapters change (ports and adapters).

**Non-negotiables:** pytest, structured logging, retries with backoff + idempotency, DQ checks, GitHub Actions CI, README, an interview-ready design doc.

**Working agreement:** Go phase by phase and stop for my review after each doc. Order: problem statement → requirements → functional design → technical design → test cases → code in small increments. Claude quizzes me like an interviewer after each doc and keeps this summary updated.

## Doc status
| # | Doc | Status |
|---|---|---|
| 01 | Problem statement | Draft v0.1, awaiting review |
| 02 | Requirements | Not started |
| 03 | Functional design | Not started |
| 04 | Technical design | Not started |
| 05 | Test cases | Not started |
| 06+ | Code increments | Not started |

## Decisions so far
- Money = integer minor units + ISO-4217. No floats.
- No card data (PANs) stored, so the service stays out of PCI DSS cardholder-data scope.
- Webhooks assumed at-least-once. Settlement files may be re-issued.
- Lateness assumptions: captures/refunds ≤ 7 days, chargebacks ≤ 120 days.
- Synthetic data generator produces duplicates, late events and drifted schemas.
- Success metrics M1–M8 (0 duplicates, 100% record accounting, p95 < 60 s events, files < 15 min, recon by 08:00 UTC, ≥ 98% auto-match, replay determinism, 100% drift detection).

## Open questions (carried forward)
1. Payment state machine for any arrival order
2. Matching keys and partial/split captures
3. Amount tolerance vs FX rounding
4. Corrected settlement files: replace or version?
5. Schema drift policy per kind of change (accept / quarantine / fail)
6. SQS vs Kinesis for phase 1
