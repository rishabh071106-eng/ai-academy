-- STEP 2 — put the custody data into Snowflake.
USE ROLE DX_ENGINEER; USE WAREHOUSE LAB_WH; USE DATABASE CUSTODY_LAB; USE SCHEMA CORE;

-- 2a. Tables: open ../sql-lab/schema.sql, copy ALL of it, paste it BELOW this line in the worksheet, Run All.
--     (Snowflake accepts the file unchanged. 15 tables appear under CUSTODY_LAB > CORE in the left-hand object tree.)

-- 2b. Data, the quick way: open ../sql-lab/seed.sql, copy all 293 INSERT statements, paste, Run All. Takes ~20 seconds.

-- 2c. Check. You should see these exact counts.
SELECT 'dim_client' AS t, COUNT(*) AS n FROM dim_client
UNION ALL SELECT 'fact_positions', COUNT(*) FROM fact_positions
UNION ALL SELECT 'fact_trades', COUNT(*) FROM fact_trades
UNION ALL SELECT 'fact_alerts', COUNT(*) FROM fact_alerts
UNION ALL SELECT 'fact_report_runs', COUNT(*) FROM fact_report_runs;
-- dim_client 3 | fact_positions 90 | fact_trades 12 | fact_alerts 25 | fact_report_runs 34

-- 2d. Data, the real-world way (Step 3 of the page): an external stage on S3 and COPY INTO. See 03_s3_stage.sql.
