from typing import Dict
import re

def classify_intent(q: str) -> str:
    t = q.lower()
    if any(k in t for k in ["charge", "unknown", "fraud", "dispute", "merchant"]):
        return "txn_explain"
    if any(k in t for k in ["balance", "card", "limit"]):
        return "account_info"
    if any(k in t for k in ["password", "login", "reset"]):
        return "kb_only"
    return "kb_first"
