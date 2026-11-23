"""Shared utilities for parsing the LLM Wiki repository and checking artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "raw"
WIKI_DIR = ROOT_DIR / "wiki"
DISCUSSION_DIR = ROOT_DIR / "discussion"
DOCS_DIR = ROOT_DIR / "docs"
LOGS_DIR = ROOT_DIR / "logs"
DATA_DIR = ROOT_DIR / "data"

WIKILINK_RE = re.compile(r"\[\[([a-z0-9-]+)\]\]")
SRC_REF_RE = re.compile(r"\[(SRC-\d{2})\]")
RAW_SRC_ID_RE = re.compile(r"src-(\d{2})-", re.IGNORECASE)


def read_text(path: Path) -> str:
    """Read UTF-8 text from disk."""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text to disk, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json(path: Path) -> Any:
    """Load UTF-8 JSON file."""
    return json.loads(read_text(path))


def save_json(path: Path, data: Any) -> None:
    """Save UTF-8 formatted JSON file."""
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse lightweight YAML frontmatter block and return (meta, body)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return {}, text

    meta: dict[str, Any] = {}
    for raw_line in lines[1:end_idx]:
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]
            meta[key] = items
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            meta[key] = val[1:-1]
        elif val.lower() in ("true", "false"):
            meta[key] = val.lower() == "true"
        else:
            meta[key] = val

    body = "\n".join(lines[end_idx + 1 :]).lstrip("\n")
    return meta, body


def load_raw_sources(raw_dir: Path = RAW_DIR) -> dict[str, dict[str, Any]]:
    """Load all immutable raw source files keyed by SRC-XX."""
    sources: dict[str, dict[str, Any]] = {}
    if not raw_dir.exists():
        return sources

    for path in sorted(raw_dir.glob("*.md")):
        raw_text = read_text(path)
        meta, body = parse_frontmatter(raw_text)
        src_id = meta.get("source_id")
        if not src_id:
            match = RAW_SRC_ID_RE.search(path.name)
            if match:
                src_id = f"SRC-{match.group(1)}"
        if not src_id:
            continue
        sources[src_id] = {
            "source_id": src_id,
            "slug": path.stem,
            "filename": path.name,
            "path": str(path.relative_to(ROOT_DIR)).replace("\\", "/"),
            "meta": meta,
            "title": meta.get("title", path.stem),
            "authors": meta.get("authors", ""),
            "date": meta.get("date", meta.get("year", "")),
            "url": meta.get("url", ""),
            "body": body,
            "raw_text": raw_text,
        }
    return sources


def load_wiki_pages(wiki_dir: Path = WIKI_DIR) -> dict[str, dict[str, Any]]:
    """Load all compiled wiki markdown pages keyed by slug."""
    pages: dict[str, dict[str, Any]] = {}
    if not wiki_dir.exists():
        return pages

    for path in sorted(wiki_dir.glob("*.md")):
        raw_text = read_text(path)
        meta, body = parse_frontmatter(raw_text)
        slug = path.stem
        prose_only = re.sub(r"```.*?```|`[^`]+`", "", body, flags=re.DOTALL)
        wikilinks = list(dict.fromkeys(WIKILINK_RE.findall(prose_only)))
        inline_sources = list(dict.fromkeys(SRC_REF_RE.findall(prose_only)))
        pages[slug] = {
            "slug": slug,
            "filename": path.name,
            "path": str(path.relative_to(ROOT_DIR)).replace("\\", "/"),
            "meta": meta,
            "id": meta.get("id", ""),
            "title": meta.get("title", slug),
            "category": meta.get("category", ""),
            "summary": meta.get("summary", ""),
            "sources": meta.get("sources", []),
            "tags": meta.get("tags", []),
            "updated": meta.get("updated", ""),
            "body": body,
            "raw_text": raw_text,
            "wikilinks": wikilinks,
            "inline_sources": inline_sources,
        }
    return pages


def parse_index_entries(index_path: Path = ROOT_DIR / "index.md") -> dict[str, str]:
    """Extract {slug: summary_text} entries listed in index.md."""
    entries: dict[str, str] = {}
    if not index_path.exists():
        return entries
    for line in read_text(index_path).splitlines():
        match = re.match(r"^\s*-\s*\[\[([a-z0-9-]+)\]\]\s*[—\-–:]\s*(.+)$", line)
        if match:
            entries[match.group(1)] = match.group(2).strip()
        else:
            for slug in WIKILINK_RE.findall(line):
                if slug not in entries:
                    entries[slug] = ""
    return entries


def extract_slide_visible_text(slide: dict[str, Any]) -> tuple[str, int]:
    """Concatenate learner-facing visible text on a slide stage and count bullet items."""
    parts: list[str] = []
    bullet_count = 0

    for key in ("title", "subtitle", "hook", "summary", "takeaway", "question"):
        val = slide.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())

    for item in slide.get("bullets", []):
        if isinstance(item, str):
            parts.append(item.strip())
            bullet_count += 1
        elif isinstance(item, dict):
            bullet_count += 1
            for sub_key in ("label", "title", "text", "detail", "example"):
                sub_val = item.get(sub_key)
                if isinstance(sub_val, str) and sub_val.strip():
                    parts.append(sub_val.strip())

    layout = slide.get("layout", "concept")
    for idx, card in enumerate(slide.get("cards", [])):
        if isinstance(card, dict):
            bullet_count += 1
            if layout == "failure_grid":
                keys = ("title", "badge", "symptom", "cause", "fix") if idx == 0 else ("title", "badge", "symptom")
            else:
                keys = ("title", "badge", "symptom", "cause", "fix", "desc", "analogy")
            for sub_key in keys:
                sub_val = card.get(sub_key)
                if isinstance(sub_val, str) and sub_val.strip():
                    parts.append(sub_val.strip())

    comparison = slide.get("comparison")
    if isinstance(comparison, dict):
        for col_key in ("left", "right"):
            col = comparison.get(col_key, {})
            if isinstance(col, dict):
                if col.get("title"):
                    parts.append(str(col["title"]).strip())
                for point in col.get("points", []):
                    parts.append(str(point).strip())
                    bullet_count += 1

    # Interactive data visible headlines if present
    interactive = slide.get("interactive")
    if isinstance(interactive, dict):
        if isinstance(interactive.get("prompt"), str):
            parts.append(interactive["prompt"].strip())

    full_text = "\n".join(parts)
    # Count non-whitespace characters as an intuitive density metric for Chinese/mixed slides
    compact_len = len(re.sub(r"\s+", "", full_text))
    return full_text, compact_len
