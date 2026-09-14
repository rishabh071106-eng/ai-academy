#!/usr/bin/env python3
"""Write-back: compute the DX scorecard in pandas and push it into Snowflake as MART.DX_SCORECARD_PY.
This closes the loop of the live project: local analysis -> cloud mart -> BI tools read it.

    pip install "snowflake-connector-python[pandas]" pandas
    export SNOWFLAKE_ACCOUNT=<orgname-accountname>   # Snowsight: bottom-left account menu -> Account -> copy "Account identifier"
    export SNOWFLAKE_USER=<your user>  SNOWFLAKE_PASSWORD=<your password>
    python3 to_snowflake.py
"""
import os, sqlite3, subprocess, sys
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.join(HERE, "..", "sql-lab"); DB = os.path.join(LAB, "custody_lab.db")
if not os.path.exists(DB):
    subprocess.run([sys.executable, os.path.join(LAB, "run_sqlite.py"), "1"], check=True, stdout=subprocess.DEVNULL)

# 1. Compute locally (same logic as analyze.py, block 5)
con = sqlite3.connect(DB)
q = lambda s: pd.read_sql_query(s, con)
users = q("SELECT client_key, status, sso_provider FROM dim_user")
alerts = q("SELECT client_key, severity, acknowledged_at FROM fact_alerts")
docs = q("SELECT client_key, published_at, first_opened_at FROM fact_documents")
runs = q("SELECT client_key, run_type FROM fact_report_runs")
clients = q("SELECT client_key, client_name FROM dim_client").set_index("client_key")
score = pd.DataFrame({
    "ACTIVE_USERS": users[users.status == "ACTIVE"].groupby("client_key").size(),
    "FEDERATED_PCT": (100 * users.groupby("client_key")["sso_provider"].apply(lambda s: (s == "CLIENT_IDP").mean())).round(0),
    "ACTIONABLE_ALERT_ACK_PCT": (100 * alerts[alerts.severity != "INFO"].groupby("client_key")["acknowledged_at"].apply(lambda s: s.notna().mean())).round(0),
    "DOCS_OPENED_PCT": (100 * docs[docs.published_at.notna()].groupby("client_key")["first_opened_at"].apply(lambda s: s.notna().mean())).round(0),
    "SELF_SERVICE_PCT": (100 * runs[runs.run_type != "SCHEDULED"].groupby("client_key")["run_type"].apply(lambda s: (s == "SELF_SERVICE").mean())).round(0),
}).join(clients).reset_index().rename(columns={"client_key": "CLIENT_KEY", "client_name": "CLIENT_NAME"})
score["REFRESHED_AT"] = pd.Timestamp.utcnow().tz_localize(None)
print(score.to_string(index=False))

# 2. Push to Snowflake
cnx = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"], user=os.environ["SNOWFLAKE_USER"], password=os.environ["SNOWFLAKE_PASSWORD"],
    role=os.getenv("SNOWFLAKE_ROLE", "DX_ENGINEER"), warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "LAB_WH"),
    database="CUSTODY_LAB", schema="MART")
ok, chunks, rows, _ = write_pandas(cnx, score, "DX_SCORECARD_PY", auto_create_table=True, overwrite=True)
print(f"write_pandas ok={ok} rows={rows}")

# 3. Read it back next to the SQL version — the two should agree
cur = cnx.cursor()
cur.execute("""SELECT s.CLIENT_NAME, s.SELF_SERVICE_PCT AS sql_pct, p.SELF_SERVICE_PCT AS py_pct
               FROM MART.DX_SCORECARD s JOIN MART.DX_SCORECARD_PY p ON p.CLIENT_KEY = s.CLIENT_KEY ORDER BY 1""")
for r in cur.fetchall(): print(r)
cnx.close()
