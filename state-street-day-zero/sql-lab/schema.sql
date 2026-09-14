-- =====================================================================
--  Custody Data Lab — star schema for a global custodian's client data
--  Portable SQL: runs unchanged on PostgreSQL, SQLite and Snowflake.
--  Grain contracts (memorise these — they are what you ask about in reviews):
--    fact_positions        one row per account, per security, per business date
--    fact_transactions     one row per cash movement on an account
--    fact_trades           one row per trade instruction (with its settlement status)
--    fact_corporate_actions one row per CA event, per affected account
--    fact_nav              one row per fund, per valuation date
-- =====================================================================

DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_corporate_actions;
DROP TABLE IF EXISTS fact_trades;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_positions;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_security;
DROP TABLE IF EXISTS dim_account;
DROP TABLE IF EXISTS dim_fund;
DROP TABLE IF EXISTS dim_client;

CREATE TABLE dim_client (
  client_key     VARCHAR(20)  PRIMARY KEY,
  client_name    VARCHAR(100) NOT NULL,
  client_type    VARCHAR(40)  NOT NULL,   -- Pension fund / Asset manager / Insurer / Sovereign
  domicile       VARCHAR(2)   NOT NULL,
  relationship_manager VARCHAR(60)
);

CREATE TABLE dim_account (
  account_key    VARCHAR(20)  PRIMARY KEY,
  client_key     VARCHAR(20)  NOT NULL REFERENCES dim_client(client_key),
  account_number VARCHAR(20)  NOT NULL,
  account_name   VARCHAR(100) NOT NULL,
  base_currency  VARCHAR(3)   NOT NULL,
  account_type   VARCHAR(30)  NOT NULL,   -- Custody / Fund / Cash
  legal_entity   VARCHAR(100)
);

CREATE TABLE dim_security (
  security_key   VARCHAR(20)  PRIMARY KEY,
  isin           VARCHAR(12)  NOT NULL,
  ticker         VARCHAR(12),
  security_name  VARCHAR(100) NOT NULL,
  asset_class    VARCHAR(30)  NOT NULL,   -- Equity / Government Bond / Corporate Bond / Cash Equivalent
  issuer_country VARCHAR(2)   NOT NULL,
  issue_currency VARCHAR(3)   NOT NULL,
  settlement_market VARCHAR(20) NOT NULL  -- the CSD that holds the final record
);

CREATE TABLE dim_date (
  date_key        DATE    PRIMARY KEY,
  year            INTEGER NOT NULL,
  quarter         INTEGER NOT NULL,
  month           INTEGER NOT NULL,
  month_name      VARCHAR(10) NOT NULL,
  day_of_week     VARCHAR(10) NOT NULL,
  is_business_day BOOLEAN NOT NULL,
  is_month_end    BOOLEAN NOT NULL
);

CREATE TABLE dim_fund (
  fund_key       VARCHAR(20)  PRIMARY KEY,
  fund_name      VARCHAR(100) NOT NULL,
  client_key     VARCHAR(20)  NOT NULL REFERENCES dim_client(client_key),
  fund_type      VARCHAR(20)  NOT NULL,   -- Mutual fund / ETF
  nav_deadline_local TIME    NOT NULL     -- when the client expects tonight's NAV
);

CREATE TABLE fact_positions (
  position_date     DATE        NOT NULL REFERENCES dim_date(date_key),
  account_key       VARCHAR(20) NOT NULL REFERENCES dim_account(account_key),
  security_key      VARCHAR(20) NOT NULL REFERENCES dim_security(security_key),
  quantity          NUMERIC(18,2) NOT NULL,
  price_local       NUMERIC(18,6) NOT NULL,
  fx_to_usd         NUMERIC(12,6) NOT NULL,
  market_value_usd  NUMERIC(18,2) NOT NULL,
  accrued_income_usd NUMERIC(18,2) NOT NULL,
  source_system     VARCHAR(30) NOT NULL,
  loaded_at         TIMESTAMP   NOT NULL,
  PRIMARY KEY (position_date, account_key, security_key)
);

CREATE TABLE fact_transactions (
  txn_id        INTEGER      PRIMARY KEY,
  account_key   VARCHAR(20)  NOT NULL REFERENCES dim_account(account_key),
  trade_date    DATE         NOT NULL,
  value_date    DATE         NOT NULL,
  txn_type      VARCHAR(30)  NOT NULL,  -- INJECTION / BUY / SELL / DIVIDEND / COUPON / FX / FEE
  currency      VARCHAR(3)   NOT NULL,
  amount_usd    NUMERIC(18,2) NOT NULL, -- positive = cash in, negative = cash out
  description   VARCHAR(120) NOT NULL
);

CREATE TABLE fact_trades (
  trade_id          VARCHAR(20)  PRIMARY KEY,
  account_key       VARCHAR(20)  NOT NULL REFERENCES dim_account(account_key),
  security_key      VARCHAR(20)  NOT NULL REFERENCES dim_security(security_key),
  side              VARCHAR(4)   NOT NULL,  -- BUY / SELL
  quantity          NUMERIC(18,2) NOT NULL,
  trade_date        DATE         NOT NULL,
  intended_settle_date DATE      NOT NULL,  -- T+1 in the US, T+2 in most of Europe/Asia
  actual_settle_date DATE,                  -- NULL until it settles
  status            VARCHAR(12)  NOT NULL,  -- MATCHED / AFFIRMED / SETTLED / FAILED / PENDING
  fail_reason       VARCHAR(60),            -- populated only when status = FAILED
  counterparty      VARCHAR(60) NOT NULL,
  affirmed_at       TIMESTAMP                -- US rule: affirm by 21:00 ET on trade date
);

CREATE TABLE fact_corporate_actions (
  event_id        VARCHAR(20)  NOT NULL,
  account_key     VARCHAR(20)  NOT NULL REFERENCES dim_account(account_key),
  security_key    VARCHAR(20)  NOT NULL REFERENCES dim_security(security_key),
  event_type      VARCHAR(30)  NOT NULL,   -- CASH_DIVIDEND / TENDER_OFFER / RIGHTS_ISSUE / DIVIDEND_OPTION / STOCK_SPLIT
  election_required BOOLEAN    NOT NULL,   -- TRUE = voluntary: client must answer
  announced_date  DATE         NOT NULL,
  record_date     DATE         NOT NULL,
  client_deadline DATE,                    -- custodian's own cutoff (earlier than the market's)
  market_deadline DATE,
  election_status VARCHAR(15)  NOT NULL,   -- N/A / PENDING / ELECTED / DEFAULTED
  eligible_quantity NUMERIC(18,2) NOT NULL,
  est_value_usd   NUMERIC(18,2) NOT NULL,  -- money at stake
  PRIMARY KEY (event_id, account_key)
);

CREATE TABLE fact_nav (
  fund_key         VARCHAR(20)  NOT NULL REFERENCES dim_fund(fund_key),
  valuation_date   DATE         NOT NULL,
  total_assets_usd NUMERIC(18,2) NOT NULL,
  total_liabilities_usd NUMERIC(18,2) NOT NULL,
  shares_outstanding NUMERIC(18,2) NOT NULL,
  nav_per_share    NUMERIC(12,4) NOT NULL,
  published_at     TIMESTAMP,              -- NULL = not yet published tonight
  status           VARCHAR(12)  NOT NULL,  -- PUBLISHED / IN_REVIEW / LATE
  benchmark_move_pct NUMERIC(8,4) NOT NULL,-- what the fund's market did that day
  PRIMARY KEY (fund_key, valuation_date)
);
