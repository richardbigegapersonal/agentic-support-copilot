from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional

class AskReq(BaseModel):
    question: str = Field(..., min_length=2, max_length=4000)
    account_id: Optional[str] = None

class AskResp(BaseModel):
    answer: str
    citations: List[str] = []
    trace: List[Dict[str, Any]] = []

class SQLTxn(BaseModel):
    account_id: str
    limit: int = 10

    @field_validator("limit")
    @classmethod
    def limit_range(cls, v):
        if v < 1 or v > 50:
            raise ValueError("limit must be 1..50")
        return v
