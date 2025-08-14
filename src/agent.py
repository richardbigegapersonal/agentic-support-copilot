from typing import Dict, Any, List
from . import tools
from .security import redact, sanitize_user

MAX_TOOL_STEPS = 2

def plan(question: str, intent: str, account_id: str|None) -> List[Dict[str, Any]]:
    steps: List[Dict[str,Any]] = []
    if intent == "txn_explain" and account_id:
        steps.append({"tool":"account_summary", "args":{"account_id": account_id}})
        steps.append({"tool":"sql_recent_transactions", "args":{"account_id": account_id, "limit": 10}})
    elif intent == "account_info" and account_id:
        steps.append({"tool":"account_summary", "args":{"account_id": account_id}})
    # Always consult KB to ground policy guidance
    steps.append({"tool":"kb_search", "args":{"question": question, "k": 2}})
    return steps[:MAX_TOOL_STEPS]

def execute(steps: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    out = []
    for i, s in enumerate(steps):
        name, args = s["tool"], s["args"]
        fn = getattr(tools, name, None)
        if not fn: break
        res = fn(**args)
        out.append({"step": i, "tool": name, "args": args, "out": res})
    return out

def compose(question: str, obs: List[Dict[str,Any]]) -> Dict[str,Any]:
    # Build a concise, grounded answer with minimal templating
    acct = None
    txns = None
    kb = []
    for o in obs:
        if o["tool"] == "account_summary":
            acct = o["out"]
        elif o["tool"] == "sql_recent_transactions":
            txns = o["out"]["rows"]
        elif o["tool"] == "kb_search":
            kb = o["out"]
    citations = [k["id"] for k in kb] if kb else []
    parts = []
    if acct:
        parts.append(f"Account {acct.get('account_id')} ({acct.get('masked_card')}) status: {acct.get('status')}, balance ${acct.get('balance'):.2f}.")
    if txns:
        recent = txns[:3]
        bullets = "; ".join([f"{t['ts']} {t['merchant']} ${t['amount']} ({t['city']})" for t in recent])
        parts.append(f"Recent activity: {bullets}. If any item is unfamiliar, consider card lock and dispute initiation.")
    if kb:
        parts.append(f"Policy guidance: see {[k['id'] for k in kb]}. Follow dispute window and provisional credit rules.")
    if not parts:
        parts.append("Here's what I found in our knowledge base. If you provide an account_id, I can check recent transactions.")
    answer = " ".join(parts)
    return {"answer": redact(answer), "citations": citations}
