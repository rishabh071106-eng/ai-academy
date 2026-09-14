#!/usr/bin/env python3
"""Exports every lab table to csv/<folder>/<table>.csv — upload the csv/ folder as-is to your
S3 bucket for the Athena and Snowflake exercises in aws/README.md (folder names match the SQL there).
Requires only Python (uses SQLite)."""
import csv, os, sqlite3, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "custody_lab.db")
if not os.path.exists(DB):
    subprocess.run([sys.executable, os.path.join(HERE, "run_sqlite.py"), "1"], check=True, stdout=subprocess.DEVNULL)
os.makedirs(os.path.join(HERE, "csv"), exist_ok=True)
con = sqlite3.connect(DB)
FOLDERS = {"dim_client": "clients", "dim_account": "accounts", "dim_security": "securities",
           "dim_date": "dates", "dim_fund": "funds", "fact_positions": "positions",
           "fact_transactions": "transactions", "fact_trades": "trades",
           "fact_corporate_actions": "corporate_actions", "fact_nav": "nav"}
for t, folder in FOLDERS.items():
    cur = con.execute(f"SELECT * FROM {t}")
    os.makedirs(os.path.join(HERE, "csv", folder), exist_ok=True)
    path = os.path.join(HERE, "csv", folder, f"{t}.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow([d[0] for d in cur.description])
        wr.writerows(cur.fetchall())
    print(f"wrote {path}")
