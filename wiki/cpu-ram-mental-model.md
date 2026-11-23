---
id: cpu-ram-mental-model
title: CPU 與 RAM（書桌）心智模型
category: foundations
summary: 用「LLM 是 CPU、Context Window 是 RAM / 書桌」解釋為何需要像作業系統一樣管理上下文。
sources: [SRC-03, SRC-06]
tags: [基礎模型, CPU, RAM, 書桌比喻]
updated: 2026-11-23
---

# CPU 與 RAM（書桌）心智模型

## 白話一句話
**把大型語言模型（LLM）想成超級聰明的 CPU 大腦，Context Window 就是它面前有限的「工作記憶體（RAM）」或「書桌」；書桌堆滿廢紙時，再聰明的大腦也會翻錯頁。**

## 核心概念
Andrej Karpathy 與 LangChain 工程師 Lance Martin 提出了一個讓初學者一眼秒懂的類比 [SRC-03][SRC-06]：

- **LLM = CPU（中央處理器）**：負責邏輯推理、語言生成與做決策，本身不會持久記住這場對話以外的新工作進度。
- **Context Window（上下文視窗）= RAM（工作記憶體） / 實體書桌**：CPU 當下只能直接看見並處理「擺在書桌上」的東西——包含系統指令、你的問題、剛查到的檔案與剛才的對話紀錄 [SRC-03]。
- **外部檔案系統 / 資料庫 = 硬碟（Disk）**：容量幾乎無限，但不會自動全部攤在書桌上，必須按需取用 [SRC-03][SRC-06]。

### 為什麼「書桌越大」不代表能「把整間圖書館倒上去」？
很多人誤以為只要模型支援 20 萬甚至 100 萬 Token 的超大視窗，就可以把整份 PDF、所有程式碼和幾十頁聊天紀錄一次全塞進去。但作業系統從來不會把整個硬碟載入 RAM——因為書桌（RAM）一旦堆滿不相干的雜物，CPU 找線索的時間變慢、注意力分散、還容易看錯行 [SRC-03]。

因此，**Context Engineering 的角色就如同電腦的作業系統（OS）**：負責在模型運作的每一個步驟，把真正用得上的重點擺上書桌，把過時與太佔空間的資料收進硬碟或壓縮整理 [SRC-03][SRC-06]。

## 與其他概念的連結
- 理解這個書桌比喻後，請接著看 [[prompt-vs-context-engineering]] 比較它和傳統提示詞的差別。
- 當書桌塞過頭時會發生什麼事？請見 [[attention-budget-and-context-rot]]。
- 將資料從書桌搬去硬碟保存的技巧，詳見 [[strategy-write-offload]] 與 [[llm-wiki-pattern]]。

## 來源依據
- [SRC-03] Lance Martin / LangChain, *Context Engineering for Agents* (2025-07)
- [SRC-06] Andrej Karpathy, *LLM Wiki — Idea File* (2026-04)
