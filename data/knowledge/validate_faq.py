import json
import os
import re
import sys

ALLOWED_AUDIENCES = {"employee", "hr", "both"}
ALLOWED_URLS = {
    "/chat?action=draft-query",
    "/chat?action=explain-salary",
    "/chat?action=explain-tds",
    "/chat?action=intro",
    ""
}
REQUIRED_FIELDS = ["id", "category", "question", "answer", "link_text", "url", "audience", "source"]

BANNED_ANSWER_PATTERNS = [
    r"\bcode\b",
    r"\bcalculation code\b",
    r"\bsystem\b",
    r"\bconfiguration\b",
    r"\bconfigured\b",
    r"\bdependency\b",
    r"\bdependencies\b",
    r"\bdependent total\b",
    r"\bscope\b",
    r"\bpersisted\b",
    r"\bthe user\b",
    r"\bmathematical readiness\b",
]

def validate_faq():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    faq_path = os.path.join(repo_root, "data", "knowledge", "payroll_faq.json")

    if not os.path.exists(faq_path):
        print(f"ERROR: FAQ file not found at {faq_path}")
        return False

    try:
        with open(faq_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Invalid JSON: {e}")
        return False

    errors = []

    # Top-level checks
    for key in ["schema_version", "dataset_name", "language", "updated_on", "total_questions", "fields", "questions"]:
        if key not in data:
            errors.append(f"Missing top-level key: {key}")

    questions = data.get("questions", [])
    total_q = data.get("total_questions", 0)

    if total_q != len(questions):
        errors.append(f"total_questions ({total_q}) does not match questions list length ({len(questions)})")

    if not (25 <= len(questions) <= 40):
        errors.append(f"Expected 25 to 40 questions, found {len(questions)}")

    seen_ids = set()
    categories = {}

    for idx, q in enumerate(questions):
        qid = q.get("id", f"index-{idx}")
        cat = q.get("category", "Uncategorized")
        categories[cat] = categories.get(cat, 0) + 1

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in q:
                errors.append(f"[{qid}] Missing required field: {field}")

        # Check unique IDs
        if qid in seen_ids:
            errors.append(f"[{qid}] Duplicate id")
        seen_ids.add(qid)

        # Check audience
        aud = q.get("audience")
        if aud not in ALLOWED_AUDIENCES:
            errors.append(f"[{qid}] Invalid audience '{aud}'. Allowed: {ALLOWED_AUDIENCES}")

        # Check URL
        url = q.get("url")
        if url not in ALLOWED_URLS:
            errors.append(f"[{qid}] Invalid URL '{url}'. Allowed: {ALLOWED_URLS}")

        # Check no digits in answer
        answer = q.get("answer", "")
        digits_found = [c for c in answer if c.isdigit()]
        if digits_found:
            errors.append(f"[{qid}] Answer contains digit(s) {digits_found}: '{answer}'")

        # Check no banned technical or internal terms in answer
        for pattern in BANNED_ANSWER_PATTERNS:
            match = re.search(pattern, answer, re.IGNORECASE)
            if match:
                errors.append(f"[{qid}] Answer contains banned term '{match.group(0)}': '{answer}'")

        # Check source points to existing file
        src = q.get("source", "")
        if not src:
            errors.append(f"[{qid}] Empty source")
        else:
            # First token is the file path
            src_file = src.split()[0].strip()
            full_src_path = os.path.join(repo_root, src_file)
            if not os.path.isfile(full_src_path):
                errors.append(f"[{qid}] Source file does not exist: {src_file}")

    print("=" * 60)
    print("HCM ONE PAYROLL FAQ VALIDATION")
    print("=" * 60)
    print(f"Dataset Name: {data.get('dataset_name')}")
    print(f"Total Questions: {len(questions)}")
    print("\nEntries per category:")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count}")

    print("\n5 Sample Entries:")
    sample_indices = [0, 4, 9, 17, 24]
    for s_idx in sample_indices:
        if s_idx < len(questions):
            sq = questions[s_idx]
            print(f"\n[{sq['id']}] Category: {sq['category']} | Audience: {sq['audience']}")
            print(f"  Q: {sq['question']}")
            print(f"  A: {sq['answer']}")
            print(f"  Link: '{sq['link_text']}' -> '{sq['url']}'")
            print(f"  Source: {sq['source']}")

    print("\n" + "=" * 60)
    if errors:
        print(f"VALIDATION FAILED WITH {len(errors)} ERROR(S):")
        for err in errors:
            print(f"  - {err}")
        print("=" * 60)
        return False
    else:
        print("ALL VALIDATION CHECKS PASSED PERFECTLY!")
        print("=" * 60)
        return True

if __name__ == "__main__":
    success = validate_faq()
    sys.exit(0 if success else 1)
