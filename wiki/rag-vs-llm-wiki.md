---
id: rag-vs-llm-wiki
title: 傳統 RAG vs LLM Wiki
category: architecture
summary: 比較「查詢時臨時拼湊碎片（RAG）」與「攝取時提前編譯連結（LLM Wiki）」在注意力品質上的差異。
sources: [SRC-01, SRC-05, SRC-06]
tags: [RAG, LLM Wiki, 檢索架構, 知識編譯]
updated: 2026-11-23
---

# 傳統 RAG vs LLM Wiki

## 白話一句話
**傳統 RAG 像是每次考試前才急忙把課本撕成幾百張碎片亂抓一把上桌；LLM Wiki 則是平常讀完一章就整理好一份互相關聯的重點筆記，考試時只需翻開目錄找對的那兩頁。**

## 核心概念
雖然兩者都是為了解決「不能把所有資料全部硬塞進 Context Window」的問題，但它們把運算與整理工作放在完全不同的時間點 [SRC-06]：

| 比較項目 | 傳統切塊 RAG（Vector Chunk RAG） | LLM Wiki（編譯型知識庫） |
| :--- | :--- | :--- |
| **知識加工時機** | **查詢時（Query-time）**才臨時拼湊碎片 [SRC-06] | **攝取時（Ingest-time）**提前消化、整合並建立雙向連結 [SRC-06] |
| **放入視窗的型態** | 固定長度切塊（容易斷章取義、重複且夾雜雜訊）[SRC-01] | 語意完整、附白話定義與來源標註的 Markdown 概念頁 [SRC-06] |
| **注意力負擔** | 若一次塞入 Top-20 碎片，極易觸發 **Lost in the Middle** 與干擾退化 [SRC-01] | 先讀 `index.md` 鎖定 2～3 頁（Just-in-Time），維持最小高訊號集合 [SRC-05][SRC-06] |
| **知識會不會越用越強** | 不會，每次提問都從零開始重算 | 會，高價值問答與教學整理可寫回 `wiki/` 產生複利 [SRC-06] |
| **維護一致性** | 難以發現前後兩份文件互相矛盾 | 透過定期 **Lint** 迴圈主動偵測斷鏈與衝突 [SRC-06] |

### 為什麼本作業適合用 LLM Wiki 做教學簡報？
製作教學簡報時，初學者需要的是**有先後順序的概念地圖**，而不是隨機抓取的論文段落 [SRC-06]。當我們先把 6 篇來源編譯成 16 篇彼此連結的 Wiki 頁面，AI 產出投影片時就能順著 `index.md` 與雙向連結（`[[wikilink]]`）嚴謹取證，讓簡報每一頁都能精準溯源回原始文章，同時大幅減少 **Context Distraction** 與幻覺風險 [SRC-05][SRC-06]。

## 與其他概念的連結
- 關於傳統切塊大量塞入 Prompt 的位置盲區實驗，見 [[lost-in-the-middle]]。
- LLM Wiki 的具體檔案結構規範，請見 [[llm-wiki-pattern]] 與 [[strategy-select-retrieval]]。
- 隔離與預先編譯如何減少錯漏？對照 [[strategy-isolate-subagents]]。

## 來源依據
- [SRC-01] Nelson F. Liu et al., *Lost in the Middle: How Language Models Use Long Contexts* (TACL / arXiv:2307.03172)
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
- [SRC-06] Andrej Karpathy, *LLM Wiki — Idea File* (2026-04)
