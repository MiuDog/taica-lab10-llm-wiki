---
id: strategy-select-retrieval
title: 策略二：Select（精準挑選與即時檢索）
category: strategies
summary: 透過 Just-in-Time 檢索與 Tool Loadouts，僅將當下步驟需要的知識與工具放進視窗。
sources: [SRC-02, SRC-03, SRC-04, SRC-05, SRC-06]
tags: [Select, Just-in-Time, Tool Loadouts, index.md]
updated: 2026-11-23
---

# 策略二：Select（精準挑選與即時檢索）

## 白話一句話
**走進圖書館找資料時，先看「目錄卡」（Select）挑出真正要看的那兩頁擺上書桌，而不是把整個書架扛回座位。**

## 核心概念
如果說 `Write` 是把資料存出去，**`Select` 就是決定「下一步推論當下，究竟該把哪幾份記憶、文件與工具放進書桌」** [SRC-03]。做好 Select 能直接防止 **Context Distraction（分心）** 與 **Context Confusion（混亂）** [SRC-02]。

### 1. Just-in-Time Context Retrieval（即時按需檢索）
Anthropic 建議不要一開始就把大量未篩選的背景文件全塞入 Prompt，而是只給輕量的指標（路徑、查詢指令、索引），讓 Agent 在需要時才用工具主動讀取特定內容 [SRC-05]。
- 這正與 Andrej Karpathy 的 **LLM Wiki `index.md` 設計**不謀而合：查詢時只需先讀取極輕量的目錄 `index.md`，再透過雙向連結（`[[wikilink]]`）精準開啟 2～3 篇最相關的頁面，既省 Token 又維持高訊噪比 [SRC-06]。

### 2. Tool Loadouts（工具精選）與動態挑選
Drew Breunig 指出當工具定義過多時會引起 **Context Confusion** [SRC-02]。解決方法是在每個工作流階段只選擇該階段需要的少數工具（Tool Loadouts）[SRC-02][SRC-03]；若系統極度重視快取命中率，則改採 Manus 的 **Logit Masking** 做法（見專頁）[SRC-04]。

## 與其他概念的連結
- Select 解決的核心痛點詳見 [[context-failure-modes]] 與 [[attention-budget-and-context-rot]]。
- `index.md` 如何讓 Select 變得像人類看書一樣自然？請見 [[llm-wiki-pattern]] 與 [[rag-vs-llm-wiki]]。
- 不想刪減工具而破壞 KV-Cache 的進階替代方案，見 [[production-lessons-manus]]。

## 來源依據
- [SRC-02] Drew Breunig, *How Long Contexts Fail & How to Fix Your Context* (2025-06)
- [SRC-03] Lance Martin / LangChain, *Context Engineering for Agents* (2025-07)
- [SRC-04] Yichao "Peak" Ji / Manus, *Context Engineering for AI Agents: Lessons from Building Manus* (2025-07)
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
- [SRC-06] Andrej Karpathy, *LLM Wiki — Idea File* (2026-04)
