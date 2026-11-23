---
id: right-altitude-prompting
title: Right Altitude（系統提示詞的適當高度）
category: practice
summary: Anthropic 提出的系統提示設計黃金區間：既不微觀硬編碼大量 if-else，也不流於空泛口號。
sources: [SRC-05]
tags: [Right Altitude, System Prompt, XML Tags, 系統提示]
updated: 2026-11-23
---

# Right Altitude（系統提示詞的適當高度）

## 白話一句話
**交代 AI 工作規則就像帶實習生：把每一步寫成死板的 `if-else` 條文會讓他卡死，只說「加油好好做」又太模糊——你要站在「Right Altitude（適當高度）」，給清楚原則與邊界。**

## 核心概念
Anthropic 工程團隊在設計長程 Agent 時發現，System Prompt（系統提示詞）的撰寫常見兩種極端錯誤 [SRC-05]：

1. **高度太低（Too Low — 過度微觀硬編碼）**：
   - 把 Prompt 寫成幾百行宛如 `if 遇到A就回B else 遇到C就做D` 的脆弱指令樹。
   - **缺點**：佔用寶貴的 **Attention Budget**、降低模型彈性推理能力，遇到未預料的新狀況立刻崩潰 [SRC-05]。
2. **高度太高（Too High — 過度空泛抽象）**：
   - 只寫「你是一個有幫助、準確的專業助手，請做好這份簡報」，缺少具體策略與驗收門檻。
   - **缺點**：模型失去明確行為邊界，不同步驟執行品質飄移不定 [SRC-05]。

### 找到「Right Altitude（適當高度）」的實作準則
- **提供強有力的啟發式原則（Heuristics）與工作邊界**：告訴模型「什麼必須查證、什麼情況要停下來檢查、目標受眾是誰」，將具體措辭與路徑微調留給模型自行推論 [SRC-05]。
- **善用結構化區塊分隔**：使用明確的 XML 標籤（例如 `<background_information>`、`<instructions>`、`<output_description>`）或乾淨的 Markdown 標題區隔不同角色與規則，幫助模型一眼定位重要約束 [SRC-05]。
- **挑選出對的 Few-Shot 範例**：與其寫一大堆「不准這樣做」的負面條列，不如放 1～2 個極精煉的正向黃金範例，訊噪比遠高於千言萬語 [SRC-05]。

## 與其他概念的連結
- 這正是 [[prompt-vs-context-engineering]] 中，現代提示設計融入整體上下文管理的具體呈現。
- 本 Wiki 專案根目錄的 `SCHEMA.md` 規範檔案，就是站在適當高度引導 LLM 維護知識庫的系統提示工程，請見 [[llm-wiki-pattern]]。
- 配合系統提示保持穩定的技巧，可對照 [[production-lessons-manus]] 的快取設計。

## 來源依據
- [SRC-05] Anthropic Engineering, *Effective Context Engineering for AI Agents* (2025-09)
