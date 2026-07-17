from app.agents.base_agent import BaseAgent


class CoderAgent(BaseAgent):
    name = "Coder"
    description = "Writes and edits code"
    icon = "Code2"
    color = "#22c55e"
    system_prompt = "You are an expert programmer. Write clean, efficient, well-documented code."
