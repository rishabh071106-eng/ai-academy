-- =====================================================================
--  Custody Data Lab — 12 queries a Digital Experience VP should be able to READ
--  As-of business date for every query: 2026-09-11 (a Friday).
--  Each block starts with "-- ==== Q<n>" so run_sqlite.py can run them one by one.
--  Portable across PostgreSQL, SQLite and Snowflake (no vendor-only syntax).
-- =====================================================================

-- ==== Q1  What does one account hold today?  (filter + project — the "holdings" screen)
SELECT security_key, quantity, market_value_usd
FROM fact_positions
WHERE account_key = 'A-1001' AND position_date = '2026-09-11'
ORDER BY market_value_usd DESC;

-- ==== Q2  Same, but readable — join to the security dimension (the point of a star schema)
SELECT s.security_name, s.asset_class, s.issue_currency, p.quantity, p.market_value_usd
FROM fact_positions p
JOIN dim_security s ON s.security_key = p.security_key
WHERE p.account_key = 'A-1001' AND p.position_date = '2026-09-11'
ORDER BY p.market_value_usd DESC;

-- ==== Q3  Client's total value by asset class, across ALL its accounts  (the portfolio pie chart)
SELECT s.asset_class,
       ROUND(SUM(p.market_value_usd), 2) AS mv_usd,
       COUNT(DISTINCT p.account_key)     AS accounts_holding
FROM fact_positions p
JOIN dim_security s ON s.security_key = p.security_key
JOIN dim_account  a ON a.account_key  = p.account_key
WHERE a.client_key = 'C-MERIDIAN' AND p.position_date = '2026-09-11'
GROUP BY s.asset_class
ORDER BY mv_usd DESC;

-- ==== Q4  Concentration check: any single holding above USD 100m?  (HAVING filters groups)
SELECT a.account_name, s.security_name, ROUND(SUM(p.market_value_usd), 2) AS mv_usd
FROM fact_positions p
JOIN dim_account  a ON a.account_key  = p.account_key
JOIN dim_security s ON s.security_key = p.security_key
WHERE p.position_date = '2026-09-11'
GROUP BY a.account_name, s.security_name
HAVING SUM(p.market_value_usd) > 100000000
ORDER BY mv_usd DESC;

-- ==== Q5  The exceptions screen: every trade that has NOT settled, with why  (T+1 world)
SELECT t.trade_id, a.account_name, s.security_name, t.side, t.quantity,
       t.trade_date, t.intended_settle_date, t.status, t.fail_reason, t.counterparty
FROM fact_trades t
JOIN dim_account  a ON a.account_key  = t.account_key
JOIN dim_security s ON s.security_key = t.security_key
WHERE t.status <> 'SETTLED'
ORDER BY CASE t.status WHEN 'FAILED' THEN 0 WHEN 'PENDING' THEN 1 ELSE 2 END, t.intended_settle_date;

-- ==== Q6  Affirmation discipline: US trades affirmed AFTER the 21:00 ET same-day cutoff
SELECT t.trade_id, a.client_key, s.security_name, t.trade_date, t.affirmed_at, t.status
FROM fact_trades t
JOIN dim_account  a ON a.account_key  = t.account_key
JOIN dim_security s ON s.security_key = t.security_key
WHERE s.settlement_market IN ('DTC', 'Fedwire')
  AND (t.affirmed_at IS NULL
       OR CAST(t.affirmed_at AS VARCHAR(19)) > CAST(t.trade_date AS VARCHAR(10)) || ' 21:00:00')
ORDER BY t.trade_date;

-- ==== Q7  Corporate-action deadline tracker: voluntary events still unanswered, soonest first
SELECT ca.event_id, ca.event_type, c.client_name, a.account_name, s.security_name,
       ca.client_deadline, ca.market_deadline, ca.election_status, ca.est_value_usd
FROM fact_corporate_actions ca
JOIN dim_account  a ON a.account_key  = ca.account_key
JOIN dim_client   c ON c.client_key   = a.client_key
JOIN dim_security s ON s.security_key = ca.security_key
WHERE ca.election_required = TRUE AND ca.election_status IN ('PENDING', 'DEFAULTED')
ORDER BY ca.client_deadline;

-- ==== Q8  NAV status board: is tonight's NAV out, and did any fund move oddly vs its market?
SELECT f.fund_name, n.valuation_date, n.nav_per_share, n.status, n.published_at,
       n.benchmark_move_pct,
       ROUND(100.0 * (n.nav_per_share / LAG(n.nav_per_share) OVER (PARTITION BY n.fund_key ORDER BY n.valuation_date) - 1), 4) AS nav_move_pct
FROM fact_nav n
JOIN dim_fund f ON f.fund_key = n.fund_key
ORDER BY f.fund_name, n.valuation_date DESC;

-- ==== Q9  Running cash balance for an account  (the "balance over time" chart on every portal)
SELECT t.trade_date, t.txn_type, t.description, t.amount_usd,
       SUM(t.amount_usd) OVER (PARTITION BY t.account_key ORDER BY t.trade_date, t.txn_id
                               ROWS UNBOUNDED PRECEDING) AS running_balance
FROM fact_transactions t
WHERE t.account_key = 'A-1001'
ORDER BY t.trade_date, t.txn_id;

-- ==== Q10 Day-over-day change in a client's total value  (the "what moved?" question)
WITH daily AS (
  SELECT p.position_date, SUM(p.market_value_usd) AS total_mv
  FROM fact_positions p
  JOIN dim_account a ON a.account_key = p.account_key
  WHERE a.client_key = 'C-MERIDIAN'
  GROUP BY p.position_date
)
SELECT position_date,
       ROUND(total_mv, 2) AS total_mv,
       ROUND(total_mv - LAG(total_mv) OVER (ORDER BY position_date), 2) AS dod_change,
       ROUND(100.0 * (total_mv / LAG(total_mv) OVER (ORDER BY position_date) - 1), 3) AS dod_pct
FROM daily
ORDER BY position_date DESC;

-- ==== Q11 Top 2 holdings per asset class for a client  (window RANK without collapsing rows)
SELECT asset_class, security_name, mv_usd, rnk
FROM (
  SELECT s.asset_class, s.security_name, ROUND(SUM(p.market_value_usd), 2) AS mv_usd,
         RANK() OVER (PARTITION BY s.asset_class ORDER BY SUM(p.market_value_usd) DESC) AS rnk
  FROM fact_positions p
  JOIN dim_security s ON s.security_key = p.security_key
  JOIN dim_account  a ON a.account_key  = p.account_key
  WHERE a.client_key = 'C-MERIDIAN' AND p.position_date = '2026-09-11'
  GROUP BY s.asset_class, s.security_name
) ranked
WHERE rnk <= 2
ORDER BY asset_class, rnk;

-- ==== Q12 Data freshness SLA check: which accounts' positions landed AFTER the 06:00 promise?
SELECT p.position_date, a.account_name, p.source_system,
       MAX(p.loaded_at) AS last_loaded_at,
       CASE WHEN MAX(CAST(p.loaded_at AS VARCHAR(19))) > CAST(p.position_date AS VARCHAR(10)) || ' 06:00:00'
            THEN 'SLA BREACH' ELSE 'OK' END AS freshness_status
FROM fact_positions p
JOIN dim_account a ON a.account_key = p.account_key
WHERE p.position_date = '2026-09-11'
GROUP BY p.position_date, a.account_name, p.source_system
ORDER BY freshness_status DESC, a.account_name;

-- ==== Q13 Entitlements in the data layer: a secure view that only ever shows ONE client's rows
--  (This is how Snowflake Secure Data Sharing enforces "you see only your accounts".)
DROP VIEW IF EXISTS v_positions_meridian;
CREATE VIEW v_positions_meridian AS
SELECT p.position_date, a.account_name, s.security_name, s.asset_class, p.quantity, p.market_value_usd
FROM fact_positions p
JOIN dim_account  a ON a.account_key  = p.account_key
JOIN dim_security s ON s.security_key = p.security_key
WHERE a.client_key = 'C-MERIDIAN';
SELECT account_name, COUNT(*) AS rows_visible, ROUND(SUM(market_value_usd), 2) AS mv_usd
FROM v_positions_meridian
WHERE position_date = '2026-09-11'
GROUP BY account_name
ORDER BY account_name;

-- =====================================================================
--  DIGITAL EXPERIENCE QUERIES — one per capability named in JD R-790937
-- =====================================================================

-- ==== Q14 IAM: who can see or act on account A-1001, and at what level  (the entitlement review screen)
SELECT u.user_name, u.job_role, c.client_name AS user_belongs_to, e.permission, e.granted_by, e.expires_at,
       u.mfa_enabled, u.status
FROM fact_user_entitlements e
JOIN dim_user   u ON u.user_key   = e.user_key
JOIN dim_client c ON c.client_key = u.client_key
WHERE e.account_key = 'A-1001'
ORDER BY CASE e.permission WHEN 'ADMIN' THEN 0 WHEN 'INSTRUCT' THEN 1 ELSE 2 END, u.user_name;

-- ==== Q15 IAM findings: cross-client grants, admins without MFA, dormant users still entitled, expired grants
SELECT 'CROSS_CLIENT_ACCESS' AS finding, u.user_name, e.account_key, e.permission
FROM fact_user_entitlements e
JOIN dim_user u ON u.user_key = e.user_key
JOIN dim_account a ON a.account_key = e.account_key
WHERE a.client_key <> u.client_key
UNION ALL
SELECT 'PRIVILEGED_NO_MFA', u.user_name, e.account_key, e.permission
FROM fact_user_entitlements e JOIN dim_user u ON u.user_key = e.user_key
WHERE e.permission IN ('ADMIN','INSTRUCT') AND u.mfa_enabled = FALSE
UNION ALL
SELECT 'DORMANT_OR_DISABLED_STILL_ENTITLED', u.user_name, e.account_key, e.permission
FROM fact_user_entitlements e JOIN dim_user u ON u.user_key = e.user_key
WHERE u.status <> 'ACTIVE'
UNION ALL
SELECT 'GRANT_EXPIRED', u.user_name, e.account_key, e.permission
FROM fact_user_entitlements e JOIN dim_user u ON u.user_key = e.user_key
WHERE e.expires_at IS NOT NULL AND e.expires_at < '2026-09-11'
ORDER BY finding, user_name;

-- ==== Q16 Alerts: volume, delivery and acknowledgement rate by type and severity  (is the notification framework working?)
SELECT alert_type, severity,
       COUNT(*)                                            AS sent,
       SUM(CASE WHEN delivered_at IS NULL THEN 1 ELSE 0 END)     AS delivery_failed,
       SUM(CASE WHEN acknowledged_at IS NOT NULL THEN 1 ELSE 0 END) AS acknowledged,
       ROUND(100.0 * SUM(CASE WHEN acknowledged_at IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS ack_pct
FROM fact_alerts
GROUP BY alert_type, severity
ORDER BY CASE severity WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1 ELSE 2 END, alert_type;

-- ==== Q17 Alerts: the escalation list — unacknowledged CRITICAL/HIGH alerts about money at stake, with every channel tried
SELECT a.related_ref, a.alert_type, c.client_name, u.user_name,
       COUNT(*) AS attempts,
       MIN(a.created_at) AS first_sent, MAX(a.created_at) AS last_sent,
       SUM(CASE WHEN a.delivered_at IS NULL THEN 1 ELSE 0 END) AS failed_deliveries
FROM fact_alerts a
JOIN dim_client c ON c.client_key = a.client_key
JOIN dim_user   u ON u.user_key   = a.user_key
WHERE a.severity IN ('CRITICAL','HIGH') AND a.related_ref IS NOT NULL
GROUP BY a.related_ref, a.alert_type, c.client_name, u.user_name
HAVING SUM(CASE WHEN a.acknowledged_at IS NOT NULL THEN 1 ELSE 0 END) = 0
ORDER BY attempts DESC, first_sent;

-- ==== Q18 Documents: published but never opened, by client and type  (what we generate that nobody reads, and the one they should have)
SELECT c.client_name, d.doc_type,
       COUNT(*) AS published,
       SUM(CASE WHEN d.first_opened_at IS NULL THEN 1 ELSE 0 END) AS never_opened,
       SUM(d.download_count) AS downloads
FROM fact_documents d
JOIN dim_client c ON c.client_key = d.client_key
WHERE d.published_at IS NOT NULL
GROUP BY c.client_name, d.doc_type
ORDER BY never_opened DESC, c.client_name;

-- ==== Q19 Self-service reporting: self-service ratio per client  (the JD's "adoption through self-service" outcome, as a number)
SELECT c.client_name,
       SUM(CASE WHEN r.run_type = 'SELF_SERVICE' THEN 1 ELSE 0 END) AS self_service,
       SUM(CASE WHEN r.run_type = 'SCHEDULED'    THEN 1 ELSE 0 END) AS scheduled,
       SUM(CASE WHEN r.run_type = 'SERVICE_DESK' THEN 1 ELSE 0 END) AS service_desk,
       ROUND(100.0 * SUM(CASE WHEN r.run_type = 'SELF_SERVICE' THEN 1 ELSE 0 END)
             / SUM(CASE WHEN r.run_type <> 'SCHEDULED' THEN 1 ELSE 0 END), 1) AS self_service_pct_of_adhoc,
       ROUND(AVG(CASE WHEN r.run_type = 'SERVICE_DESK' THEN r.duration_ms END) / 60000.0, 1) AS avg_desk_minutes
FROM fact_report_runs r
JOIN dim_client c ON c.client_key = r.client_key
GROUP BY c.client_name
ORDER BY self_service_pct_of_adhoc;

-- ==== Q20 The Digital Experience scorecard: one row per client across all four capabilities
SELECT c.client_name,
       (SELECT COUNT(*) FROM dim_user u WHERE u.client_key = c.client_key AND u.status = 'ACTIVE') AS active_users,
       (SELECT COUNT(*) FROM dim_user u WHERE u.client_key = c.client_key AND u.sso_provider = 'CLIENT_IDP') AS federated_users,
       (SELECT ROUND(100.0 * SUM(CASE WHEN a.acknowledged_at IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 0)
          FROM fact_alerts a WHERE a.client_key = c.client_key AND a.severity <> 'INFO') AS actionable_alert_ack_pct,
       (SELECT ROUND(100.0 * SUM(CASE WHEN d.first_opened_at IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 0)
          FROM fact_documents d WHERE d.client_key = c.client_key AND d.published_at IS NOT NULL) AS docs_opened_pct,
       (SELECT ROUND(100.0 * SUM(CASE WHEN r.run_type = 'SELF_SERVICE' THEN 1 ELSE 0 END)
                     / SUM(CASE WHEN r.run_type <> 'SCHEDULED' THEN 1 ELSE 0 END), 0)
          FROM fact_report_runs r WHERE r.client_key = c.client_key) AS self_service_pct
FROM dim_client c
ORDER BY c.client_name;
