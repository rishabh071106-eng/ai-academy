#!/usr/bin/env python3
"""A working client-facing dashboard prototype in ~120 lines — the kind of thing you show a design team
before anyone writes a Figma frame.

    pip install streamlit pandas plotly
    streamlit run dashboard.py          # opens http://localhost:8501

Exceptions-first layout (the custody rule): fails and deadlines at the top, then cash, then holdings.
Entitlements are enforced in the query, not the UI: pick a user and you only see their accounts (Q13/Q14).
"""
import os, sqlite3, subprocess, sys
import pandas as pd
import plotly.express as px
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.join(HERE, "..", "sql-lab")
DB = os.path.join(LAB, "custody_lab.db")
if not os.path.exists(DB):
    subprocess.run([sys.executable, os.path.join(LAB, "run_sqlite.py"), "1"], check=True, stdout=subprocess.DEVNULL)
AS_OF = "2026-09-11"

@st.cache_data
def q(sql, params=()):
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query(sql, con, params=params)

st.set_page_config(page_title="Custody client portal (prototype)", layout="wide")
st.title("Client portal prototype")
st.caption(f"As of business date {AS_OF}. Sample data, fictional clients.")

# ---- identity: who is logged in decides what every query below can return ----
users = q("SELECT u.user_key, u.user_name, u.job_role, c.client_name FROM dim_user u JOIN dim_client c ON c.client_key=u.client_key WHERE u.status='ACTIVE' ORDER BY c.client_name, u.user_name")
choice = st.sidebar.selectbox("Signed in as", users.apply(lambda r: f"{r.user_name} · {r.job_role} · {r.client_name}", axis=1))
user_key = users.iloc[users.apply(lambda r: f"{r.user_name} · {r.job_role} · {r.client_name}", axis=1).tolist().index(choice)].user_key
ent = q("SELECT account_key, permission FROM fact_user_entitlements WHERE user_key=?", (user_key,))
accounts = tuple(ent.account_key.unique().tolist()) or ("NONE",)
ph = ",".join("?" * len(accounts))
st.sidebar.write("**Entitled accounts**"); st.sidebar.dataframe(ent, hide_index=True)

# ---- exceptions first ----
fails = q(f"""SELECT t.trade_id, a.account_name, s.security_name, t.side, t.quantity, t.intended_settle_date, t.status, t.fail_reason
              FROM fact_trades t JOIN dim_account a ON a.account_key=t.account_key JOIN dim_security s ON s.security_key=t.security_key
              WHERE t.status<>'SETTLED' AND t.account_key IN ({ph}) ORDER BY CASE t.status WHEN 'FAILED' THEN 0 ELSE 1 END""", accounts)
cas = q(f"""SELECT ca.event_id, ca.event_type, s.security_name, ca.client_deadline, ca.election_status, ca.est_value_usd
            FROM fact_corporate_actions ca JOIN dim_security s ON s.security_key=ca.security_key
            WHERE ca.election_required=1 AND ca.election_status IN ('PENDING','DEFAULTED') AND ca.account_key IN ({ph}) ORDER BY ca.client_deadline""", accounts)
c1, c2, c3 = st.columns(3)
c1.metric("Failed trades", int((fails.status == "FAILED").sum()))
c2.metric("Elections due", int((cas.election_status == "PENDING").sum()), delta=f"{int((cas.election_status=='DEFAULTED').sum())} defaulted", delta_color="inverse")
c3.metric("Money at stake (USD)", f"{cas.est_value_usd.sum():,.0f}")
left, right = st.columns(2)
with left:
    st.subheader("Unsettled trades"); st.dataframe(fails, hide_index=True, use_container_width=True)
with right:
    st.subheader("Corporate-action deadlines"); st.dataframe(cas, hide_index=True, use_container_width=True)

# ---- cash ----
st.subheader("Cash running balance")
cash = q(f"""SELECT t.account_key, t.trade_date, t.amount_usd,
              SUM(t.amount_usd) OVER (PARTITION BY t.account_key ORDER BY t.trade_date, t.txn_id ROWS UNBOUNDED PRECEDING) AS balance
              FROM fact_transactions t WHERE t.account_key IN ({ph}) ORDER BY t.trade_date""", accounts)
if len(cash):
    st.plotly_chart(px.line(cash, x="trade_date", y="balance", color="account_key", markers=True), use_container_width=True)

# ---- holdings ----
st.subheader("Holdings by asset class")
pos = q(f"""SELECT a.account_name, s.asset_class, s.security_name, p.market_value_usd
            FROM fact_positions p JOIN dim_account a ON a.account_key=p.account_key JOIN dim_security s ON s.security_key=p.security_key
            WHERE p.position_date=? AND p.account_key IN ({ph})""", (AS_OF, *accounts))
if len(pos):
    st.plotly_chart(px.treemap(pos, path=["account_name", "asset_class", "security_name"], values="market_value_usd"), use_container_width=True)
    st.download_button("Download holdings (CSV)", pos.to_csv(index=False), "holdings.csv", "text/csv")
