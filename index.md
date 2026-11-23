# LLM Wiki Master Index（知識庫總目錄）

> 主題：**Context Engineering（上下文工程）**  
> 架構：依 `SCHEMA.md` 維護之三層知識庫（6 篇 `raw/` 唯讀來源 → 16 篇 `wiki/` 概念頁）。  
> 用途：查詢或產出教學簡報前，AI 先讀取本目錄定位關鍵頁面（Just-in-Time Select），節省注意力預算。

---

## 1. Overview（全覽地圖）
- [[overview-context-engineering]] — 從 Prompt Engineering 進化到 Context Engineering 的核心定義、問題成因與四大策略全景。

## 2. Foundations（基礎心智與退化原理）
- [[cpu-ram-mental-model]] — 用「LLM 是 CPU、Context Window 是 RAM / 書桌」解釋為何需要像作業系統一樣管理上下文。
- [[prompt-vs-context-engineering]] — 從「單次寫好一句問法」進化到「動態策展整個多輪推論所需的 Token 集合」。
- [[attention-budget-and-context-rot]] — 解釋為何 Token 越多注意力越被攤薄，遠在滿額前模型推論準確率就開始衰退。
- [[lost-in-the-middle]] — Stanford 與 UC Berkeley 實證發現模型最容易遺忘放在長上下文中段的關鍵資訊。

## 3. Failures（長上下文失效模式）
- [[context-failure-modes]] — Drew Breunig 歸納的 Poisoning（投毒）、Distraction（分心）、Confusion（混亂）與 Clash（衝突）及對策。

## 4. Strategies（WSCI 四大工程策略）
- [[four-strategies-wsci]] — Lance Martin 整理的 Write、Select、Compress、Isolate 四大上下文工程操作支柱。
- [[strategy-write-offload]] — 將龐大工具結果與長程狀態寫到 Context 之外的檔案或 State，只在主視窗保留指標。
- [[strategy-select-retrieval]] — 透過 Just-in-Time 檢索與 Tool Loadouts，僅將當下步驟需要的知識與工具放進視窗。
- [[strategy-compress-compaction]] — 在對話逼近容量或雜訊過高時，將歷史軌跡高保真濃縮並開啟乾淨視窗，對抗 Context Rot。
- [[strategy-isolate-subagents]] — 利用子代理人與隔離沙盒吸收數萬 Token 的探索雜訊，只回傳 1～2 千 Token 精華結論。

## 5. Practice（提示工程與生產級實戰）
- [[right-altitude-prompting]] — Anthropic 提出的系統提示設計黃金區間：既不微觀硬編碼大量 if-else，也不流於空泛口號。
- [[production-lessons-manus]] — KV-Cache 為王、Logit Masking 工具遮罩、檔案系統外部記憶、todo.md 復誦與保留失敗軌跡。

## 6. Architecture（知識庫架構模式）
- [[llm-wiki-pattern]] — 以 raw 唯讀層、wiki 編譯層、index.md、log.md 與 schema 構成的持續累積型個人知識庫。
- [[rag-vs-llm-wiki]] — 比較「查詢時臨時拼湊碎片（RAG）」與「攝取時提前編譯連結（LLM Wiki）」在注意力品質上的差異。

## 7. Reference（初學者詞彙標準）
- [[glossary-for-beginners]] — 彙整本知識庫與教學簡報全部專有名詞的標準中文解釋、生活比喻與原始出處。
