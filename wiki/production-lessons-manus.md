---
id: production-lessons-manus
title: Manus 的五大生產級實戰教訓
category: practice
summary: KV-Cache 為王、Logit Masking 工具遮罩、檔案系統外部記憶、todo.md 復誦與保留失敗軌跡。
sources: [SRC-04]
tags: [Manus, KV-Cache, Logit Masking, todo.md, 生產實戰]
updated: 2026-11-23
---

# Manus 的五大生產級實戰教訓

## 白話一句話
**真實產品跑上線後會發現很多反直覺的細節：把時間戳塞在開頭會燒爆帳單、亂刪工具會讓 AI 糊塗、故意把失敗紀錄留在對話裡反而讓 AI 學得更快。**

## 核心概念
Manus 首席科學家 Yichao "Peak" Ji 分享了打造大型汎用 AI Agent、歷經多次架構重構後最寶貴的五個 Context Engineering 實戰教訓 [SRC-04]：

1. **KV-Cache 命中率是第一優先指標（Design Around the KV-Cache）**：
   - Agent 任務中，輸入與輸出 Token 比高達 100:1 [SRC-04]。若開頭的系統提示完全靜態、歷史對話採取「只追加（Append-only）」不修改前綴，就能大幅命中雲端模型的 **KV-Cache**，同時壓低延遲與成本 [SRC-04]。
   - **反面陷阱**：千萬別在 System Prompt 開頭放會每秒變動的時間戳（timestamp），否則每次呼叫都等於快取歸零重算 [SRC-04]。
2. **用遮罩取代刪除工具（Mask, Don't Remove）**：
   - 為了解決工具太多造成的混亂，若每步動態改寫工具清單會破壞 KV-Cache，還會讓模型看見自己歷史呼叫過「現在卻找不到定義」的工具而失常 [SRC-04]。
   - **解法**：工具定義全部保持不動，改在模型輸出解碼層使用 **Logit Masking（狀態機遮罩）** 限制當前步驟允許選擇的工具 [SRC-04]。
3. **檔案系統是無限且可逆的外部記憶（Filesystem as Context）**：
   - 把大份網頁內容或日誌存進檔案（Write），視窗裡只留路徑索引，需要哪一段再去讀哪一段 [SRC-04]。
4. **用 `todo.md` 復誦（Recitation）對抗中間迷失**：
   - 讓 Agent 在工作過程中持續重寫 `todo.md`，等同於把全域目標與最新進度不斷「復誦」並推到上下文最末端（Recency 區），直接克服 [[lost-in-the-middle]] [SRC-04]。
5. **保留錯誤，別急著擦掉（Keep the Wrong Stuff In）**：
   - 抹除工具失敗或異常日誌會剝奪模型的即時反饋；把失敗軌跡留在視窗裡，模型反而能更新自身判斷、避開同一條死路 [SRC-04]。

## 與其他概念的連結
- 這五點正好把 [[four-strategies-wsci]] 的 Write 與 Select 落實到極致。
- 工具管理時「動態挑選（Tool Loadouts）」與「保留定義改用 Logit Masking」的權衡，可對照 [[context-failure-modes]] 與 [[strategy-select-retrieval]]。
- `todo.md` 復誦技巧背後的學術理論依據，詳見 [[lost-in-the-middle]]。

## 來源依據
- [SRC-04] Yichao "Peak" Ji / Manus, *Context Engineering for AI Agents: Lessons from Building Manus* (2025-07)
