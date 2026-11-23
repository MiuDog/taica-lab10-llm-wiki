"""Gate 2: OutlineGate — Pre-generation validation for teaching slide outlines."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from wiki_utils import (  # noqa: E402
    DATA_DIR,
    ROOT_DIR,
    load_json,
    load_raw_sources,
    load_wiki_pages,
)

# Prerequisite concepts that must appear strictly before or alongside downstream concepts:
# (prerequisite_wiki_slug, dependent_wiki_slug, reason)
PREREQ_PAIRS = [
    (
        "cpu-ram-mental-model",
        "lost-in-the-middle",
        "必須先建立「書桌/RAM」心智模型，再解釋 U 型記憶曲線與中間迷失。",
    ),
    (
        "prompt-vs-context-engineering",
        "context-failure-modes",
        "必須先區分 Prompt 與 Context Engineering，再討論長上下文四大失效模式。",
    ),
    (
        "context-failure-modes",
        "four-strategies-wsci",
        "必須先診斷 Context 四大失效症狀，再引入 WSCI 四大治本策略。",
    ),
    (
        "four-strategies-wsci",
        "production-lessons-manus",
        "必須先理解 WSCI 基礎策略，再進入 Manus 生產環境實戰課。",
    ),
    (
        "llm-wiki-pattern",
        "rag-vs-llm-wiki",
        "必須先理解 LLM Wiki 三層架構，再比較它與傳統切塊 RAG 的差異。",
    ),
]


def run_outline_gate(outline_path: Path, root_dir: Path = ROOT_DIR) -> dict[str, Any]:
    """Validate pre-generation outline structure, prerequisite DAG, budgets, and coverage."""
    raw_sources = load_raw_sources(root_dir / "raw")
    wiki_pages = load_wiki_pages(root_dir / "wiki")
    outline = load_json(outline_path)
    slides = outline.get("slides", [])

    checks: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    def add_check(check_id: str, name: str, ok: bool, detail: str) -> None:
        checks.append({"id": check_id, "name": name, "passed": ok, "detail": detail})
        if not ok:
            issues.append({"gate": "Gate 2 (OutlineGate)", "check": check_id, "detail": detail})

    # 1. Slide count between 10 and 16
    count_ok = 10 <= len(slides) <= 16
    add_check(
        "G2-SLIDE-COUNT",
        "投影片總頁數合理 (10~16 頁)",
        count_ok,
        f"大綱共規劃 {len(slides)} 頁投影片（適合 15~20 分鐘零基礎教學）。",
    )

    # 2. Wiki & source binding per slide
    mapping_errors: list[str] = []
    first_seen_wiki: dict[str, int] = {}
    covered_wiki: set[str] = set()
    covered_sources: set[str] = set()

    for idx, sl in enumerate(slides, start=1):
        sid = sl.get("id", f"slide-{idx}")
        w_refs = sl.get("wiki_refs", [])
        s_refs = sl.get("source_refs", [])
        if not w_refs or not s_refs:
            mapping_errors.append(f"{sid}: 未綁定 wiki_refs 或 source_refs")
            continue
        for w in w_refs:
            if w not in wiki_pages:
                mapping_errors.append(f"{sid}: 無效 wiki_refs '{w}'")
            else:
                covered_wiki.add(w)
                first_seen_wiki.setdefault(w, idx)
        for s in s_refs:
            if s not in raw_sources:
                mapping_errors.append(f"{sid}: 無效 source_refs '{s}'")
            else:
                covered_sources.add(s)

    add_check(
        "G2-WIKI-MAPPING",
        "每頁大綱明確綁定 Wiki 與 Raw 來源",
        len(mapping_errors) == 0,
        f"全數 {len(slides)} 頁大綱皆綁定有效 wiki_refs 與 source_refs。"
        if not mapping_errors
        else "; ".join(mapping_errors),
    )

    # 3. Prerequisite DAG ordering
    dag_errors: list[str] = []
    for prereq, dep, reason in PREREQ_PAIRS:
        p_idx = first_seen_wiki.get(prereq)
        d_idx = first_seen_wiki.get(dep)
        if p_idx is None:
            dag_errors.append(f"缺少先修概念頁 [[{prereq}]]")
        elif d_idx is not None and p_idx > d_idx:
            dag_errors.append(
                f"教學順序倒置：[[{dep}]] 在第 {d_idx} 頁出現，早於先修概念 [[{prereq}]]（第 {p_idx} 頁）。{reason}"
            )

    # Also require quiz / matrix unit at the end (unit 5)
    if slides and slides[-1].get("unit_num", 0) < 4:
        dag_errors.append("結尾未安排綜合測驗或知識總覽單元。")

    add_check(
        "G2-PREREQ-DAG",
        "先修概念依賴圖（Prerequisite DAG）驗證",
        len(dag_errors) == 0,
        "全數 5 組先修概念依賴順序正確無倒置。" if not dag_errors else "; ".join(dag_errors),
    )

    # 4. Budget declaration check
    budget_errors: list[str] = []
    for idx, sl in enumerate(slides, start=1):
        sid = sl.get("id", f"slide-{idx}")
        layout = sl.get("layout", "concept")
        max_chars = sl.get("max_chars", 999)
        max_bullets = sl.get("max_bullets", 99)
        char_cap = 650 if layout in ("matrix", "quiz") else 450
        if max_chars > char_cap:
            budget_errors.append(f"{sid}: max_chars={max_chars} 超過上限 {char_cap}")
        if max_bullets > 5:
            budget_errors.append(f"{sid}: max_bullets={max_bullets} 超過 5 點")

    add_check(
        "G2-CHAR-BUDGET",
        "單頁字數與要點密度預算鎖定",
        len(budget_errors) == 0,
        "全數投影片大綱皆已鎖定單頁密度上限（一般頁 <= 450 字、要點 <= 5）。"
        if not budget_errors
        else "; ".join(budget_errors),
    )

    # 5. Coverage >= 80% wiki pages & 100% raw sources
    wiki_ratio = len(covered_wiki) / len(wiki_pages) if wiki_pages else 0.0
    src_ratio = len(covered_sources) / len(raw_sources) if raw_sources else 0.0
    cov_ok = wiki_ratio >= 0.8 and src_ratio == 1.0
    add_check(
        "G2-COVERAGE",
        "Wiki 與 Raw 來源覆蓋率達標",
        cov_ok,
        f"覆蓋 {len(covered_wiki)}/{len(wiki_pages)} 篇 Wiki ({wiki_ratio:.0%}) 及 {len(covered_sources)}/{len(raw_sources)} 篇 Raw ({src_ratio:.0%})。",
    )

    passed = all(c["passed"] for c in checks)
    return {
        "gate": "Gate 2: OutlineGate",
        "outline_file": str(outline_path.relative_to(root_dir)).replace("\\", "/"),
        "passed": passed,
        "checks": checks,
        "issues": issues,
        "stats": {
            "slide_count": len(slides),
            "wiki_coverage": f"{len(covered_wiki)}/{len(wiki_pages)}",
            "source_coverage": f"{len(covered_sources)}/{len(raw_sources)}",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Gate 2: OutlineGate")
    parser.add_argument("--outline", default=str(DATA_DIR / "outline-v2.json"), help="Path to outline JSON")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()
    result = run_outline_gate(Path(args.outline).resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[Gate 2: OutlineGate] {status} ({len(result['issues'])} issues)")
        for chk in result["checks"]:
            mark = "OK" if chk["passed"] else "FAIL"
            print(f"  [{mark}] {chk['id']} - {chk['name']}: {chk['detail']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
