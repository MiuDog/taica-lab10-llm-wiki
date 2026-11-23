---
source_id: SRC-05
title: "Effective Context Engineering for AI Agents"
authors: Anthropic Applied AI Engineering Team
date: 2025-09-29
url: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
immutable: true
---

# [SRC-05] Effective Context Engineering for AI Agents

## 書目資訊
- **作者**：Anthropic Engineering
- **發表日期**：2025-09-29
- **原文連結**：https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

## 原始文獻核心論點摘錄（Immutable Source）

### 一、從 Prompt Engineering 演進到 Context Engineering
Prompt Engineering 聚焦於「如何措辭寫好單次提問或系統提示」；而進入長程多輪 AI Agent 時代，**Context Engineering** 關注的是更宏觀的問題：**在模型每一次推論當下，應該如何策展（curate）與維護整個 Token 集合（包含系統提示、工具定義、範例、歷史訊息與外部檢索資料）**。

### 二、核心概念：Attention Budget（注意力預算）與 Context Rot（上下文腐化）
- Transformer 架構下，每個 Token 都要與其他所有 Token 兩兩建立關聯（$n^2$ 級注意力配對關係）。
- 因此 **Context 是一種有限的「注意力預算」（Attention Budget）**：隨著視窗內的 Token 數增加，模型能分配給單一關鍵細節的注意力被不斷攤薄。
- **Context Rot（上下文腐化）**：遠在觸及硬體 Token 上限之前，隨著無關文字累積，模型精準召回資訊與進行複雜推理的能力就已經明顯退化。目標不是「塞進越多越好」，而是找到**能最大化預期結果的最小高訊號 Token 集合（Smallest possible set of high-signal tokens）**。

### 三、系統提示設計原則：找到 Right Altitude（適當高度）
Anthropic 強調系統提示詞不能太低（過度微觀硬編碼大量 `if-else` 脆弱規則），也不能太高（只給空泛口號導致缺乏引導）。
- **Right Altitude**：給予清晰的啟發式原則、行為邊界與角色定位，把具體的細微決策空間留給模型彈性推論。
- 建議使用清楚的區塊分隔（如 XML 標籤 `<instructions>`、`<background_information>` 或 Markdown 標題）讓模型容易解析結構。

### 四、長程 Agent 的四大實務技術
1. **Just-in-Time Context Retrieval（即時輕量檢索）**：
   不必預先把所有文件都做成傳統 Embedding 塞進 Prompt，而是只保留輕量指標（如檔案路徑、查詢指令），讓 Agent 像人類工程師一樣在需要時用工具即時探索取證。
2. **Compaction（高保真緊縮）**：
   當對話逼近容量上限時，觸發壓縮流程，將冗長歷史濃縮為保留「架構決策、未解錯誤與目前進度」的高保真摘要，並丟棄過時的工具雜訊，在乾淨視窗重新出發。
3. **Structured Note-Taking（結構化筆記）**：
   讓 Agent 主動在外部維護 `NOTES.md` 或待辦清單，將長程規劃從短期工作記憶體解耦。
4. **Sub-Agent Architectures（子代理隔離架構）**：
   協調者只握有高層次計畫；把大量消耗 Token 的深度搜查或程式探勘派給獨立的 **Sub-agent**，讓子代理在獨立視窗消耗上萬（甚至十萬級）Token 後，只回傳 **1,000～2,000 Token 的精煉摘要**給主代理。
