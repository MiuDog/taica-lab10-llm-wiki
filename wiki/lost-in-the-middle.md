---
id: lost-in-the-middle
title: Lost in the Middle（中間迷失與 U 型曲線）
category: foundations
summary: Stanford 與 UC Berkeley 實證發現模型最容易遺忘放在長上下文中段的關鍵資訊。
sources: [SRC-01, SRC-04]
tags: [Lost in the Middle, U型曲線, Primacy Bias, Recency Bias]
updated: 2026-11-23
---

# Lost in the Middle（中間迷失與 U 型曲線）

## 白話一句話
**就像人讀長文章一樣，AI 對「最開頭」和「最結尾」的記憶最深刻，把最重要的線索塞在長文正中間，它有極高機率視而不見——這叫做「中間迷失（Lost in the Middle）」。**

## 核心概念
2024 年發表於 TACL 的經典論文 *Lost in the Middle: How Language Models Use Long Contexts*（Stanford / UC Berkeley / Samaya AI）用多文件問答與鍵值對檢索實驗，揭露了長上下文模型的真實表現規律 [SRC-01]：

### 1. 經典 U 型效能曲線（U-Shaped Curve）
當研究者把「真正包含答案的文件」分別放在長提示詞的不同位置時，準確率呈現明顯的 **U 字型** [SRC-01]：
- **開頭位置最高（Primacy Bias，首因效應）**：放在第 1 份的位置時，模型抓得最準 [SRC-01]。
- **結尾位置次高（Recency Bias，近因效應）**：放在最後 1 份的位置時，模型也記得很清楚 [SRC-01]。
- **中間位置暴跌**：一旦把關鍵答案移到長文本中段，模型準確率大幅掉下谷底 [SRC-01]。

### 2. 驚人反直覺現象：塞資料可能輸給「完全不給資料」
研究更發現，當正確文件被迫夾在大量無關干擾文件中段時，模型的答題準確率有時會**低於 Closed-book Baseline**（完全不附參考文件、只靠模型自己背下來的常識來猜）[SRC-01]。這直接證明雜訊位置不當會主動干擾推理。

### 3. 工程實務如何破解「中間迷失」？
- **把高優先資料擺兩端**：最重要的系統規則放最開頭，當下步驟必須遵守的待辦目標放在最結尾 [SRC-01][SRC-04]。
- **Manus 的 `todo.md` 復誦技巧（Recitation）**：長任務跑了幾十步後，最開頭的目標容易被歷史對話越推越遠、掉進中段盲區。Manus 讓 Agent 每走幾步就重寫一次 `todo.md` 到上下文最末端，把全局目標「復誦」回 Recency 黃金區 [SRC-04]。

## 與其他概念的連結
- 這份實驗正是理解 [[attention-budget-and-context-rot]] 的關鍵實證基石。
- `todo.md` 復誦技巧的完整生產脈絡，請見 [[production-lessons-manus]]。
- 傳統 RAG 若把 20 塊 chunk 無腦倒進中間會發生什麼事？請見 [[rag-vs-llm-wiki]]。

## 來源依據
- [SRC-01] Nelson F. Liu et al., *Lost in the Middle: How Language Models Use Long Contexts* (TACL / arXiv:2307.03172)
- [SRC-04] Yichao "Peak" Ji / Manus, *Context Engineering for AI Agents: Lessons from Building Manus* (2025-07)
