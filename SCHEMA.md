# LLM Wiki Governance Schema (Layer 3)

本文件為「Context Engineering（上下文工程）」LLM Wiki 知識庫之治理規格（Schema），遵循 Andrej Karpathy 提出的三層式 LLM Wiki 架構設計，確保 AI 在 `Ingest`、`Query`、`Lint` 與 `Slide-Gen` 循環中保持知識一致性、可溯源性與高教學可讀性。

---

## 1. 三層目錄架構（Three-Layer Architecture）

| 層級 | 路徑 | 權限 | 職責 |
| :--- | :--- | :--- | :--- |
| **Layer 1: Raw** | `raw/` | **唯讀（Immutable）** | 存放真實原始文獻摘要、論文重點、工程部落格摘錄。LLM 僅可讀取與引用，嚴禁修改內容。 |
| **Layer 2: Wiki** | `wiki/`, `index.md`, `log.md` | **LLM 編譯維護** | 由 LLM 依規範編譯、更新與重組的互連 Markdown 知識庫、主目錄索引與追加式審計日誌。 |
| **Layer 3: Schema & Discussion** | `SCHEMA.md`, `discussion/` | **人機共同治理** | 定義討論紀錄、命名規則、YAML frontmatter 欄位與自動化檢查協議。 |

---

## 2. 頁面格式與命名規則

### 2.1 檔案命名
- `raw/` 檔案一律採用：`src-<NN>-<kebab-case-slug>.md`（例如 `src-01-lost-in-the-middle.md`）。
- `wiki/` 檔案一律採用：`<kebab-case-slug>.md`（例如 `lost-in-the-middle.md`），檔名（不含副檔名）必須與 YAML frontmatter 的 `id` 完全一致。

### 2.2 `wiki/*.md` YAML Frontmatter 必備欄位
每篇 `wiki/` 頁面開頭必須包含合法 YAML frontmatter，缺一不可：

```yaml
---
id: kebab-case-slug
title: 概念名稱（可含英文專有名詞）
category: overview | foundations | failures | strategies | practice | architecture | reference
summary: 一句話精簡摘要，同時同步至 index.md。
sources: [SRC-01, SRC-02]
tags: [關鍵字1, 關鍵字2]
updated: 2026-11-23
---
```

### 2.3 頁面標準章節結構
每篇 `wiki/*.md` 需依序包含：
1. `# {title}`
2. `## 白話一句話`（給零基礎初學者的直覺比喻或一句話定義）
3. `## 核心概念`（條理分明拆解機制、實驗數據或實戰作法，重要陳述須於句末標註來源如 `[SRC-01]`）
4. `## 與其他概念的連結`（至少包含 2 個以上的 `[[wikilink]]` 雙向關聯說明，不可成為知識孤島）
5. `## 來源依據`（明確條列 `[SRC-XX]` 來源代碼、文件標題與連結）

---

## 3. 引用與連結語法規範

1. **Wiki 內部連結（Wikilinks）**：
   - 使用標準雙括號 `[[slug]]`（對應 `wiki/<slug>.md`）。
   - 嚴禁出現沒有對應實體檔案的斷鏈（Broken Link）。
2. **原始資料引用（Source Grounding）**：
   - 使用方括號代碼 `[SRC-01]` ~ `[SRC-06]`。
   - 每個出現的 `[SRC-XX]` 必須對應到 `raw/src-XX-*.md`，且該來源代碼也必須同步列於頁面 frontmatter 的 `sources` 清單中。

---

## 4. 四大核心操作迴圈（Core Workflows）

### A. Discuss Before Generate（先討論、後生成）
1. 在寫入任何 `wiki/` 頁面之前，必須先在 `discussion/00-discuss-before-generate.md` 與學習目標對話，確立目標受眾（零基礎初學者）、7 大知識分類、來源挑選原則與教學先修依賴圖（Prerequisite DAG）。

### B. Ingest（資料攝取：`raw/` → `wiki/`）
每當新增一篇 `raw/src-XX-*.md`：
1. 徹底閱讀該原始資料，萃取出核心概念、實驗證據、類比與實作技巧。
2. 新建或更新相關的 `wiki/*.md` 概念頁，補充行內 `[SRC-XX]` 與 `[[wikilink]]`。
3. 同步更新 `index.md` 對應分類下的條目與單行摘要。
4. 在 `log.md` 底部追加一筆 `## [YYYY-MM-DD] ingest | [SRC-XX] ...` 紀錄。

### C. Lint（知識庫健檢：`Gate 1: WikiLintGate`）
定期與每次變動後執行 `python pipeline/wiki_lint.py` 驗證：
- `raw/` 是否達 5 篇以上且具 `discussion/` 紀錄。
- 全數 `wiki/*.md` frontmatter 欄位是否完整且 `id == filename`。
- 全庫 `[[wikilinks]]` 零斷鏈、零孤島頁（至少被一篇其他頁面或 `index.md` 雙向連通，且入度大於 0）。
- `index.md` 與 `wiki/*.md` 100% 雙向同步。
- `[SRC-XX]` 來源引用完全真實且無幻覺代碼。

### D. Slide-Gen（教學簡報生成：`Gate 2 OutlineGate` → `Gate 3 SlideGate` → `Gate 4 BrowserGate`）
從 Wiki 產出教學 HTML 簡報時，**嚴禁直接自由發揮**，必須經過：
1. **前置大綱檢查（`Gate 2: OutlineGate`）**：鎖定投影片頁數、先修概念順序（DAG）、單頁字數上限與 Wiki/Source 覆蓋率。
2. **逐頁溯源與教學密度檢查（`Gate 3: SlideGate`）**：確認每頁 `wiki_refs` 與 `source_refs` 一致無 Citation Drift、核心術語 `grounded_terms` 確實存在於 Wiki、單頁字數與要點數不超過初學者負荷、術語不可早於其定義頁出現。
3. **實機渲染與互動檢查（`Gate 4: BrowserGate`）**：於 `1280×720` 與 `390×844` 實際啟動瀏覽器檢查零控制台錯誤、零舞台溢出、互動模擬器與溯源抽屜運作正常。
