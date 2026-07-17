from typing import Any
from app.services.llm_service import llm_service


class BaseAgent:
    name: str = ""
    description: str = ""
    icon: str = ""
    color: str = ""
    system_prompt: str = ""

    async def execute(self, request: str, context: dict[str, Any] | None = None) -> dict:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if context:
            ctx_str = "\n".join(f"{k}: {v}" for k, v in context.items()) if isinstance(context, dict) else str(context)
            messages.append({"role": "system", "content": f"Context:\n{ctx_str}"})
        messages.append({"role": "user", "content": request})
        try:
            result = await llm_service.chat(messages, stream=False)
            if isinstance(result, dict):
                return {"content": result.get("content", ""), "tokens_used": result.get("tokens_used", 0)}
            return {"content": str(result), "tokens_used": 0}
        except Exception as e:
            return {"content": f"Error: {e}", "tokens_used": 0}

    @property
    def metadata(self) -> dict:
        return {
            "key": type(self).__name__.replace("Agent", "").lower(),
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "system_prompt": self.system_prompt,
        }
