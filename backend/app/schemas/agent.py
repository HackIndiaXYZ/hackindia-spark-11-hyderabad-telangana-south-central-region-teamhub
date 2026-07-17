from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class AgentRequest(BaseModel):
    request: str
    context: Dict[str, Any] = {}
    agents: Optional[List[str]] = None

class AgentResponse(BaseModel):
    agent_name: str
    status: str
    output: Any
    error: Optional[str] = None
    execution_time_ms: int = 0
    tokens_used: int = 0

class OrchestratorResponse(BaseModel):
    request: str
    agents_used: List[str]
    execution_plan: List[Dict[str, Any]]
    results: List[AgentResponse]
    merged_output: Dict[str, Any]
    total_time_ms: int
