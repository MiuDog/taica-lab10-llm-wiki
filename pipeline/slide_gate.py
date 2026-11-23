"""Gate 3: SlideGate — Per-slide grounding, citation consistency, density, and jargon-order checks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from wiki_utils import (  # noqa: E402
    DATA_DIR,
    ROOT_DIR,
    extract_slide_visible_text,
    load_json,
    load_raw_sources,
    load_wiki_pages,
)

# Controlled beginner jargon progression:
# Each term may only appear on stage text starting from the slide that introduces it
# (unless that slide itself declares it in `introduces_terms`).
TRACKED_JARGON = [
    "Attention Budget",
    "Context Rot",
    "Lost in the Middle",
    "Primacy Bias",
    "Recency Bias",
    "Context Poisoning",
    "Context Distraction",
    "Context Confusion",
    "Context Clash",
    "Tool Loadouts",
    "Compaction",
    "KV-Cache",
    "Logit Masking",
    "Right Altitude",
    "Structured Note-Taking",
    "Sub-Agent",
    "LLM Wiki",
]


def _term_in_text(term: str, text: str) -> bool:
    """Case-insensitive substring match handling spaces/hyphens cleanly."""
    parts = [re.escape(part) for part in re.split(r"[\s\-]+", term.strip()) if part]
    if not parts:
        return False
    pattern = r"[\s\-]+".join(parts)
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def run_slide_gate(slides_path: Path, root_dir: Path = ROOT_DIR) -> dict[str, Any]:
    """Validate every generated slide for Wiki grounding, citation drift, beginner density, and jargon order."""
    raw_sources = load_raw_sources(root_dir / "raw")
    wiki_pages = load_wiki_pages(root_dir / "wiki")
    deck = load_json(slides_path)
    slides = deck.get("slides", [])

    checks: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    per_slide_metrics: list[dict[str, Any]] = []

    def add_check(check_id: str, name: str, ok: bool, detail: str) -> None:
        checks.append({"id": check_id, "name": name, "passed": ok, "detail": detail})

    def add_issue(check_id: str, slide_id: str, detail: str) -> None:
        issues.append({"gate": "Gate 3 (SlideGate)", "check": check_id, "slide": slide_id, "detail": detail})

    # Pre-scan introduction order for tracked jargon
    introduced_at: dict[str, int] = {}
    for idx, sl in enumerate(slides, start=1):
        for term in sl.get("introduces_terms", []):
            key = term.lower()
            if key not in introduced_at:
                introduced_at[key] = idx

    invalid_wiki_errs: list[str] = []
    citation_drift_errs: list[str] = []
    ungrounded_term_errs: list[str] = []
    density_errs: list[str] = []
    jargon_order_errs: list[str] = []
    speaker_note_errs: list[str] = []

    for idx, sl in enumerate(slides, start=1):
        sid = sl.get("id", f"slide-{idx}")
        w_refs = sl.get("wiki_refs", [])
        s_refs = sl.get("source_refs", [])
        g_terms = sl.get("grounded_terms", [])
        layout = sl.get("layout", "concept")
        max_chars = sl.get("max_chars", 650 if layout in ("matrix", "quiz") else 420)
        max_bullets = sl.get("max_bullets", 5)

        visible_text, char_len = extract_slide_visible_text(sl)
        bullet_count = len(sl.get("bullets", [])) + len(sl.get("cards", []))
        if isinstance(sl.get("comparison"), dict):
            left_cnt = len(sl["comparison"].get("left", {}).get("points", []))
            right_cnt = len(sl["comparison"].get("right", {}).get("points", []))
            bullet_count += max(left_cnt, right_cnt)

        # 1. Valid wiki_refs
        valid_pages = []
        if not w_refs:
            invalid_wiki_errs.append(f"{sid}: 缺少 wiki_refs")
            add_issue("G3-WIKI-REFS-VALID", sid, f"{sid} 缺少 wiki_refs。")
        else:
            for w in w_refs:
                if w not in wiki_pages:
                    invalid_wiki_errs.append(f"{sid}: 引用不存在的 wiki '{w}'")
                    add_issue("G3-WIKI-REFS-VALID", sid, f"{sid} 引用不存在的 wiki '{w}'。")
                else:
                    valid_pages.append(wiki_pages[w])

        # 2. Source consistency (catch Citation Drift)
        wiki_union_sources: set[str] = set()
        for page in valid_pages:
            wiki_union_sources.update(page["sources"])

        if not s_refs:
            citation_drift_errs.append(f"{sid}: 缺少 source_refs")
            add_issue("G3-SOURCE-CONSISTENCY", sid, f"{sid} 缺少 source_refs。")
        else:
            for src in s_refs:
                if src not in raw_sources:
                    msg = f"{sid}: 引用未知來源 {src}"
                    citation_drift_errs.append(msg)
                    add_issue("G3-SOURCE-CONSISTENCY", sid, msg)
                elif valid_pages and src not in wiki_union_sources:
                    msg = (
                        f"{sid}: Citation Drift — 標註了 [{src}]，但本頁所引用的 Wiki ({', '.join(w_refs)}) "
                        f"只包含 {sorted(wiki_union_sources)}，未包含 [{src}]。"
                    )
                    citation_drift_errs.append(msg)
                    add_issue("G3-SOURCE-CONSISTENCY", sid, msg)

        # 3. Grounded terms check against cited wiki pages
        combined_wiki_text = "\n".join(p["raw_text"] for p in valid_pages)
        if not g_terms:
            msg = f"{sid}: 未提供 grounded_terms 供機器核對"
            ungrounded_term_errs.append(msg)
            add_issue("G3-KEY-TERM-GROUNDED", sid, msg)
        else:
            for term in g_terms:
                if not _term_in_text(term, combined_wiki_text):
                    msg = f"{sid}: 術語 '{term}' 未出現在所引用的 Wiki 頁面 ({', '.join(w_refs)}) 中"
                    ungrounded_term_errs.append(msg)
                    add_issue("G3-KEY-TERM-GROUNDED", sid, msg)

        # 4. Beginner density check
        density_ok = char_len <= max_chars and bullet_count <= max_bullets
        if not density_ok:
            msg = (
                f"{sid}: 教學密度超標 — 可見字數 {char_len}（上限 {max_chars}），"
                f"要點數 {bullet_count}（上限 {max_bullets}），易導致初學者認知過載與 1280×720 溢出。"
            )
            density_errs.append(msg)
            add_issue("G3-BEGINNER-DENSITY", sid, msg)

        # 5. Jargon introduction order check
        for term in TRACKED_JARGON:
            if _term_in_text(term, visible_text):
                intro_idx = introduced_at.get(term.lower())
                if intro_idx is None:
                    msg = f"{sid}: 使用專有名詞 '{term}'，但整份簡報未在任何投影片宣告首次白話介紹（introduces_terms）。"
                    jargon_order_errs.append(msg)
                    add_issue("G3-JARGON-ORDER", sid, msg)
                elif idx < intro_idx:
                    msg = (
                        f"{sid} (第 {idx} 頁): 過早出現未解釋術語 '{term}'（該術語要到第 {intro_idx} 頁才正式介紹）。"
                    )
                    jargon_order_errs.append(msg)
                    add_issue("G3-JARGON-ORDER", sid, msg)

        # 6. Speaker notes check
        notes = str(sl.get("speaker_notes", "")).strip()
        if len(notes) < 25:
            msg = f"{sid}: speaker_notes 過短或空白（目前 {len(notes)} 字）"
            speaker_note_errs.append(msg)
            add_issue("G3-SPEAKER-NOTES", sid, msg)

        per_slide_metrics.append(
            {
                "index": idx,
                "id": sid,
                "title": sl.get("title", ""),
                "chars": char_len,
                "max_chars": max_chars,
                "bullets": bullet_count,
                "max_bullets": max_bullets,
                "wiki_refs": w_refs,
                "source_refs": s_refs,
            }
        )

    add_check(
        "G3-WIKI-REFS-VALID",
        "每頁皆有效連結 Wiki 知識頁",
        len(invalid_wiki_errs) == 0,
        f"全數 {len(slides)} 頁皆綁定有效 wiki_refs。" if not invalid_wiki_errs else "; ".join(invalid_wiki_errs),
    )
    add_check(
        "G3-SOURCE-CONSISTENCY",
        "無來源引用漂移（Citation Drift）",
        len(citation_drift_errs) == 0,
        f"全數 {len(slides)} 頁之 source_refs 與其所引 Wiki 之來源 100% 一致。"
        if not citation_drift_errs
        else "; ".join(citation_drift_errs),
    )
    add_check(
        "G3-KEY-TERM-GROUNDED",
        "核心術語完全溯源於所引 Wiki",
        len(ungrounded_term_errs) == 0,
        "每頁核心術語皆實際存在於對應 Wiki 頁面，無外部幻覺概念。"
        if not ungrounded_term_errs
        else "; ".join(ungrounded_term_errs),
    )
    add_check(
        "G3-BEGINNER-DENSITY",
        "初學者字數與要點密度不超載",
        len(density_errs) == 0,
        f"全數 {len(slides)} 頁皆符合單頁字數上限與 <= 5 要點規範。"
        if not density_errs
        else "; ".join(density_errs),
    )
    add_check(
        "G3-JARGON-ORDER",
        "專有名詞先解釋後登場順序檢查",
        len(jargon_order_errs) == 0,
        "全數追蹤專有名詞皆於首次白話定義頁（含）之後才使用。"
        if not jargon_order_errs
        else "; ".join(jargon_order_errs),
    )
    add_check(
        "G3-SPEAKER-NOTES",
        "每頁皆附白話演講備忘錄",
        len(speaker_note_errs) == 0,
        f"全數 {len(slides)} 頁均附完整講者備忘錄。"
        if not speaker_note_errs
        else "; ".join(speaker_note_errs),
    )

    passed = all(c["passed"] for c in checks)
    return {
        "gate": "Gate 3: SlideGate",
        "slides_file": str(slides_path.relative_to(root_dir)).replace("\\", "/"),
        "passed": passed,
        "checks": checks,
        "issues": issues,
        "per_slide": per_slide_metrics,
        "stats": {
            "slide_count": len(slides),
            "issue_count": len(issues),
            "max_slide_chars": max((m["chars"] for m in per_slide_metrics), default=0),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Gate 3: SlideGate")
    parser.add_argument("--slides", default=str(DATA_DIR / "slides-v2.json"), help="Path to slides JSON")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()
    result = run_slide_gate(Path(args.slides).resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[Gate 3: SlideGate] {status} ({len(result['issues'])} issues)")
        for chk in result["checks"]:
            mark = "OK" if chk["passed"] else "FAIL"
            print(f"  [{mark}] {chk['id']} - {chk['name']}: {chk['detail']}")
        for iss in result["issues"]:
            print(f"    -> [{iss['slide']}] {iss['detail']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
