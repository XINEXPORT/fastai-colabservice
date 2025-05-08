from typing import List, Tuple
from pydantic import BaseModel

class GPTSummaryRequest(BaseModel):
    question: str
    chunks: List[str]
    history: List[Tuple[str, str]] 

class GPTSummaryResponse(BaseModel):
    answer: str
