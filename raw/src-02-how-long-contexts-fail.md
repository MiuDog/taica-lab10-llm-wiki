---
source_id: SRC-02
title: "How Long Contexts Fail & How to Fix Your Context"
authors: Drew Breunig
date: 2025-06-22 / 2025-06-26
url: https://www.dbreunig.com/2025/06/22/how-long-contexts-fail.html
follow_up_url: https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html
immutable: true
---

# [SRC-02] How Long Contexts Fail & How to Fix Your Context

## 書目資訊
- **作者**：Drew Breunig
- **發表日期**：2025-06-22（失效模式）、2025-06-26（修正方法）
- **原文連結**：https://www.dbreunig.com/2025/06/22/how-long-contexts-fail.html

## 原始文獻核心論點摘錄（Immutable Source）

### 一、破除迷思：更大的 Context Window 不等於問題消失
即使模型支援高達百萬 Token 的上下文視窗，將過多檔案、工具定義與冗長對話歷史盲目塞進視窗，並不會讓 AI Agent 更聰明，反而會引發**Context Rot（上下文腐化）**。Context 是稀缺且脆弱的系統資源。

### 二、長上下文的四大失效模式（Four Failure Modes）

1. **Context Poisoning（上下文投毒）**：
   - **定義**：當幻覺（hallucination）、錯誤假設或異常的工具輸出進入了活躍上下文（例如工作摘要或目標追蹤區），後續模型就會不斷把該錯誤當成既定事實繼續推理。
   - **案例**：長程執行的 Agent（如玩遊戲或大規模改寫程式碼）只要有一次錯誤狀態被寫進紀錄，就會像毒藥一樣污染後續幾十步決策，甚至陷入無窮迴圈。

2. **Context Distraction（上下文分心）**：
   - **定義**：當上下文長度膨脹到充滿過多瑣碎歷史紀錄時，模型過度專注於重複模仿對話紀錄中的模式，反而忽略了訓練階段學到的通用能力與指令遵循。
   - **後果**：模型在冗長歷史裡迷失方向，開始機械式重複舊動作或遺漏明確規則。

3. **Context Confusion（上下文混亂）**：
   - **定義**：無關或多餘的資訊——特別是**過多工具定義（Tool Schemas / MCP APIs）**——充斥於上下文中，導致模型品質下降、叫錯工具或在不需要時亂叫工具。
   - **後果**：工具清單越多，選擇決策的雜訊就越大。

4. **Context Clash（上下文衝突）**：
   - **定義**：新加入的資訊、工具回傳或使用者新規則，與先前提及的系統指令或舊文件**彼此矛盾**。
   - **後果**：模型被迫在兩個相互矛盾的規則中「靜默猜測」該聽誰的，導致輸出結果忽左忽右、高度不可預測。

### 三、對應的修補手段（How to Fix Your Context）
Drew Breunig 在後續文章歸納出對應的工程解法：
- **RAG / Select**：精準挑選必要片段，避免無關文字造成 Distraction。
- **Tool Loadouts（動態工具載入）**：依當前任務階段只提供相關工具，解決 Confusion。
- **Context Quarantine（隔離區）**：用獨立子對話 / 子代理把髒資料隔開，防止 Poisoning 與 Clash 污染主線。
- **Context Pruning（修剪）& Summarization（摘要）**：主動刪除過時資訊與矛盾片段。
- **Context Offloading（卸載）**：把龐大狀態寫到上下文以外的檔案或筆記中。
