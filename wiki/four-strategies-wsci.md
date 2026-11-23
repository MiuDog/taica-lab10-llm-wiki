---
id: four-strategies-wsci
title: 四大工程策略總覽（WSCI 框架）
category: strategies
summary: Lance Martin 整理的 Write、Select、Compress、Isolate 四大上下文工程操作支柱。
sources: [SRC-03, SRC-05]
tags: [WSCI, Write, Select, Compress, Isolate]
updated: 2026-11-23
---

# 四大工程策略總覽（WSCI 框架）

## 白話一句話
**整理 AI 書桌只需要記住四個動詞：Write（寫到桌上外保存）、Select（只拿這步需要的上桌）、Compress（把厚筆記濃縮）、Isolate（找小幫手到隔壁桌做雜事）。**

## 核心概念
LangChain 的 Lance Martin 綜合業界建置 AI Agent 的實戰模式，提出 **WSCI 四大策略框架**，對應作業系統管理記憶體的四種基本機制 [SRC-03]，也與 Anthropic 的長程 Agent 實務高度互補 [SRC-05]：

1. **Write（寫出 / 外部卸載）**：
   把長篇工具輸出、草稿與專案進度寫到 Context Window 外部的檔案或筆記（如 `NOTES.md`、`todo.md`），主視窗只留簡短索引，避免 RAM 瞬間爆掉 [SRC-03][SRC-05]。
2. **Select（挑選 / 即時檢索）**：
   每執行一步之前，精準抽取當下真正用得到的記憶、規則、文件頁與工具，保持高訊噪比 [SRC-03][SRC-05]。
3. **Compress（壓縮 / 濃縮）**：
   透過可逆緊縮（Compaction）或重點摘要（Summarization），替必須留在視窗內的冗長歷史減肥，保住關鍵決策並清掉過時雜訊 [SRC-03][SRC-05]。
4. **Isolate（隔離 / 子代理分工）**：
   把搜尋大量資料或試驗試錯的髒活交給擁有獨立視窗的 **Sub-Agent** 或沙盒，完成後只回傳精煉結果給協調者 [SRC-03][SRC-05]。

### 四大策略與四大失效的對應處方

| 策略 | 白話動作 | 主要對治哪種問題？ | 專頁深入閱讀 |
| :--- | :--- | :--- | :--- |
| **Write** | 筆記存硬碟，桌上留書籤 | 視窗爆滿、長期遺忘 | [[strategy-write-offload]] |
| **Select** | 按目錄精準抽頁 | Distraction（分心）、Confusion（混亂） | [[strategy-select-retrieval]] |
| **Compress** | 考前重點濃縮摘要 | Context Rot（腐化）、Token 成本暴增 | [[strategy-compress-compaction]] |
| **Isolate** | 開獨立副駕駛房間處理 | Poisoning（投毒）、Clash（衝突） | [[strategy-isolate-subagents]] |

## 與其他概念的連結
- 這四大策略的共同源頭心智模型是 [[cpu-ram-mental-model]]。
- 欲看每項策略的細部設計與權衡，請點上方表格的專頁，或直接查看 [[production-lessons-manus]] 看真實產品怎麼組合使用它們。

## 來源依據
- [SRC-03] Lance Martin / LangChain, *Context Engineering for Agents* (2025-07)
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
