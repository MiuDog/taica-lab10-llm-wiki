---
id: strategy-write-offload
title: 策略一：Write（外部筆記與檔案卸載）
category: strategies
summary: 將龐大工具結果與長程狀態寫到 Context 之外的檔案或 State，只在主視窗保留指標。
sources: [SRC-03, SRC-04, SRC-05]
tags: [Write, Offloading, Structured Note-Taking, 外部記憶]
updated: 2026-11-23
---

# 策略一：Write（外部筆記與檔案卸載）

## 白話一句話
**不要把整本兩萬字的工具報告直接攤在工作桌上，而是把它存進電腦檔案夾（Write），桌上只貼一張寫著「報告位置與三行結論」的便利貼。**

## 核心概念
在多步驟 AI Agent 工作流中，爬蟲、資料庫查詢或程式碼搜尋工具動輒回傳上萬字元 [SRC-04]。如果每次工具執行結果都硬留在對話歷史裡，Context Window 很快就會陷入 **Context Rot** [SRC-03][SRC-05]。

**Write 策略**包含兩種核心實作方式：

1. **工具輸出卸載（Filesystem as Context）**：
   將龐大的原始輸出或中繼產物寫入外部檔案系統或工作流 State 欄位，僅在主上下文保留「檔案路徑 + 簡短摘要（Pointer）」 [SRC-03][SRC-04]。這是一種**可逆（Reversible）**的減量——模型真的需要查某一行的細節時，再透過讀檔工具拿回來即可 [SRC-04]。
2. **結構化筆記（Structured Note-Taking）**：
   Anthropic 與 Manus 都強調讓 Agent 主動在外部維護結構化筆記（例如 `NOTES.md` 或 `todo.md`），把專案架構決策、尚未解決的錯誤、待辦進度記錄在視窗之外的持久文件中 [SRC-04][SRC-05]。
   - 好處是即使進行上百輪操作甚至中間重開一個乾淨視窗，Agent 依然能藉由重讀筆記快速接續工作 [SRC-05]。

## 與其他概念的連結
- Write 負責把資料寫出去，之後要怎麼精準拿回來？請看 [[strategy-select-retrieval]]。
- Manus 如何巧妙用 `todo.md` 同時實現 Write 與對抗 [[lost-in-the-middle]]？詳見 [[production-lessons-manus]]。
- 本專案先寫下 `raw/` 與 `wiki/` 檔案其實就是人類與 LLM 共用的高級 Write 模式，詳見 [[llm-wiki-pattern]]。

## 來源依據
- [SRC-03] Lance Martin / LangChain, *Context Engineering for Agents* (2025-07)
- [SRC-04] Yichao "Peak" Ji / Manus, *Context Engineering for AI Agents: Lessons from Building Manus* (2025-07)
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
