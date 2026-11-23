"""Gate 4: BrowserVisualGate — Real Chromium/Edge verification of static docs/ site."""

from __future__ import annotations

import argparse
import functools
import json
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, Playwright, sync_playwright

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from wiki_utils import DOCS_DIR, ROOT_DIR, load_json, save_json, write_text  # noqa: E402


class QuietHandler(SimpleHTTPRequestHandler):
    """Serve static files cleanly without noisy stderr logging."""

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return


def _launch_browser(p: Playwright) -> Browser:
    """Launch installed system Chrome or fall back to Edge."""
    last_err: Exception | None = None
    for channel in ("chrome", "msedge"):
        try:
            return p.chromium.launch(channel=channel, headless=True)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
    raise RuntimeError(f"Unable to launch Chrome or Edge via Playwright: {last_err}")


def run_browser_gate(
    docs_dir: Path = DOCS_DIR,
    screenshots_dir: Path | None = None,
    mode: str = "v2",
) -> dict[str, Any]:
    """Spin up an ephemeral 127.0.0.1 HTTP server in-process and verify all pages with Playwright."""
    handler = functools.partial(QuietHandler, directory=str(docs_dir))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    if screenshots_dir is not None:
        screenshots_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    slide_measurements: list[dict[str, Any]] = []

    def add_check(check_id: str, name: str, ok: bool, detail: str) -> None:
        checks.append({"id": check_id, "name": name, "passed": ok, "detail": detail})
        if not ok:
            issues.append({"gate": "Gate 4 (BrowserGate)", "check": check_id, "detail": detail})

    try:
        with sync_playwright() as p:
            browser = _launch_browser(p)
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            page = context.new_page()

            page_errors: list[str] = []
            console_errors: list[str] = []
            page.on("pageerror", lambda err: page_errors.append(str(err)))
            page.on(
                "console",
                lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
            )

            # 1. Portal index.html
            page.goto(f"{base_url}/index.html", wait_until="networkidle")
            portal_cards = page.locator(".portal-card").count()
            portal_h1 = page.locator("h1").inner_text().strip()
            portal_overflow = page.evaluate(
                "() => document.documentElement.scrollWidth > window.innerWidth + 2"
            )
            portal_ok = portal_cards >= 4 and len(portal_h1) > 0 and not portal_overflow
            add_check(
                "B4-INDEX-PORTAL",
                "入口頁 (index.html) 載入與排版",
                portal_ok,
                f"H1='{portal_h1}'，導覽卡片={portal_cards}，水平溢出={portal_overflow}。",
            )
            if screenshots_dir is not None:
                page.screenshot(path=str(screenshots_dir / "portal.png"))

            # 2. Slideshow slides.html — walk all slides 1..N at 1280x720
            page.goto(f"{base_url}/slides.html", wait_until="networkidle")
            total_slides = page.evaluate("() => window.SITE_DATA.deck.slides.length")
            overflow_slides: list[str] = []

            for idx in range(1, total_slides + 1):
                if idx > 1:
                    page.keyboard.press("ArrowRight")
                    page.wait_for_timeout(120)
                metrics = page.evaluate(
                    """() => {
                        const stage = document.querySelector('.slide-stage');
                        const card = document.querySelector('.slide-card');
                        const body = document.querySelector('.slide-body');
                        const sRect = stage ? stage.getBoundingClientRect() : null;
                        return {
                            activeIndex: Number(document.body.dataset.activeSlide || 0),
                            stageScrollH: stage ? stage.scrollHeight : 0,
                            stageClientH: stage ? stage.clientHeight : 0,
                            stageScrollW: stage ? stage.scrollWidth : 0,
                            stageClientW: stage ? stage.clientWidth : 0,
                            cardScrollH: card ? card.scrollHeight : 0,
                            cardClientH: card ? card.clientHeight : 0,
                            bodyScrollH: body ? body.scrollHeight : 0,
                            bodyClientH: body ? body.clientHeight : 0,
                            docOverflowX: document.documentElement.scrollWidth > window.innerWidth + 2,
                            stageHeight: sRect ? Math.round(sRect.height) : 0,
                        };
                    }"""
                )
                v_over = (
                    metrics["stageScrollH"] > metrics["stageClientH"] + 2
                    or metrics["cardScrollH"] > metrics["cardClientH"] + 2
                    or metrics["bodyScrollH"] > metrics["bodyClientH"] + 2
                )
                h_over = metrics["stageScrollW"] > metrics["stageClientW"] + 2 or metrics["docOverflowX"]
                slide_measurements.append(
                    {
                        "slide": idx,
                        "stage_scroll_h": metrics["stageScrollH"],
                        "stage_client_h": metrics["stageClientH"],
                        "card_scroll_h": metrics["cardScrollH"],
                        "card_client_h": metrics["cardClientH"],
                        "body_scroll_h": metrics["bodyScrollH"],
                        "body_client_h": metrics["bodyClientH"],
                        "overflow": v_over or h_over,
                    }
                )
                if v_over or h_over:
                    overflow_slides.append(
                        f"S{idx}(stage {metrics['stageScrollH']}/{metrics['stageClientH']}, "
                        f"card {metrics['cardScrollH']}/{metrics['cardClientH']}, "
                        f"body {metrics['bodyScrollH']}/{metrics['bodyClientH']})"
                    )
                if screenshots_dir is not None:
                    page.screenshot(path=str(screenshots_dir / f"slide-{idx:02d}.png"))

            add_check(
                "B4-SLIDES-1280X720",
                f"1280×720 全 {total_slides} 頁投影片零裁切零溢出",
                len(overflow_slides) == 0,
                f"實測全部 {total_slides} 頁皆零垂直/水平溢出。"
                if not overflow_slides
                else f"以下頁次在 1280×720 發生內容溢出: {', '.join(overflow_slides)}",
            )

            # 3. Interactive widgets & Wiki Provenance Drawer on slides.html
            interact_ok = True
            interact_notes: list[str] = []

            # Provenance drawer test on Slide 1
            page.goto(f"{base_url}/slides.html#slide-1", wait_until="networkidle")
            if page.locator(".provenance-pill").count() > 0:
                page.locator(".provenance-pill").first.click()
                page.wait_for_timeout(120)
                drawer_open = page.locator("#wiki-drawer.open").count() == 1
                drawer_len = len(page.locator("#wiki-drawer-body").inner_text().strip())
                if not (drawer_open and drawer_len > 50):
                    interact_ok = False
                interact_notes.append(f"溯源抽屜={'OK' if drawer_open and drawer_len > 50 else 'FAIL'}")
                page.locator("#wiki-drawer-close").click()
                page.wait_for_timeout(80)

            # Slide 2 Desk Simulator (if present)
            page.goto(f"{base_url}/slides.html#slide-2", wait_until="networkidle")
            if page.locator("[data-sim-action='add-noise']").count() > 0:
                before = page.locator("#desk-usage-label").inner_text()
                page.locator("[data-sim-action='add-noise']").click()
                after = page.locator("#desk-usage-label").inner_text()
                ok_sim = before != after
                if not ok_sim:
                    interact_ok = False
                interact_notes.append(f"書桌模擬器={'OK' if ok_sim else 'FAIL'}")

            # Slide 4 U-Curve experiment (if present)
            page.goto(f"{base_url}/slides.html#slide-4", wait_until="networkidle")
            if page.locator("[data-pos='start']").count() > 0:
                page.locator("[data-pos='start']").click()
                acc_start = page.locator("#u-curve-readout").inner_text()
                page.locator("[data-pos='middle']").click()
                acc_mid = page.locator("#u-curve-readout").inner_text()
                ok_u = ("Primacy" in acc_start or "開頭" in acc_start) and ("中段" in acc_mid or "谷底" in acc_mid)
                if not ok_u:
                    interact_ok = False
                interact_notes.append(f"U型曲線互動={'OK' if ok_u else 'FAIL'}")

            # Slide 11 Quiz widget (scan for .quiz-widget)
            quiz_idx = page.evaluate(
                """() => {
                    const slides = window.SITE_DATA.deck.slides;
                    const idx = slides.findIndex(s => s.layout === 'quiz');
                    return idx >= 0 ? idx + 1 : -1;
                }"""
            )
            if quiz_idx > 0:
                page.goto(f"{base_url}/slides.html#slide-{quiz_idx}", wait_until="networkidle")
                if page.locator(".quiz-option").count() > 0:
                    page.locator(".quiz-option").first.click()
                    fb_len = len(page.locator(".quiz-feedback").first.inner_text().strip())
                    ok_quiz = fb_len > 10
                    if not ok_quiz:
                        interact_ok = False
                    interact_notes.append(f"小測驗回饋={'OK' if ok_quiz else 'FAIL'}")

            add_check(
                "B4-SLIDES-INTERACT",
                "簡報互動元件與 Wiki 溯源抽屜驗證",
                interact_ok,
                "；".join(interact_notes) if interact_notes else "簡報無互動元件可測試。",
            )

            # 4. Wiki Reader wiki.html
            page.goto(f"{base_url}/wiki.html", wait_until="networkidle")
            nav_count = page.locator(".wiki-nav-item").count()
            initial_title = page.locator("#wiki-doc-title").inner_text().strip()
            link_clicked = False
            if page.locator("#wiki-doc-body a.wikilink").count() > 0:
                page.locator("#wiki-doc-body a.wikilink").first.click()
                page.wait_for_timeout(120)
                new_title = page.locator("#wiki-doc-title").inner_text().strip()
                link_clicked = new_title != initial_title

            # Switch to Graph view
            graph_nodes = 0
            if page.locator("#btn-toggle-graph").count() > 0:
                page.locator("#btn-toggle-graph").click()
                page.wait_for_timeout(150)
                graph_nodes = page.locator("#knowledge-graph-svg circle").count()
                if screenshots_dir is not None:
                    page.screenshot(path=str(screenshots_dir / "wiki-graph.png"))
                page.locator("#btn-toggle-graph").click()
                page.wait_for_timeout(100)

            if screenshots_dir is not None:
                page.screenshot(path=str(screenshots_dir / "wiki.png"))

            wiki_ok = nav_count >= 25 and link_clicked and graph_nodes >= 20
            add_check(
                "B4-WIKI-READER",
                "互動式 Wiki 閱讀器、雙向連結與知識圖譜",
                wiki_ok,
                f"側欄條目={nav_count}，點擊 [[wikilink]] 切換={link_clicked}，知識圖譜節點={graph_nodes}。",
            )

            # 5. Workflow & Reflection workflow.html
            page.goto(f"{base_url}/workflow.html", wait_until="networkidle")
            svg_boxes = page.locator("#workflow-graph-svg rect").count()
            if page.locator("#btn-graph-v1").count() > 0:
                page.locator("#btn-graph-v1").click()
                page.wait_for_timeout(100)
                page.locator("#btn-graph-v2").click()
                page.wait_for_timeout(100)
            if screenshots_dir is not None:
                page.screenshot(path=str(screenshots_dir / "workflow.png"))
            wf_ok = svg_boxes >= 5 and page.locator(".audit-table").count() >= 1
            add_check(
                "B4-WORKFLOW-PAGE",
                "Loop/Graph 架構圖與執行反思報告頁",
                wf_ok,
                f"SVG 流程節點框={svg_boxes}，審計對比表已渲染。",
            )

            # 6. Mobile responsive check (390x844)
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(f"{base_url}/index.html", wait_until="networkidle")
            mob_idx_over = page.evaluate(
                "() => document.documentElement.scrollWidth > window.innerWidth + 2"
            )
            page.goto(f"{base_url}/slides.html#reading", wait_until="networkidle")
            mob_sl_over = page.evaluate(
                "() => document.documentElement.scrollWidth > window.innerWidth + 2"
            )
            add_check(
                "B4-MOBILE-RWD",
                "行動端 390×844 RWD 零水平溢出",
                (not mob_idx_over) and (not mob_sl_over),
                f"index溢出={mob_idx_over}，slides閱讀模式溢出={mob_sl_over}。",
            )

            # 7. Zero JS / Console errors
            total_errs = len(page_errors) + len(console_errors)
            add_check(
                "B4-ZERO-JS-ERRORS",
                "全站 0 Console / Page JS 錯誤",
                total_errs == 0,
                f"Console errors={len(console_errors)}, Page errors={len(page_errors)}"
                + (f": {(page_errors + console_errors)[:3]}" if total_errs else "。"),
            )

            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    passed = all(c["passed"] for c in checks)
    return {
        "gate": "Gate 4: BrowserVisualGate",
        "mode": mode,
        "passed": passed,
        "checks": checks,
        "issues": issues,
        "slide_measurements": slide_measurements,
        "stats": {
            "total_slides_checked": len(slide_measurements),
            "overflow_slide_count": sum(1 for m in slide_measurements if m["overflow"]),
        },
    }


def merge_into_report(report_path: Path, browser_result: dict[str, Any]) -> None:
    """Merge browser verification results into a pipeline JSON report and update its Markdown summary."""
    report = load_json(report_path)
    report["gates"]["browser_gate"] = browser_result
    all_gates = [g for g in report["gates"].values() if g.get("status") != "skipped"]
    report["overall_passed"] = all(g.get("passed", False) for g in all_gates)

    all_issues: list[dict[str, Any]] = []
    for g in all_gates:
        all_issues.extend(g.get("issues", []))
    report["total_issues"] = len(all_issues)
    report["issues"] = all_issues
    save_json(report_path, report)

    # Refresh companion Markdown audit file
    md_path = report_path.with_name(report_path.name.replace("-report.json", "-audit.md"))
    write_text(md_path, format_markdown_audit(report))


def format_markdown_audit(report: dict[str, Any]) -> str:
    """Render concise Markdown audit report from structured pipeline JSON."""
    lines = [
        f"# Pipeline Execution Audit — {report['run_label']}",
        "",
        f"- **Mode**: `{report['mode']}`",
        f"- **Slides File**: `{report['slides_file']}`",
        f"- **Overall Status**: {'PASS' if report['overall_passed'] else 'FAIL'} ({report['total_issues']} issues)",
        "",
        "## Gate Summary",
        "",
        "| Gate | Status | Details |",
        "| :--- | :--- | :--- |",
    ]
    for key, gate in report["gates"].items():
        if gate.get("status") == "skipped":
            lines.append(f"| {gate.get('gate', key)} | SKIPPED | {gate.get('reason', '')} |")
        else:
            st = "PASS" if gate.get("passed") else "FAIL"
            iss_cnt = len(gate.get("issues", []))
            lines.append(f"| {gate.get('gate', key)} | {st} | {iss_cnt} issues |")

    if report.get("issues"):
        lines.extend(["", "## Detected Issues", ""])
        for idx, iss in enumerate(report["issues"], start=1):
            slide_tag = f"[{iss['slide']}] " if iss.get("slide") else ""
            lines.append(f"{idx}. **{iss['gate']} / {iss['check']}**: {slide_tag}{iss['detail']}")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Gate 4: BrowserVisualGate")
    parser.add_argument("--mode", default="v2", help="Run mode label (v1 or v2)")
    parser.add_argument("--report", default="", help="Optional pipeline JSON report to merge results into")
    parser.add_argument("--screenshots", default="", help="Directory to save screenshots")
    args = parser.parse_args()

    shots_dir = Path(args.screenshots).resolve() if args.screenshots else None
    result = run_browser_gate(DOCS_DIR, screenshots_dir=shots_dir, mode=args.mode)

    if args.report:
        merge_into_report(Path(args.report).resolve(), result)

    status = "PASS" if result["passed"] else "FAIL"
    print(f"[Gate 4: BrowserVisualGate ({args.mode})] {status} ({len(result['issues'])} issues)")
    for chk in result["checks"]:
        mark = "OK" if chk["passed"] else "FAIL"
        print(f"  [{mark}] {chk['id']} - {chk['name']}: {chk['detail']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
