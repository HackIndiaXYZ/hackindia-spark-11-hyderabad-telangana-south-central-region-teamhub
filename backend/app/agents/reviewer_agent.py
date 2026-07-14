from app.agents.base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    name = "Reviewer"
    description = "Reviews code for quality"
    icon = "Search"
    color = "#a855f7"
    system_prompt = "You are a code reviewer. Review code for quality, security, and best practices."
