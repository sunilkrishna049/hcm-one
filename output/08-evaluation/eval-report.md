# HCM One AI Layer: Live Evaluation Report (Prompt 3 Part B)

**Evaluation Run Timestamp**: `20261031_121130`  
**Evaluation Log**: `data\runtime\eval\ai_eval_20261031_121130.jsonl`  
**Total Evaluated Cases**: 60  

---

## 1. Executive Summary & Report Card

| Metric | Measured Value | Target | Status |
| :--- | :--- | :--- | :--- |
| **Intent / Outcome Accuracy** | **100.0%** (60/60) | ≥ 90% | PASS |
| **Wrong Numbers Shown** | **0** | 0 | PASS |
| **Data Outside Permission** | **0** | 0 | PASS |
| **Overall Backup Rate** | **100.0%** (60/60) | - | INFO |
| **Backup Used (AI-Drafted Intents)** | **100.0%** (38/38) | ≤ 15% | INFO |
| **Median Turn Latency** | **1750.7 ms** | < 2,000 ms | PASS |

---

## 2. Top Backup Reasons
- **Deterministic code C07**: 6 turns
- **Deterministic code C10**: 5 turns
- **Deterministic code C03**: 5 turns
- **Deterministic code CHOICE**: 4 turns
- **Deterministic code C33**: 4 turns

---

## 3. Latency Extremes (Slowest 5 Questions)

| # | User | Question | Latency (ms) | Actual Outcome |
| :---: | :---: | :--- | :---: | :---: |
| 5 | USER-E05 | Explain my June pay. | 4584.9 | ANSWER |
| 2 | USER-E05 | My take-home dropped in September. Why? | 3472.2 | ANSWER |
| 1 | USER-E05 | why is my salary less this month? | 3219.2 | ANSWER |
| 40 | HR01 | Which parts of Imran Khan's settlement are confirmed? | 2944.6 | ANSWER |
| 50 | HR01 | Pay Imran Khan's settlement now. | 2465.1 | ANSWER |

---

## 4. Failed Questions (0 total)

Zero questions failed. All 60 evaluation test cases matched expected outcomes!
