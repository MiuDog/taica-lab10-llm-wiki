---
source_id: SRC-01
title: "Lost in the Middle: How Language Models Use Long Contexts"
authors: Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang
affiliation: Stanford University, UC Berkeley, Samaya AI
venue: Transactions of the Association for Computational Linguistics (TACL) / arXiv:2307.03172
year: 2024
url: https://arxiv.org/abs/2307.03172
immutable: true
---

# [SRC-01] Lost in the Middle: How Language Models Use Long Contexts

## 書目資訊
- **作者**：Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang
- **發表單位 / 期刊**：Stanford / UC Berkeley / Samaya AI，發表於 *TACL* (arXiv:2307.03172)
- **原文連結**：https://arxiv.org/abs/2307.03172

## 原始文獻核心論點摘錄（Immutable Source）

1. **問題設定**：
   雖然語言模型宣稱支援愈來愈長的上下文視窗（Long Context Window），但模型是否真的能「均勻且可靠地」使用視窗中每個位置的資訊，一直缺乏系統性檢驗。作者透過兩項可控實驗進行評估：
   - **多文件問答（Multi-Document Question Answering）**：在大量無關干擾文件（distractor documents）中，改變包含正確答案的關鍵文件放置位置。
   - **合成鍵值對檢索（Synthetic Key-Value Retrieval）**：在大量 JSON 鍵值對清單中，測試模型找出特定 Key 對應 Value 的準確率。

2. **關鍵發現一：U 型效能曲線（U-Shaped Performance Curve）**：
   - 模型表現與關鍵資訊在輸入脈絡中的**相對位置**高度相關。
   - 當關鍵文件放在提示詞的**最開頭（Primacy Bias，首因效應）**或**最結尾（Recency Bias，近因效應）**時，模型回答準確率最高。
   - 當關鍵資訊被埋在**長上下文的中間位置（Middle）**時，準確率大幅滑落，形成明顯的「**U 型（U-shaped）**」曲線。

3. **關鍵發現二：塞進長文有時還不如「不給任何文件」**：
   - 研究觀察到一個驚人現象：當正確答案被迫埋在長篇干擾文件的中間區段時，模型的問答準確率甚至會**低於 Closed-book Baseline**（完全不給任何外部文件、只靠模型訓練參數記憶來回答的基準線）。
   - 這意味著無關或低相關的「干擾文本」並非只是無害佔空間，而是會實質**破壞**模型的推理判斷。

4. **關鍵發現三：擴大視窗上限與指令微調無法根治問題**：
   - 即使測試當時號稱支援長上下文（Explicitly Long-Context）的模型，隨著總文件數量與 Token 長度增加，只要關鍵資訊落在中段，效能依舊顯著下滑。
   - 無論是 Decoder-only 還是 Encoder-decoder 架構，以及經過指令微調（Instruction Tuning）的模型，都無法憑藉架構本身免疫「中間迷失」現象。

5. **對工程實作的啟示**：
   - **Context Window 的容量不等於有效注意力（Effective Context）**。
   - RAG 或 Agent 系統不能只是「把所有檢索到的 Chunk 全部倒進 Prompt」，必須重視資訊的排序（把最重要的放到開頭或結尾）並嚴格控制干擾文件數量。
