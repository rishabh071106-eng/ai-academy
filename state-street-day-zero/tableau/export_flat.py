#!/usr/bin/env python3
"""Exports denormalised (already-joined) extracts for Tableau Public, Sigma or Excel into tableau/data/.
BI tools work best on wide, readable tables; the star schema stays in the database.
    python3 export_flat.py
"""
import os, sqlite3, subprocess, sys
import csv
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.join(HERE, "..", "sql-lab"); DB = os.path.join(LAB, "custody_lab.db")
if not os.path.exists(DB):
    subprocess.run([sys.executable, os.path.join(LAB, "run_sqlite.py"), "1"], check=True, stdout=subprocess.DEVNULL)
OUT = os.path.join(HERE, "data"); os.makedirs(OUT, exist_ok=True)
EXTRACTS = {
 "positions_flat": """SELECT p.position_date, c.client_name, a.account_name, a.account_type, s.security_name, s.asset_class,
                             s.issuer_country, s.issue_currency, p.quantity, p.market_value_usd, p.accrued_income_usd, p.source_system, p.loaded_at
                      FROM fact_positions p JOIN dim_account a ON a.account_key=p.account_key JOIN dim_client c ON c.client_key=a.client_key
                      JOIN dim_security s ON s.security_key=p.security_key""",
 "trades_flat": """SELECT t.trade_id, c.client_name, a.account_name, s.security_name, s.asset_class, s.settlement_market, t.side, t.quantity,
                          t.trade_date, t.intended_settle_date, t.actual_settle_date, t.status, t.fail_reason, t.counterparty, t.affirmed_at
                   FROM fact_trades t JOIN dim_account a ON a.account_key=t.account_key JOIN dim_client c ON c.client_key=a.client_key
                   JOIN dim_security s ON s.security_key=t.security_key""",
 "corporate_actions_flat": """SELECT ca.event_id, ca.event_type, c.client_name, a.account_name, s.security_name, ca.election_required,
                                     ca.announced_date, ca.record_date, ca.client_deadline, ca.market_deadline, ca.election_status, ca.est_value_usd
                              FROM fact_corporate_actions ca JOIN dim_account a ON a.account_key=ca.account_key
                              JOIN dim_client c ON c.client_key=a.client_key JOIN dim_security s ON s.security_key=ca.security_key""",
 "alerts_flat": """SELECT al.alert_id, c.client_name, u.user_name, u.job_role, u.region, al.alert_type, al.severity, al.channel, al.related_ref,
                          al.created_at, al.delivered_at, al.acknowledged_at
                   FROM fact_alerts al JOIN dim_client c ON c.client_key=al.client_key JOIN dim_user u ON u.user_key=al.user_key""",
 "documents_flat": """SELECT d.doc_id, c.client_name, a.account_name, d.doc_type, d.period_end, d.generated_at, d.published_at, d.first_opened_at,
                             d.download_count, d.size_kb, d.retention_until
                      FROM fact_documents d JOIN dim_client c ON c.client_key=d.client_key LEFT JOIN dim_account a ON a.account_key=d.account_key""",
 "report_runs_flat": """SELECT r.run_id, c.client_name, u.user_name, u.job_role, r.report_name, r.run_type, r.run_at, r.duration_ms,
                               r.rows_returned, r.export_format, r.as_of_date
                        FROM fact_report_runs r JOIN dim_client c ON c.client_key=r.client_key JOIN dim_user u ON u.user_key=r.user_key""",
 "entitlements_flat": """SELECT u.user_name, u.job_role, u.region, c.client_name AS user_client, a.account_name, ac.client_name AS account_client,
                                e.permission, e.granted_by, e.granted_at, e.expires_at, u.mfa_enabled, u.sso_provider, u.status
                         FROM fact_user_entitlements e JOIN dim_user u ON u.user_key=e.user_key JOIN dim_client c ON c.client_key=u.client_key
                         JOIN dim_account a ON a.account_key=e.account_key JOIN dim_client ac ON ac.client_key=a.client_key""",
}
con = sqlite3.connect(DB)
for name, sql in EXTRACTS.items():
    cur = con.execute(sql); path = os.path.join(OUT, f"{name}.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow([d[0] for d in cur.description]); w.writerows(cur.fetchall())
    print(f"wrote {path}")
