# Custody Data Lab

A small, realistic star schema of a global custodian's client data (fictional clients), 13 queries that
map one-to-one to screens on a custody client portal, and three ways to run it: no-install SQLite,
PostgreSQL in Docker, and the cloud (Amazon RDS, S3 + Athena, Snowflake on AWS).

Companion to the **Day Zero briefing** page one folder up (`../index.html`) — read Step 6 there for the
guided walkthrough. This README is the quick reference.

## Run it in 60 seconds (no install beyond Python)

```bash
cd state-street-day-zero/sql-lab
python3 run_sqlite.py          # builds custody_lab.db and prints all 20 query results
python3 run_sqlite.py 5 7      # only Q5 (fails) and Q7 (corporate-action deadlines)
python3 run_sqlite.py --shell  # write your own SQL against the database
```

## Run it on real PostgreSQL

```bash
docker compose up -d           # PostgreSQL 16 on localhost:5432, schema + data preloaded
psql -h localhost -U lab -d custody_lab -f queries.sql      # password: lab
pip install psycopg2-binary pandas sqlalchemy && python3 connect.py
```
No Docker? Install PostgreSQL 16 (Windows: `winget install PostgreSQL.PostgreSQL.16`, macOS: `brew install postgresql@16`),
create the database `custody_lab` and a user `lab`/`lab`, then run `schema.sql` and `seed.sql`.

## Run it in the cloud

`python3 export_csv.py` produces one CSV per table in `csv/`, then follow `aws/README.md`.

## What is in here

| File | Purpose |
|---|---|
| `schema.sql` | 15 tables. Custody core: 5 dimensions (client, account, security, date, fund) and 5 facts (positions, transactions, trades, corporate actions, NAV). Digital Experience extension for the four JD capabilities: `dim_user` + `fact_user_entitlements` (IAM), `fact_alerts` (notifications), `fact_documents` (document management), `fact_report_runs` (self-service reporting). Grain documented in the file. |
| `seed.sql` | Generated data: 3 clients, 6 accounts, 9 securities, 5 business dates, 12 trades (2 failed), 9 corporate-action rows, 10 NAV rows. Regenerate with `python3 make_seed.py > seed.sql`. |
| `queries.sql` | Q1–Q13 custody screens; Q14–Q20 the Digital Experience capabilities: entitlement review and IAM findings, alert effectiveness and the escalation list, unread documents, self-service ratio, and a one-row-per-client DX scorecard. Portable SQL. |
| `run_sqlite.py` | Zero-install runner and shell. |
| `docker-compose.yml` | PostgreSQL 16 with the lab preloaded. |
| `connect.py` | Python + pandas connection (local or RDS). |
| `export_csv.py` | Tables to CSV for S3. |
| `aws/` | Step-by-step RDS, Athena and Snowflake guides plus their SQL. |

## The stories hidden in the data (find them with the queries)

- **Q5 / Q6** — two fails and a late affirmation: `T-90003` (counterparty short of SAP shares), `T-90006` (client short of EUR cash), `T-90011` (settlement-instruction mismatch in Japan); `T-90009` was affirmed at 21:40, after the US 21:00 cutoff.
- **Q7** — a tender offer worth USD 2.7m already **DEFAULTED** because nobody answered by the custodian's deadline; a USD 4.1m tender offer on SAP still pending with the deadline four days out.
- **Q8** — on 10 Sep the ETF's NAV moved +0.89% while its market fell 0.48%: the sanity check a fund accountant should have caught before publishing. Tonight's Income Fund NAV is still `IN_REVIEW`.
- **Q12** — the Japanese sub-custodian's positions landed at 06:52, breaching a 06:00 freshness promise.
- **Q15** — an RM granted herself VIEW on another client's account (cross-client access), two admins have no MFA, a dormant executive still holds expired grants, a disabled user is still entitled.
- **Q17** — the defaulted tender offer (CA-5005) had three alerts and zero acknowledgements; the Toyota election alert's SMS never delivered.
- **Q18** — Halcyon's tender notice was published and never opened, which is why CA-5005 defaulted.
- **Q19 / Q20** — Halcyon's self-service ratio is 25%: the service desk runs their reports for them. That is the adoption problem the JD asks you to fix, as a number.
