-- Snowflake (trial on AWS) — run section by section in a Snowsight worksheet.

-- 1. Compute: a tiny warehouse that suspends itself (the Day 18 cost-governance habit)
CREATE WAREHOUSE IF NOT EXISTS LAB_WH WITH WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;
CREATE DATABASE IF NOT EXISTS CUSTODY_LAB;
USE WAREHOUSE LAB_WH; USE DATABASE CUSTODY_LAB; USE SCHEMA PUBLIC;

-- 2. Tables: paste the whole of ../schema.sql here and run it (Snowflake accepts it unchanged).

-- 3a. Load, option A (simplest): paste the whole of ../seed.sql here and run it.

-- 3b. Load, option B (real-world): stage the CSVs from your S3 bucket and COPY INTO.
CREATE OR REPLACE FILE FORMAT LAB_CSV TYPE = 'CSV' SKIP_HEADER = 1 NULL_IF = ('') FIELD_OPTIONALLY_ENCLOSED_BY = '"';
CREATE OR REPLACE STAGE LAB_S3
  URL = 's3://<bucket>/'
  CREDENTIALS = (AWS_KEY_ID = '<access key id>' AWS_SECRET_KEY = '<secret access key>')
  FILE_FORMAT = LAB_CSV;
LIST @LAB_S3;                                    -- you should see your CSV files
COPY INTO DIM_CLIENT   FROM @LAB_S3/clients/;
COPY INTO DIM_ACCOUNT  FROM @LAB_S3/accounts/;
COPY INTO DIM_SECURITY FROM @LAB_S3/securities/;
COPY INTO DIM_DATE     FROM @LAB_S3/dates/;
COPY INTO DIM_FUND     FROM @LAB_S3/funds/;
COPY INTO FACT_POSITIONS          FROM @LAB_S3/positions/;
COPY INTO FACT_TRANSACTIONS       FROM @LAB_S3/transactions/;
COPY INTO FACT_TRADES             FROM @LAB_S3/trades/;
COPY INTO FACT_CORPORATE_ACTIONS  FROM @LAB_S3/corporate_actions/;
COPY INTO FACT_NAV                FROM @LAB_S3/nav/;
COPY INTO DIM_USER                FROM @LAB_S3/users/;
COPY INTO FACT_USER_ENTITLEMENTS  FROM @LAB_S3/entitlements/;
COPY INTO FACT_ALERTS             FROM @LAB_S3/alerts/;
COPY INTO FACT_DOCUMENTS          FROM @LAB_S3/documents/;
COPY INTO FACT_REPORT_RUNS        FROM @LAB_S3/report_runs/;
SELECT 'positions' AS t, COUNT(*) FROM FACT_POSITIONS UNION ALL SELECT 'trades', COUNT(*) FROM FACT_TRADES;

-- 4. Queries: paste ../queries.sql — all 20 run unchanged.  Snowflake-native version of Q11:
SELECT s.asset_class, s.security_name, SUM(p.market_value_usd) AS mv_usd,
       RANK() OVER (PARTITION BY s.asset_class ORDER BY SUM(p.market_value_usd) DESC) AS rnk
FROM FACT_POSITIONS p
JOIN DIM_SECURITY s ON s.security_key = p.security_key
JOIN DIM_ACCOUNT  a ON a.account_key  = p.account_key
WHERE a.client_key = 'C-MERIDIAN' AND p.position_date = '2026-09-11'
GROUP BY s.asset_class, s.security_name
QUALIFY rnk <= 2
ORDER BY s.asset_class, rnk;

-- 5. Entitlements at the data layer: a SECURE view is what you would share with one client.
CREATE OR REPLACE SECURE VIEW V_CLIENT_POSITIONS_MERIDIAN AS
SELECT p.position_date, a.account_name, s.security_name, s.asset_class, p.quantity, p.market_value_usd
FROM FACT_POSITIONS p
JOIN DIM_ACCOUNT  a ON a.account_key  = p.account_key
JOIN DIM_SECURITY s ON s.security_key = p.security_key
WHERE a.client_key = 'C-MERIDIAN';
-- (Secure Data Sharing = CREATE SHARE + GRANT SELECT ON this view; the client queries it live, nothing is copied.)

-- 6. Two features that make "we can't reproduce what the client saw" unacceptable:
SELECT COUNT(*) FROM FACT_POSITIONS AT (OFFSET => -60*5);        -- Time Travel: the table as of 5 minutes ago
CREATE TABLE FACT_POSITIONS_TEST CLONE FACT_POSITIONS;             -- zero-copy clone: instant full-size test data
DROP TABLE FACT_POSITIONS_TEST;

-- 7. Cost check: what did all this burn?
SELECT WAREHOUSE_NAME, SUM(CREDITS_USED) AS credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME > DATEADD('day', -1, CURRENT_TIMESTAMP()) GROUP BY 1;
