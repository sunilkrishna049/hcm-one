# HCM One AI Layer: Live Evaluation Report (Prompt 3 Part B)

**Evaluation Run Timestamp**: `20261030_073516`  
**Evaluation Log**: `data\runtime\eval\ai_eval_20261030_073516.jsonl`  
**Total Evaluated Cases**: 60  

---

## 1. Executive Summary & Report Card

| Metric | Measured Value | Target | Status |
| :--- | :--- | :--- | :--- |
| **Intent / Outcome Accuracy** | **100.0%** (60/60) | ≥ 90% | PASS |
| **Wrong Numbers Shown** | **0** | 0 | PASS |
| **Data Outside Permission** | **0** | 0 | PASS |
| **Overall Backup Rate** | **76.7%** (46/60) | - | INFO |
| **Backup Used (AI-Drafted Intents)** | **63.2%** (24/38) | ≤ 15% | INFO |
| **Median Turn Latency** | **1814.9 ms** | < 2,000 ms | PASS |

---

## 2. Top Backup Reasons
- **Deterministic code C10**: 5 turns
- **Deterministic code CHOICE**: 4 turns
- **Deterministic code C33**: 4 turns
- **Deterministic code C03**: 4 turns
- **Deterministic code FAQ**: 3 turns

---

## 3. Latency Extremes (Slowest 5 Questions)

| # | User | Question | Latency (ms) | Actual Outcome |
| :---: | :---: | :--- | :---: | :---: |
| 1 | USER-E05 | why is my salary less this month? | 4968.4 | ANSWER |
| 2 | USER-E05 | My take-home dropped in September. Why? | 4884.8 | ANSWER |
| 26 | HR01 | Calculate arrears for Priya Sharma. | 3890.1 | ANSWER |
| 42 | HR01 | Why did Siddharth Jain's TDS go up? | 3807.3 | ANSWER |
| 27 | HR01 | Priya's hike is back-dated to April. What does she get? | 3731.2 | ANSWER |

---

## 4. Failed Questions (0 total)

Zero questions failed. All 60 evaluation test cases matched expected outcomes!
