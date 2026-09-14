# Snowflake live project — step files

Run in order in a Snowsight SQL worksheet. Each file is one phase of the live-project page.

| File | Phase | What you end up with |
|---|---|---|
| `01_setup.sql` | Set up the account | A role, a warehouse that auto-suspends, a database with RAW / CORE / MART schemas, a credit guard rail |
| `02_load.sql` | Load the custody data | 15 tables in CORE with the lab data (paste schema.sql and seed.sql) |
| `03_s3_stage.sql` | Load from S3 | The same data loaded through an external stage with COPY INTO, the way real pipelines do |
| `04_marts_and_sharing.sql` | Data products | A scorecard mart, a secure view that filters by the caller's role, a client role that proves it, a share, Time Travel, a clone |
| `05_cost_and_monitoring.sql` | Run it like a VP | Credits by warehouse and day, most expensive queries, who can see what, storage size |

Python write-back: `../python-lab/to_snowflake.py` pushes the pandas scorecard into `MART.DX_SCORECARD_PY` so you can compare it with the SQL version.
