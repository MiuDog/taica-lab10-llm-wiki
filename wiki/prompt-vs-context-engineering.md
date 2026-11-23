---
id: prompt-vs-context-engineering
title: Prompt Engineering vs Context Engineering
category: foundations
summary: 從「單次寫好一句問法」進化到「動態策展整個多輪推論所需的 Token 集合」。
sources: [SRC-03, SRC-05]
tags: [Prompt Engineering, Context Engineering, AI Agent, 演進]
updated: 2026-11-23
---

# Prompt Engineering vs Context Engineering

## 白話一句話
**Prompt Engineering 是在問「單一題目怎麼寫得清楚」；Context Engineering 是在設計「AI 連續工作 20 步時，每一步眼前看到的所有資料該怎麼動態更換」。**

## 核心概念
在早期與 AI 單輪對話（一問一答）的時代，我們只需要把系統提示與問題潤飾漂亮（**Prompt Engineering**），就能獲得不錯的回應 [SRC-05]。然而，當我們打造的不再只是聊天機器人，而是需要呼叫搜尋、讀檔、寫程式、自我修正的多回合 **AI Agent** 時，輸入視窗裡塞滿了各種動態變化的資訊 [SRC-03][SRC-05]：

| 比較維度 | Prompt Engineering（提示詞工程） | Context Engineering（上下文工程） |
| :--- | :--- | :--- |
| **關注焦點** | 單一指令的措辭、角色設定、輸出格式 | 每次推論當下整個 Token 集合的動態配置 [SRC-05] |
| **典型場景** | 單輪或少輪一問一答 | 數十至上百步的長程 AI Agent 迴圈 [SRC-03][SRC-05] |
| **包含元素** | System Prompt + 使用者提問 | 系統提示 + 工具定義 + 記憶 + 檢索片段 + 歷史訊息 + 筆記 [SRC-03][SRC-05] |
| **核心難題** | 怎麼把規則寫清楚？ | 如何維持**最小的高訊號 Token 集合**而不腐化？ [SRC-05] |

Anthropic 指出，這並非否定 Prompt Engineering，而是把它視為整體 Context 設計中的一塊拼圖 [SRC-05]。進入 Agent 時代後，工程師的關鍵任務是確保「系統能在對的時刻，提供對的資訊與工具給模型」[SRC-03][SRC-05]。

## 與其他概念的連結
- 上下文為什麼有限制？請見 [[cpu-ram-mental-model]] 與 [[attention-budget-and-context-rot]]。
- 寫系統提示本身該掌握什麼分寸？請看 [[right-altitude-prompting]]。
- 多輪任務的系統化整理方法，見 [[four-strategies-wsci]]。

## 來源依據
- [SRC-03] Lance Martin / LangChain, *Context Engineering for Agents* (2025-07)
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
