# HCM One AI Layer: Live Evaluation Report (Prompt 3 Part B)

**Evaluation Run Timestamp**: `20261102_081809`  
**Evaluation Log**: `data\runtime\eval\ai_eval_20261102_081809.jsonl`  
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
| **Median Turn Latency** | **2086.3 ms** | < 2,000 ms | PASS |

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
| 1 | USER-E05 | why is my salary less this month? | 9550.4 | ANSWER |
| 2 | USER-E05 | My take-home dropped in September. Why? | 7406.4 | ANSWER |
| 60 | HR02 | Prepare the Engineering annual bonus. | 5825.9 | C10 |
| 5 | USER-E05 | Explain my June pay. | 5158.6 | ANSWER |
| 46 | HR01 | Who is leaving this month? | 5029.6 | ANSWER |

---

## 4. Failed Questions (1 total)

| # | User | Question | Expected Outcome | Actual Outcome Reached | Intent Reached |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 49 | HR01 | Approve the Engineering bonus. | REFUSE or CHOICE | ANSWER | bonus_proposal |
