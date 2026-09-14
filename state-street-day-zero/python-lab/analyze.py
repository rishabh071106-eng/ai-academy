#!/usr/bin/env python3
"""Python for a data product leader — the four JD capabilities analysed with pandas.

    pip install pandas matplotlib
    python3 analyze.py            # prints five analyses and saves dx_scorecard.png

Reads the SQLite database the SQL lab builds (../sql-lab/custody_lab.db); builds it if missing.
Every block is the Python twin of a query in ../sql-lab/queries.sql, plus the things SQL is bad at:
time arithmetic, reshaping, and charts.
"""
import os, sqlite3, subprocess, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.join(HERE, "..", "sql-lab")
DB = os.path.join(LAB, "custody_lab.db")
if not os.path.exists(DB):
    subprocess.run([sys.executable, os.path.join(LAB, "run_sqlite.py"), "1"], check=True, stdout=subprocess.DEVNULL)

con = sqlite3.connect(DB)
def q(sql): return pd.read_sql_query(sql, con)
pd.set_option("display.width", 160); pd.set_option("display.max_columns", 20)

# ---------- 1. Alerts: time-to-acknowledge by severity (SQL cannot do date maths portably; pandas can) ----------
alerts = q("SELECT * FROM fact_alerts")
for col in ("created_at", "delivered_at", "acknowledged_at"):
    alerts[col] = pd.to_datetime(alerts[col])
alerts["hours_to_ack"] = (alerts["acknowledged_at"] - alerts["created_at"]).dt.total_seconds() / 3600
tta = (alerts.groupby("severity")
       .agg(sent=("alert_id", "count"),
            acknowledged=("acknowledged_at", lambda s: s.notna().sum()),
            median_hours_to_ack=("hours_to_ack", "median"),
            p90_hours_to_ack=("hours_to_ack", lambda s: s.quantile(0.9)))
       .reindex(["CRITICAL", "HIGH", "INFO"]).round(2))
print("\n1. Time to acknowledge, by severity\n", tta)

# ---------- 2. Alerts: channel effectiveness (which channel actually gets acted on) ----------
chan = (alerts.assign(acked=alerts["acknowledged_at"].notna(), failed=alerts["delivered_at"].isna())
        .groupby("channel").agg(sent=("alert_id", "count"), delivery_failed=("failed", "sum"), acked=("acked", "sum")))
chan["ack_rate_pct"] = (100 * chan["acked"] / chan["sent"]).round(0)
print("\n2. Channel effectiveness\n", chan.sort_values("ack_rate_pct", ascending=False))

# ---------- 3. Documents: time from publish to first open, and the never-opened list ----------
docs = q("SELECT d.*, c.client_name FROM fact_documents d JOIN dim_client c ON c.client_key = d.client_key")
for col in ("generated_at", "published_at", "first_opened_at"):
    docs[col] = pd.to_datetime(docs[col])
docs["hours_to_open"] = (docs["first_opened_at"] - docs["published_at"]).dt.total_seconds() / 3600
print("\n3. Hours from publish to first open, by document type\n",
      docs.groupby("doc_type")["hours_to_open"].agg(["count", "median", "max"]).round(1))
never = docs[docs["published_at"].notna() & docs["first_opened_at"].isna()][["doc_id", "client_name", "doc_type", "period_end"]]
print("\n   Published but never opened:\n", never.to_string(index=False))

# ---------- 4. Self-service: a pivot table (rows = client, columns = run type) ----------
runs = q("SELECT r.*, c.client_name FROM fact_report_runs r JOIN dim_client c ON c.client_key = r.client_key")
pivot = runs.pivot_table(index="client_name", columns="run_type", values="run_id", aggfunc="count", fill_value=0)
pivot["self_service_pct"] = (100 * pivot["SELF_SERVICE"] / (pivot["SELF_SERVICE"] + pivot["SERVICE_DESK"])).round(0)
desk_minutes = runs[runs["run_type"] == "SERVICE_DESK"].groupby("client_name")["duration_ms"].sum() / 60000
pivot["desk_minutes_spent"] = desk_minutes.round(0)
print("\n4. Report runs by type (pivot)\n", pivot)

# ---------- 5. The DX scorecard, joined in pandas from four frames, then charted ----------
users = q("SELECT client_key, status, sso_provider, mfa_enabled FROM dim_user")
clients = q("SELECT client_key, client_name FROM dim_client").set_index("client_key")
score = pd.DataFrame({
    "active_users": users[users.status == "ACTIVE"].groupby("client_key").size(),
    "federated_pct": (100 * users.groupby("client_key")["sso_provider"].apply(lambda s: (s == "CLIENT_IDP").mean())).round(0),
    "alert_ack_pct": (100 * alerts[alerts.severity != "INFO"].groupby("client_key")["acknowledged_at"].apply(lambda s: s.notna().mean())).round(0),
    "docs_opened_pct": (100 * docs[docs.published_at.notna()].groupby("client_key")["first_opened_at"].apply(lambda s: s.notna().mean())).round(0),
    "self_service_pct": (100 * runs[runs.run_type != "SCHEDULED"].groupby("client_key")["run_type"].apply(lambda s: (s == "SELF_SERVICE").mean())).round(0),
}).join(clients).set_index("client_name")
print("\n5. Digital Experience scorecard\n", score)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    metrics = ["federated_pct", "alert_ack_pct", "docs_opened_pct", "self_service_pct"]
    ax = score[metrics].plot.barh(figsize=(9, 4.5), width=0.8, color=["#1E6B55", "#3C8DBC", "#B4622B", "#7A6FBE"])
    ax.set_xlim(0, 100); ax.set_xlabel("percent"); ax.set_title("Digital Experience scorecard by client (sample data)")
    ax.legend(loc="lower right", frameon=False); ax.grid(axis="x", alpha=.3); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    plt.tight_layout(); out = os.path.join(HERE, "dx_scorecard.png"); plt.savefig(out, dpi=150)
    print(f"\nSaved chart: {out}")
except ImportError:
    print("\n(matplotlib not installed: pip install matplotlib to get the chart)")
