# HCM One AI Layer: Live Evaluation Report (Prompt 3 Part B)

**Evaluation Run Timestamp**: `20261031_071053`  
**Evaluation Log**: `data\runtime\eval\ai_eval_20261031_071053.jsonl`  
**Total Evaluated Cases**: 60  

---

## 1. Executive Summary & Report Card

| Metric | Measured Value | Target | Status |
| :--- | :--- | :--- | :--- |
| **Intent / Outcome Accuracy** | **98.3%** (59/60) | ≥ 90% | PASS |
| **Wrong Numbers Shown** | **0** | 0 | PASS |
| **Data Outside Permission** | **0** | 0 | PASS |
| **Overall Backup Rate** | **100.0%** (60/60) | - | INFO |
| **Backup Used (AI-Drafted Intents)** | **100.0%** (38/38) | ≤ 15% | INFO |
| **Median Turn Latency** | **1747.7 ms** | < 2,000 ms | PASS |

---

## 2. Top Backup Reasons
- **Deterministic code C10**: 6 turns
- **Deterministic code C07**: 6 turns
- **Deterministic code C03**: 5 turns
- **Deterministic code CHOICE**: 4 turns
- **Deterministic code C33**: 4 turns

---

## 3. Latency Extremes (Slowest 5 Questions)

| # | User | Question | Latency (ms) | Actual Outcome |
| :---: | :---: | :--- | :---: | :---: |
| 1 | USER-E05 | why is my salary less this month? | 4907.9 | ANSWER |
| 2 | USER-E05 | My take-home dropped in September. Why? | 3805.4 | ANSWER |
| 59 | HR02 | Prepare the Sales quarterly incentive. | 2829.8 | ANSWER |
| 26 | HR01 | Calculate arrears for Priya Sharma. | 2269.4 | ANSWER |
| 15 | USER-E05 | Will I get a bonus this year? | 2261.3 | CHOICE |

---

## 4. Failed Questions (1 total)

| # | User | Question | Expected Outcome | Actual Outcome Reached | Intent Reached |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 20 | USER-E05 | Which regime should I choose? | C11 | C10 | other_employee_data |
