-- Data-quality rules for the custody lab, written as queries that return VIOLATIONS (zero rows = pass).
-- This is what a Collibra DQ / dbt test / Great Expectations suite does; run them with: python3 run_dq.py
-- Each block: "-- ==== RULE <name> | <dimension> | <severity>"

-- ==== RULE positions_unique_grain | uniqueness | BLOCK
SELECT position_date, account_key, security_key, COUNT(*) AS dupes
FROM fact_positions GROUP BY position_date, account_key, security_key HAVING COUNT(*) > 1;

-- ==== RULE positions_market_value_recomputes | accuracy | BLOCK
SELECT position_date, account_key, security_key, market_value_usd,
       ROUND(quantity * price_local * fx_to_usd / CASE WHEN security_key IN ('S-US-T34','S-DE-BUND31','S-GB-GILT35','S-US-IBM28','S-US-TBILL') THEN 100 ELSE 1 END, 2) AS recomputed
FROM fact_positions
WHERE ABS(market_value_usd - quantity * price_local * fx_to_usd / CASE WHEN security_key IN ('S-US-T34','S-DE-BUND31','S-GB-GILT35','S-US-IBM28','S-US-TBILL') THEN 100 ELSE 1 END) > 1.0;

-- ==== RULE positions_freshness_0600 | timeliness | WARN
SELECT position_date, account_key, MAX(loaded_at) AS loaded_at
FROM fact_positions GROUP BY position_date, account_key
HAVING MAX(CAST(loaded_at AS VARCHAR(19))) > CAST(position_date AS VARCHAR(10)) || ' 06:00:00';

-- ==== RULE trades_fail_reason_present | completeness | BLOCK
SELECT trade_id, status, fail_reason FROM fact_trades WHERE status = 'FAILED' AND fail_reason IS NULL;

-- ==== RULE trades_status_in_set | validity | BLOCK
SELECT trade_id, status FROM fact_trades WHERE status NOT IN ('MATCHED','AFFIRMED','PENDING','SETTLED','FAILED');

-- ==== RULE ca_client_deadline_before_market | consistency | BLOCK
SELECT event_id, account_key, client_deadline, market_deadline FROM fact_corporate_actions
WHERE client_deadline IS NOT NULL AND market_deadline IS NOT NULL AND client_deadline >= market_deadline;

-- ==== RULE nav_recomputes | accuracy | BLOCK
SELECT fund_key, valuation_date, nav_per_share, ROUND((total_assets_usd - total_liabilities_usd) / shares_outstanding, 4) AS recomputed
FROM fact_nav WHERE ABS(nav_per_share - (total_assets_usd - total_liabilities_usd) / shares_outstanding) > 0.0001;

-- ==== RULE entitlements_no_cross_client | consistency | BLOCK
SELECT e.user_key, e.account_key, e.permission FROM fact_user_entitlements e
JOIN dim_user u ON u.user_key = e.user_key JOIN dim_account a ON a.account_key = e.account_key
WHERE u.client_key <> a.client_key;

-- ==== RULE entitlements_have_expiry | completeness | WARN
SELECT user_key, account_key, permission FROM fact_user_entitlements WHERE expires_at IS NULL;

-- ==== RULE alerts_ack_after_create | consistency | BLOCK
SELECT alert_id, created_at, acknowledged_at FROM fact_alerts
WHERE acknowledged_at IS NOT NULL AND CAST(acknowledged_at AS VARCHAR(19)) < CAST(created_at AS VARCHAR(19));

-- ==== RULE alerts_delivered | timeliness | WARN
SELECT alert_id, alert_type, channel, created_at FROM fact_alerts WHERE delivered_at IS NULL;

-- ==== RULE documents_published_after_generated | consistency | BLOCK
SELECT doc_id, generated_at, published_at FROM fact_documents
WHERE published_at IS NOT NULL AND CAST(published_at AS VARCHAR(19)) < CAST(generated_at AS VARCHAR(19));

-- ==== RULE documents_retention_set | completeness | BLOCK
SELECT doc_id FROM fact_documents WHERE retention_until IS NULL;
