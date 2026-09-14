-- STEP 3 — load from Amazon S3 the way a bank's pipeline does.
-- Prerequisites (done on the page, Phase 3): a bucket with the csv/ folders uploaded, and an IAM user with read-only access
-- whose access key id and secret you paste below. Never commit real keys to git.
USE ROLE DX_ENGINEER; USE WAREHOUSE LAB_WH; USE DATABASE CUSTODY_LAB; USE SCHEMA RAW;

CREATE OR REPLACE FILE FORMAT LAB_CSV
  TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"' NULL_IF = ('') EMPTY_FIELD_AS_NULL = TRUE;

CREATE OR REPLACE STAGE LAB_S3
  URL = 's3://custody-lab-<yourname>-2026/'
  CREDENTIALS = (AWS_KEY_ID = '<paste access key id>' AWS_SECRET_KEY = '<paste secret access key>')
  FILE_FORMAT = LAB_CSV;

LIST @LAB_S3;   -- expected: one row per CSV file, with size and last-modified. If this errors, the key or bucket name is wrong.

-- Truncate and reload the CORE tables from the files (same result as 2b, different mechanism).
USE SCHEMA CORE;
TRUNCATE TABLE fact_report_runs; TRUNCATE TABLE fact_documents; TRUNCATE TABLE fact_alerts; TRUNCATE TABLE fact_user_entitlements;
TRUNCATE TABLE dim_user; TRUNCATE TABLE fact_nav; TRUNCATE TABLE fact_corporate_actions; TRUNCATE TABLE fact_trades;
TRUNCATE TABLE fact_transactions; TRUNCATE TABLE fact_positions; TRUNCATE TABLE dim_fund; TRUNCATE TABLE dim_date;
TRUNCATE TABLE dim_security; TRUNCATE TABLE dim_account; TRUNCATE TABLE dim_client;

COPY INTO dim_client               FROM @RAW.LAB_S3/clients/;
COPY INTO dim_account              FROM @RAW.LAB_S3/accounts/;
COPY INTO dim_security             FROM @RAW.LAB_S3/securities/;
COPY INTO dim_date                 FROM @RAW.LAB_S3/dates/;
COPY INTO dim_fund                 FROM @RAW.LAB_S3/funds/;
COPY INTO fact_positions           FROM @RAW.LAB_S3/positions/;
COPY INTO fact_transactions        FROM @RAW.LAB_S3/transactions/;
COPY INTO fact_trades              FROM @RAW.LAB_S3/trades/;
COPY INTO fact_corporate_actions   FROM @RAW.LAB_S3/corporate_actions/;
COPY INTO fact_nav                 FROM @RAW.LAB_S3/nav/;
COPY INTO dim_user                 FROM @RAW.LAB_S3/users/;
COPY INTO fact_user_entitlements   FROM @RAW.LAB_S3/entitlements/;
COPY INTO fact_alerts              FROM @RAW.LAB_S3/alerts/;
COPY INTO fact_documents           FROM @RAW.LAB_S3/documents/;
COPY INTO fact_report_runs         FROM @RAW.LAB_S3/report_runs/;
-- Each COPY returns a row: file, status LOADED, rows_parsed, rows_loaded, errors_seen 0.

SELECT COUNT(*) AS positions FROM fact_positions;   -- 90 again
