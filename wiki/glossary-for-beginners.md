---
id: glossary-for-beginners
title: 初學者專有名詞白話對照表
category: reference
summary: 彙整本知識庫與教學簡報全部專有名詞的標準中文解釋、生活比喻與原始出處。
sources: [SRC-01, SRC-02, SRC-03, SRC-04, SRC-05, SRC-06]
tags: [名詞表, 初學者, 詞彙, 對照表]
updated: 2026-11-23
---

# 初學者專有名詞白話對照表

## 白話一句話
**這張總表把「Context Engineering」領域看起來很嚇人的英文術語，通通翻譯成人話與真實檔案出處，確保整份教學簡報用詞完全統一、零黑話門檻。**

## 核心概念
以下所有術語均直接對應本知識庫 `raw/` 中的 6 篇一手資料，也是教學簡報檢查關卡（`Gate 3`）用來驗證「術語必須先解釋才登場、不得擅自造詞」的唯一標準辭典：

| 英文專有名詞 | 白話比喻 / 定義 | 對應深入頁面 | 來源 |
| :--- | :--- | :--- | :--- |
| **Context Window** | AI 當下能同時看見的「工作書桌 / RAM」大小 | [[cpu-ram-mental-model]] | [SRC-03][SRC-05] |
| **Context Engineering** | 在每一步推理時，設計並策展書桌上要擺哪些資訊與工具 | [[overview-context-engineering]] | [SRC-03][SRC-05] |
| **Prompt Engineering** | 琢磨單一句指令或提示詞怎麼寫得清楚 | [[prompt-vs-context-engineering]] | [SRC-05] |
| **Attention Budget** | 模型在單次運算中能分給每個字的有限「專注力預算」 | [[attention-budget-and-context-rot]] | [SRC-05] |
| **Context Rot** | 視窗還沒滿，但雜訊太多導致模型表現提前衰退（腐化） | [[attention-budget-and-context-rot]] | [SRC-02][SRC-05] |
| **Lost in the Middle** | 關鍵資料塞在長文中段時最容易被遺忘的「U 型記憶曲線」 | [[lost-in-the-middle]] | [SRC-01] |
| **Primacy / Recency Bias** | 模型對最開頭（首因）與最結尾（近因）的資訊記得最牢 | [[lost-in-the-middle]] | [SRC-01] |
| **Context Poisoning** | 幻覺或錯誤工具回傳寫進紀錄後，毒害後續所有決策 | [[context-failure-modes]] | [SRC-02] |
| **Context Distraction** | 冗長歷史太多讓模型分心，只會重複舊模式而忘了規則 | [[context-failure-modes]] | [SRC-02] |
| **Context Confusion** | 塞入過多無關工具定義（Tool Schemas）導致選錯或亂叫工具 | [[context-failure-modes]] | [SRC-02] |
| **Context Clash** | 新舊指令或兩份文件彼此矛盾，逼模型靜默亂猜 | [[context-failure-modes]] | [SRC-02] |
| **Tool Loadouts** | 依階段只挑選當下真正需要的小組工具給模型 | [[strategy-select-retrieval]] | [SRC-02] |
| **WSCI (Write/Select/Compress/Isolate)** | 管理上下文的四大操作策略：寫出、挑選、壓縮、隔離 | [[four-strategies-wsci]] | [SRC-03] |
| **Compaction** | 保留決策與未解錯誤的高保真緊縮，清掉雜訊後重開乾淨視窗 | [[strategy-compress-compaction]] | [SRC-05] |
| **Structured Note-Taking** | 讓 Agent 維護外部 `NOTES.md` 等筆記，使長程計畫持久化 | [[strategy-write-offload]] | [SRC-05] |
| **Sub-Agent** | 到隔壁房間獨立翻查大量資料、只回傳濃縮報告的「子代理人」 | [[strategy-isolate-subagents]] | [SRC-03][SRC-05] |
| **Right Altitude** | 系統提示不寫死板 `if-else`、也不寫空話的「適當高度」原則 | [[right-altitude-prompting]] | [SRC-05] |
| **KV-Cache** | 把靜態前綴計算結果快取重複使用，省時間又省錢的關鍵指標 | [[production-lessons-manus]] | [SRC-04] |
| **Logit Masking** | 保持工具清單不動以免破快取，改在輸出端遮罩限制可選工具 | [[production-lessons-manus]] | [SRC-04] |
| **todo.md / Keep the Wrong Stuff In** | 末端復誦待辦錨定目標，且保留失敗日誌讓 Agent 學會避坑 | [[production-lessons-manus]] | [SRC-04] |
| **LLM Wiki** | 透過 `raw/`、`wiki/`、`index.md`、`log.md` 提前編譯知識的架構 | [[llm-wiki-pattern]] | [SRC-06] |
| **RAG** | 查詢時才切塊撈取片段拼湊答案的傳統檢索增強生成 | [[rag-vs-llm-wiki]] | [SRC-06] |

## 與其他概念的連結
- 初學者建議搭配 [[overview-context-engineering]] 一同瀏覽。
- 寫作或檢查簡報術語時，可直接從 [[four-strategies-wsci]] 與 [[llm-wiki-pattern]] 查核完整脈絡。

## 來源依據
- [SRC-01] Nelson F. Liu et al., *Lost in the Middle: How Language Models Use Long Contexts* (TACL / arXiv:2307.03172)
- [SRC-02] Drew Breunig, *How Long Contexts Fail & How to Fix Your Context* (2025-06)
- [SRC-03] Lance Martin / LangChain, *Context Engineering for Agents* (2025-07)
- [SRC-04] Yichao "Peak" Ji / Manus, *Context Engineering for AI Agents: Lessons from Building Manus* (2025-07)
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
- [SRC-06] Andrej Karpathy, *LLM Wiki — Idea File* (2026-04)
