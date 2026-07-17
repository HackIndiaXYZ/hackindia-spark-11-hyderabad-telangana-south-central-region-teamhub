from app.agents.base_agent import BaseAgent


class ExplainerAgent(BaseAgent):
    name = "Explainer"
    description = "Explains code in simple terms"
    icon = "BookOpen"
    color = "#14b8a6"
    system_prompt = "You are a technical educator. Explain complex code concepts in simple, easy-to-understand language."
