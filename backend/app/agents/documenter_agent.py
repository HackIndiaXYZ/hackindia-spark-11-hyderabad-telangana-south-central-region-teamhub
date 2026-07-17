from app.agents.base_agent import BaseAgent


class DocumenterAgent(BaseAgent):
    name = "Documenter"
    description = "Writes documentation"
    icon = "FileText"
    color = "#06b6d4"
    system_prompt = "You are a technical writer. Write clear, comprehensive documentation."
