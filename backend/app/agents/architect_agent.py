from app.agents.base_agent import BaseAgent


class ArchitectAgent(BaseAgent):
    name = "Architect"
    description = "Designs software architecture"
    icon = "Building2"
    color = "#3b82f6"
    system_prompt = "You are a software architect. Design scalable, maintainable system architectures."
