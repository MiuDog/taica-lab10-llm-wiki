/* Interactive LLM Wiki Reader, Bidirectional Backlinks & 3-Layer Knowledge Graph */
(function () {
  const data = window.SITE_DATA;
  if (!data || !data.documents) return;

  const docs = data.documents;
  const docList = Object.values(docs);
  let activeDocId = "overview-context-engineering";
  let showGraph = false;

  const elNavTree = document.getElementById("wiki-nav-tree");
  const elSearch = document.getElementById("wiki-search");
  const elMeta = document.getElementById("wiki-doc-meta");
  const elTitle = document.getElementById("wiki-doc-title");
  const elSummary = document.getElementById("wiki-doc-summary");
  const elBody = document.getElementById("wiki-doc-body");
  const elBackWiki = document.getElementById("backlinks-wiki-list");
  const elBackSlides = document.getElementById("backlinks-slide-list");
  const elArticleView = document.getElementById("wiki-article-view");
  const elGraphView = document.getElementById("wiki-graph-view");
  const elGraphSvg = document.getElementById("knowledge-graph-svg");

  const GROUP_ORDER = [
    "governance",
    "overview",
    "foundations",
    "failures",
    "strategies",
    "practice",
    "architecture",
    "reference",
    "raw",
  ];

  function esc(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderSidebar(filterText = "") {
    const q = filterText.trim().toLowerCase();
    const groups = new Map();
    for (const g of GROUP_ORDER) groups.set(g, []);

    for (const d of docList) {
      const cat = d.category || d.layer;
      const matchText = `${d.id} ${d.title} ${d.summary} ${(d.tags || []).join(" ")} ${(d.sources || []).join(" ")}`.toLowerCase();
      if (q && !matchText.includes(q)) continue;
      if (!groups.has(cat)) groups.set(cat, []);
      groups.get(cat).push(d);
    }

    let html = "";
    for (const [cat, items] of groups.entries()) {
      if (!items.length) continue;
      const label = data.categories[cat] || cat;
      html += `<div class="wiki-group-title">${esc(label)} (${items.length})</div>`;
      for (const item of items) {
        const cls = item.id === activeDocId && !showGraph ? "wiki-nav-item active" : "wiki-nav-item";
        html += `<button class="${cls}" data-select-doc="${esc(item.id)}">${esc(item.title)}</button>`;
      }
    }
    elNavTree.innerHTML = html || `<p style="font-size:0.85rem;color:var(--ink-muted);">找不到符合的條目</p>`;
  }

  function renderDoc(docId) {
    const doc = docs[docId] || docs["overview-context-engineering"];
    if (!doc) return;
    activeDocId = doc.id;
    showGraph = false;
    elArticleView.style.display = "block";
    elGraphView.style.display = "none";

    const pills = [
      `<span class="pill">${esc(doc.category_label || doc.layer)}</span>`,
      `<span class="pill" style="font-family:var(--font-mono);">${esc(doc.path || "")}</span>`,
    ];
    for (const s of doc.sources || []) {
      const rawId = `raw-${s.toLowerCase()}`;
      if (docs[rawId]) {
        pills.push(`<a href="#${rawId}" class="src-badge" data-doc-id="${rawId}">[${esc(s)}]</a>`);
      } else {
        pills.push(`<span class="src-badge">[${esc(s)}]</span>`);
      }
    }
    if (doc.url) {
      pills.push(
        `<a class="pill" href="${esc(doc.url)}" target="_blank" rel="noopener noreferrer">原文連結 ↗</a>`
      );
    }

    elMeta.innerHTML = pills.join(" ");
    elTitle.textContent = doc.title;
    elSummary.textContent = doc.summary || "";
    elBody.innerHTML = doc.html || "";

    const backWiki = doc.backlinks_wiki || [];
    elBackWiki.innerHTML = backWiki.length
      ? backWiki
          .map(
            (b) =>
              `<a href="#${esc(b.id)}" class="wikilink" data-doc-id="${esc(b.id)}">[[${esc(b.id)}]] ${esc(b.title)}</a>`
          )
          .join("")
      : `<span style="font-size:0.85rem;color:var(--ink-muted);">本層文件為知識上游或總控中心。</span>`;

    const backSlides = doc.backlinks_slides || [];
    elBackSlides.innerHTML = backSlides.length
      ? backSlides
          .map(
            (s) =>
              `<a href="./slides.html#${esc(s.id)}" class="pill" style="background:var(--accent-amber-bg);color:#78350f;">Slide ${s.index}: ${esc(s.title)} →</a>`
          )
          .join("")
      : `<span style="font-size:0.85rem;color:var(--ink-muted);">尚未直接映射至單一投影片。</span>`;

    renderSidebar(elSearch.value);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function renderGraph() {
    showGraph = true;
    elArticleView.style.display = "none";
    elGraphView.style.display = "block";
    renderSidebar(elSearch.value);

    const nodes = data.graph.nodes || [];
    const edges = data.graph.edges || [];

    const rawNodes = nodes.filter((n) => n.layer === "raw");
    const wikiNodes = nodes.filter((n) => n.layer === "wiki");
    const slideNodes = nodes.filter((n) => n.layer === "slide");

    const pos = {};
    function assignColumn(list, x, topPad, bottomPad) {
      const span = 620 - topPad - bottomPad;
      const step = list.length > 1 ? span / (list.length - 1) : 0;
      list.forEach((n, i) => {
        pos[n.id] = { x, y: topPad + i * step, node: n };
      });
    }
    assignColumn(rawNodes, 110, 75, 75);
    assignColumn(wikiNodes, 435, 42, 42);
    assignColumn(slideNodes, 760, 48, 48);

    const headers = `
      <text x="110" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#1d4ed8">Layer 1: Raw 來源 (${rawNodes.length})</text>
      <text x="435" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#0f766e">Layer 2: 編譯 Wiki (${wikiNodes.length})</text>
      <text x="760" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#b45309">教學簡報投影片 (${slideNodes.length})</text>
    `;

    const edgeSvg = edges
      .map((e) => {
        const a = pos[e.from];
        const b = pos[e.to];
        if (!a || !b) return "";
        const stroke =
          e.type === "ingest"
            ? "#93c5fd"
            : e.type === "slide_ref"
            ? "#fcd34d"
            : "#cbd5e1";
        if (e.from && e.to && a.x === b.x) {
          const curveX = a.x - 48;
          return `<path class="kg-edge" data-from="${esc(e.from)}" data-to="${esc(e.to)}" d="M ${a.x} ${a.y} Q ${curveX} ${(a.y + b.y) / 2} ${b.x} ${b.y}" fill="none" stroke="${stroke}" stroke-width="1.2" opacity="0.55"/>`;
        }
        const midX = (a.x + b.x) / 2;
        return `<path class="kg-edge" data-from="${esc(e.from)}" data-to="${esc(e.to)}" d="M ${a.x} ${a.y} C ${midX} ${a.y}, ${midX} ${b.y}, ${b.x} ${b.y}" fill="none" stroke="${stroke}" stroke-width="1.35" opacity="0.65"/>`;
      })
      .join("");

    const nodeSvg = nodes
      .map((n) => {
        const p = pos[n.id];
        if (!p) return "";
        const fill =
          n.layer === "raw" ? "#dbeafe" : n.layer === "wiki" ? "#ccfbf1" : "#fef3c7";
        const stroke =
          n.layer === "raw" ? "#1d4ed8" : n.layer === "wiki" ? "#0f766e" : "#b45309";
        const maxLen = n.layer === "slide" ? 14 : 18;
        const shortLabel = n.label.length > maxLen ? n.label.slice(0, maxLen) + "…" : n.label;
        const anchor = n.layer === "raw" ? "end" : n.layer === "slide" ? "start" : "start";
        const tx = n.layer === "raw" ? p.x - 12 : p.x + 12;
        return `
          <g class="kg-node" data-node-id="${esc(n.id)}" data-layer="${esc(n.layer)}" style="cursor:pointer;">
            <circle cx="${p.x}" cy="${p.y}" r="7.5" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
            <text x="${tx}" y="${p.y + 4}" text-anchor="${anchor}" font-size="11" font-weight="600" fill="#14213d">${esc(shortLabel)}</text>
            <title>${esc(n.label)} — ${esc(n.full_title || "")}</title>
          </g>
        `;
      })
      .join("");

    elGraphSvg.innerHTML = headers + edgeSvg + nodeSvg;
  }

  document.addEventListener("click", (ev) => {
    const navBtn = ev.target.closest("[data-select-doc]");
    if (navBtn) {
      const id = navBtn.dataset.selectDoc;
      history.replaceState(null, "", `#${id}`);
      renderDoc(id);
      return;
    }

    const linkEl = ev.target.closest("a.wikilink, a.src-badge");
    if (linkEl && linkEl.dataset.docId) {
      ev.preventDefault();
      const id = linkEl.dataset.docId;
      history.replaceState(null, "", `#${id}`);
      renderDoc(id);
      return;
    }

    const kgNode = ev.target.closest(".kg-node");
    if (kgNode) {
      const id = kgNode.dataset.nodeId;
      const layer = kgNode.dataset.layer;
      if (layer === "slide") {
        window.location.href = `./slides.html#${encodeURIComponent(id)}`;
      } else {
        history.replaceState(null, "", `#${id}`);
        renderDoc(id);
      }
    }
  });

  elGraphSvg.addEventListener("mouseover", (ev) => {
    const kgNode = ev.target.closest(".kg-node");
    if (!kgNode) return;
    const id = kgNode.dataset.nodeId;
    elGraphSvg.querySelectorAll(".kg-edge").forEach((edge) => {
      const connected = edge.dataset.from === id || edge.dataset.to === id;
      edge.setAttribute("opacity", connected ? "1" : "0.12");
      edge.setAttribute("stroke-width", connected ? "2.4" : "1");
    });
  });

  elGraphSvg.addEventListener("mouseout", () => {
    elGraphSvg.querySelectorAll(".kg-edge").forEach((edge) => {
      edge.setAttribute("opacity", "0.65");
      edge.setAttribute("stroke-width", "1.35");
    });
  });

  elSearch.addEventListener("input", () => renderSidebar(elSearch.value));

  document.getElementById("btn-toggle-graph").addEventListener("click", () => {
    if (showGraph) renderDoc(activeDocId);
    else renderGraph();
  });

  document.getElementById("btn-back-article").addEventListener("click", () => {
    renderDoc(activeDocId);
  });

  function initFromHash() {
    const h = decodeURIComponent((location.hash || "").replace(/^#/, ""));
    if (h === "graph") {
      renderGraph();
      return;
    }
    if (h && docs[h]) {
      renderDoc(h);
      return;
    }
    renderDoc(activeDocId);
  }

  window.addEventListener("hashchange", initFromHash);
  initFromHash();
})();
