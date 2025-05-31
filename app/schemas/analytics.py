from pydantic import BaseModel
from typing import List, Dict, Optional

class CallMetrics(BaseModel):
    total_calls: int
    inbound_calls: int
    outbound_calls: int
    average_duration: float
    completed_calls: int
    failed_calls: int

class IntentSummary(BaseModel):
    intent: str
    count: int
    percentage: float

class CallAnalytics(BaseModel):
    metrics: CallMetrics
    intents: List[IntentSummary]
    call_volume_by_day: Dict[str, int]
    call_duration_by_intent: Dict[str, float]