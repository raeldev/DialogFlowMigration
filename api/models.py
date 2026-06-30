from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique conversational session identifier")
    user_message: str = Field(..., description="The user's input utterance")

class TurnInsight(BaseModel):
    sentiment_score: float = Field(..., description="Sentiment score from -1.0 to 1.0")
    sentiment_magnitude: float = Field(..., description="Sentiment magnitude >= 0.0")
    detected_topic: str = Field(..., description="Categorized customer topic")

class ChatResponse(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    reply: str = Field(..., description="Agent text response")
    latency_ms: float = Field(..., description="Turn execution latency in ms")
    tools_executed: List[str] = Field(default_factory=list, description="List of CRM tools executed during turn")
    insights: Optional[TurnInsight] = Field(None, description="Simulated CCAI Insights metadata")
