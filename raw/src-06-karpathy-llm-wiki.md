---
source_id: SRC-06
title: "LLM Wiki — Idea File"
authors: Andrej Karpathy
date: 2026-04-04
url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
immutable: true
---

# [SRC-06] LLM Wiki — Idea File

## 書目資訊
- **作者**：Andrej Karpathy
- **發表日期**：2026-04-04
- **原文連結**：https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## 原始文獻核心論點摘錄（Immutable Source）

### 一、從傳統 RAG 切塊轉向「持續編譯的 LLM Wiki」
在傳統 RAG（檢索增強生成）模式下，知識庫只是一堆靜態原始文件切成的向量碎片；每次使用者提問時，系統才臨時撈出幾個片段讓 LLM 從零拼湊答案。知識從未被真正消化或累積起來。

**LLM Wiki** 的核心轉變在於：不再讓 LLM 每次查詢都從原始零碎文件重新出發，而是讓 LLM 扮演「知識策展人與編譯器」，在**攝取資料（Ingest）階段就提前把知識編譯（Compile）進一個結構化、彼此雙向連結的 Markdown Wiki**，並隨著新資料不斷滾動更新與修正矛盾。

### 二、三層檔案架構（Core File Layout）
1. **`raw/`（原始來源層 — 不可變）**：存放蒐集來的原始文章、論文、逐字稿等一手資料，由人類收藏，LLM 只能讀取、不可修改。
2. **`wiki/`（編譯知識層 — LLM 全權維護）**：存放概念頁、實體頁、比較頁與總覽頁，頁面之間透過 `[[wikilinks]]` 相互連結。
3. **三個關鍵控制檔案**：
   - **`index.md`（內容總目錄）**：依分類列出所有 Wiki 頁面與單行摘要。LLM 回答問題時只需先讀取輕量的 `index.md`，即可精準定位該打開哪幾頁，而不必盲目塞入大量全文。
   - **`log.md`（追加式審計日誌）**：以時間軸（如 `## [YYYY-MM-DD] ingest | Title`）記錄每次攝取、查詢與健檢事件，方便追溯演進歷程。
   - **`Schema`（`CLAUDE.md` / `AGENTS.md` / `SCHEMA.md`）**：定義整個 Wiki 的目錄規範、命名格式與操作流程。

### 三、三大核心迴圈（Core Operations）
1. **Ingest（攝取）**：讀入一篇 `raw/` 文件 → 跨越多篇相關 `wiki/` 頁面進行建立與交叉更新 → 更新 `index.md` → 追加紀錄到 `log.md`。
2. **Query（查詢）**：先看 `index.md` → 鎖定相關 `wiki/` 頁面深入閱讀 → 合成帶有出處的回答（高價值問答亦可回寫成新 Wiki 頁面，使探索成果複利累積）。
3. **Lint（健檢）**：定期掃描知識庫，檢查是否有斷裂的 `[[wikilinks]]`、孤島頁面（Orphan pages）、過時資訊或前後來源之間的矛盾，保持知識庫健康一致。
