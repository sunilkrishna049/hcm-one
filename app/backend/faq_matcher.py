"""Transparent keyword overlap FAQ lookup against data/knowledge/payroll_faq.json.
Follows the course faq_lookup style: returns matched id, question, answer, link_text, url, and confidence.
Never hallucinates or invents an answer.
"""
import json
import re
from typing import Dict, List, Optional, Tuple

from .config import ROOT_DIR

FAQ_PATH = ROOT_DIR / "data" / "knowledge" / "payroll_faq.json"

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "is", "are", "was", "were", "be", "been", "being",
    "what", "why", "how", "when", "where", "who", "which",
    "do", "does", "did", "can", "could", "would", "should",
    "i", "my", "me", "you", "your", "they", "their", "it", "its"
}


class FAQMatcher:
    def __init__(self):
        self._faq_data = None
        self._load()

    def _load(self):
        if not FAQ_PATH.exists():
            self._faq_data = []
            return
        content = json.loads(FAQ_PATH.read_text(encoding="utf-8"))
        self._faq_data = content.get("questions", [])

    def _tokenize(self, text: str) -> set:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = set(cleaned.split())
        return {t for t in tokens if t and t not in STOP_WORDS}

    def match(self, query: str) -> Tuple[Optional[dict], float]:
        """Returns (matched_entry, confidence) or (None, 0.0) if low confidence."""
        if not self._faq_data:
            self._load()

        query_tokens = self._tokenize(query)
        lower_query = query.lower().strip()

        # Direct acronym / keyword priority mappings
        exact_triggers = [
            (r"\blop\b", "FAQ-PAY-01"),
            (r"\bepf\b", "FAQ-PAY-03"),
            (r"\beps\b", "FAQ-PAY-04"),
            (r"\bpf\b", "FAQ-PAY-02"),
            (r"\btds\b", "FAQ-PAY-05"),
            (r"\barrears\b", "FAQ-PAY-06"),
            (r"\bgratuity\b", "FAQ-PAY-07"),
            (r"\bencashment\b", "FAQ-PAY-08"),
            (r"\bnotice recovery\b", "FAQ-PAY-09"),
            (r"\bpredict\b", "FAQ-PAY-11"),
            (r"\bbank deposit\b|\bbank credit\b", "FAQ-PAY-12"),
            (r"\bincomplete\b", "FAQ-PAY-13"),
            (r"\bcannot explain\b", "FAQ-PAY-14"),
            (r"\btax regime\b", "FAQ-PAY-15"),
            (r"\bquery process\b|\bquery workflow\b", "FAQ-PAY-17"),
            (r"\bquery statuses\b|\bquery status\b", "FAQ-PAY-18"),
            (r"\bwithout.*confirmation\b", "FAQ-PAY-19"),
            (r"\bapproving.*payment\b", "FAQ-PAY-20"),
            (r"\bapprove.*payroll change\b", "FAQ-PAY-21"),
            (r"\brule not verified\b", "FAQ-PAY-24"),
            (r"\bdue date\b", "FAQ-PAY-25"),
            (r"\basset clearance\b", "FAQ-PAY-26"),
            (r"\bidentification numbers\b|\bpan\b", "FAQ-PAY-29"),
            (r"\bwhat is hcm one\b|\babout hcm one\b", "FAQ-PAY-30"),
        ]

        for pattern, faq_id in exact_triggers:
            if re.search(pattern, lower_query):
                for entry in self._faq_data:
                    if entry["id"] == faq_id:
                        return entry, 0.95

        best_entry = None
        best_score = 0.0

        for entry in self._faq_data:
            q_tokens = self._tokenize(entry["question"])
            if not q_tokens:
                continue

            intersection = query_tokens.intersection(q_tokens)
            if not intersection:
                continue

            # Jaccard overlap on question tokens
            union = query_tokens.union(q_tokens)
            score = len(intersection) / len(union) if union else 0.0

            # Boost if key question tokens are completely present
            subset_ratio = len(intersection) / len(q_tokens)
            combined = 0.5 * score + 0.5 * subset_ratio

            if combined > best_score:
                best_score = combined
                best_entry = entry

        # Threshold: require at least 0.35 confidence to prevent false positive matches
        if best_entry and best_score >= 0.35:
            return best_entry, round(best_score, 2)

        return None, 0.0


faq_matcher = FAQMatcher()
