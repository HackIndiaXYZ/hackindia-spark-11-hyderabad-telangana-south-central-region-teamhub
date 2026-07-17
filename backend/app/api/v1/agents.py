from fastapi import APIRouter
from app.schemas.agent import AgentRequest, AgentResponse, OrchestratorResponse
from app.services.agent_orchestrator import agent_orchestrator

router = APIRouter()

@router.post("/execute", response_model=AgentResponse)
async def execute_agent(data: AgentRequest):
    agent_key = (data.agents or ["coder"])[0]
    result = await agent_orchestrator.execute_single(data.request, data.context, agent_key)
    return result

@router.post("/orchestrate", response_model=OrchestratorResponse)
async def orchestrate_agents(data: AgentRequest):
    result = await agent_orchestrator.orchestrate(data.request, data.context, data.agents)
    return result

@router.get("/list")
async def list_agents():
    from app.services.agent_orchestrator import AGENTS
    return [{"key": k, **v} for k, v in AGENTS.items()]
