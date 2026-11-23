"""Static site compiler: converts LLM Wiki markdown, slides JSON, and audit logs into docs/assets/wiki-data.js."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

import markdown

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from wiki_utils import (  # noqa: E402
    DATA_DIR,
    DISCUSSION_DIR,
    DOCS_DIR,
    LOGS_DIR,
    ROOT_DIR,
    SRC_REF_RE,
    WIKILINK_RE,
    load_json,
    load_raw_sources,
    load_wiki_pages,
    read_text,
    write_text,
)

CATEGORY_LABELS = {
    "governance": "治理與紀錄",
    "overview": "全覽地圖",
    "foundations": "基礎心智與退化原理",
    "failures": "長上下文失效模式",
    "strategies": "WSCI 四大工程策略",
    "practice": "提示與生產實戰",
    "architecture": "知識庫架構模式",
    "reference": "詞彙與標準",
    "raw": "原始文獻（唯讀）",
}


def render_markdown_with_links(md_text: str, valid_wiki_slugs: set[str], valid_raw_ids: set[str]) -> str:
    """Render Markdown to HTML while converting [[wikilinks]] and [SRC-XX] badges."""

    def replace_wikilink(match: re.Match[str]) -> str:
        slug = match.group(1)
        if slug in valid_wiki_slugs:
            return f'<a href="#{slug}" class="wikilink" data-doc-id="{slug}">[[{slug}]]</a>'
        return f'<span class="wikilink broken">[[{slug}]]</span>'

    def replace_src_badge(match: re.Match[str]) -> str:
        src_id = match.group(1)
        doc_id = f"raw-{src_id.lower()}"
        if src_id in valid_raw_ids:
            return f'<a href="#{doc_id}" class="src-badge" data-doc-id="{doc_id}">[{src_id}]</a>'
        return f'<span class="src-badge broken">[{src_id}]</span>'

    # Render markdown first, then convert wikilinks/source badges in non-code HTML text
    rendered = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    # Avoid replacing inside <code> or <pre> blocks by splitting on code tags
    segments = re.split(r"(<pre>.*?</pre>|<code>.*?</code>)", rendered, flags=re.DOTALL)
    for idx, seg in enumerate(segments):
        if idx % 2 == 0:
            seg = WIKILINK_RE.sub(replace_wikilink, seg)
            seg = SRC_REF_RE.sub(replace_src_badge, seg)
            segments[idx] = seg
    return "".join(segments)


def load_audit_reports(logs_dir: Path = LOGS_DIR) -> dict[str, Any]:
    """Load any existing Run #1 (v1) and Run #2 (v2) JSON audit reports."""
    runs: list[dict[str, Any]] = []
    for fname in ("run-01-v1-report.json", "run-02-v2-report.json"):
        fpath = logs_dir / fname
        if fpath.exists():
            runs.append(load_json(fpath))
    return {"runs": runs}


def build_site_data(slides_path: Path, root_dir: Path = ROOT_DIR) -> dict[str, Any]:
    """Compile all repository layers into a unified JSON bundle for the static frontend."""
    raw_sources = load_raw_sources(root_dir / "raw")
    wiki_pages = load_wiki_pages(root_dir / "wiki")
    deck = load_json(slides_path)
    slides = deck.get("slides", [])

    valid_wiki_slugs = set(wiki_pages)
    valid_raw_ids = set(raw_sources)

    # Calculate backlinks across wiki pages and slides
    wiki_backlinks: dict[str, list[dict[str, str]]] = {slug: [] for slug in wiki_pages}
    for src_slug, page in wiki_pages.items():
        for target in page["wikilinks"]:
            if target in wiki_backlinks and target != src_slug:
                wiki_backlinks[target].append({"id": src_slug, "title": page["title"]})

    slide_backlinks_wiki: dict[str, list[dict[str, Any]]] = {slug: [] for slug in wiki_pages}
    slide_backlinks_raw: dict[str, list[dict[str, Any]]] = {src_id: [] for src_id in raw_sources}
    for idx, sl in enumerate(slides, start=1):
        sl_ref = {"index": idx, "id": sl["id"], "title": sl["title"]}
        for w in sl.get("wiki_refs", []):
            if w in slide_backlinks_wiki:
                slide_backlinks_wiki[w].append(sl_ref)
        for s in sl.get("source_refs", []):
            if s in slide_backlinks_raw:
                slide_backlinks_raw[s].append(sl_ref)

    raw_backlinks_wiki: dict[str, list[dict[str, str]]] = {src_id: [] for src_id in raw_sources}
    for slug, page in wiki_pages.items():
        for src_id in page["sources"]:
            if src_id in raw_backlinks_wiki:
                raw_backlinks_wiki[src_id].append({"id": slug, "title": page["title"]})

    documents: dict[str, dict[str, Any]] = {}

    # 1. Governance & Discussion docs
    gov_specs = [
        ("gov-index", "index.md — 知識庫總目錄", root_dir / "index.md", "Layer 2 控制中心：分類導覽與單行摘要"),
        (
            "gov-discussion",
            "00-discuss-before-generate.md — 先討論紀錄",
            DISCUSSION_DIR / "00-discuss-before-generate.md",
            "Layer 3：建庫前針對受眾、分類與 DAG 的討論決策",
        ),
        ("gov-schema", "SCHEMA.md — 治理規格", root_dir / "SCHEMA.md", "Layer 3：LLM Wiki 操作規範與檢查協議"),
        ("gov-log", "log.md — 操作審計日誌", root_dir / "log.md", "Layer 2 控制中心：追加式 Ingest / Lint / Gen 紀錄"),
    ]
    for doc_id, title, path, summary in gov_specs:
        if path.exists():
            md_text = read_text(path)
            documents[doc_id] = {
                "id": doc_id,
                "layer": "governance",
                "category": "governance",
                "category_label": CATEGORY_LABELS["governance"],
                "title": title,
                "summary": summary,
                "path": str(path.relative_to(root_dir)).replace("\\", "/"),
                "sources": [],
                "tags": ["治理", "流程"],
                "html": render_markdown_with_links(md_text, valid_wiki_slugs, valid_raw_ids),
                "backlinks_wiki": [],
                "backlinks_slides": [],
            }

    # 2. Compiled Wiki pages
    for slug, page in wiki_pages.items():
        documents[slug] = {
            "id": slug,
            "layer": "wiki",
            "category": page["category"],
            "category_label": CATEGORY_LABELS.get(page["category"], page["category"]),
            "title": page["title"],
            "summary": page["summary"],
            "path": page["path"],
            "sources": page["sources"],
            "tags": page["tags"],
            "updated": page["updated"],
            "wikilinks": page["wikilinks"],
            "html": render_markdown_with_links(page["body"], valid_wiki_slugs, valid_raw_ids),
            "backlinks_wiki": wiki_backlinks[slug],
            "backlinks_slides": slide_backlinks_wiki[slug],
        }

    # 3. Immutable Raw sources
    for src_id, src in raw_sources.items():
        doc_id = f"raw-{src_id.lower()}"
        documents[doc_id] = {
            "id": doc_id,
            "source_id": src_id,
            "layer": "raw",
            "category": "raw",
            "category_label": CATEGORY_LABELS["raw"],
            "title": f"[{src_id}] {src['title']}",
            "summary": f"{src['authors']} ({src['date']})",
            "authors": src["authors"],
            "date": str(src["date"]),
            "url": src["url"],
            "path": src["path"],
            "sources": [src_id],
            "tags": ["Raw", "唯讀來源"],
            "html": render_markdown_with_links(src["body"], valid_wiki_slugs, valid_raw_ids),
            "backlinks_wiki": raw_backlinks_wiki[src_id],
            "backlinks_slides": slide_backlinks_raw[src_id],
        }

    # 4. Build Knowledge Graph (Raw -> Wiki -> Slide)
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []

    for src_id, src in raw_sources.items():
        nodes.append(
            {
                "id": f"raw-{src_id.lower()}",
                "label": src_id,
                "full_title": src["title"],
                "layer": "raw",
                "category": "raw",
            }
        )
    for slug, page in wiki_pages.items():
        nodes.append(
            {
                "id": slug,
                "label": page["title"],
                "full_title": page["summary"],
                "layer": "wiki",
                "category": page["category"],
            }
        )
        for src_id in page["sources"]:
            if src_id in raw_sources:
                edges.append({"from": f"raw-{src_id.lower()}", "to": slug, "type": "ingest"})
        for target in page["wikilinks"]:
            if target in wiki_pages and target != slug:
                edges.append({"from": slug, "to": target, "type": "wikilink"})

    for idx, sl in enumerate(slides, start=1):
        sl_node_id = f"slide-{idx}"
        nodes.append(
            {
                "id": sl_node_id,
                "label": f"S{idx}: {sl['title']}",
                "full_title": sl.get("subtitle", sl["title"]),
                "layer": "slide",
                "category": f"unit-{sl.get('unit_num', 1)}",
                "slide_index": idx,
            }
        )
        for w in sl.get("wiki_refs", []):
            if w in wiki_pages:
                edges.append({"from": w, "to": sl_node_id, "type": "slide_ref"})

    audit_data = load_audit_reports(root_dir / "logs")

    return {
        "meta": {
            "topic": "Context Engineering（上下文工程）",
            "deck_title": deck.get("title", "Context Engineering 教學簡報"),
            "deck_version": deck.get("version", "v2"),
            "raw_count": len(raw_sources),
            "wiki_count": len(wiki_pages),
            "slide_count": len(slides),
            "wikilink_count": sum(len(p["wikilinks"]) for p in wiki_pages.values()),
        },
        "categories": CATEGORY_LABELS,
        "documents": documents,
        "deck": deck,
        "graph": {"nodes": nodes, "edges": edges},
        "audit": audit_data,
    }


def write_site_bundle(slides_path: Path, docs_dir: Path = DOCS_DIR) -> Path:
    """Compile site data and write docs/assets/wiki-data.js plus docs/.nojekyll."""
    site_data = build_site_data(slides_path)
    out_path = docs_dir / "assets" / "wiki-data.js"
    js_payload = "// Auto-generated by pipeline/build_site.py — do not edit manually.\n"
    js_payload += "window.SITE_DATA = " + json.dumps(site_data, ensure_ascii=False) + ";\n"
    write_text(out_path, js_payload)
    write_text(docs_dir / ".nojekyll", "")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile Wiki, Slides, and Audit Logs into docs/assets/wiki-data.js")
    parser.add_argument("--slides", default=str(DATA_DIR / "slides-v2.json"), help="Path to slides JSON")
    args = parser.parse_args()
    out_path = write_site_bundle(Path(args.slides).resolve())
    print(f"[build_site] Generated {out_path.relative_to(ROOT_DIR)} successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
