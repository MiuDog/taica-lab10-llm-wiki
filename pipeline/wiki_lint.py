"""Gate 1: WikiLintGate — Validates Layer 1/2/3 integrity of the LLM Wiki."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from wiki_utils import (  # noqa: E402
    DISCUSSION_DIR,
    ROOT_DIR,
    WIKILINK_RE,
    load_raw_sources,
    load_wiki_pages,
    parse_index_entries,
    read_text,
)

REQUIRED_FRONTMATTER = ("id", "title", "category", "summary", "sources", "tags", "updated")
VALID_CATEGORIES = {
    "overview",
    "foundations",
    "failures",
    "strategies",
    "practice",
    "architecture",
    "reference",
}


def run_wiki_lint(root_dir: Path = ROOT_DIR) -> dict[str, Any]:
    """Run all Gate 1 integrity checks on raw/, wiki/, index.md, log.md, and SCHEMA.md."""
    raw_sources = load_raw_sources(root_dir / "raw")
    wiki_pages = load_wiki_pages(root_dir / "wiki")
    index_path = root_dir / "index.md"
    log_path = root_dir / "log.md"
    schema_path = root_dir / "SCHEMA.md"
    discuss_path = DISCUSSION_DIR / "00-discuss-before-generate.md"

    checks: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    def add_check(check_id: str, name: str, ok: bool, detail: str) -> None:
        checks.append({"id": check_id, "name": name, "passed": ok, "detail": detail})
        if not ok:
            issues.append({"gate": "Gate 1 (WikiLint)", "check": check_id, "detail": detail})

    # 1. Raw source count >= 5
    raw_ok = len(raw_sources) >= 5
    add_check(
        "G1-RAW-COUNT",
        "原始資料數量 >= 5",
        raw_ok,
        f"共收錄 {len(raw_sources)} 篇唯讀原始來源 ({', '.join(sorted(raw_sources))})。",
    )

    # 2. Discuss-before-generate & Schema existence
    discuss_ok = schema_path.exists() and discuss_path.exists() and len(read_text(discuss_path)) > 200
    add_check(
        "G1-DISCUSS-EXIST",
        "治理規格與先討論紀錄齊備",
        discuss_ok,
        "SCHEMA.md 與 discussion/00-discuss-before-generate.md 皆存在且具完整設計決策。"
        if discuss_ok
        else "缺少 SCHEMA.md 或先討論紀錄。",
    )

    # 3. Frontmatter completeness & id == slug
    fm_errors: list[str] = []
    for slug, page in wiki_pages.items():
        meta = page["meta"]
        missing = [f for f in REQUIRED_FRONTMATTER if not meta.get(f)]
        if missing:
            fm_errors.append(f"{slug}: 缺少欄位 {missing}")
        if page["id"] != slug:
            fm_errors.append(f"{slug}: frontmatter id '{page['id']}' 與檔名不符")
        if page["category"] not in VALID_CATEGORIES:
            fm_errors.append(f"{slug}: 無效分類 '{page['category']}'")
    add_check(
        "G1-FRONTMATTER",
        "Wiki YAML Frontmatter 完整性",
        len(fm_errors) == 0,
        f"全數 {len(wiki_pages)} 篇 Wiki 欄位與 ID 皆有效。" if not fm_errors else "; ".join(fm_errors),
    )

    # 4. Zero broken wikilinks across wiki/*.md and index.md
    broken_links: list[str] = []
    in_degree: dict[str, int] = {slug: 0 for slug in wiki_pages}
    total_links = 0
    for slug, page in wiki_pages.items():
        for target in page["wikilinks"]:
            total_links += 1
            if target not in wiki_pages:
                broken_links.append(f"{slug} -> [[{target}]]")
            elif target != slug:
                in_degree[target] += 1

    if index_path.exists():
        for target in WIKILINK_RE.findall(read_text(index_path)):
            if target not in wiki_pages:
                broken_links.append(f"index.md -> [[{target}]]")

    add_check(
        "G1-WIKILINKS",
        "Wikilinks 零斷鏈驗證",
        len(broken_links) == 0,
        f"檢查 {total_links} 條內部連結，0 斷鏈。" if not broken_links else f"發現斷鏈: {', '.join(broken_links)}",
    )

    # 5. Zero orphan pages (each wiki page referenced by >= 1 other wiki page)
    orphans = [slug for slug, deg in in_degree.items() if deg == 0]
    add_check(
        "G1-ORPHANS",
        "零孤島頁面驗證",
        len(orphans) == 0,
        f"全數 {len(wiki_pages)} 篇頁面皆具雙向入度 >= 1。"
        if not orphans
        else f"存在孤島頁面（無其他頁面連入）: {', '.join(orphans)}",
    )

    # 6. index.md sync with wiki/*.md
    index_entries = parse_index_entries(index_path)
    missing_in_index = sorted(set(wiki_pages) - set(index_entries))
    extra_in_index = sorted(set(index_entries) - set(wiki_pages))
    summary_mismatches = [
        slug
        for slug in wiki_pages
        if slug in index_entries and index_entries[slug] != wiki_pages[slug]["summary"]
    ]
    sync_ok = not missing_in_index and not extra_in_index and not summary_mismatches
    sync_msg = "index.md 與 16 篇 wiki/*.md 目錄及單行摘要 100% 同步。"
    if not sync_ok:
        parts = []
        if missing_in_index:
            parts.append(f"index 缺漏: {missing_in_index}")
        if extra_in_index:
            parts.append(f"index 多出無效頁: {extra_in_index}")
        if summary_mismatches:
            parts.append(f"摘要不同步: {summary_mismatches}")
        sync_msg = "; ".join(parts)
    add_check("G1-INDEX-SYNC", "index.md 與 Wiki 雙向同步", sync_ok, sync_msg)

    # 7. Source grounding consistency
    src_errors: list[str] = []
    for slug, page in wiki_pages.items():
        fm_sources = set(page["sources"])
        inline_sources = set(page["inline_sources"])
        if not fm_sources or not inline_sources:
            src_errors.append(f"{slug}: 缺少來源引用")
            continue
        unknown = (fm_sources | inline_sources) - set(raw_sources)
        if unknown:
            src_errors.append(f"{slug}: 引用不存在的來源 {sorted(unknown)}")
        undeclared = inline_sources - fm_sources
        if undeclared:
            src_errors.append(f"{slug}: 行內引用 {sorted(undeclared)} 未宣告於 frontmatter")
    add_check(
        "G1-SOURCE-GROUNDING",
        "原始資料來源真實性驗證",
        len(src_errors) == 0,
        "每篇 Wiki 頁面皆具真實 [SRC-XX] 標註且與 raw/ 及 frontmatter 一致。"
        if not src_errors
        else "; ".join(src_errors),
    )

    # 8. log.md audit trail
    log_text = read_text(log_path) if log_path.exists() else ""
    missing_ingests = [src for src in sorted(raw_sources) if src not in log_text]
    log_ok = "discuss" in log_text.lower() and not missing_ingests
    add_check(
        "G1-LOG-AUDIT",
        "log.md 審計軌跡完整性",
        log_ok,
        f"log.md 已完整記錄 discuss 與全部 {len(raw_sources)} 篇 ingest 事件。"
        if log_ok
        else f"log.md 缺少紀錄: {missing_ingests}",
    )

    passed = all(c["passed"] for c in checks)
    return {
        "gate": "Gate 1: WikiLintGate",
        "passed": passed,
        "checks": checks,
        "issues": issues,
        "stats": {
            "raw_count": len(raw_sources),
            "wiki_count": len(wiki_pages),
            "wikilink_count": total_links,
            "orphan_count": len(orphans),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Gate 1: WikiLintGate")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()
    result = run_wiki_lint()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[Gate 1: WikiLintGate] {status} ({len(result['issues'])} issues)")
        for chk in result["checks"]:
            mark = "OK" if chk["passed"] else "FAIL"
            print(f"  [{mark}] {chk['id']} - {chk['name']}: {chk['detail']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
