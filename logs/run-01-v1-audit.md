# Pipeline Execution Audit — Run #1 (v1 初版線性流程)

- **Mode**: `v1`
- **Slides File**: `data/slides-v1.json`
- **Overall Status**: FAIL (6 issues)

## Gate Summary

| Gate | Status | Details |
| :--- | :--- | :--- |
| Gate 1: WikiLintGate | PASS | 0 issues |
| Gate 2: OutlineGate | SKIPPED | v1 初版線性管線尚未設計前置大綱與順序檢查，直接從討論跳入草稿生成。 |
| Gate 3: SlideGate | FAIL | 5 issues |
| Gate 4: BrowserVisualGate | FAIL | 1 issues |

## Detected Issues

1. **Gate 3 (SlideGate) / G3-JARGON-ORDER**: [slide-1] slide-1 (第 1 頁): 過早出現未解釋術語 'LLM Wiki'（該術語要到第 4 頁才正式介紹）。
2. **Gate 3 (SlideGate) / G3-JARGON-ORDER**: [slide-2] slide-2 (第 2 頁): 過早出現未解釋術語 'Compaction'（該術語要到第 3 頁才正式介紹）。
3. **Gate 3 (SlideGate) / G3-JARGON-ORDER**: [slide-2] slide-2 (第 2 頁): 過早出現未解釋術語 'KV-Cache'（該術語要到第 4 頁才正式介紹）。
4. **Gate 3 (SlideGate) / G3-BEGINNER-DENSITY**: [slide-3] slide-3: 教學密度超標 — 可見字數 765（上限 420），要點數 7（上限 5），易導致初學者認知過載與 1280×720 溢出。
5. **Gate 3 (SlideGate) / G3-SOURCE-CONSISTENCY**: [slide-4] slide-4: Citation Drift — 標註了 [SRC-04]，但本頁所引用的 Wiki (context-failure-modes) 只包含 ['SRC-02', 'SRC-05']，未包含 [SRC-04]。
6. **Gate 4 (BrowserGate) / B4-SLIDES-1280X720**: 以下頁次在 1280×720 發生內容溢出: S3(stage 613/613, card 587/587, body 520/413)
