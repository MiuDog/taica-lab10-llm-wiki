# 先討論、後生成：LLM Wiki 建庫設計討論紀錄

> 紀錄日期：2026-11-23  
> 階段：Step 1 — Discuss Before Generate（討論定案後才執行 Ingest 與編譯）

---

## 1. 為什麼我們不直接丟給 AI 寫簡報？

在做這份作業時，最容易踩的坑就是把 5 篇網路文章塞進一個長對話，叫模型「幫我做一份 15 頁的教學簡報」。這樣做通常會有三個後果：
1. **概念順序混亂**：第 2 頁就突然冒出 `KV-Cache` 或 `Compaction`，沒學過的人完全看不懂。
2. **來源張冠李戴（Citation Drift）**：AI 把 Anthropic 講的概念貼上 Manus 的出處，事後無法核對。
3. **一次性消耗品**：簡報生完後，知識沒有沉澱下來，下次想改動或加新文章時只能重來。

因此我們遵循 **Andrej Karpathy 的 LLM Wiki 模式**，在生成任何知識頁與簡報前，先完成以下五個維度的設計討論。

---

## 2. 討論定案（Design Decisions）

### Q1：主題與目標受眾是誰？
- **主題**：**Context Engineering（上下文工程）** — 2025～2026 年 AI Agent 領域從「寫好一句 Prompt」演進到「精準設計整個注意力視窗」的核心工程學科。
- **目標受眾**：**會用 ChatGPT 等 AI 聊天機器人、但對 AI Agent 架構與 Context Engineering 零基礎的初學者**。
- **教學目標**：看完簡報後，學員能用生活比喻（CPU 與書桌、U 型記憶盲區）理解為什麼塞滿文件 AI 反而變笨，並能看懂 Write / Select / Compress / Isolate 四大治本策略，甚至理解本專案自己用的 LLM Wiki 為何就是 Context Engineering 的最佳實踐。

### Q2：原始資料（Layer 1 `raw/`）該如何挑選才夠全面？
決定收集 **6 篇真實且具代表性的一手文獻**（高於作業「至少 5 篇」要求），涵蓋學術實驗、失效分析、架構框架、生產實戰與 Wiki 模式本身：

| 來源代碼 | 作者 / 機構 | 日期 | 文獻標題 | 核心貢獻 |
| :--- | :--- | :--- | :--- | :--- |
| `SRC-01` | Nelson F. Liu et al. (Stanford / UC Berkeley) | 2024 (TACL / arXiv) | *Lost in the Middle: How Language Models Use Long Contexts* | 實證揭示 U 型注意力退化曲線與「塞太多反而輸給沒給資料」現象 |
| `SRC-02` | Drew Breunig | 2025-06-22 / 26 | *How Long Contexts Fail* & *How to Fix Your Context* | 歸納長上下文四大失效模式（Poisoning / Distraction / Confusion / Clash） |
| `SRC-03` | Lance Martin (LangChain) | 2025-07-02 | *Context Engineering for Agents* | 提出 Write / Select / Compress / Isolate（WSCI）四大策略分類學 |
| `SRC-04` | Yichao "Peak" Ji (Manus) | 2025-07-18 | *Context Engineering for AI Agents: Lessons from Building Manus* | 揭露生產環境實戰：KV-Cache、Logit Masking、`todo.md` 復誦與保留錯誤 |
| `SRC-05` | Anthropic Engineering | 2025-09-29 | *Effective Context Engineering for AI Agents* | 提出 Context Rot、Attention Budget、Right Altitude 與 Sub-Agent 濃縮 |
| `SRC-06` | Andrej Karpathy | 2026-04-04 | *LLM Wiki — Idea File* | 提出以 `raw/` + `wiki/` + `index.md` + `log.md` + `schema` 取代靜態切塊 RAG |

### Q3：Layer 2 `wiki/` 要如何分層分類，才能兼顧「檢索精準」與「教學展開」？
討論後決定不照文章一對一寫 6 篇摘要，而是打散重組為 **7 大分類、16 篇原子化概念頁（Concept Pages）**：
1. `overview`（1 篇）：`overview-context-engineering`（全覽地圖）
2. `foundations`（4 篇）：`cpu-ram-mental-model`、`prompt-vs-context-engineering`、`attention-budget-and-context-rot`、`lost-in-the-middle`
3. `failures`（1 篇）：`context-failure-modes`（四大失效症狀）
4. `strategies`（5 篇）：`four-strategies-wsci` 總覽 + `write` / `select` / `compress` / `isolate` 各 1 篇專頁
5. `practice`（2 篇）：`right-altitude-prompting`、`production-lessons-manus`
6. `architecture`（2 篇）：`llm-wiki-pattern`、`rag-vs-llm-wiki`
7. `reference`（1 篇）：`glossary-for-beginners`（初學者詞彙與白話對照表）

### Q4：簡報教學順序（Prerequisite DAG）如何規劃？
為了防止初學者一開頭就被專有名詞轟炸，我們在討論階段便明確定義 5 個教學單元與先修依賴關係（後續會直接寫入 `Gate 2: OutlineGate` 自動把關）：
- **Unit 1 破題與心智模型**：必須先講「LLM=CPU, Context=書桌/RAM」與「Prompt vs Context」，建立基礎比喻。
- **Unit 2 問題診斷**：有了書桌與注意力預算觀念後，再講「Lost in the Middle (U型曲線)」與「四大失效模式」。
- **Unit 3 四大解決策略（WSCI）**：先給 Write / Select / Compress / Isolate 全景圖，再拆解工具運作方式。
- **Unit 4 工程實戰與 LLM Wiki 應用**：介紹 Right Altitude 提示設計、Manus 實戰課，並回扣「本作業本身的 LLM Wiki 如何實踐 Context Engineering」。
- **Unit 5 驗收與知識地圖**：互動小測驗 + 完整 14 頁對 Wiki 與 Raw 的可溯源矩陣 + 行動清單。

### Q5：如何避免簡報內容脫離 Wiki 產生幻覺？
討論決定建立「可程式化檢查管線（Verification Graph）」：
- 每張投影片在資料結構上必須綁定 `wiki_refs`、`source_refs` 與 `grounded_terms`。
- `Gate 1 (WikiLint)` 先保護知識庫本身無斷鏈、無孤島、索引同步。
- `Gate 2 (OutlineGate)` 在生成內文前先鎖住順序與字數預算。
- `Gate 3 (SlideGate)` 逐頁查核來源一致性與術語先修順序。
- `Gate 4 (BrowserGate)` 啟動真實瀏覽器檢查 `1280×720` 舞台零溢出與互動元件正確性。

---

## 3. 討論結論簽核
- [x] 受眾與教學目標確定（零基礎初學者，生活比喻優先於專有名詞）
- [x] 6 篇真實 `raw/` 來源選定並配發 `[SRC-01]` ~ `[SRC-06]` 編號
- [x] 16 篇 `wiki/` 概念切分與 `SCHEMA.md` 格式定案
- [x] 準備進入下一階段：**依序攝取 `SRC-01` ~ `SRC-06`（Ingest Loop）並即時執行 `WikiLint`**
