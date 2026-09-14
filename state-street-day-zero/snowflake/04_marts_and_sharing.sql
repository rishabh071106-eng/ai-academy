-- STEP 4 — turn tables into client-facing products: governed marts, entitlement-filtered secure views, a share.
USE ROLE DX_ENGINEER; USE WAREHOUSE LAB_WH; USE DATABASE CUSTODY_LAB; USE SCHEMA MART;

-- 4a. The DX scorecard as a mart table (Q20 materialised). Clients and dashboards read THIS, never the facts directly.
CREATE OR REPLACE TABLE MART.DX_SCORECARD AS
SELECT c.client_key, c.client_name,
       (SELECT COUNT(*) FROM CORE.dim_user u WHERE u.client_key = c.client_key AND u.status = 'ACTIVE') AS active_users,
       (SELECT ROUND(100.0 * SUM(IFF(a.acknowledged_at IS NOT NULL,1,0)) / COUNT(*), 0)
          FROM CORE.fact_alerts a WHERE a.client_key = c.client_key AND a.severity <> 'INFO') AS actionable_alert_ack_pct,
       (SELECT ROUND(100.0 * SUM(IFF(d.first_opened_at IS NOT NULL,1,0)) / COUNT(*), 0)
          FROM CORE.fact_documents d WHERE d.client_key = c.client_key AND d.published_at IS NOT NULL) AS docs_opened_pct,
       (SELECT ROUND(100.0 * SUM(IFF(r.run_type = 'SELF_SERVICE',1,0)) / SUM(IFF(r.run_type <> 'SCHEDULED',1,0)), 0)
          FROM CORE.fact_report_runs r WHERE r.client_key = c.client_key) AS self_service_pct,
       CURRENT_TIMESTAMP() AS refreshed_at
FROM CORE.dim_client c;
SELECT * FROM MART.DX_SCORECARD ORDER BY client_name;

-- 4b. Entitlements in the data layer. A mapping of Snowflake roles to clients, then ONE secure view that filters by the caller's role.
CREATE OR REPLACE TABLE MART.ROLE_CLIENT_MAP (role_name STRING, client_key STRING);
INSERT INTO MART.ROLE_CLIENT_MAP VALUES ('CLIENT_MERIDIAN','C-MERIDIAN'), ('CLIENT_HALCYON','C-HALCYON'), ('CLIENT_ORIENT','C-ORIENT'), ('DX_ENGINEER','C-MERIDIAN'), ('DX_ENGINEER','C-HALCYON'), ('DX_ENGINEER','C-ORIENT');

CREATE OR REPLACE SECURE VIEW MART.V_CLIENT_POSITIONS AS
SELECT p.position_date, a.client_key, a.account_name, s.security_name, s.asset_class, p.quantity, p.market_value_usd
FROM CORE.fact_positions p
JOIN CORE.dim_account  a ON a.account_key  = p.account_key
JOIN CORE.dim_security s ON s.security_key = p.security_key
WHERE a.client_key IN (SELECT client_key FROM MART.ROLE_CLIENT_MAP WHERE role_name = CURRENT_ROLE());

-- 4c. Prove it. Create a client role, grant it ONLY the view, switch to it, and see only that client's rows.
USE ROLE ACCOUNTADMIN;
CREATE ROLE IF NOT EXISTS CLIENT_HALCYON;
GRANT ROLE CLIENT_HALCYON TO USER IDENTIFIER(CURRENT_USER());
GRANT USAGE ON WAREHOUSE LAB_WH TO ROLE CLIENT_HALCYON;
GRANT USAGE ON DATABASE CUSTODY_LAB TO ROLE CLIENT_HALCYON;
GRANT USAGE ON SCHEMA CUSTODY_LAB.MART TO ROLE CLIENT_HALCYON;
GRANT SELECT ON VIEW CUSTODY_LAB.MART.V_CLIENT_POSITIONS TO ROLE CLIENT_HALCYON;

USE ROLE CLIENT_HALCYON; USE WAREHOUSE LAB_WH;
SELECT client_key, account_name, COUNT(*) AS rows_visible, SUM(market_value_usd) AS mv
FROM CUSTODY_LAB.MART.V_CLIENT_POSITIONS WHERE position_date = '2026-09-11' GROUP BY 1,2;
-- Only Halcyon's two accounts appear. Try SELECT * FROM CUSTODY_LAB.CORE.FACT_POSITIONS as this role: "Object does not exist or not authorized".

-- 4d. Sharing: what you would do for a real client that has its own Snowflake account (needs their account locator; skip if none).
USE ROLE ACCOUNTADMIN;
CREATE SHARE IF NOT EXISTS HALCYON_DATA_SHARE;
GRANT USAGE ON DATABASE CUSTODY_LAB TO SHARE HALCYON_DATA_SHARE;
GRANT USAGE ON SCHEMA CUSTODY_LAB.MART TO SHARE HALCYON_DATA_SHARE;
GRANT SELECT ON VIEW CUSTODY_LAB.MART.V_CLIENT_POSITIONS TO SHARE HALCYON_DATA_SHARE;
-- ALTER SHARE HALCYON_DATA_SHARE ADD ACCOUNTS = <client_account_locator>;   -- the one line that turns it on; one line to revoke.

-- 4e. Two features you will quote in incident reviews.
USE ROLE DX_ENGINEER;
SELECT COUNT(*) FROM CORE.fact_positions AT (OFFSET => -60*10);          -- Time Travel: the table as it was 10 minutes ago
CREATE OR REPLACE TABLE CORE.fact_positions_test CLONE CORE.fact_positions;  -- zero-copy clone: full-size test data, instantly, no extra storage
DROP TABLE CORE.fact_positions_test;
