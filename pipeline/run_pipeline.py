"""Pipeline orchestrator for Run #1 (v1 linear draft) and Run #2 (v2 shift-left gated)."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from browser_gate import format_markdown_audit, run_browser_gate  # noqa: E402
from build_site import write_site_bundle  # noqa: E402
from outline_gate import run_outline_gate  # noqa: E402
from slide_gate import run_slide_gate  # noqa: E402
from wiki_lint import run_wiki_lint  # noqa: E402
from wiki_utils import DATA_DIR, DOCS_DIR, LOGS_DIR, ROOT_DIR, save_json, write_text  # noqa: E402


def run_pipeline(mode: str, skip_browser: bool = False) -> dict[str, Any]:
    """Execute the configured verification graph for v1 or v2 and emit JSON/MD audit logs."""
    if mode not in ("v1", "v2"):
        raise ValueError(f"Unsupported mode: {mode}")

    slides_path = DATA_DIR / f"slides-{mode}.json"
    outline_path = DATA_DIR / f"outline-{mode}.json"
    report_path = LOGS_DIR / ("run-01-v1-report.json" if mode == "v1" else "run-02-v2-report.json")
    audit_md_path = LOGS_DIR / ("run-01-v1-audit.md" if mode == "v1" else "run-02-v2-audit.md")

    gates: dict[str, Any] = {}

    # Gate 1: WikiLint
    gates["wiki_lint"] = run_wiki_lint(ROOT_DIR)

    # Gate 2: OutlineGate (only enabled in v2 shift-left architecture!)
    if mode == "v2":
        gates["outline_gate"] = run_outline_gate(outline_path, ROOT_DIR)
    else:
        gates["outline_gate"] = {
            "gate": "Gate 2: OutlineGate",
            "status": "skipped",
            "passed": True,
            "reason": "v1 初版線性管線尚未設計前置大綱與順序檢查，直接從討論跳入草稿生成。",
            "issues": [],
        }

    # Gate 3: SlideGate
    gates["slide_gate"] = run_slide_gate(slides_path, ROOT_DIR)

    # Build docs/assets/wiki-data.js so BrowserGate can inspect real output
    write_site_bundle(slides_path, DOCS_DIR)

    # Gate 4: BrowserGate
    if skip_browser:
        gates["browser_gate"] = {
            "gate": "Gate 4: BrowserVisualGate",
            "status": "skipped",
            "passed": True,
            "reason": "使用 --skip-browser 暫時略過，待下一步執行 Playwright 實機檢驗並回填。",
            "issues": [],
        }
    else:
        shots_dir = LOGS_DIR / "screenshots" if mode == "v2" else None
        gates["browser_gate"] = run_browser_gate(DOCS_DIR, screenshots_dir=shots_dir, mode=mode)

    active_gates = [g for g in gates.values() if g.get("status") != "skipped"]
    overall_passed = all(g.get("passed", False) for g in active_gates)
    all_issues: list[dict[str, Any]] = []
    for g in active_gates:
        all_issues.extend(g.get("issues", []))

    report = {
        "run_label": "Run #1 (v1 初版線性流程)" if mode == "v1" else "Run #2 (v2 前移檢查狀態圖)",
        "mode": mode,
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "slides_file": str(slides_path.relative_to(ROOT_DIR)).replace("\\", "/"),
        "overall_passed": overall_passed,
        "total_issues": len(all_issues),
        "gates": gates,
        "issues": all_issues,
    }
    save_json(report_path, report)
    write_text(audit_md_path, format_markdown_audit(report))

    # Re-build site data once after writing report so workflow.html sees latest audit
    write_site_bundle(slides_path, DOCS_DIR)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TAICA Lab 10 LLM Wiki Slide Verification Pipeline")
    parser.add_argument("--mode", choices=["v1", "v2"], required=True, help="Pipeline version to run")
    parser.add_argument("--skip-browser", action="store_true", help="Skip Gate 4 Playwright run")
    args = parser.parse_args()

    report = run_pipeline(args.mode, skip_browser=args.skip_browser)
    print(f"\n=== {report['run_label']} ===")
    print(f"Overall: {'PASS' if report['overall_passed'] else 'FAIL'} | Issues: {report['total_issues']}")
    for name, gate in report["gates"].items():
        if gate.get("status") == "skipped":
            print(f"  - {name}: SKIPPED ({gate['reason']})")
        else:
            st = "PASS" if gate["passed"] else "FAIL"
            print(f"  - {name}: {st} ({len(gate.get('issues', []))} issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
