# Python lab

Two scripts, both reading the SQL lab's SQLite database (built automatically if missing).

| Script | What it teaches | Run |
|---|---|---|
| `analyze.py` | pandas for a product leader: date maths, groupby, pivot, joining frames, one chart | `pip install pandas matplotlib` then `python3 analyze.py` |
| `dashboard.py` | a working exceptions-first portal prototype with entitlements enforced in the query | `pip install streamlit pandas plotly` then `streamlit run dashboard.py` |

Install Python first if needed: python.org (Windows: tick "Add python.exe to PATH"), or `brew install python` on macOS.
Prefer a virtual environment so nothing collides: `python3 -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`).
