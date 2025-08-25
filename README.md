# Agentic AI Customer Support Copilot (Hands-on)

This project supports my book available at: https://a.co/d/gHgzKdS
<img width="1077" height="451" alt="Screen Shot 2025-08-24 at 23 51 07" src="https://github.com/user-attachments/assets/8b460b96-d128-422a-96aa-71dd7e2b035f" />


A runnable skeleton for an **agentic, finance-grade support assistant**:
- **Tools:** SQLite account/transactions lookup + TF‑IDF KB search
- **Agent loop:** router → plan (max 2 tool steps) → execute → compose
- **Guardrails:** PII redaction, prompt sanitization, schema validation via Pydantic
- **Observability:** correlation IDs, trace returned in API response
- **Citations:** KB file names returned to ground responses

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run API
uvicorn src.app:app --host 0.0.0.0 --port 8081
```

### Sample calls

**Unknown charge (with account context):**
```bash
curl -s -X POST http://localhost:8081/ask -H "Content-Type: application/json" -d '{
  "question":"I see an unknown $125 charge from ONLINE SHOP — what should I do?",
  "account_id":"ACC1000"
}' | jq
```

**Policy question (no account context):**
```bash
curl -s -X POST http://localhost:8081/ask -H "Content-Type: application/json" -d '{
  "question":"What is the dispute window for unauthorized card charges?"
}' | jq
```

## Emphasize:
- **Routing:** cheap heuristics/SLM for intent; escalate complexity only when needed.
- **Tooling:** parameterized SQL, TF‑IDF grounding, **citations**.
- **Budgets:** max tool steps ensure predictable latency.
- **Safety:** redact PII; sanitize prompts; never log raw PII.

## Project structure
```
agentic-support-copilot/
├─ data/
│  ├─ bank.db           # SQLite with accounts + transactions (seeded)
│  └─ kb/               # knowledge base markdown files
├─ src/
│  ├─ app.py            # FastAPI service (/ask, /healthz)
│  ├─ agent.py          # plan/execute/compose loop with budgets
│  ├─ tools.py          # kb_search (TF‑IDF), account_summary, sql_recent_transactions
│  ├─ router.py         # keyword-based intent classifier
│  ├─ security.py       # redact + sanitize
│  ├─ schemas.py        # Pydantic request/response
│  └─ __init__.py
├─ tests/
│  └─ test_agent.py     # basic guardrail tests
├─ artifacts/
└─ requirements.txt
```

## Next steps: Extending (tie to Chapters 5–8) in the Ace Machine Learning and Artificial Intelligence Interview book
- Swap TF‑IDF for embeddings + reranker; add metadata prefilter.
- Add JSON schema output validation for agent answers.
- Persist traces to an immutable audit log (S3) with correlation IDs.
- Introduce **step/latency budgets** and cache KB results per intent.
