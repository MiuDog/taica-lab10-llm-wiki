---
id: attention-budget-and-context-rot
title: 注意力預算與上下文腐化（Context Rot）
category: foundations
summary: 解釋為何 Token 越多注意力越被攤薄，遠在滿額前模型推論準確率就開始衰退。
sources: [SRC-01, SRC-02, SRC-05]
tags: [Attention Budget, Context Rot, Transformer, 訊噪比]
updated: 2026-11-23
---

# 注意力預算與上下文腐化（Context Rot）

## 白話一句話
**AI 的注意力就像一筆固定金額的「預算」（Attention Budget）；書桌上的字數越多，每個字分到的專注力就越少，久了就會產生「上下文腐化（Context Rot）」——明明還沒塞滿上限，AI 卻開始健忘與胡言亂語。**

## 核心概念
許多使用者常疑惑：「模型規格表不是寫支援 128K 或 1M Token 嗎？為什麼我貼了 50 頁資料進去，它就開始漏掉規則或抓錯重點？」

### 1. 注意力預算的數學限制（Attention Budget）
在 Transformer 架構下，視窗裡的每個 Token 都必須和視窗中其他所有 Token 兩兩計算注意力關聯（$n^2$ 級的配對消耗）[SRC-05]。因此，把更多文字丟進視窗，就等於把一筆有限的「**注意力預算**」硬生生攤薄到更多無關字詞上 [SRC-05]。

### 2. 什麼是 Context Rot（上下文腐化）？
**Context Rot** 指的是：**遠在到達模型技術上限之前，隨著脈絡變長、雜訊累積，模型精準召回細節與維持高品質推理的能力就持續下滑的現象** [SRC-02][SRC-05]。
- 實驗證實，當大量無關的干擾文件塞入上下文時，模型的回答表現甚至會低於「完全不提供參考資料（Closed-book）」的表現 [SRC-01]。
- 就算模型通過單純的「大海撈針（Needle-in-a-Haystack）」測試，在需要同時整合多條規則的複雜推理任務上，長上下文依然容易出現漏看與幻覺 [SRC-02][SRC-05]。

### 3. 設計黃金準則
Anthropic 歸納 Context Engineering 的目標不是把視窗塞好塞滿，而是追求：**「能最大化預期任務成果的最小高訊號 Token 集合（Smallest possible set of high-signal tokens）」** [SRC-05]。

## 與其他概念的連結
- 注意力不平均最經典的實驗證據，就是 [[lost-in-the-middle]]。
- 腐化進一步惡化後會表現為哪四種故障？請看 [[context-failure-modes]]。
- 減少雜訊、維持高訊號的核心解法見 [[strategy-select-retrieval]] 與 [[strategy-compress-compaction]]。

## 來源依據
- [SRC-01] Nelson F. Liu et al., *Lost in the Middle: How Language Models Use Long Contexts* (TACL / arXiv:2307.03172)
- [SRC-02] Drew Breunig, *How Long Contexts Fail & How to Fix Your Context* (2025-06)
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
