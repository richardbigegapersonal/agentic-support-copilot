import re, hashlib, hmac, base64, os

PATTERNS = {
    "email": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    "phone": re.compile(r"\+?\d[\d -]{7,}\d"),
}

def redact(text: str) -> str:
    out = text
    for name, rx in PATTERNS.items():
        out = rx.sub(f"<REDACTED:{name}>", out)
    return out

def tokenize(value: str, secret: bytes, ctx: str="acc") -> str:
    msg = f"{ctx}:{value}".encode()
    digest = hmac.new(secret, msg, hashlib.sha256).digest()
    return "TOK_" + ctx + "_" + base64.urlsafe_b64encode(digest[:18]).decode().rstrip("=")

FORBIDDEN = ("BEGIN_TOOL", "api_key", "system prompt", "override", "ignore previous", "DROP TABLE", "DELETE FROM")
def sanitize_user(text: str) -> str:
    t = text
    for kw in FORBIDDEN:
        t = t.replace(kw, "<BLOCKED>")
    return t
