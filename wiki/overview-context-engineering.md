---
id: overview-context-engineering
title: Context Engineering 全覽地圖
category: overview
summary: 從 Prompt Engineering 進化到 Context Engineering 的核心定義、問題成因與四大策略全景。
sources: [SRC-01, SRC-02, SRC-03, SRC-04, SRC-05, SRC-06]
tags: [總覽, Context Engineering, AI Agent, 心智模型]
updated: 2026-11-23
---

# Context Engineering 全覽地圖

## 白話一句話
**Context Engineering（上下文工程）就是幫 AI 這顆聰明的大腦，在每次思考前把「書桌」整理乾淨——只留下剛剛好的重點資料，不讓雜物把注意力淹沒。**

## 核心概念
過去大家習慣學習「Prompt Engineering（提示詞工程）」，專注於如何寫出一句漂亮的提問；但當 AI 開始扮演能自己查資料、呼叫工具、多步驟執行任務的 **AI Agent（代理人）** 時，真正的挑戰已經從「怎麼問一句話」變成「**如何在每次推論當下，精準策展整個輸入視窗裡的所有資訊**」[SRC-03][SRC-05]。

這門工程之所以必要，背後有兩個殘酷現實：
1. **注意力是稀缺預算（Attention Budget）**：AI 的上下文視窗就像有限的 **書桌 / RAM**，塞入越多無關歷史與文件，模型能分配給關鍵線索的注意力就越被稀釋，進而引發 **Context Rot（上下文腐化）** 與 **Lost in the Middle（中間迷失）** [SRC-01][SRC-05]。
2. **長上下文會以四種方式失靈**：一旦缺乏治理，上下文會發生 **Poisoning（投毒）**、**Distraction（分心）**、**Confusion（混亂）** 與 **Clash（衝突）** 四大故障 [SRC-02]。

為了解決這些問題，業界歸納出 **WSCI 四大工程策略**——**Write（寫出）**、**Select（挑選）**、**Compress（壓縮）** 與 **Isolate（隔離）** [SRC-03][SRC-05]，並在生產環境（如 Manus）與現代知識系統（如 Karpathy 的 **LLM Wiki**）中得到具體驗證 [SRC-04][SRC-06]。

| 學習層次 | 核心問題 | 本 Wiki 對應頁面 |
| :--- | :--- | :--- |
| 1. 基礎模型 | AI 的視窗像什麼？和寫 Prompt 差在哪？ | [[cpu-ram-mental-model]]、[[prompt-vs-context-engineering]] |
| 2. 退化與故障 | 為什麼資料給越多反而越笨？ | [[attention-budget-and-context-rot]]、[[lost-in-the-middle]]、[[context-failure-modes]] |
| 3. 四大治本策略 | 工程上怎麼管好上下文？ | [[four-strategies-wsci]] |
| 4. 實戰與知識架構 | 真實產品與知識庫如何落地？ | [[right-altitude-prompting]]、[[production-lessons-manus]]、[[llm-wiki-pattern]] |

## 與其他概念的連結
- 建議初學者從生活比喻頁面 [[cpu-ram-mental-model]] 與名詞對照表 [[glossary-for-beginners]] 開始閱讀。
- 想理解為何 Context Engineering 取代單純寫好 Prompt，請見 [[prompt-vs-context-engineering]]。
- 想看完整解決手段，請接續 [[four-strategies-wsci]] 與 [[rag-vs-llm-wiki]]。

## 來源依據
- [SRC-01] Nelson F. Liu et al., *Lost in the Middle: How Language Models Use Long Contexts* (TACL / arXiv:2307.03172)
- [SRC-02] Drew Breunig, *How Long Contexts Fail & How to Fix Your Context* (2025-06)
- [SRC-03] Lance Martin / LangChain, *Context Engineering for Agents* (2025-07)
- [SRC-04] Yichao "Peak" Ji / Manus, *Context Engineering for AI Agents: Lessons from Building Manus* (2025-07)
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
- [SRC-06] Andrej Karpathy, *LLM Wiki — Idea File* (2026-04)
