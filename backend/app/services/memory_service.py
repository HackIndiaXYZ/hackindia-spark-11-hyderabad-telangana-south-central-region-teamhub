import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Any
import numpy as np
from app.core.database import get_db, async_session_factory
from app.models.memory import Memory

logger = logging.getLogger(__name__)


class VectorMemoryStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._vectors: dict[str, np.ndarray] = {}
        self._texts: dict[str, str] = {}
        self._metadata: dict[str, dict] = {}

    def add(self, key: str, text: str, metadata: dict | None = None) -> str:
        vector = self._embed(text)
        self._vectors[key] = vector
        self._texts[key] = text
        self._metadata[key] = metadata or {}
        return key

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self._vectors:
            return []
        query_vec = self._embed(query)
        scores = []
        for key, vec in self._vectors.items():
            score = self._cosine_similarity(query_vec, vec)
            scores.append((score, key))
        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, key in scores[:top_k]:
            results.append({
                "key": key,
                "text": self._texts.get(key, ""),
                "metadata": self._metadata.get(key, {}),
                "score": float(score),
            })
        return results

    def remove(self, key: str) -> bool:
        if key in self._vectors:
            del self._vectors[key]
            del self._texts[key]
            del self._metadata[key]
            return True
        return False

    def clear(self):
        self._vectors.clear()
        self._texts.clear()
        self._metadata.clear()

    def _embed(self, text: str) -> np.ndarray:
        hash_bytes = hashlib.md5(text.encode()).digest()
        seed = int.from_bytes(hash_bytes[:4], "little")
        rng = np.random.RandomState(seed)
        vec = rng.randn(self.dimension)
        vec = vec / (np.linalg.norm(vec) + 1e-10)
        return vec

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))


memory_store = VectorMemoryStore()


class MemoryService:
    def __init__(self):
        self.store = memory_store

    async def save(self, user_id: str, key: str, value: str, agent_name: str | None = None, project_id: str | None = None) -> dict:
        mem_id = self.store.add(key, value, {"user_id": user_id, "agent_name": agent_name, "project_id": project_id})
        try:
            async with async_session_factory() as db:
                db_mem = Memory(
                    user_id=user_id,
                    project_id=project_id,
                    key=key,
                    value=value,
                    agent_name=agent_name,
                )
                db.add(db_mem)
                await db.commit()
        except Exception as e:
            logger.error(f"Database memory save failed: {e}")
        return {"id": mem_id, "key": key, "value": value, "agent_name": agent_name}

    async def search(self, query: str, top_k: int = 5, user_id: str | None = None) -> list[dict]:
        results = self.store.search(query, top_k)
        if user_id:
            results = [r for r in results if r.get("metadata", {}).get("user_id") == user_id]
        try:
            async with async_session_factory() as db:
                from sqlalchemy import select
                from sqlalchemy.ext.asyncio import AsyncSession
                result = await db.execute(
                    select(Memory).where(Memory.key == query).limit(top_k)
                )
                db_mems = result.scalars().all()
                for mem in db_mems:
                    key = mem.key
                    if not any(r["key"] == key for r in results):
                        results.append({
                            "key": key,
                            "text": mem.value,
                            "metadata": {
                                "user_id": mem.user_id,
                                "agent_name": mem.agent_name,
                                "project_id": mem.project_id,
                                "created_at": mem.created_at.isoformat() if mem.created_at else "",
                            },
                            "score": 0.5,
                        })
        except Exception as e:
            logger.error(f"Database memory search failed: {e}")
        return results[:top_k]

    async def get_recent(self, user_id: str, limit: int = 10) -> list[dict]:
        try:
            async with async_session_factory() as db:
                from sqlalchemy import select, desc
                result = await db.execute(
                    select(Memory)
                    .where(Memory.user_id == user_id)
                    .order_by(desc(Memory.created_at))
                    .limit(limit)
                )
                memories = result.scalars().all()
                return [
                    {
                        "key": m.key,
                        "value": m.value[:200],
                        "agent_name": m.agent_name,
                        "project_id": m.project_id,
                        "created_at": m.created_at.isoformat() if m.created_at else "",
                    }
                    for m in memories
                ]
        except Exception as e:
            logger.error(f"Failed to get recent memories: {e}")
            return []

    async def delete(self, key: str) -> bool:
        self.store.remove(key)
        try:
            async with async_session_factory() as db:
                from sqlalchemy import select
                result = await db.execute(select(Memory).where(Memory.key == key))
                mem = result.scalar_one_or_none()
                if mem:
                    await db.delete(mem)
                    await db.commit()
                    return True
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
        return False

    async def get_context(self, request: str, user_id: str | None = None) -> str:
        memories = await self.search(request, top_k=3, user_id=user_id)
        if not memories:
            return ""
        lines = []
        for mem in memories:
            agent = mem.get("metadata", {}).get("agent_name", "")
            text = mem.get("text", "")
            if agent and text:
                lines.append(f"[{agent}] {text[:300]}")
            elif text:
                lines.append(text[:300])
        return "\n".join(lines) if lines else ""


memory_service = MemoryService()
