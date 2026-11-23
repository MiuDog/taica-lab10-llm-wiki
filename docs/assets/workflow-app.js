/* Interactive Workflow Graph (v1 vs v2) & Live Audit Report Renderer */
(function () {
  const data = window.SITE_DATA;
  const elSvg = document.getElementById("workflow-graph-svg");
  const elInspector = document.getElementById("node-inspector");
  const elAudit = document.getElementById("audit-runs-container");
  const btnV1 = document.getElementById("btn-graph-v1");
  const btnV2 = document.getElementById("btn-graph-v2");

  let graphMode = "v2";

  const NODE_DETAILS = {
    discuss: {
      title: "1. 先討論後生成 (discussion/00-discuss-before-generate.md)",
      io: "輸入：作業目標與教學對象 → 輸出：受眾定義、7 大分類與 DAG 原則",
      rule: "必須在寫入任何 Wiki 知識頁與簡報前先定案，決定「教給誰看」與「先修順序」。",
    },
    ingest: {
      title: "2. Ingest 編譯迴圈 (raw/ × 6 → wiki/ × 16)",
      io: "輸入：唯讀 raw/src-01..06 → 輸出：跨頁互連 wiki/*.md + index.md + log.md",
      rule: "每攝取 1 篇原始資料即更新多張概念頁、補上 [SRC-XX] 與雙向連結，重複執行 6 輪。",
    },
    gate1: {
      title: "3. Gate 1: WikiLintGate (pipeline/wiki_lint.py)",
      io: "檢查對象：SCHEMA.md、raw/、wiki/、index.md、log.md",
      rule: "強制通過 8 項健檢：Frontmatter 欄位、83 條 [[wikilink]] 零斷鏈、零孤島、索引同步、來源真確性。失敗即回退重編。",
    },
    v1_draft: {
      title: "[v1 初版] 一次直接生成所有投影片 (DraftSlides)",
      io: "輸入：Wiki 檔案 → 輸出：data/slides-v1.json",
      rule: "v1 缺乏前置大綱檢查（OutlineGate）與嚴格字數/術語約束，導致單頁過密溢出、術語早洩與 Citation Drift。",
    },
    v1_review: {
      title: "[v1 初版] 事後才統一檢查與重修",
      io: "輸入：已生成的全部投影片 → 輸出：大量返工清單",
      rule: "錯誤到生成完才被抓出，修一頁的概念順序常牽動前後好幾頁一起重寫，成本極高。",
    },
    outline: {
      title: "4. 規劃教學大綱 (data/outline-v2.json)",
      io: "輸入：index.md + glossary-for-beginners → 輸出：14 頁骨架與先修順序宣告",
      rule: "僅規劃每頁單元定位、預計引用之 wiki_refs / source_refs 與字數上限，尚未展開正文。",
    },
    gate2: {
      title: "5. Gate 2: OutlineGate 前移攔截 (pipeline/outline_gate.py)",
      io: "檢查對象：outline-v2.json",
      rule: "前移檢查 5 大要件：頁數 10~16 頁、先修概念 DAG 順序不倒置、字數預算 <=450、覆蓋 >=80% Wiki 與 100% Raw。",
    },
    draft_v2: {
      title: "6. 逐頁生成投影片 (data/slides-v2.json)",
      io: "輸入：通過 Gate 2 的單頁大綱 + 該頁指定的 1~2 篇 Wiki（Select）",
      rule: "每次只載入該頁對應的 Wiki 頁面進行撰寫，並強制附上 wiki_refs、source_refs 與 grounded_terms。",
    },
    gate3: {
      title: "7. Gate 3: SlideGate 逐頁檢查 (pipeline/slide_gate.py)",
      io: "檢查對象：每張投影片獨立檢查 6 項條件",
      rule: "抓出 Citation Drift、未據實溯源術語、初學者字數/要點超載、以及術語未介紹先登場；不通過僅重寫該單頁。",
    },
    gate4: {
      title: "8. Gate 4: BrowserGate 實機瀏覽器驗證 (pipeline/browser_gate.py)",
      io: "檢查對象：build_site.py 產出的 docs/ 全站",
      rule: "Playwright 實測 1280×720 全 14 頁零垂直/水平溢出、互動元件、溯源抽屜、Wiki 圖譜與 390×844 RWD，全站 0 JS Error。",
    },
  };

  function esc(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function box(id, x, y, w, h, title, sub, fill, stroke) {
    return `
      <g class="wf-node" data-node-id="${id}" style="cursor:pointer;">
        <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
        <text x="${x + w / 2}" y="${y + 24}" text-anchor="middle" font-size="13" font-weight="700" fill="#14213d">${esc(title)}</text>
        <text x="${x + w / 2}" y="${y + 44}" text-anchor="middle" font-size="11" fill="#475569">${esc(sub)}</text>
      </g>
    `;
  }

  function arrow(x1, y1, x2, y2, color = "#64748b", dashed = false) {
    return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="2" ${
      dashed ? 'stroke-dasharray="5 4"' : ""
    } marker-end="url(#arrowhead)"/>`;
  }

  function renderGraph() {
    if (btnV1 && btnV2) {
      btnV1.className = graphMode === "v1" ? "btn btn-sm btn-primary" : "btn btn-sm";
      btnV2.className = graphMode === "v2" ? "btn btn-sm btn-primary" : "btn btn-sm";
    }

    const defs = `
      <defs>
        <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="#64748b"/>
        </marker>
      </defs>
    `;

    // Loop A (Top row: always active)
    const loopA = `
      <text x="20" y="26" font-size="13" font-weight="800" fill="#0f766e">Loop A · LLM Wiki 知識編譯與健檢迴圈（反覆執行 6 輪 Ingest）</text>
      ${box("discuss", 20, 42, 200, 62, "1. 先討論後生成", "discussion/ + SCHEMA.md", "#f3efe6", "#b45309")}
      ${arrow(220, 73, 270, 73)}
      ${box("ingest", 270, 42, 230, 62, "2. Ingest 編譯迴圈", "6 篇 Raw → 16 篇 Wiki", "#ccfbf1", "#0f766e")}
      ${arrow(500, 73, 555, 73)}
      ${box("gate1", 555, 42, 215, 62, "3. Gate 1: WikiLint", "斷鏈 / 孤島 / 索引 / 來源", "#fef3c7", "#d97706")}
      <path d="M 662 104 C 662 136, 385 136, 385 106" fill="none" stroke="#be123c" stroke-width="1.8" stroke-dasharray="5 3" marker-end="url(#arrowhead)"/>
      <text x="524" y="138" text-anchor="middle" font-size="11" font-weight="700" fill="#be123c">FAIL → 回退修補斷鏈或摘要</text>
      ${arrow(770, 73, 835, 73)}
      <rect x="835" y="42" width="125" height="62" rx="10" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
      <text x="897" y="68" text-anchor="middle" font-size="12" font-weight="700" fill="#166534">Wiki PASS</text>
      <text x="897" y="86" text-anchor="middle" font-size="11" fill="#166534">進入簡報階段</text>
    `;

    let loopB = "";
    if (graphMode === "v1") {
      loopB = `
        <text x="20" y="190" font-size="13" font-weight="800" fill="#be123c">Loop B (v1 初版線性流程) · 缺乏 OutlineGate 前移檢查，問題集中在最後才爆發</text>
        ${box("v1_draft", 40, 215, 250, 66, "DraftSlides (一次寫全部)", "未限制字數與先修順序 DAG", "#ffe4e6", "#be123c")}
        ${arrow(290, 248, 360, 248)}
        ${box("v1_review", 360, 215, 250, 66, "事後人工/腳本掃描 (SlideGate)", "抓出 1280×720 溢出、術語早洩與漂移", "#fef3c7", "#d97706")}
        ${arrow(610, 248, 680, 248)}
        ${box("gate4", 680, 215, 250, 66, "Gate 4: BrowserGate 實機測試", "v1 實測抓出第 3 頁垂直溢出", "#ffe4e6", "#be123c")}
        <path d="M 805 281 C 805 345, 165 345, 165 283" fill="none" stroke="#be123c" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#arrowhead)"/>
        <text x="485" y="340" text-anchor="middle" font-size="12" font-weight="700" fill="#be123c">Run #1 實測結果：FAIL（4 項缺陷 → 需大幅返工重排）</text>
      `;
    } else {
      loopB = `
        <text x="20" y="190" font-size="13" font-weight="800" fill="#14213d">Loop B (v2 前移檢查狀態圖) · 把順序與密度鎖在寫作前，失敗只局部重試單一節點</text>
        ${box("outline", 20, 215, 165, 64, "4. 教學大綱", "outline-v2.json", "#f8fafc", "#475569")}
        ${arrow(185, 247, 215, 247)}
        ${box("gate2", 215, 215, 180, 64, "5. Gate 2: Outline", "DAG / 字數預算 (前移!)", "#fef3c7", "#d97706")}
        ${arrow(395, 247, 425, 247)}
        ${box("draft_v2", 425, 215, 165, 64, "6. 逐頁生成正文", "Select 該頁 Wiki", "#dbeafe", "#1d4ed8")}
        ${arrow(590, 247, 620, 247)}
        ${box("gate3", 620, 215, 165, 64, "7. Gate 3: SlideGate", "Citation / 密度 / 術語", "#fef3c7", "#d97706")}
        ${arrow(785, 247, 815, 247)}
        ${box("gate4", 815, 215, 145, 64, "8. Gate 4: 實機", "1280×720 + 互動", "#dcfce7", "#16a34a")}
        <path d="M 305 279 C 305 322, 102 322, 102 281" fill="none" stroke="#d97706" stroke-width="1.8" stroke-dasharray="4 3" marker-end="url(#arrowhead)"/>
        <text x="205" y="335" text-anchor="middle" font-size="11" font-weight="700" fill="#b45309">FAIL → 僅調大綱</text>
        <path d="M 702 279 C 702 322, 507 322, 507 281" fill="none" stroke="#1d4ed8" stroke-width="1.8" stroke-dasharray="4 3" marker-end="url(#arrowhead)"/>
        <text x="605" y="335" text-anchor="middle" font-size="11" font-weight="700" fill="#1d4ed8">FAIL → 僅重寫該單頁</text>
        <text x="490" y="382" text-anchor="middle" font-size="12" font-weight="700" fill="#166534">Run #2 實測結果：4 道關卡全部 PASS（0 錯誤、14 頁全過）</text>
      `;
    }

    elSvg.innerHTML = defs + loopA + loopB;
  }

  function renderAuditRuns() {
    if (!data || !data.audit || !Array.isArray(data.audit.runs) || !data.audit.runs.length) {
      elAudit.innerHTML = `<p style="color:var(--ink-muted);">尚未產生審計紀錄（請執行 <code>python pipeline/run_pipeline.py</code>）。</p>`;
      return;
    }

    const runs = data.audit.runs;
    let html = `
      <table class="audit-table">
        <thead>
          <tr>
            <th>執行輪次</th>
            <th>Gate 1 (WikiLint)</th>
            <th>Gate 2 (OutlineGate)</th>
            <th>Gate 3 (SlideGate)</th>
            <th>Gate 4 (BrowserGate)</th>
            <th>總結</th>
          </tr>
        </thead>
        <tbody>
    `;

    function gatePill(g) {
      if (!g) return `<span class="pill pill-skip">N/A</span>`;
      if (g.status === "skipped") return `<span class="pill pill-skip">未啟用 (v1 缺失)</span>`;
      const cnt = (g.issues || []).length;
      return g.passed
        ? `<span class="pill pill-pass">PASS (0 錯)</span>`
        : `<span class="pill pill-fail">FAIL (${cnt} 錯)</span>`;
    }

    for (const r of runs) {
      const g = r.gates || {};
      html += `
        <tr>
          <td><strong>${esc(r.run_label)}</strong><br><span style="font-size:0.78rem;color:var(--ink-muted);">${esc(r.slides_file)}</span></td>
          <td>${gatePill(g.wiki_lint)}</td>
          <td>${gatePill(g.outline_gate)}</td>
          <td>${gatePill(g.slide_gate)}</td>
          <td>${gatePill(g.browser_gate)}</td>
          <td>${
            r.overall_passed
              ? `<span class="pill pill-pass">ALL PASS</span>`
              : `<span class="pill pill-fail">FAIL · 共 ${r.total_issues} 項問題</span>`
          }</td>
        </tr>
      `;
    }
    html += `</tbody></table>`;

    // Detailed issues list for any failing run (Run #1) and verification checks for Run #2
    for (const r of runs) {
      if (r.issues && r.issues.length) {
        html += `
          <div class="callout-warn" style="margin-top:1rem;">
            <strong>${esc(r.run_label)} 實際偵測到的問題明細（共 ${r.issues.length} 條）：</strong>
            <ol style="margin:0.5rem 0 0;padding-left:1.3rem;">
              ${r.issues
                .map(
                  (iss) =>
                    `<li><strong>[${esc(iss.gate)} / ${esc(iss.check)}]</strong> ${
                      iss.slide ? `<code>${esc(iss.slide)}</code> ` : ""
                    }${esc(iss.detail)}</li>`
                )
                .join("")}
            </ol>
          </div>
        `;
      } else if (r.overall_passed) {
        const bg = (r.gates && r.gates.browser_gate) || {};
        const sc = (bg.stats && bg.stats.total_slides_checked) || 14;
        html += `
          <div class="callout-info" style="margin-top:1rem;">
            <strong>${esc(r.run_label)} 驗收結果：全數通過！</strong>
            <div style="margin-top:0.35rem;font-size:0.92rem;">
              實機 Playwright 已走訪全數 <strong>${sc} 頁</strong> <code>1280×720</code> 簡報舞台（0 頁面溢出）、點測所有互動模擬器與小測驗、驗證 Wiki <code>[[wikilink]]</code> 與知識圖譜渲染，以及 <code>390×844</code> 行動版零水平溢出（0 Console/JS Errors）。
            </div>
          </div>
        `;
      }
    }

    elAudit.innerHTML = html;
  }

  document.addEventListener("click", (ev) => {
    const node = ev.target.closest(".wf-node");
    if (node) {
      const info = NODE_DETAILS[node.dataset.nodeId];
      if (info && elInspector) {
        elInspector.innerHTML = `
          <strong>${esc(info.title)}</strong><br>
          <span style="font-size:0.88rem;color:var(--ink-muted);">${esc(info.io)}</span><br>
          <span style="font-size:0.92rem;">${esc(info.rule)}</span>
        `;
      }
    }
  });

  if (btnV1) {
    btnV1.addEventListener("click", () => {
      graphMode = "v1";
      renderGraph();
    });
  }
  if (btnV2) {
    btnV2.addEventListener("click", () => {
      graphMode = "v2";
      renderGraph();
    });
  }

  renderGraph();
  renderAuditRuns();
})();
