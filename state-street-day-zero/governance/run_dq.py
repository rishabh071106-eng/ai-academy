#!/usr/bin/env python3
"""Runs every rule in dq_rules.sql against the lab database and prints a data-quality scorecard.
Zero rows returned by a rule = PASS. This is the mechanism behind Collibra DQ, dbt tests and Great Expectations.
    python3 run_dq.py
"""
import os, re, sqlite3, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.join(HERE, "..", "sql-lab"); DB = os.path.join(LAB, "custody_lab.db")
if not os.path.exists(DB):
    subprocess.run([sys.executable, os.path.join(LAB, "run_sqlite.py"), "1"], check=True, stdout=subprocess.DEVNULL)
con = sqlite3.connect(DB)
blocks = re.split(r"^-- ==== RULE ", open(os.path.join(HERE, "dq_rules.sql"), encoding="utf-8").read(), flags=re.M)[1:]
rows = []
for b in blocks:
    head, _, body = b.partition("\n")
    name, dim, sev = [x.strip() for x in head.split("|")]
    sql = " ".join(l for l in body.splitlines() if not l.strip().startswith("--")).strip().rstrip(";")
    cur = con.execute(sql); viol = cur.fetchall()
    rows.append((name, dim, sev, len(viol), [d[0] for d in cur.description], viol[:3]))
print(f"{'RULE':42} {'DIMENSION':12} {'SEVERITY':8} RESULT")
print("-" * 80)
blocked = 0
for name, dim, sev, n, cols, sample in rows:
    res = "PASS" if n == 0 else f"FAIL ({n} violation{'s' if n > 1 else ''})"
    if n and sev == "BLOCK": blocked += 1
    print(f"{name:42} {dim:12} {sev:8} {res}")
    for s in sample:
        print(f"{'':42} {'':12} {'':8}   e.g. " + ", ".join(f"{c}={v}" for c, v in zip(cols, s)))
print("-" * 80)
print("Publish decision:", "HOLD the mart — blocking rules failed" if blocked else "PUBLISH — no blocking failures (warnings are visible to clients as status)")
