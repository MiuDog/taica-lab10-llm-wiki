---
source_id: SRC-04
title: "Context Engineering for AI Agents: Lessons from Building Manus"
authors: Yichao "Peak" Ji (Manus)
date: 2025-07-18
url: https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
zh_url: https://manus.im/zh-tw/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
immutable: true
---

# [SRC-04] Context Engineering for AI Agents: Lessons from Building Manus

## 書目資訊
- **作者**：Yichao "Peak" Ji（Manus 共同創辦人兼首席科學家）
- **發表日期**：2025-07-18
- **原文連結**：https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus

## 原始文獻核心論點摘錄（Immutable Source）

Manus 在實際打造商用汎用 AI Agent 的過程中走過多次重構（Stochastic Gradient Descent on Architecture），總結出以下反直覺但極關鍵的實戰經驗：

1. **把 KV-Cache 命中率視為第一指標（Design Around the KV-Cache）**：
   - 在多回合 Agent 執行中，輸入 Token 遠大於輸出 Token（比例可達 100:1）。若系統提示詞（System Prompt）開頭保持完全靜態、且歷史上下文採用 **Append-only（只追加、不改寫前綴）**，就能高度重複命中雲端 LLM 的 **KV-Cache**。
   - **實戰規範**：不要在 System Prompt 開頭放會每秒跳動的精確時間戳記（timestamp），否則每一次請求都會整段重算，延遲與費用大幅飆升。

2. **用遮罩取代增刪工具（Mask, Don't Remove）**：
   - 工具太多容易讓 Agent 迷糊，但如果每回合動態把工具定義從 Prompt 中「刪掉或重排」，會直接破壞前綴的 KV-Cache，還會讓歷史訊息出現「找不到對應定義的工具呼叫」而使模型混亂。
   - **解法**：保持工具清單定義固定不變，改在模型解碼階段透過 **Logit Masking（狀態機遮罩）** 限制當前步驟允許呼叫的工具前綴。

3. **把檔案系統當成終極外部記憶（Use the File System as Context）**：
   - 當網頁抓取或工具輸出動輒上萬字時，把完整資料寫進本地檔案，在上下文中只保留「檔案路徑 + 簡短索引」，讓 Agent 需要細節時再用讀檔/搜尋工具取回，實現可逆的壓縮。

4. **透過復誦（Recitation）對抗 Lost in the Middle**：
   - 長任務跑了幾十步之後，Agent 很容易忘記最一開始要完成的全局目標。
   - Manus 讓 Agent 持續建立並更新一份 **`todo.md`** 清單，把已完成與待辦項目不斷「復誦」寫在上下文的最末端（Recency 區域），利用模型對末尾文字的天然高注意力，牢牢錨定任務方向。

5. **把錯誤留在上下文裡（Keep the Wrong Stuff In）**：
   - 很多人直覺想在工具失敗時把錯誤日誌抹乾淨，讓 Prompt 看起來漂漂亮亮。
   - Manus 發現這樣反而害模型失去反饋訊號、一再重複犯同樣的錯；把失敗的操作與報錯訊息保留在上下文中，模型才能即時觀察到「哪條路走不通」並自動修正策略。
