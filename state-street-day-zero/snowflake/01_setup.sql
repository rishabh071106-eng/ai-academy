-- STEP 1 of the live project — first five minutes in Snowsight.
-- Paste this whole file into a new SQL worksheet and click "Run All" (the ▶ with a dropdown → Run All).

-- 1a. A role for the project. ACCOUNTADMIN is the trial's superuser; you use it once to set things up, then work as a lesser role.
USE ROLE ACCOUNTADMIN;
CREATE ROLE IF NOT EXISTS DX_ENGINEER;
GRANT ROLE DX_ENGINEER TO USER IDENTIFIER(CURRENT_USER());

-- 1b. Compute. A "virtual warehouse" is a cluster of servers that runs your queries. XSMALL is the cheapest (1 credit/hour).
--     AUTO_SUSPEND = 60 means it switches itself off after 60 idle seconds, so you never pay for it sitting there.
CREATE WAREHOUSE IF NOT EXISTS LAB_WH
  WITH WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Custody Digital Experience lab';

-- 1c. Storage. A database holds schemas; a schema holds tables. We keep raw loads, the conformed model and client-facing marts apart.
CREATE DATABASE IF NOT EXISTS CUSTODY_LAB;
CREATE SCHEMA IF NOT EXISTS CUSTODY_LAB.CORE     COMMENT = 'Conformed star schema: dims and facts';
CREATE SCHEMA IF NOT EXISTS CUSTODY_LAB.MART     COMMENT = 'Client-facing, governed views and tables';
CREATE SCHEMA IF NOT EXISTS CUSTODY_LAB.RAW      COMMENT = 'Files as received (S3 stage)';

-- 1d. Give the project role what it needs, then switch to it.
GRANT USAGE ON WAREHOUSE LAB_WH TO ROLE DX_ENGINEER;
GRANT ALL ON DATABASE CUSTODY_LAB TO ROLE DX_ENGINEER;
GRANT ALL ON ALL SCHEMAS IN DATABASE CUSTODY_LAB TO ROLE DX_ENGINEER;
GRANT ALL ON FUTURE TABLES IN SCHEMA CUSTODY_LAB.CORE TO ROLE DX_ENGINEER;
GRANT ALL ON FUTURE VIEWS  IN SCHEMA CUSTODY_LAB.MART TO ROLE DX_ENGINEER;

-- 1e. A guard rail: a resource monitor that suspends the warehouse if the lab burns more than 20 credits in a month.
CREATE RESOURCE MONITOR IF NOT EXISTS LAB_MONITOR WITH CREDIT_QUOTA = 20
  TRIGGERS ON 80 PERCENT DO NOTIFY ON 100 PERCENT DO SUSPEND;
ALTER WAREHOUSE LAB_WH SET RESOURCE_MONITOR = LAB_MONITOR;

USE ROLE DX_ENGINEER; USE WAREHOUSE LAB_WH; USE DATABASE CUSTODY_LAB; USE SCHEMA CORE;
SELECT CURRENT_ROLE() AS role, CURRENT_WAREHOUSE() AS warehouse, CURRENT_DATABASE() AS db, CURRENT_SCHEMA() AS schema;
-- Expected result: DX_ENGINEER | LAB_WH | CUSTODY_LAB | CORE
