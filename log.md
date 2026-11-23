# LLM Wiki Audit Log（追加式操作日誌）

本檔案記錄所有對知識庫與衍生簡報執行的重大操作事件（Append-Only）。

---

## [2026-11-23] discuss | 建立治理規格與先討論定案
- 依據 Karpathy LLM Wiki 三層架構完成 `SCHEMA.md`。
- 產出 `discussion/00-discuss-before-generate.md`：鎖定「零基礎初學者」受眾、7 大知識分類、6 篇真實一手來源，以及教學簡報 5 單元先修依賴關係（DAG）。

## [2026-11-23] ingest | [SRC-01] Lost in the Middle (Stanford / UC Berkeley, TACL)
- 匯入唯讀原始檔 `raw/src-01-lost-in-the-middle.md`。
- 新建概念頁：`[[lost-in-the-middle]]`。
- 交叉補充：`[[attention-budget-and-context-rot]]`、`[[rag-vs-llm-wiki]]`。
- 同步更新 `index.md`。

## [2026-11-23] ingest | [SRC-02] How Long Contexts Fail & How to Fix Your Context (Drew Breunig)
- 匯入唯讀原始檔 `raw/src-02-how-long-contexts-fail.md`。
- 新建概念頁：`[[context-failure-modes]]`。
- 交叉補充四大失效對策至 `[[attention-budget-and-context-rot]]`、`[[strategy-select-retrieval]]`、`[[strategy-isolate-subagents]]`。
- 同步更新 `index.md`。

## [2026-11-23] ingest | [SRC-03] Context Engineering for Agents (Lance Martin / LangChain)
- 匯入唯讀原始檔 `raw/src-03-langchain-context-engineering.md`。
- 新建基礎模型與四大策略頁：`[[cpu-ram-mental-model]]`、`[[four-strategies-wsci]]`、`[[strategy-write-offload]]`、`[[strategy-select-retrieval]]`、`[[strategy-compress-compaction]]`、`[[strategy-isolate-subagents]]`。
- 同步更新 `index.md`。

## [2026-11-23] ingest | [SRC-04] Lessons from Building Manus (Yichao "Peak" Ji)
- 匯入唯讀原始檔 `raw/src-04-manus-lessons.md`。
- 新建生產實戰專頁：`[[production-lessons-manus]]`。
- 將 `todo.md` 復誦與檔案卸載交叉補充至 `[[lost-in-the-middle]]` 與 `[[strategy-write-offload]]`。
- 同步更新 `index.md`。

## [2026-11-23] ingest | [SRC-05] Effective Context Engineering for AI Agents (Anthropic)
- 匯入唯讀原始檔 `raw/src-05-anthropic-effective-ce.md`。
- 新建專頁：`[[prompt-vs-context-engineering]]`、`[[attention-budget-and-context-rot]]`、`[[right-altitude-prompting]]`。
- 深化 Just-in-Time 檢索、Compaction 與 Sub-Agent 濃縮比至 `[[four-strategies-wsci]]` 系列頁面。
- 同步更新 `index.md`。

## [2026-11-23] ingest | [SRC-06] LLM Wiki — Idea File (Andrej Karpathy)
- 匯入唯讀原始檔 `raw/src-06-karpathy-llm-wiki.md`。
- 新建架構與總覽專頁：`[[llm-wiki-pattern]]`、`[[rag-vs-llm-wiki]]`、`[[overview-context-engineering]]`、`[[glossary-for-beginners]]`。
- 同步更新 `index.md`，完成 16 篇高度互連 Wiki 編譯。

## [2026-11-23] lint | 執行 Gate 1: WikiLintGate 初次全面健檢
- 執行 `python pipeline/wiki_lint.py` 發現 2 處問題：`[[wikilinks]]` 範例未加反引號誤判為斷鏈、以及 `strategy-select-retrieval.md` 漏宣告 `[SRC-04]`。
- 修正後重跑 `Gate 1: WikiLintGate` 全數通過（6 Raw、16 Wiki、83 條內部連結、0 斷鏈、0 孤島、`index.md` 100% 同步）。

## [2026-11-23] slide-gen | Run #1 (v1 初版線性管線實測)
- 未經大綱檢查直接生成 `data/slides-v1.json` 並執行 `python pipeline/run_pipeline.py --mode v1`。
- 實測抓出 6 項缺陷（`SlideGate` 5 項 + `BrowserGate` 1 項）：
  - `slide-1`、`slide-2` 過早出現尚未定義之術語（`LLM Wiki`, `Compaction`, `KV-Cache`）。
  - `slide-3` 密度高達 765 字 / 7 要點，於 `1280×720` 實機檢測發生 `body 469/413` 垂直溢出。
  - `slide-4` 發生 Citation Drift（誤標未出現在所引 Wiki 的 `[SRC-04]`）。

## [2026-11-23] refactor | 流程圖重構為 v2 前移檢查狀態圖（Shift-Left）
- 新增 `Gate 2: OutlineGate` (`pipeline/outline_gate.py`)，把先修順序 DAG、單頁字數上限與覆蓋率檢查移至生成正文之前。
- 依據 `Gate 2` 鎖定 `data/outline-v2.json`（14 頁、5 單元、100% 覆蓋 16 篇 Wiki 與 6 篇 Raw）。
- 逐頁重編 `data/slides-v2.json` 並準備執行 Run #2 全面驗證。

## [2026-11-23] slide-gen | Run #2 (v2 前移檢查狀態圖定稿驗收通過)
- 依初輪 Run #2 回報再精修 `slide-1`, `slide-5`, `slide-8`, `slide-14` 與雙欄矩陣緊湊樣式。
- 重跑 `python pipeline/run_pipeline.py --mode v2`，全數 4 道關卡皆通過（**0 issues**）：
  - `Gate 1 (WikiLintGate)`: PASS（6 Raw / 16 Wiki / 83 條 `[[wikilink]]` 0 斷鏈 0 孤島）
  - `Gate 2 (OutlineGate)`: PASS（14 頁大綱 DAG 先修順序與 100% 覆蓋率達標）
  - `Gate 3 (SlideGate)`: PASS（0 Citation Drift、術語先解釋後登場、單頁密度受控）
  - `Gate 4 (BrowserVisualGate)`: PASS（`1280×720` 全 14 頁 `body 413/413` 零溢出、互動元件與 Wiki 溯源抽屜、Knowledge Graph 與 `390×844` RWD 皆正常、0 JS Errors）

