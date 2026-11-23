---
id: context-failure-modes
title: 長上下文的四大失效模式
category: failures
summary: Drew Breunig 歸納的 Poisoning（投毒）、Distraction（分心）、Confusion（混亂）與 Clash（衝突）及對策。
sources: [SRC-02, SRC-05]
tags: [Context Poisoning, Context Distraction, Context Confusion, Context Clash, Tool Loadouts]
updated: 2026-11-23
---

# 長上下文的四大失效模式

## 白話一句話
**上下文出包不是只有「字數爆掉」一種死法，而是有四種明確病症：中毒（假消息當真）、分心（歷史太吵）、混亂（工具太多選錯）、打架（前後規定矛盾）。**

## 核心概念
技術專家 Drew Breunig 在 *How Long Contexts Fail* 與後續修復指南中指出，盲目塞滿上下文視窗會引發以下四種典型故障 [SRC-02]：

| 失效模式 | 發生原因 | 典型症狀 | 工程解法 |
| :--- | :--- | :--- | :--- |
| **1. Context Poisoning（投毒）** | 幻覺或錯誤工具回傳寫進工作摘要 [SRC-02] | 模型把錯誤當成既定事實，在不可能的目標上不斷打轉 [SRC-02] | **Context Quarantine（隔離）** 與檢查驗證門檻 [SRC-02] |
| **2. Context Distraction（分心）** | 歷史訊息過度冗長，雜訊淹沒規則 [SRC-02] | 忘記原始指令，機械式模仿對話紀錄中的舊動作 [SRC-02] | **Select / Pruning（挑選與修剪）**、壓縮歷史 [SRC-02][SRC-05] |
| **3. Context Confusion（混亂）** | 塞入過多無關文件或數十個工具定義（Tool Schemas）[SRC-02] | 不需要用工具時硬要呼叫、或叫錯相似功能的工具 [SRC-02] | **Tool Loadouts（動態工具載入）** 與遮罩 [SRC-02] |
| **4. Context Clash（衝突）** | 新資料、新指令與先前的系統提示或舊文件互相矛盾 [SRC-02] | 模型被迫靜默猜測該聽誰的，行為飄忽不定 [SRC-02] | **Quarantine / Pruning** 清除過時矛盾內容 [SRC-02] |

### 初學者最容易踩的坑
許多人在接上多個 MCP 伺服器或塞入大量教學 PDF 時，一口氣給 AI 掛載 40 個工具與 5 份不同版本的規範，結果反而觸發 **Confusion（選錯工具）** 與 **Clash（新舊版本規定打架）** [SRC-02]。解決之道不是換更大的模型，而是先把無關工具與過時衝突資訊排除在主視窗外 [SRC-02][SRC-05]。

## 與其他概念的連結
- 這四種病症背後共同的體質原因，見 [[attention-budget-and-context-rot]]。
- 如何透過四大策略系統性治本？請見 [[four-strategies-wsci]] 與 [[strategy-isolate-subagents]]。
- 工具數量控制除了刪減（Tool Loadouts），在重視快取的系統怎麼做？見 [[production-lessons-manus]]。

## 來源依據
- [SRC-02] Drew Breunig, *How Long Contexts Fail & How to Fix Your Context* (2025-06)
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
