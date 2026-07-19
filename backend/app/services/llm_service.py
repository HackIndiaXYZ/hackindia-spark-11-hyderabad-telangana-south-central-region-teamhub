import json
import logging
import time
from typing import Any, AsyncGenerator
import httpx
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field
from app.core.config import settings

logger = logging.getLogger(__name__)

MOCK_RESPONSES = {
    "coder": "def hello_world():\n    print(\"Hello, World!\")\n\nif __name__ == \"__main__\":\n    hello_world()",
    "debugger": "**Bug Analysis:**\nThe issue is a null pointer exception on line 42. The variable `data` is not checked before accessing its properties.\n\n**Fix:**\nAdd a null check before the access:\n```python\nif data is not None:\n    return data.value\nreturn None\n```",
    "architect": "## System Architecture\n\n### Components:\n1. **API Gateway** - Entry point for all client requests\n2. **Auth Service** - Handles authentication and authorization\n3. **Core Engine** - Business logic processing\n4. **Data Layer** - Database and caching\n5. **Message Queue** - Async task processing\n\n### Data Flow:\nClient -> API Gateway -> Auth -> Core Engine -> Data Layer",
    "reviewer": "## Code Review Report\n\n### Issues Found:\n1. **Security**: SQL injection vulnerability in user input handling\n2. **Performance**: N+1 query in the list endpoint\n3. **Style**: Inconsistent naming conventions\n\n### Recommendations:\n- Use parameterized queries\n- Add eager loading for related models\n- Follow PEP 8 naming conventions",
    "documenter": "# API Documentation\n\n## Endpoints\n\n### `GET /api/users`\nReturns a list of all users.\n\n#### Parameters\n- `page` (int): Page number (default: 1)\n- `limit` (int): Items per page (default: 20)\n\n#### Response\n```json\n{\"users\": [], \"total\": 0, \"page\": 1}\n```",
    "tester": "import pytest\nfrom app import create_app\n\n@pytest.fixture\ndef client():\n    app = create_app()\n    return app.test_client()\n\ndef test_health_endpoint(client):\n    response = client.get(\"/health\")\n    assert response.status_code == 200\n    assert response.json[\"status\"] == \"healthy\"\n\ndef test_create_user(client):\n    response = client.post(\"/api/users\", json={\"name\": \"Test\"})\n    assert response.status_code == 201",
    "refactorer": "**Refactored Code:**\n\nOriginal issues:\n- Deeply nested conditionals\n- Duplicate logic\n- Magic numbers\n\n```python\n# Before\ndef calculate(price, discount, tax):\n    if discount:\n        price = price - (price * discount / 100)\n    if tax:\n        price = price + (price * tax / 100)\n    return price\n\n# After\nDISCOUNT_RATE = 0.1\nTAX_RATE = 0.08\n\ndef apply_discount(price: float) -> float:\n    return price * (1 - DISCOUNT_RATE)\n\ndef apply_tax(price: float) -> float:\n    return price * (1 + TAX_RATE)\n```",
    "explainer": "## Code Explanation\n\nThis function implements a **binary search algorithm**:\n\n1. **Input**: A sorted array and a target value\n2. **Process**: Repeatedly divides the search range in half\n3. **Output**: The index of the target, or -1 if not found\n\n**Time Complexity**: O(log n)\n**Space Complexity**: O(1)\n\nThink of it like looking up a word in a dictionary - you open to the middle, then decide whether to go left or right based on the letter.",
}


class FallbackChatModel(BaseChatModel):
    model_name: str = Field(default="fallback")

    def _generate(self, messages: list, stop: list[str] | None = None, run_manager: Any = None, **kwargs: Any) -> ChatResult:
        content = self._get_fallback_content(messages)
        generation = ChatGeneration(message=HumanMessage(content=content))
        return ChatResult(generations=[generation])

    async def _agenerate(self, messages: list, stop: list[str] | None = None, run_manager: Any = None, **kwargs: Any) -> ChatResult:
        return self._generate(messages, stop, run_manager, **kwargs)

    def _get_fallback_content(self, messages: list) -> str:
        for msg in reversed(messages):
            if isinstance(msg, SystemMessage):
                content = msg.content.lower()
                for key in MOCK_RESPONSES:
                    if key in content:
                        return MOCK_RESPONSES[key]
        return MOCK_RESPONSES["coder"]

    @property
    def _llm_type(self) -> str:
        return "fallback"


class OllamaChatModel(BaseChatModel):
    model_name: str = Field(default="llama3")
    base_url: str = Field(default="http://localhost:11434")

    def _generate(self, messages: list, stop: list[str] | None = None, run_manager: Any = None, **kwargs: Any) -> ChatResult:
        raise NotImplementedError("Synchronous generation not supported, use async")

    async def _agenerate(self, messages: list, stop: list[str] | None = None, run_manager: Any = None, **kwargs: Any) -> ChatResult:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code != 200:
                    raise ConnectionError(f"Ollama tags returned {resp.status_code}")
        except Exception as e:
            logger.warning(f"Ollama not available ({e}), using fallback")
            return FallbackChatModel()._generate(messages, stop, run_manager, **kwargs)
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": self.model_name,
                "messages": [{"role": self._to_role(m), "content": m.content} for m in messages],
                "stream": False,
            }
            logger.info(f"Calling Ollama model={self.model_name} at {self.base_url}")
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data["message"]["content"]
                generation = ChatGeneration(message=HumanMessage(content=content))
                return ChatResult(generations=[generation])
        except Exception as e:
            logger.warning(f"Ollama call failed ({e}), using fallback")
            return FallbackChatModel()._generate(messages, stop, run_manager, **kwargs)

    def _to_role(self, message: Any) -> str:
        msg_type = type(message).__name__
        if "System" in msg_type:
            return "system"
        if "Human" in msg_type:
            return "user"
        if "AI" in msg_type:
            return "assistant"
        return "user"

    @property
    def _llm_type(self) -> str:
        return "ollama"


class OpenAIChatModel(BaseChatModel):
    model_name: str = Field(default="gpt-4")
    openai_api_key: str = Field(default="")

    def _generate(self, messages: list, stop: list[str] | None = None, run_manager: Any = None, **kwargs: Any) -> ChatResult:
        raise NotImplementedError("Synchronous generation not supported, use async")

    async def _agenerate(self, messages: list, stop: list[str] | None = None, run_manager: Any = None, **kwargs: Any) -> ChatResult:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model_name,
            "messages": [{"role": self._to_role(m), "content": m.content} for m in messages],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            generation = ChatGeneration(message=HumanMessage(content=content))
            return ChatResult(generations=[generation])

    def _to_role(self, message: Any) -> str:
        msg_type = type(message).__name__
        if "System" in msg_type:
            return "system"
        if "Human" in msg_type:
            return "user"
        if "AI" in msg_type:
            return "assistant"
        return "user"

    @property
    def _llm_type(self) -> str:
        return "openai"


class LLMService:
    def __init__(self):
        self.provider = settings.MODEL_PROVIDER
        self.model = settings.MODEL_NAME
        self.ollama_base = settings.OLLAMA_BASE_URL
        self._chat_model: BaseChatModel | None = None

    def get_chat_model(self) -> BaseChatModel:
        if self._chat_model is not None:
            return self._chat_model
        if self.provider == "ollama":
            self._chat_model = OllamaChatModel(model_name=self.model, base_url=self.ollama_base)
        elif self.provider == "openai":
            self._chat_model = OpenAIChatModel(model_name=self.model, openai_api_key=settings.OPENAI_API_KEY or "")
        else:
            self._chat_model = FallbackChatModel()
        return self._chat_model

    async def _check_ollama(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                resp = await client.get(f"{self.ollama_base}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def _call_ollama(self, messages: list[dict], stream: bool = False) -> dict | AsyncGenerator[str, None]:
        url = f"{self.ollama_base}/api/chat"
        payload = {"model": self.model, "messages": messages, "stream": stream, "keep_alive": "5m"}
        if stream:
            return self._stream_ollama(url, payload)
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {"content": data["message"]["content"], "tokens_used": data.get("eval_count", 0)}

    async def _stream_ollama(self, url: str, payload: dict) -> AsyncGenerator[str, None]:
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream("POST", url, json=payload) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if line:
                            chunk = json.loads(line)
                            if "message" in chunk and "content" in chunk["message"]:
                                yield chunk["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            yield f"\n[Streaming error: {e}]"

    async def _call_openai(self, messages: list[dict], stream: bool = False) -> dict | AsyncGenerator[str, None]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": messages, "stream": stream}
        if stream:
            return self._stream_openai(url, headers, payload)
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return {"content": data["choices"][0]["message"]["content"], "tokens_used": data["usage"]["total_tokens"]}

    async def _stream_openai(self, url: str, headers: dict, payload: dict) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        chunk = json.loads(line[6:])
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]

    def _fallback(self, messages: list[dict], agent_name: str = "") -> dict:
        content = MOCK_RESPONSES.get(agent_name, MOCK_RESPONSES["coder"])
        return {"content": content, "tokens_used": 50}

    async def _call_ollama_generate(self, messages: list[dict]) -> dict:
        url = f"{self.ollama_base}/api/generate"
        prompt = messages[-1]["content"] if messages else ""
        payload = {"model": self.model, "prompt": prompt, "stream": False, "keep_alive": "5m"}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {"content": data.get("response", ""), "tokens_used": data.get("eval_count", 0)}

    async def chat(self, messages: list[dict], stream: bool = False) -> dict | AsyncGenerator[str, None]:
        if self.provider == "ollama":
            if not await self._check_ollama():
                logger.warning("Ollama not available, using fallback")
                return self._fallback(messages)
            try:
                return await self._call_ollama(messages, stream)
            except Exception as e:
                logger.warning(f"Ollama chat endpoint failed ({e}), trying generate endpoint")
                try:
                    return await self._call_ollama_generate(messages)
                except Exception as e2:
                    logger.warning(f"Ollama generate also failed ({e2}), using fallback")
                    return self._fallback(messages)
        elif self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured")
            return await self._call_openai(messages, stream)
        else:
            last_msg = messages[-1]["content"].lower() if messages else ""
            agent_name = ""
            for key in MOCK_RESPONSES:
                if key in last_msg:
                    agent_name = key
                    break
            return self._fallback(messages, agent_name)

    async def chat_with_agents(self, messages: list[dict], agent_name: str, system_prompt: str | None = None) -> dict:
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.extend(messages)
        start = time.monotonic()
        result = await self.chat(msgs, stream=False)
        elapsed = int((time.monotonic() - start) * 1000)
        if isinstance(result, dict):
            return {"content": result["content"], "tokens_used": result.get("tokens_used", 0), "execution_time_ms": elapsed, "agent_name": agent_name}
        content = self._fallback(msgs, agent_name).get("content", "")
        logger.warning(f"Unexpected result type from chat for agent {agent_name}, using fallback response")
        return {"content": content, "tokens_used": 0, "execution_time_ms": elapsed, "agent_name": agent_name}


llm_service = LLMService()
