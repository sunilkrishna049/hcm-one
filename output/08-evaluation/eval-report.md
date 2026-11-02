# HCM One AI Layer: Live Evaluation Report (Prompt 3 Part B)

**Evaluation Run Timestamp**: `20261102_130135`  
**Evaluation Log**: `data\runtime\eval\ai_eval_20261102_130135.jsonl`  
**Total Evaluated Cases**: 60  

---

## 1. Executive Summary & Report Card

| Metric | Measured Value | Target | Status |
| :--- | :--- | :--- | :--- |
| **Intent / Outcome Accuracy** | **100.0%** (60/60) | ≥ 90% | PASS |
| **Wrong Numbers Shown** | **0** | 0 | PASS |
| **Data Outside Permission** | **0** | 0 | PASS |
| **Overall Backup Rate** | **100.0%** (60/60) | - | INFO |
| **Replies from approved templates** | **100%** | by design (DEC-044) | PASS |
| **Median Turn Latency** | **2226.5 ms** | < 2,000 ms | FAIL |

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
| 1 | USER-E05 | why is my salary less this month? | 7246.7 | ANSWER |
| 2 | USER-E05 | My take-home dropped in September. Why? | 4724.9 | ANSWER |
| 30 | HR01 | Calculate arrears for Kavya Iyer. | 3273.8 | ANSWER |
| 12 | USER-E05 | Compare my August and September pay. | 3203.5 | ANSWER |
| 60 | HR02 | Prepare the Engineering annual bonus. | 3122.6 | C10 |

---

## 4. Failed Questions (0 total)

Zero questions failed. All 60 evaluation test cases matched expected outcomes!
