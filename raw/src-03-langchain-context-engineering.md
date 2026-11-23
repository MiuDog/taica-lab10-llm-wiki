---
source_id: SRC-03
title: "Context Engineering for Agents"
authors: Lance Martin (LangChain)
date: 2025-07-02
url: https://blog.langchain.com/context-engineering-for-agents/
immutable: true
---

# [SRC-03] Context Engineering for Agents

## 書目資訊
- **作者**：Lance Martin（LangChain）
- **發表日期**：2025-07-02
- **原文連結**：https://blog.langchain.com/context-engineering-for-agents/

## 原始文獻核心論點摘錄（Immutable Source）

### 一、核心心智模型：LLM 是 CPU，Context Window 是 RAM
借鏡 Andrej Karpathy 的經典比喻：如果說 **LLM 是中央處理器（CPU）**，那麼 **Context Window 就是電腦的記憶體（RAM）**，存放模型推論當前步驟所需的工作資料。
就像作業系統必須負責管理有限且寶貴的 RAM，**Context Engineering（上下文工程）** 就是是一門藝術與科學——在 AI Agent 執行的每一個步驟中，精準決定要把「剛剛好夠用的資訊」放進有限的 Context Window 裡。

### 二、Context Engineering 的四大策略（WSCI Framework）

Lance Martin 將業界與 LangGraph 等 Agent 系統實踐整理成四個操作象限：

1. **Write Context（寫入 / 外部持久化）**：
   - **作法**：將長期記憶、重要中間產物或龐大的工具輸出**寫到 Context Window 之外**（例如檔案系統、Scratchpad 筆記或 LangGraph State 物件），只在對話視窗內保留簡短指標（Pointer）。
   - **效益**：避免工具回傳數萬字把 RAM 瞬間塞爆，需要時再讀取。

2. **Select Context（挑選 / 動態檢索）**：
   - **作法**：僅在當下這一步需要時，動態抓取真正相關的記憶（Memories）、規則（Rules）、工具定義（Tools）或知識片段（RAG / Knowledge Search）放進視窗。
   - **效益**：維持高訊噪比（Signal-to-Noise Ratio），避免不相干背景知識造成注意力稀釋。

3. **Compress Context（壓縮 / 濃縮）**：
   - **作法**：針對必須留在 Context Window 裡的歷史軌跡或工具結果，透過 **Summarization（摘要）** 或 **Trimming / Pruning（修剪）** 縮減 Token 佔用體積。
   - **效益**：讓多回合（數十到上百步）長程 Agent 不致於因歷史雪球越滾越大而崩潰或成本暴增。

4. **Isolate Context（隔離 / 分工）**：
   - **作法**：不強迫單一 Agent 在同一個視窗包辦所有雜務，而是把任務拆解交給獨立的 **Sub-agents（子代理人）**、沙盒執行環境或狀態結構化欄位（State Schema）。
   - **效益**：每個 Sub-agent 擁有乾淨獨立的 Context Window 與專屬工具集，探索過程的試錯與大量雜訊不會污染協調者主線。
