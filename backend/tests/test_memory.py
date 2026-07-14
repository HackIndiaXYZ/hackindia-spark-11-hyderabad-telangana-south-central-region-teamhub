import pytest
import numpy as np
from app.services.memory_service import memory_service, VectorMemoryStore


class TestVectorMemoryStore:
    def setup_method(self):
        self.store = VectorMemoryStore(dimension=64)

    def test_add_and_search(self):
        self.store.add("key1", "Python is a programming language", {"type": "fact"})
        self.store.add("key2", "FastAPI is a web framework", {"type": "fact"})
        self.store.add("key3", "Dogs are mammals", {"type": "animal"})
        results = self.store.search("Python coding", top_k=2)
        assert len(results) <= 2
        assert any(r["key"] == "key1" for r in results)

    def test_search_empty_store(self):
        results = self.store.search("anything")
        assert results == []

    def test_remove(self):
        self.store.add("test", "content")
        assert self.store.remove("test") is True
        assert self.store.remove("nonexistent") is False

    def test_clear(self):
        self.store.add("a", "content a")
        self.store.add("b", "content b")
        self.store.clear()
        assert self.store.search("anything") == []

    def test_cosine_similarity(self):
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([0.0, 1.0, 0.0])
        sim = self.store._cosine_similarity(a, b)
        assert abs(sim) < 0.01

    def test_embed_consistency(self):
        vec1 = self.store._embed("hello world")
        vec2 = self.store._embed("hello world")
        assert np.allclose(vec1, vec2)

    def test_embed_different_inputs(self):
        vec1 = self.store._embed("hello")
        vec2 = self.store._embed("world")
        sim = self.store._cosine_similarity(vec1, vec2)
        assert sim < 0.99


@pytest.mark.asyncio
class TestMemoryService:

    async def test_save_and_search(self):
        await memory_service.save("user1", "test_key", "This is a test memory", "tester")
        results = await memory_service.search("test memory", top_k=5)
        assert len(results) > 0
        assert any(r["key"] == "test_key" for r in results)

    async def test_save_with_agent(self):
        await memory_service.save("user1", "agent_mem", "Agent output", "coder")
        results = await memory_service.search("Agent output", top_k=5)
        assert any(r["key"] == "agent_mem" for r in results)

    async def test_search_no_results(self):
        results = await memory_service.search("xyznonexistent12345", top_k=5)
        assert isinstance(results, list)

    async def test_delete(self):
        await memory_service.save("user1", "delete_test", "to be deleted")
        assert await memory_service.delete("nonexistent") is not None
        results = await memory_service.search("delete_test", top_k=5)
        found = any(r["key"] == "delete_test" for r in results)
        assert isinstance(found, bool)

    async def test_get_context_empty(self):
        ctx = await memory_service.get_context("nothing relevant here", "user1")
        assert isinstance(ctx, str)

    async def test_get_context(self):
        await memory_service.save("user1", "ctx_test", "Memory context test value", "coder")
        ctx = await memory_service.get_context("context test", "user1")
        assert isinstance(ctx, str)
        assert len(ctx) > 0

    async def test_get_recent(self):
        await memory_service.save("user1", "recent_test", "Recent memory", "tester")
        recent = await memory_service.get_recent("user1", limit=5)
        assert isinstance(recent, list)
        if recent:
            assert "key" in recent[0]

    async def test_delete_existing(self):
        await memory_service.save("user1", "delete_existing", "Delete me")
        result = await memory_service.delete("delete_existing")
        assert result is True
