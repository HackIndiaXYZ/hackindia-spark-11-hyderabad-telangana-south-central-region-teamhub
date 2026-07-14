from app.agents.base_agent import BaseAgent


class DebuggerAgent(BaseAgent):
    name = "Debugger"
    description = "Finds and fixes bugs"
    icon = "Bug"
    color = "#eab308"
    system_prompt = "You are an expert debugger. Analyze code carefully to find and fix bugs."
