---
id: strategy-isolate-subagents
title: 策略四：Isolate（Sub-Agent 隔離與環境沙盒）
category: strategies
summary: 利用子代理人與隔離沙盒吸收數萬 Token 的探索雜訊，只回傳 1～2 千 Token 精華結論。
sources: [SRC-02, SRC-03, SRC-05]
tags: [Isolate, Sub-Agent, Quarantine, 隔離]
updated: 2026-11-23
---

# 策略四：Isolate（Sub-Agent 隔離與環境沙盒）

## 白話一句話
**不要自己邊開會邊翻遍整座倉庫找零件；請一位助手（Sub-Agent）去「隔壁房間」翻箱倒櫃找完後，只拿一張一頁紙的報告回來向你簡報。**

## 核心概念
在處理大型程式碼重構或跨數十份文件研究的任務時，光靠單一視窗很快就會被各種探索過程、錯誤嘗試與矛盾資訊塞爆。**Isolate（隔離）**透過邊界切分，把高風險或高雜訊的工作流關進獨立空間 [SRC-02][SRC-03][SRC-05]：

### 1. Sub-Agent 架構（主從上下文隔離）
Anthropic 的多代理人實踐展示了非常具體的壓縮比 [SRC-05]：
- **Coordinator（主協調者）**：始終保持乾淨精簡的高層規劃視窗。
- **Sub-Agent（子代理人）**：在自己獨立的 Context Window 中工作，放手消耗 **數萬甚至十萬級 Token** 去搜尋文件、試跑指令、排查報錯。
- **回傳介面**：任務結束後，Sub-Agent 只把濃縮過的 **1,000～2,000 Token 關鍵洞察與證據**回報給主代理，所有中間試錯雜訊隨著子代理結束一併留存在隔壁房間 [SRC-05]。

### 2. State Schema 與沙盒環境隔離（Environment / Quarantine）
- Drew Breunig 稱這種作法為 **Context Quarantine（上下文檢疫隔離）**：當某段資料高度容易引發 **Poisoning（投毒）** 或 **Clash（衝突）** 時，放在隔離的子環境先檢查，合格結果才准進入主流程 [SRC-02]。
- LangChain 也指出透過獨立沙盒（執行程式碼後只把結果文字傳回，不把整個二進位資料丟進對話）與結構化 State 欄位分區，能有效降低上下文混亂 [SRC-03]。

## 與其他概念的連結
- Isolate 是解決 [[context-failure-modes]] 中「投毒」與「衝突」最乾淨的防線。
- 請回顧 [[four-strategies-wsci]] 看 Isolate 如何與 Write / Select / Compress 協同作戰。
- 本專案本身的檢查流程就是把 `OutlineGate`、`SlideGate` 與 `BrowserGate` 拆分成獨立節點，體現了結構化的隔離精神，詳見 [[rag-vs-llm-wiki]]。

## 來源依據
- [SRC-02] Drew Breunig, *How Long Contexts Fail & How to Fix Your Context* (2025-06)
- [SRC-03] Lance Martin / LangChain, *Context Engineering for Agents* (2025-07)
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
