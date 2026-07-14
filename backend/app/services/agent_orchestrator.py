import logging
from typing import Any
from app.agents import AGENT_REGISTRY
from app.agents.orchestrator import agent_orchestrator as langgraph_orchestrator

logger = logging.getLogger(__name__)

AGENTS = {
    key: {
        "name": cls.name,
        "description": cls.description,
        "icon": cls.icon,
        "color": cls.color,
        "system_prompt": cls.system_prompt,
    }
    for key, cls in AGENT_REGISTRY.items()
}


class AgentOrchestrator:
    async def execute_single(self, request: str, context: dict | None = None, agent_key: str = "coder") -> dict:
        return await langgraph_orchestrator.execute_single(request, context, agent_key)

    async def orchestrate(self, request: str, context: dict | None = None, agents: list[str] | None = None) -> dict:
        return await langgraph_orchestrator.orchestrate(request, context, agents)


agent_orchestrator = AgentOrchestrator()
