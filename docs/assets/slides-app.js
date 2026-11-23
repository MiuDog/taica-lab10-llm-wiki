/* Interactive HTML Slide Deck Engine with Wiki Provenance Drawer & Embedded Simulators */
(function () {
  const data = window.SITE_DATA;
  if (!data || !data.deck || !Array.isArray(data.deck.slides)) {
    return;
  }

  const slides = data.deck.slides;
  const total = slides.length;
  let activeIdx = 0;
  let notesOpen = false;
  let readingMode = false;

  // Per-slide ephemeral interactive states
  const deskState = {
    docs: 1,
    tools: 3,
    chatTurns: 4,
  };
  let uCurvePos = "middle";
  let activeFailureIdx = 0;
  const quizAnswers = {};

  const elStage = document.getElementById("slide-stage");
  const elUnitBadge = document.getElementById("slide-unit-badge");
  const elProgress = document.getElementById("slide-progress-fill");
  const elCounter = document.getElementById("slide-counter");
  const elProvenance = document.getElementById("provenance-strip");
  const elNotesBar = document.getElementById("notes-bar");
  const elNotesText = document.getElementById("notes-text");
  const elOverviewModal = document.getElementById("overview-modal");
  const elOverviewGrid = document.getElementById("overview-grid");
  const elDrawer = document.getElementById("wiki-drawer");
  const elBackdrop = document.getElementById("drawer-backdrop");
  const elDrawerTitle = document.getElementById("wiki-drawer-title");
  const elDrawerBody = document.getElementById("wiki-drawer-body");
  const elDrawerFullLink = document.getElementById("wiki-drawer-open-full");

  function esc(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderBullets(items) {
    if (!items || !items.length) return "";
    return `<ul class="bullet-list">${items
      .map((item) => {
        if (typeof item === "string") {
          return `<li class="bullet-item">${esc(item)}</li>`;
        }
        const label = item.label || item.title || "";
        const text = item.text || item.detail || "";
        return `<li class="bullet-item">${label ? `<strong>${esc(label)}：</strong>` : ""}${esc(text)}</li>`;
      })
      .join("")}</ul>`;
  }

  function renderDeskSimulator() {
    const signalTokens = 2500;
    const noiseTokens = deskState.docs * 4500 + deskState.tools * 850 + deskState.chatTurns * 400;
    const totalTokens = signalTokens + noiseTokens;
    const cap = 40000;
    const pct = Math.min(100, Math.round((totalTokens / cap) * 100));
    const signalPct = Math.round((signalTokens / totalTokens) * 100);
    const sigWidth = Math.max(4, Math.round((signalTokens / cap) * 100));
    const noiseWidth = Math.min(100 - sigWidth, Math.round((noiseTokens / cap) * 100));

    let statusText = "書桌清爽：注意力高度集中於關鍵任務。";
    let statusColor = "var(--accent-teal)";
    if (signalPct < 30 && signalPct >= 12) {
      statusText = "警告：雜訊開始稀釋 Attention Budget，容易發生漏看規則。";
      statusColor = "var(--accent-amber)";
    } else if (signalPct < 12) {
      statusText = "嚴重 Context Rot：關鍵指令被淹沒在雜物堆中，AI 準確率大幅下滑！";
      statusColor = "var(--accent-rose)";
    }

    return `
      <div class="sim-panel" id="desk-sim">
        <div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <strong style="color:var(--ink-primary);font-size:0.95rem;">互動實驗：AI 的工作書桌 (RAM) 壓力測試</strong>
            <span id="desk-usage-label" style="font-family:var(--font-mono);font-size:0.82rem;font-weight:700;">
              已用 ${totalTokens.toLocaleString()} Tokens · 有效訊號佔 ${signalPct}%
            </span>
          </div>
          <div class="sim-bar-track" aria-label="書桌空間分佈">
            <div class="sim-bar-signal" style="width:${sigWidth}%" title="真正需要的關鍵任務資訊"></div>
            <div class="sim-bar-noise" style="width:${noiseWidth}%" title="累積的無關文件/多餘工具/舊聊天"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.76rem;color:var(--ink-muted);margin-top:4px;">
            <span>■ 關鍵指令與本步線索 (${signalTokens.toLocaleString()} tok)</span>
            <span>■ 干擾雜物 (${noiseTokens.toLocaleString()} tok / 佔比 ${pct}%)</span>
          </div>
        </div>

        <div style="font-size:0.86rem;font-weight:700;color:${statusColor};background:#fff;border:1px solid var(--border-warm);border-radius:8px;padding:8px 10px;">
          ${statusText}
        </div>

        <div class="sim-btns">
          <button class="sim-btn" data-sim-action="add-noise">+ 塞進 2 份無關 PDF</button>
          <button class="sim-btn" data-sim-action="add-tools">+ 掛載 10 個備用工具</button>
          <button class="sim-btn" data-sim-action="add-chat">+ 累積 15 輪舊閒聊</button>
          <button class="sim-btn active" data-sim-action="reset-select">🧹 套用 Select：清空雜物</button>
        </div>
      </div>
    `;
  }

  function renderUCurveSimulator() {
    const scenarios = {
      start: {
        label: "放在最開頭（Primacy 首因區）",
        acc: "約 75%～82%（高記憶區）",
        cx: 65,
        cy: 34,
        msg: "模型具備首因效應（Primacy Bias），放在最前端的系統規則與關鍵文件最容易被精準抓住。",
      },
      middle: {
        label: "埋在長文中段（Middle 迷失谷底）",
        acc: "低於 55%（甚至低於完全不給資料！）",
        cx: 210,
        cy: 118,
        msg: "陷入「中段盲區（Lost in the Middle）」：大量干擾文件把注意力稀釋，準確率跌進 U 型谷底。",
      },
      end: {
        label: "放在最結尾（Recency 近因區）",
        acc: "約 73%～80%（高記憶區）",
        cx: 355,
        cy: 40,
        msg: "觸發近因效應（Recency Bias）——這也是 Manus 用 todo.md 在對話末端「復誦目標」的原因！",
      },
    };
    const cur = scenarios[uCurvePos] || scenarios.middle;

    return `
      <div class="sim-panel" id="u-curve-sim">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <strong style="color:var(--ink-primary);font-size:0.9rem;">互動實證：關鍵答案放哪裡，AI 最記得？</strong>
          <span style="font-size:0.74rem;color:var(--ink-muted);">[SRC-01] U 型曲線模擬</span>
        </div>

        <svg viewBox="0 0 420 148" style="width:100%;max-height:136px;background:#fff;border:1px solid var(--border-warm);border-radius:10px;">
          <line x1="38" y1="14" x2="38" y2="128" stroke="#cbd5e1" stroke-width="1.5"/>
          <line x1="38" y1="128" x2="395" y2="128" stroke="#cbd5e1" stroke-width="1.5"/>
          <line x1="38" y1="96" x2="395" y2="96" stroke="#94a3b8" stroke-dasharray="4 4" stroke-width="1.2"/>
          <text x="46" y="91" font-size="9.5" fill="#64748b">Closed-book Baseline（不給任何文件基準線）</text>
          <path d="M 65 34 Q 210 162 355 40" fill="none" stroke="#0f766e" stroke-width="3.2" stroke-linecap="round"/>
          <circle cx="65" cy="34" r="4.5" fill="#94a3b8"/>
          <circle cx="210" cy="118" r="4.5" fill="#94a3b8"/>
          <circle cx="355" cy="40" r="4.5" fill="#94a3b8"/>
          <circle cx="${cur.cx}" cy="${cur.cy}" r="8" fill="#d97706" stroke="#fff" stroke-width="2"/>
          <text x="48" y="142" font-size="10" fill="#334155">開頭 (Start)</text>
          <text x="180" y="142" font-size="10" fill="#334155">中段 (Middle)</text>
          <text x="322" y="142" font-size="10" fill="#334155">結尾 (End)</text>
        </svg>

        <div id="u-curve-readout" style="background:#fff;border:1px solid var(--border-warm);border-radius:8px;padding:7px 10px;font-size:0.8rem;line-height:1.42;">
          <strong>${esc(cur.label)}</strong> · 參考表現：<strong>${esc(cur.acc)}</strong><br>
          <span>${esc(cur.msg)}</span>
        </div>

        <div class="sim-btns">
          <button class="sim-btn ${uCurvePos === "start" ? "active" : ""}" data-pos="start">放在開頭 (Primacy)</button>
          <button class="sim-btn ${uCurvePos === "middle" ? "active" : ""}" data-pos="middle">放在中間 (Middle)</button>
          <button class="sim-btn ${uCurvePos === "end" ? "active" : ""}" data-pos="end">放在結尾 (Recency)</button>
        </div>
      </div>
    `;
  }

  function renderSlideInner(slide, idx) {
    const layout = slide.layout || "concept";
    let bodyHtml = "";

    if (layout === "hero") {
      const steps = slide.cards || [];
      bodyHtml = `
        <div class="hero-slide-box">
          ${slide.hook ? `<div class="slide-hook">${esc(slide.hook)}</div>` : ""}
          ${renderBullets(slide.bullets)}
          <div class="hero-journey">
            ${steps
              .map(
                (st, i) => `
              <div class="journey-step">
                <div class="journey-step-num">STEP 0${i + 1}</div>
                <div class="journey-step-title">${esc(st.title)}</div>
                <div class="journey-step-desc">${esc(st.desc)}</div>
              </div>`
              )
              .join("")}
          </div>
        </div>
      `;
    } else if (layout === "desk_sim") {
      bodyHtml = `
        ${slide.hook ? `<div class="slide-hook">${esc(slide.hook)}</div>` : ""}
        <div class="grid-2">
          <div style="display:flex;flex-direction:column;justify-content:center;">
            ${renderBullets(slide.bullets)}
          </div>
          ${renderDeskSimulator()}
        </div>
      `;
    } else if (layout === "compare" && slide.comparison) {
      const left = slide.comparison.left || {};
      const right = slide.comparison.right || {};
      bodyHtml = `
        ${slide.hook ? `<div class="slide-hook">${esc(slide.hook)}</div>` : ""}
        <div class="grid-2-equal">
          <div class="mini-card" style="background:var(--bg-paper);">
            <h3 style="color:var(--ink-muted);">${esc(left.title)}</h3>
            ${renderBullets(left.points)}
          </div>
          <div class="mini-card" style="border-color:var(--accent-teal);background:#f0fdfa;">
            <h3 style="color:var(--accent-teal);">${esc(right.title)}</h3>
            ${renderBullets(right.points)}
          </div>
        </div>
      `;
    } else if (layout === "u_curve") {
      bodyHtml = `
        ${slide.hook ? `<div class="slide-hook">${esc(slide.hook)}</div>` : ""}
        <div class="grid-2">
          <div style="display:flex;flex-direction:column;justify-content:center;">
            ${renderBullets(slide.bullets)}
          </div>
          ${renderUCurveSimulator()}
        </div>
      `;
    } else if (layout === "failure_grid") {
      const cards = slide.cards || [];
      const active = cards[activeFailureIdx] || cards[0] || {};
      bodyHtml = `
        ${slide.hook ? `<div class="slide-hook">${esc(slide.hook)}</div>` : ""}
        <div class="grid-4" id="failure-cards">
          ${cards
            .map(
              (c, i) => `
            <button class="failure-card ${i === activeFailureIdx ? "active" : ""}" data-failure-idx="${i}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <strong style="color:var(--ink-primary);font-size:0.96rem;">${esc(c.title)}</strong>
                <span class="pill" style="font-size:0.72rem;padding:0.12rem 0.5rem;">${esc(c.badge || "點擊診斷")}</span>
              </div>
              <div style="font-size:0.84rem;color:var(--ink-body);">${esc(c.symptom)}</div>
            </button>`
            )
            .join("")}
        </div>
        <div class="failure-detail-box" id="failure-detail-box">
          <strong>🔍 症狀診斷 · ${esc(active.title)}：</strong>${esc(active.cause || active.desc || "")}
          ${active.fix ? `<br><strong>🛠 工程處方：</strong>${esc(active.fix)}` : ""}
        </div>
      `;
    } else if (layout === "wsci_overview") {
      const cards = slide.cards || [];
      bodyHtml = `
        ${slide.hook ? `<div class="slide-hook">${esc(slide.hook)}</div>` : ""}
        <div class="grid-4">
          ${cards
            .map(
              (c) => `
            <div class="mini-card">
              <h3>${esc(c.title)}</h3>
              <p style="margin-bottom:4px;"><strong>白話比喻：</strong>${esc(c.analogy || c.desc)}</p>
              ${c.fix ? `<p style="font-size:0.82rem;color:var(--accent-teal);font-weight:700;">對治：${esc(c.fix)}</p>` : ""}
            </div>`
            )
            .join("")}
        </div>
      `;
    } else if (layout === "wsci_pair") {
      const cards = slide.cards || [];
      bodyHtml = `
        ${slide.hook ? `<div class="slide-hook">${esc(slide.hook)}</div>` : ""}
        <div class="grid-2-equal">
          ${cards
            .map(
              (c) => `
            <div class="mini-card" style="display:flex;flex-direction:column;justify-content:space-between;gap:8px;">
              <div>
                <h3>${esc(c.title)}</h3>
                <p>${esc(c.desc)}</p>
              </div>
              ${
                c.cause
                  ? `<div style="background:#fff;border:1px dashed var(--border-warm);border-radius:8px;padding:8px 10px;font-size:0.82rem;color:var(--ink-primary);font-weight:600;">${esc(c.cause)}</div>`
                  : ""
              }
            </div>`
            )
            .join("")}
        </div>
        ${renderBullets(slide.bullets)}
      `;
    } else if (layout === "concept_cards") {
      const cards = slide.cards || [];
      bodyHtml = `
        ${slide.hook ? `<div class="slide-hook">${esc(slide.hook)}</div>` : ""}
        ${
          cards.length
            ? `<div class="cards-row">${cards
                .map(
                  (c) => `
                <div class="mini-card">
                  <h3>${esc(c.title)}</h3>
                  <p>${esc(c.desc || c.symptom || "")}</p>
                </div>`
                )
                .join("")}</div>`
            : ""
        }
        ${renderBullets(slide.bullets)}
      `;
    } else if (layout === "quiz") {
      const items = (slide.interactive && slide.interactive.questions) || [];
      bodyHtml = `
        ${slide.hook ? `<div class="slide-hook">${esc(slide.hook)}</div>` : ""}
        <div class="quiz-grid quiz-widget">
          ${items
            .map((q, qIdx) => {
              const chosen = quizAnswers[qIdx];
              let fbHtml = "點選上方任一選項檢驗你的觀念。";
              if (chosen !== undefined) {
                const isOk = chosen === q.answer;
                fbHtml = `<span style="color:${isOk ? "#166534" : "#be123c"};font-weight:700;">${
                  isOk ? "✓ 答對了！" : "✗ 再想一下："
                }</span> ${esc(q.explain)} <button class="provenance-pill" data-wiki-open="${esc(q.wiki)}" style="margin-top:4px;">[[${esc(q.wiki)}]]</button>`;
              }
              return `
                <div class="quiz-card">
                  <div class="quiz-q">Q${qIdx + 1}. ${esc(q.q)}</div>
                  <div class="quiz-options">
                    ${q.options
                      .map((opt, oIdx) => {
                        let cls = "quiz-option";
                        if (chosen !== undefined) {
                          if (oIdx === q.answer) cls += " correct";
                          else if (oIdx === chosen) cls += " wrong";
                        }
                        return `<button class="${cls}" data-quiz-q="${qIdx}" data-quiz-opt="${oIdx}">${esc(opt)}</button>`;
                      })
                      .join("")}
                  </div>
                  <div class="quiz-feedback">${fbHtml}</div>
                </div>
              `;
            })
            .join("")}
        </div>
      `;
    } else if (layout === "matrix") {
      const mid = Math.ceil(slides.length / 2);
      const renderTable = (subset, offset) => `
        <div class="matrix-wrap">
          <table class="matrix-table">
            <thead>
              <tr>
                <th>頁</th>
                <th>簡報主題</th>
                <th>對應 Wiki（點擊查看）</th>
                <th>來源</th>
              </tr>
            </thead>
            <tbody>
              ${subset
                .map((s, idx) => {
                  const realIdx = offset + idx;
                  const shortTitle = s.title.length > 14 ? s.title.slice(0, 13) + "…" : s.title;
                  return `
                    <tr>
                      <td><button class="sim-btn" data-jump-slide="${realIdx}" style="padding:1px 6px;font-size:0.7rem;">S${realIdx + 1}</button></td>
                      <td title="${esc(s.title)}"><strong>${esc(shortTitle)}</strong></td>
                      <td>${(s.wiki_refs || [])
                        .map((w) => `<button class="provenance-pill" data-wiki-open="${esc(w)}" style="padding:1px 5px;font-size:0.68rem;margin:1px;">${esc(w)}</button>`)
                        .join(" ")}</td>
                      <td style="font-family:var(--font-mono);font-size:0.68rem;">${esc((s.source_refs || []).join(", "))}</td>
                    </tr>`;
                })
                .join("")}
            </tbody>
          </table>
        </div>
      `;
      bodyHtml = `
        ${slide.hook ? `<div class="slide-hook">${esc(slide.hook)}</div>` : ""}
        <div class="matrix-2col">
          ${renderTable(slides.slice(0, mid), 0)}
          ${renderTable(slides.slice(mid), mid)}
        </div>
      `;
    } else {
      bodyHtml = `
        ${slide.hook ? `<div class="slide-hook">${esc(slide.hook)}</div>` : ""}
        ${renderBullets(slide.bullets)}
      `;
    }

    return `
      <div class="slide-header">
        <div>
          <h1 class="slide-title">${esc(slide.title)}</h1>
          ${slide.subtitle ? `<p class="slide-subtitle">${esc(slide.subtitle)}</p>` : ""}
        </div>
        <span class="slide-num-pill">Slide ${idx + 1} / ${total}</span>
      </div>
      <div class="slide-body">${bodyHtml}</div>
      ${slide.takeaway ? `<div class="slide-takeaway">💡 本頁帶走一句話：${esc(slide.takeaway)}</div>` : ""}
    `;
  }

  function renderProvenanceBar(slide) {
    const wikiPills = (slide.wiki_refs || [])
      .map(
        (slug) =>
          `<button class="provenance-pill" data-wiki-open="${esc(slug)}" title="開啟 Wiki 知識頁">[[${esc(slug)}]]</button>`
      )
      .join("");
    const srcPills = (slide.source_refs || [])
      .map(
        (src) =>
          `<button class="provenance-pill provenance-src" data-wiki-open="raw-${esc(src.toLowerCase())}" title="開啟原始文獻">[${esc(src)}]</button>`
      )
      .join("");
    elProvenance.innerHTML = `<span class="provenance-label">本頁知識溯源（點擊驗證）：</span>${wikiPills}${srcPills}`;
  }

  function render() {
    if (readingMode) {
      document.body.classList.add("reading-mode");
      elStage.innerHTML = slides
        .map(
          (sl, i) => `
          <article class="slide-card" id="${esc(sl.id)}">
            ${renderSlideInner(sl, i)}
            <div style="margin-top:8px;padding-top:8px;border-top:1px dashed var(--border-warm);display:flex;flex-wrap:wrap;gap:6px;align-items:center;">
              <span style="font-size:0.78rem;color:var(--ink-muted);font-weight:700;">溯源：</span>
              ${(sl.wiki_refs || []).map((w) => `<button class="provenance-pill" data-wiki-open="${esc(w)}">[[${esc(w)}]]</button>`).join("")}
              ${(sl.source_refs || []).map((s) => `<button class="provenance-pill provenance-src" data-wiki-open="raw-${esc(s.toLowerCase())}">[${esc(s)}]</button>`).join("")}
            </div>
          </article>`
        )
        .join("");
      elUnitBadge.textContent = "全覽捲動閱讀模式";
      elCounter.textContent = `${total} 頁全部展開`;
      elProgress.style.width = "100%";
      document.getElementById("btn-mode-toggle").textContent = "切回單頁簡報模式";
      return;
    }

    document.body.classList.remove("reading-mode");
    const slide = slides[activeIdx];
    document.body.dataset.activeSlide = String(activeIdx + 1);
    elStage.innerHTML = `<article class="slide-card" id="slide-card">${renderSlideInner(slide, activeIdx)}</article>`;
    elUnitBadge.textContent = slide.unit_name || `Unit ${slide.unit_num || 1}`;
    elCounter.textContent = `${activeIdx + 1} / ${total}`;
    elProgress.style.width = `${Math.round(((activeIdx + 1) / total) * 100)}%`;
    elNotesText.textContent = slide.speaker_notes || "";
    renderProvenanceBar(slide);
    document.getElementById("btn-mode-toggle").textContent = "捲動閱讀模式";
  }

  function goToSlide(idx, updateHash = true) {
    activeIdx = Math.max(0, Math.min(total - 1, idx));
    if (readingMode) {
      readingMode = false;
    }
    if (updateHash) {
      history.replaceState(null, "", `#${slides[activeIdx].id}`);
    }
    render();
  }

  function openWikiDrawer(docId) {
    const doc = data.documents[docId];
    if (!doc) return;
    elDrawerTitle.textContent = doc.title;
    elDrawerBody.innerHTML = `
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;">
        <span class="pill">${esc(doc.category_label || doc.layer)}</span>
        ${(doc.sources || []).map((s) => `<span class="src-badge">[${esc(s)}]</span>`).join("")}
      </div>
      ${doc.html}
    `;
    elDrawerFullLink.href = `./wiki.html#${encodeURIComponent(docId)}`;
    elDrawer.classList.add("open");
    elBackdrop.classList.add("open");
    elDrawer.setAttribute("aria-hidden", "false");
  }

  function closeWikiDrawer() {
    elDrawer.classList.remove("open");
    elBackdrop.classList.remove("open");
    elDrawer.setAttribute("aria-hidden", "true");
  }

  function openOverview() {
    elOverviewGrid.innerHTML = slides
      .map(
        (sl, i) => `
      <button class="overview-thumb ${i === activeIdx ? "active" : ""}" data-jump-slide="${i}">
        <div style="font-family:var(--font-mono);font-size:0.75rem;color:var(--accent-teal);font-weight:700;">
          S${i + 1} · ${esc(sl.unit_name || "")}
        </div>
        <div style="font-weight:700;color:var(--ink-primary);margin-top:3px;font-size:0.9rem;">
          ${esc(sl.title)}
        </div>
      </button>`
      )
      .join("");
    elOverviewModal.classList.add("open");
    elOverviewModal.setAttribute("aria-hidden", "false");
  }

  function closeOverview() {
    elOverviewModal.classList.remove("open");
    elOverviewModal.setAttribute("aria-hidden", "true");
  }

  // Event delegation for interactive controls inside stage, provenance strip, drawer, and overview
  document.addEventListener("click", (ev) => {
    const target = ev.target.closest("[data-wiki-open], [data-doc-id], [data-sim-action], [data-pos], [data-failure-idx], [data-quiz-q], [data-jump-slide]");
    if (!target) return;

    if (target.dataset.wikiOpen) {
      ev.preventDefault();
      openWikiDrawer(target.dataset.wikiOpen);
      return;
    }
    if (target.dataset.docId) {
      ev.preventDefault();
      openWikiDrawer(target.dataset.docId);
      return;
    }
    if (target.dataset.simAction) {
      const act = target.dataset.simAction;
      if (act === "add-noise") deskState.docs += 2;
      else if (act === "add-tools") deskState.tools += 10;
      else if (act === "add-chat") deskState.chatTurns += 15;
      else if (act === "reset-select") {
        deskState.docs = 0;
        deskState.tools = 2;
        deskState.chatTurns = 2;
      }
      render();
      return;
    }
    if (target.dataset.pos) {
      uCurvePos = target.dataset.pos;
      render();
      return;
    }
    if (target.dataset.failureIdx !== undefined) {
      activeFailureIdx = Number(target.dataset.failureIdx);
      render();
      return;
    }
    if (target.dataset.quizQ !== undefined) {
      const qIdx = Number(target.dataset.quizQ);
      const optIdx = Number(target.dataset.quizOpt);
      quizAnswers[qIdx] = optIdx;
      render();
      return;
    }
    if (target.dataset.jumpSlide !== undefined) {
      const jumpIdx = Number(target.dataset.jumpSlide);
      closeOverview();
      goToSlide(jumpIdx);
    }
  });

  document.getElementById("btn-prev").addEventListener("click", () => goToSlide(activeIdx - 1));
  document.getElementById("btn-next").addEventListener("click", () => goToSlide(activeIdx + 1));
  document.getElementById("btn-overview").addEventListener("click", openOverview);
  document.getElementById("btn-close-overview").addEventListener("click", closeOverview);
  document.getElementById("wiki-drawer-close").addEventListener("click", closeWikiDrawer);
  elBackdrop.addEventListener("click", closeWikiDrawer);

  document.getElementById("btn-notes").addEventListener("click", () => {
    notesOpen = !notesOpen;
    elNotesBar.classList.toggle("open", notesOpen);
  });

  document.getElementById("btn-mode-toggle").addEventListener("click", () => {
    readingMode = !readingMode;
    history.replaceState(null, "", readingMode ? "#reading" : `#${slides[activeIdx].id}`);
    render();
  });

  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Escape") {
      closeWikiDrawer();
      closeOverview();
      return;
    }
    if (elDrawer.classList.contains("open") || elOverviewModal.classList.contains("open")) {
      return;
    }
    if (ev.key === "ArrowRight" || ev.key === "PageDown") {
      ev.preventDefault();
      goToSlide(activeIdx + 1);
    } else if (ev.key === "ArrowLeft" || ev.key === "PageUp") {
      ev.preventDefault();
      goToSlide(activeIdx - 1);
    } else if (ev.key === "Home") {
      ev.preventDefault();
      goToSlide(0);
    } else if (ev.key === "End") {
      ev.preventDefault();
      goToSlide(total - 1);
    } else if (ev.key.toLowerCase() === "g") {
      openOverview();
    } else if (ev.key.toLowerCase() === "s") {
      notesOpen = !notesOpen;
      elNotesBar.classList.toggle("open", notesOpen);
    }
  });

  function initFromHash() {
    const h = decodeURIComponent((location.hash || "").replace(/^#/, ""));
    if (h === "reading") {
      readingMode = true;
      render();
      return;
    }
    if (h) {
      const idx = slides.findIndex((s) => s.id === h);
      if (idx >= 0) {
        activeIdx = idx;
      }
    }
    render();
  }

  window.addEventListener("hashchange", initFromHash);
  initFromHash();
})();
