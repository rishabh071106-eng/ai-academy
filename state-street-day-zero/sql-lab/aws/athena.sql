-- Amazon Athena: query the lab CSVs directly in S3.  Replace <bucket> with your bucket name.
-- Run each CREATE separately (Athena runs one statement at a time).

CREATE DATABASE IF NOT EXISTS custody_lab;

CREATE EXTERNAL TABLE IF NOT EXISTS custody_lab.positions (
  position_date string, account_key string, security_key string,
  quantity double, price_local double, fx_to_usd double,
  market_value_usd double, accrued_income_usd double, source_system string, loaded_at string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
LOCATION 's3://<bucket>/positions/'
TBLPROPERTIES ('skip.header.line.count' = '1');

CREATE EXTERNAL TABLE IF NOT EXISTS custody_lab.trades (
  trade_id string, account_key string, security_key string, side string, quantity double,
  trade_date string, intended_settle_date string, actual_settle_date string,
  status string, fail_reason string, counterparty string, affirmed_at string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
LOCATION 's3://<bucket>/trades/'
TBLPROPERTIES ('skip.header.line.count' = '1');

CREATE EXTERNAL TABLE IF NOT EXISTS custody_lab.accounts (
  account_key string, client_key string, account_number string, account_name string,
  base_currency string, account_type string, legal_entity string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
LOCATION 's3://<bucket>/accounts/'
TBLPROPERTIES ('skip.header.line.count' = '1');

CREATE EXTERNAL TABLE IF NOT EXISTS custody_lab.securities (
  security_key string, isin string, ticker string, security_name string, asset_class string,
  issuer_country string, issue_currency string, settlement_market string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
LOCATION 's3://<bucket>/securities/'
TBLPROPERTIES ('skip.header.line.count' = '1');

-- Q3 again, now serverless against files: client value by asset class
SELECT s.asset_class, ROUND(SUM(p.market_value_usd), 2) AS mv_usd
FROM custody_lab.positions p
JOIN custody_lab.securities s ON s.security_key = p.security_key
JOIN custody_lab.accounts   a ON a.account_key  = p.account_key
WHERE a.client_key = 'C-MERIDIAN' AND p.position_date = '2026-09-11'
GROUP BY s.asset_class ORDER BY mv_usd DESC;

-- Q5 again: the exceptions screen
SELECT t.trade_id, a.account_name, s.security_name, t.status, t.fail_reason, t.intended_settle_date
FROM custody_lab.trades t
JOIN custody_lab.accounts   a ON a.account_key  = t.account_key
JOIN custody_lab.securities s ON s.security_key = t.security_key
WHERE t.status <> 'SETTLED' ORDER BY t.intended_settle_date;

-- Cost lesson: convert to Parquet (columnar, compressed) and compare "Data scanned" on the query above.
CREATE TABLE custody_lab.positions_parquet
WITH (format = 'PARQUET', external_location = 's3://<bucket>/positions_parquet/') AS
SELECT * FROM custody_lab.positions;
