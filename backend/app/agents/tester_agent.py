from app.agents.base_agent import BaseAgent


class TesterAgent(BaseAgent):
    name = "Tester"
    description = "Writes and runs unit tests"
    icon = "TestTube"
    color = "#f97316"
    system_prompt = "You are a QA engineer. Write comprehensive unit tests and integration tests."
