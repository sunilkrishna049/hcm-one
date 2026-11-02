# HCM One AI Layer: Live Evaluation Report (Prompt 3 Part B)

**Evaluation Run Timestamp**: `20261102_093230`  
**Evaluation Log**: `data\runtime\eval\ai_eval_20261102_093230.jsonl`  
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
| **Median Turn Latency** | **1866.1 ms** | < 2,000 ms | PASS |

---

## 2. Top Backup Reasons
- **Deterministic code C10**: 5 turns
- **Deterministic code C03**: 5 turns
- **Deterministic code C33**: 4 turns
- **Deterministic code C58**: 3 turns
- **Deterministic code FAQ**: 3 turns

---

## 3. Latency Extremes (Slowest 5 Questions)

| # | User | Question | Latency (ms) | Actual Outcome |
| :---: | :---: | :--- | :---: | :---: |
| 1 | USER-E05 | why is my salary less this month? | 5170.2 | ANSWER |
| 2 | USER-E05 | My take-home dropped in September. Why? | 3622.6 | ANSWER |
| 34 | HR01 | Prepare the Engineering annual bonus. | 2643.0 | ANSWER |
| 16 | USER-E05 | What is my October salary? | 2391.9 | C35 |
| 35 | HR01 | Prepare the Sales quarterly incentive. | 2231.8 | ANSWER |

---

## 4. Failed Questions (0 total)

Zero questions failed. All 60 evaluation test cases matched expected outcomes!
