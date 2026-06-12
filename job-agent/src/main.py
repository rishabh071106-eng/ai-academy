"""Orchestrator: discover -> filter -> score -> tailor -> apply -> record.

Run once:        python -m src.main
Run continuously: python -m src.main --loop --interval-hours 6
Dry run:          python -m src.main --dry-run
"""

from __future__ import annotations

import argparse
import time
import traceback

from .applier import apply_to_job
from .config import load_config
from .discover import discover, fetch_description
from .llm import LLM, RefusalError
from .score import score_job
from .state import State
from .tailor import build_application_package


def run_once(dry_run_override: bool | None = None) -> None:
    cfg = load_config()
    llm = LLM(cfg.model)
    state = State(cfg.path("state_db", "state/jobs.db"))
    policy = cfg.policy
    dry_run = policy.get("dry_run", False) if dry_run_override is None else dry_run_override
    max_apps = int(policy.get("max_applications_per_run", 5))
    min_score = int(policy.get("min_fit_score", 70))

    print("== discovery ==")
    jobs = discover(cfg, llm)
    print(f"found {len(jobs)} postings")

    applied = 0
    for job in jobs:
        if applied >= max_apps:
            print(f"reached cap of {max_apps} applications this run")
            break
        if state.seen(job.url):
            continue

        # Cheap filters before spending tokens.
        if cfg.blocklist.matches(job.company):
            state.record(job.url, "blocked", job.company, job.title, job.source,
                         notes="blocklisted company")
            print(f"  BLOCKED  {job.company} — {job.title}")
            continue
        if not cfg.title_pattern.search(job.title):
            state.record(job.url, "skipped", job.company, job.title, job.source,
                         notes="title below target seniority")
            continue

        print(f"\n-- {job.title} @ {job.company} ({job.source})")
        try:
            fetch_description(job)
            verdict = score_job(job, cfg, llm)
            print(f"   fit={verdict['fit_score']} decision={verdict['decision']} "
                  f"emphasis={verdict['emphasis']}")
            print(f"   {verdict['reasons']}")

            if verdict["blocked"]:
                state.record(job.url, "blocked", job.company, job.title, job.source,
                             verdict["fit_score"], verdict["reasons"])
                continue
            if verdict["decision"] != "apply" or verdict["fit_score"] < min_score:
                state.record(job.url, "skipped", job.company, job.title, job.source,
                             verdict["fit_score"], verdict["reasons"])
                continue

            pkg_dir = build_application_package(job, verdict["emphasis"], cfg, llm)
            state.record(job.url, "tailored", job.company, job.title, job.source,
                         verdict["fit_score"])
            print(f"   package: {pkg_dir}")

            if dry_run:
                print("   dry-run: skipping submission")
                continue

            result = apply_to_job(job, pkg_dir, cfg, llm)
            state.record(job.url, result.status, job.company, job.title, job.source,
                         verdict["fit_score"], result.detail)
            print(f"   {result.status.upper()}: {result.detail}")
            if result.status == "applied":
                applied += 1

        except RefusalError as e:
            state.record(job.url, "failed", job.company, job.title, job.source, notes=str(e))
            print(f"   model refusal: {e}")
        except Exception as e:
            state.record(job.url, "failed", job.company, job.title, job.source,
                         notes=f"{type(e).__name__}: {e}")
            print(f"   error: {e}")
            traceback.print_exc()

    print("\n== summary ==")
    for status, count in sorted(state.summary().items()):
        print(f"  {status:10s} {count}")
    print(f"applications submitted this run: {applied}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous senior-product job application agent")
    parser.add_argument("--loop", action="store_true", help="run forever on an interval")
    parser.add_argument("--interval-hours", type=float, default=6.0)
    parser.add_argument("--dry-run", action="store_true",
                        help="discover/score/tailor but never open a browser")
    args = parser.parse_args()

    if not args.loop:
        run_once(dry_run_override=args.dry_run or None)
        return

    while True:
        try:
            run_once(dry_run_override=args.dry_run or None)
        except Exception:
            traceback.print_exc()
        print(f"\nsleeping {args.interval_hours}h...\n")
        time.sleep(args.interval_hours * 3600)


if __name__ == "__main__":
    main()
