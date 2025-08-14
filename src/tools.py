from typing import Dict, Any, List, Tuple
from pathlib import Path
import sqlite3, json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DB_PATH = str(Path(__file__).resolve().parents[1] / "data" / "bank.db")
KB_DIR = Path(__file__).resolve().parents[1] / "data" / "kb"

# Build TF-IDF index on startup
DOCS: List[Tuple[str,str]] = []
for p in sorted(KB_DIR.glob("*.md")):
    DOCS.append((p.name, p.read_text()))
VECT = TfidfVectorizer(stop_words="english")
MATRIX = VECT.fit_transform([t for _,t in DOCS])

def kb_search(question: str, k: int = 3) -> List[Dict[str, Any]]:
    qv = VECT.transform([question])
    sims = cosine_similarity(qv, MATRIX)[0]
    top = sims.argsort()[::-1][:k]
    results = []
    for idx in top:
        fn, txt = DOCS[idx]
        results.append({"id": fn, "score": float(sims[idx]), "snippet": txt.splitlines()[:6]})
    return results

def sql_recent_transactions(account_id: str, limit: int = 10) -> Dict[str, Any]:
    # Parameterized query to avoid injection
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""SELECT ts, merchant, amount, city, mcc
                FROM transactions
                WHERE account_id = ?
                ORDER BY ts DESC
                LIMIT ?""", (account_id, int(limit)))
    rows = cur.fetchall()
    con.close()
    cols = ["ts","merchant","amount","city","mcc"]
    return {"rows": [dict(zip(cols, r)) for r in rows]}

def account_summary(account_id: str) -> Dict[str, Any]:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""SELECT account_id, customer_name, masked_card, balance, status
                FROM accounts WHERE account_id = ?""", (account_id,))
    row = cur.fetchone()
    con.close()
    if not row: return {}
    cols = ["account_id","customer_name","masked_card","balance","status"]
    return dict(zip(cols, row))
