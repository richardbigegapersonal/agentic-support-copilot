from fastapi import FastAPI, Request
from uuid import uuid4
from .schemas import AskReq, AskResp
from .router import classify_intent
from .agent import plan, execute, compose
from .security import sanitize_user

app = FastAPI(title="Agentic Support Copilot")

@app.middleware("http")
async def corr_id_mw(req: Request, call_next):
    cid = req.headers.get("x-correlation-id", uuid4().hex)
    req.state.correlation_id = cid
    resp = await call_next(req)
    resp.headers["x-correlation-id"] = cid
    return resp

@app.get("/healthz")
def healthz(): return {"ok": True}

@app.post("/ask", response_model=AskResp)
def ask(payload: AskReq, request: Request):
    q = sanitize_user(payload.question)
    intent = classify_intent(q)
    steps = plan(q, intent, payload.account_id)
    trace = execute(steps)
    final = compose(q, trace)
    return AskResp(answer=final["answer"], citations=final["citations"], trace=trace)
