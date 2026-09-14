#!/usr/bin/env python3
"""Zero-install runner: builds custody_lab.db with SQLite (bundled with Python) and runs every
query in queries.sql, printing each result as a table.

    python3 run_sqlite.py            # run all 13 queries
    python3 run_sqlite.py 5 7        # run only Q5 and Q7
    python3 run_sqlite.py --shell    # drop into an interactive prompt on the built database
"""
import os, re, sqlite3, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "custody_lab.db")

def build():
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    for f in ("schema.sql", "seed.sql"):
        with open(os.path.join(HERE, f), encoding="utf-8") as fh:
            con.executescript(fh.read())
    con.commit()
    return con

def fmt_table(cols, rows):
    if not rows:
        return "  (no rows)"
    cells = [[("" if v is None else f"{v:,.2f}" if isinstance(v, float) else str(v)) for v in r] for r in rows]
    widths = [max(len(c), *(len(r[i]) for r in cells)) for i, c in enumerate(cols)]
    numeric = [all(isinstance(r[i], (int, float)) or r[i] is None for r in rows) for i in range(len(cols))]
    def line(vals):
        return "  " + " | ".join(v.rjust(w) if numeric[i] else v.ljust(w) for i, (v, w) in enumerate(zip(vals, widths)))
    return "\n".join([line(cols), "  " + "-+-".join("-" * w for w in widths)] + [line(r) for r in cells])

def main():
    args = sys.argv[1:]
    con = build()
    if "--shell" in args:
        print(f"Built {DB}. Type SQL ending with ';'  (Ctrl-D or 'exit;' to quit)")
        buf = ""
        while True:
            try:
                buf += input("custody_lab> " if not buf else "          ...> ") + "\n"
            except EOFError:
                break
            if buf.strip().endswith(";"):
                if buf.strip().lower() == "exit;":
                    break
                try:
                    cur = con.execute(buf)
                    if cur.description:
                        print(fmt_table([d[0] for d in cur.description], cur.fetchall()))
                    else:
                        con.commit(); print("  ok")
                except sqlite3.Error as e:
                    print(f"  error: {e}")
                buf = ""
        return
    wanted = {int(a) for a in args if a.isdigit()}
    with open(os.path.join(HERE, "queries.sql"), encoding="utf-8") as fh:
        blocks = re.split(r"^-- ==== ", fh.read(), flags=re.M)[1:]
    for block in blocks:
        title, _, body = block.partition("\n")
        n = int(re.match(r"Q(\d+)", title).group(1))
        if wanted and n not in wanted:
            continue
        print(f"\n{'=' * 100}\n{title.strip()}\n{'=' * 100}")
        stmts = [s.strip() for s in body.split(";") if s.strip() and not all(l.strip().startswith("--") for l in s.strip().splitlines())]
        for stmt in stmts:
            cur = con.execute(stmt)
            if cur.description:
                print(fmt_table([d[0] for d in cur.description], cur.fetchall()))
        con.commit()
    print(f"\nDatabase saved at {DB} — open it in DBeaver (SQLite driver) or run: python3 run_sqlite.py --shell")

if __name__ == "__main__":
    main()
