---
id: llm-wiki-pattern
title: LLM Wiki 模式（Karpathy 三層架構）
category: architecture
summary: 以 raw 唯讀層、wiki 編譯層、index.md、log.md 與 schema 構成的持續累積型個人知識庫。
sources: [SRC-06]
tags: [LLM Wiki, Karpathy, index.md, log.md, Schema]
updated: 2026-11-23
---

# LLM Wiki 模式（Karpathy 三層架構）

## 白話一句話
**與其每次問 AI 問題才把幾十份 PDF 亂切塊塞進視窗，不如讓 AI 像「維基百科編輯」一樣，平常收到文章就提前消化整理成互相連結的 Markdown 知識庫。**

## 核心概念
Andrej Karpathy 在 2026 年 4 月分享的 **LLM Wiki** 設計模式，本質上正是把 Context Engineering 的 **Write、Select 與 Schema 治理**應用在「知識庫建構」上的代表範例 [SRC-06]：

### 三層檔案結構
1. **`raw/`（第一層：唯讀原始資料）**：
   - 存放蒐集來的原文摘要、論文、網頁摘錄。LLM 絕對不能擅自塗改這裡的文字，確保真相來源（Source of Truth）不會在轉寫過程中失真 [SRC-06]。
2. **`wiki/`（第二層：LLM 編譯維護層）**：
   - 存放由 LLM 負責建立、重組與交叉更新的 Markdown 頁面（概念頁、實體頁、比較頁），頁面間以雙向連結（`[[wikilink]]`）形成知識網路 [SRC-06]。
3. **三個關鍵控制中心**：
   - **`index.md`**：總目錄與每頁一句話摘要。查詢時只先載入這份輕量目錄，大幅省下寶貴上下文 [SRC-06]。
   - **`log.md`**：追加式時間軸日誌（如 `ingest`、`query`、`lint`），完整留下誰在何時編修了哪頁的審計軌跡 [SRC-06]。
   - **Schema（如 `SCHEMA.md` / `CLAUDE.md`）**：規範資料夾結構、命名與編輯作業流的操作手冊 [SRC-06]。

### 三大持續運作迴圈
- **Ingest（攝取編譯）**：每讀入一篇 `raw/` 資料，即跨頁更新多個 `wiki/` 概念並同步 `index.md` 與 `log.md` [SRC-06]。
- **Query（按圖索驥查詢）**：先看 `index.md` 鎖定目標頁面，再深入讀取並產出帶出處的答案或簡報 [SRC-06]。
- **Lint（定期健檢）**：主動掃描斷鏈、孤島頁面、前後矛盾與引用失準，維持知識庫長期健康 [SRC-06]。

## 與其他概念的連結
- 為什麼這套架構比傳統向量切塊檢索更適合教學與深度理解？詳見 [[rag-vs-llm-wiki]]。
- `index.md` 與 `raw/` 分層背後體現的心智模型，就是 [[cpu-ram-mental-model]] 與 [[strategy-select-retrieval]]。
- 本專案本身的規範見 [[overview-context-engineering]] 與 [[glossary-for-beginners]]。

## 來源依據
- [SRC-06] Andrej Karpathy, *LLM Wiki — Idea File* (2026-04)
