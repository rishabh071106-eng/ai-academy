# Tableau lab — build the Digital Experience dashboard

**Download.** Tableau Public is free and has the full authoring UI; it only connects to files and publishes to your public profile (never use real data). Tableau Desktop has a 14-day trial and also connects to PostgreSQL and Snowflake. Get either at tableau.com. Sigma (sigmacomputing.com) is the cloud alternative named in the JD: it runs on top of Snowflake; use the free trial once your Snowflake trial exists.

**Data.** `python3 export_flat.py` writes seven wide CSVs into `data/`. Tableau: Connect → Text file → pick one; add the others with *Add* and relate them on `client_name` where needed.

## Sheet by sheet (about 60 minutes)

1. **Fails board** (trades_flat). Rows: `client_name`, `account_name`. Columns: `status`. Marks: count of `trade_id`. Filter `status` ≠ SETTLED. Colour by `fail_reason`. Sort so FAILED is first. This is Q5 as a picture.
2. **Deadline calendar** (corporate_actions_flat). Columns: `client_deadline` (exact date). Rows: `client_name`. Marks: circle, size `est_value_usd`, colour `election_status` (DEFAULTED red, PENDING amber). Add a reference line at today's date (2026-09-11). Q7 as a picture.
3. **Alert funnel** (alerts_flat). Create calculated fields `Delivered = NOT ISNULL([delivered_at])` and `Acknowledged = NOT ISNULL([acknowledged_at])`. Bar chart: rows `alert_type`, columns count of sent, delivered, acknowledged. Colour by `severity`. Q16.
4. **Time to acknowledge** (alerts_flat). Calculated field `Hours to ack = DATEDIFF('minute',[created_at],[acknowledged_at])/60`. Box plot by `severity`. The Python lab computes the same number; they should match.
5. **Documents nobody reads** (documents_flat). Calculated field `Opened = NOT ISNULL([first_opened_at])`. Stacked bar by `doc_type`, colour Opened true/false. Q18.
6. **Self-service ratio** (report_runs_flat). Calculated field `Self-service % = SUM(IF [run_type]='SELF_SERVICE' THEN 1 END) / SUM(IF [run_type]<>'SCHEDULED' THEN 1 END)`. Bar per `client_name`, reference line at a 70% target. Q19.
7. **Entitlement review** (entitlements_flat). Text table: `user_name`, `account_name`, `permission`, `mfa_enabled`, `expires_at`. Highlight rows where `user_client` ≠ `account_client` with a calculated field `Cross-client = [user_client] <> [account_client]`. Q15.

**Dashboard.** New Dashboard, 1200 × 800. Exceptions first: sheets 1 and 2 across the top, 3 and 6 in the middle, 5 and 7 at the bottom. Add a `client_name` filter and apply it to all sheets (Filter → Apply to Worksheets → All Using This Data Source). Add a title with the as-of date. Publish to Tableau Public (File → Save to Tableau Public) and send yourself the link.

**What to notice, as the product leader.** Every sheet is a metric you would put in a client QBR or your own scorecard. The calculated fields are exactly the definitions that belong in a data glossary (see `../governance/glossary.csv`): if "acknowledged" means something different in Tableau, in the portal and in the API, you have three numbers and one argument.
