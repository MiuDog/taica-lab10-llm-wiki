---
id: strategy-compress-compaction
title: 策略三：Compress（Compaction 與高保真壓縮）
category: strategies
summary: 在對話逼近容量或雜訊過高時，將歷史軌跡高保真濃縮並開啟乾淨視窗，對抗 Context Rot。
sources: [SRC-03, SRC-05]
tags: [Compress, Compaction, Summarization, Context Rot]
updated: 2026-11-23
---

# 策略三：Compress（Compaction 與高保真壓縮）

## 白話一句話
**書桌用到一半開始變亂時，花五分鐘把已經做完的筆記濃縮成「一頁精要交接單」，然後換一張乾淨的新桌子繼續下一回合。**

## 核心概念
隨著 AI Agent 連續執行 20、50 甚至上百個回合，歷史對話與工具執行紀錄會像雪球一樣越滾越大 [SRC-03][SRC-05]。**Compress（壓縮）**的目的，就是在不丟失關鍵上下文的前提下，大幅瘦身 Token 體積 [SRC-03]。

Anthropic 與 LangChain 區分了兩種常見作法 [SRC-03][SRC-05]：

1. **Compaction（高保真緊縮）**：
   - 當對話累積到門檻時，系統觸發一次專門的整理動作：保留**架構決策、尚未解決的錯誤狀態、重要結論與目前進度**，同時大刀闊斧刪除已經讀完的冗長工具原始輸出與寒暄文字 [SRC-05]。
   - 完成後，用這份高保真摘要作為種子，開啟一個清爽的全新視窗繼續任務 [SRC-05]。
2. **Summarization & Trimming（摘要與修剪）**：
   - 針對單次工具回傳過長或歷史訊息過舊的段落，直接用精簡摘要覆寫或修剪舊對話回合，常見於長對話記憶體管理 [SRC-03]。

### 壓縮時最怕犯的錯
如果在壓縮時把「剛才試過但失敗的報錯原因」也一併刪光，模型在重啟後往往會重蹈覆轍 [SRC-05]。因此好的 Compaction 提示詞必須明確要求保留 **unresolved errors（未解決錯誤）** 與核心決策依據 [SRC-05]。

## 與其他概念的連結
- Compress 直接對抗的是 [[attention-budget-and-context-rot]] 中的注意力稀釋問題。
- 如果資料太大，該選「寫出到檔案」還是「壓縮」？請對照 [[strategy-write-offload]] 與 [[four-strategies-wsci]]。
- 關於為何「不要把失敗紀錄抹乾淨」，可對照 Manus 在 [[production-lessons-manus]] 的經驗。

## 來源依據
- [SRC-03] Lance Martin / LangChain, *Context Engineering for Agents* (2025-07)
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
