#!/usr/bin/env python3
"""Connect to the lab from Python and pull a query into pandas — the pattern every analyst,
Tableau prep script and Jupyter notebook at a bank uses.

Install once:   pip install psycopg2-binary pandas sqlalchemy
Local Postgres: python3 connect.py
Amazon RDS:     PGHOST=<your-rds-endpoint>.rds.amazonaws.com PGPASSWORD=<pw> python3 connect.py
Any settings can be overridden with PGHOST / PGPORT / PGDATABASE / PGUSER / PGPASSWORD.
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text

host = os.getenv("PGHOST", "localhost")
port = os.getenv("PGPORT", "5432")
db   = os.getenv("PGDATABASE", "custody_lab")
user = os.getenv("PGUSER", "lab")
pw   = os.getenv("PGPASSWORD", "lab")
sslmode = "require" if host.endswith("amazonaws.com") else "prefer"

engine = create_engine(f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}?sslmode={sslmode}")

EXCEPTIONS = text("""
    SELECT t.trade_id, a.account_name, s.security_name, t.status, t.fail_reason, t.intended_settle_date
    FROM fact_trades t
    JOIN dim_account  a ON a.account_key  = t.account_key
    JOIN dim_security s ON s.security_key = t.security_key
    WHERE t.status <> 'SETTLED'
    ORDER BY t.intended_settle_date
""")

with engine.connect() as conn:
    print(f"Connected to {host}:{port}/{db} as {user}")
    df = pd.read_sql(EXCEPTIONS, conn)

print("\nUnsettled trades (the exceptions screen):")
print(df.to_string(index=False))
print(f"\n{len(df)} rows. Failed: {(df['status'] == 'FAILED').sum()}")

# Save for Excel / Tableau
df.to_csv("exceptions_today.csv", index=False)
print("Saved exceptions_today.csv")
