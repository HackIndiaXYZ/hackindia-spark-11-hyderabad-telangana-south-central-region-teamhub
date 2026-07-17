from app.agents.base_agent import BaseAgent


class RefactorerAgent(BaseAgent):
    name = "Refactorer"
    description = "Optimizes and restructures code"
    icon = "RefreshCw"
    color = "#ec4899"
    system_prompt = "You are a code optimization expert. Refactor code for better performance and readability."
