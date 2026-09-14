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
