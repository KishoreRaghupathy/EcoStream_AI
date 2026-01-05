from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ChatRequest(BaseModel):
    city: str
    question: str

class ChatResponse(BaseModel):
    answer: str
    data_used: List[str]
    confidence: str # "high", "medium", "low"
    sql_generated: Optional[str] = None
    execution_time_ms: Optional[float] = None
