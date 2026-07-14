"""Sample test examples for CODEBUDDY - copy/paste into your own test files."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ──────────────────────────────────────────────
# 1. API endpoint tests (health, CRUD)
# ──────────────────────────────────────────────

class TestApiBasics:
    async def test_health_check(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    async def test_create_and_get_project(self, client: AsyncClient):
        """Create a project, then fetch it by ID."""
        create = await client.post(
            "/api/v1/projects?user_id=default",
            json={"name": "Demo", "description": "testing", "language": "python"},
        )
        assert create.status_code == 201
        pid = create.json()["id"]

        get = await client.get(f"/api/v1/projects/{pid}")
        assert get.status_code == 200
        assert get.json()["name"] == "Demo"

    async def test_chat_roundtrip(self, client: AsyncClient):
        """Send a chat message and verify the response."""
        resp = await client.post(
            "/api/v1/chat?user_id=default",
            json={"message": "Hello world", "stream": False},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["chat_id"] is not None
        assert len(data["message"]) > 0


# ──────────────────────────────────────────────
# 2. Agent execution tests
# ──────────────────────────────────────────────

class TestAgents:
    async def test_list_all_agents(self, client: AsyncClient):
        resp = await client.get("/api/v1/agents/list")
        assert resp.status_code == 200
        agents = resp.json()
        assert len(agents) >= 8
        keys = {a["key"] for a in agents}
        assert keys == {"coder", "debugger", "architect", "reviewer",
                         "documenter", "tester", "refactorer", "explainer"}

    @pytest.mark.parametrize("agent", ["coder", "debugger", "tester"])
    async def test_run_single_agent(self, client: AsyncClient, agent: str):
        resp = await client.post(
            "/api/v1/agents/execute",
            json={"request": f"Write a Python function", "agents": [agent]},
        )
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["agent_name"] == agent
        assert d["execution_time_ms"] >= 0
        assert len(d["output"]) > 0

    async def test_orchestrate_all_agents(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/agents/orchestrate",
            json={"request": "Build a calculator app"},
        )
        assert resp.status_code == 200
        d = resp.json()
        assert len(d["agents_used"]) == 8
        assert len(d["results"]) == 8

    async def test_unknown_agent_returns_error(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/agents/execute",
            json={"request": "hi", "agents": ["nonexistent"]},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "error"


# ──────────────────────────────────────────────
# 3. Memory system tests
# ──────────────────────────────────────────────

class TestMemory:
    async def test_save_and_search_memory(self, client: AsyncClient):
        # Save a memory
        save = await client.post(
            "/api/v1/memory",
            params={"key": "mykey", "value": "Python is great", "user_id": "u1", "agent_name": "coder"},
        )
        assert save.status_code == 200

        # Search for it
        search = await client.get(
            "/api/v1/memory/search",
            params={"query": "Python", "user_id": "u1"},
        )
        assert search.status_code == 200
        results = search.json()
        assert any(r["key"] == "mykey" for r in results)

    async def test_memory_context(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/memory/context",
            params={"request": "Python coding", "user_id": "u1"},
        )
        assert resp.status_code == 200
        assert isinstance(resp.json()["context"], str)

    async def test_recent_memories(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/memory/recent",
            params={"user_id": "u1", "limit": 5},
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


# ──────────────────────────────────────────────
# 4. Vector store unit tests (no HTTP needed)
# ──────────────────────────────────────────────

from app.services.memory_service import VectorMemoryStore

class TestVectorStore:
    def setup_method(self):
        self.store = VectorMemoryStore(dimension=64)

    def test_add_and_search(self):
        self.store.add("k1", "Python programming", {"type": "lang"})
        self.store.add("k2", "FastAPI web framework", {"type": "framework"})
        results = self.store.search("Python code", top_k=1)
        assert len(results) == 1
        assert results[0]["key"] == "k1"

    def test_similarity_scoring(self):
        self.store.add("a", "hello world")
        self.store.add("b", "goodbye world")
        results = self.store.search("hello", top_k=2)
        assert len(results) == 2
        assert results[0]["score"] >= results[1]["score"]

    def test_remove_and_clear(self):
        self.store.add("x", "content")
        assert self.store.remove("x") is True
        assert self.store.remove("x") is False
        self.store.add("y", "content")
        self.store.clear()
        assert self.store.search("anything") == []


# ──────────────────────────────────────────────
# 5. Project + file workflow test
# ──────────────────────────────────────────────

class TestWorkflow:
    async def test_full_project_workflow(self, client: AsyncClient):
        # Create project
        p = await client.post("/api/v1/projects?user_id=default", json={"name": "Workflow"})
        pid = p.json()["id"]

        # Create files
        f1 = await client.post(f"/api/v1/files/{pid}", json={"path": "main.py", "content": "print(1)", "language": "python"})
        f2 = await client.post(f"/api/v1/files/{pid}", json={"path": "utils.py", "content": "def foo(): pass", "language": "python"})
        assert f1.status_code == 201
        assert f2.status_code == 201

        # List files
        ls = await client.get(f"/api/v1/files/{pid}")
        assert len(ls.json()) == 2

        # Update file
        fid = f1.json()["id"]
        upd = await client.put(f"/api/v1/files/{pid}/{fid}", json={"content": "print(2)"})
        assert upd.json()["content"] == "print(2)"

        # Delete file
        del_resp = await client.delete(f"/api/v1/files/{pid}/{fid}")
        assert del_resp.status_code == 204

        # Project stats
        stats = await client.get(f"/api/v1/projects/{pid}/stats")
        assert stats.json()["file_count"] == 1

        # Delete project
        await client.delete(f"/api/v1/projects/{pid}")
        get = await client.get(f"/api/v1/projects/{pid}")
        assert get.status_code == 404


# ──────────────────────────────────────────────
# 6. Visualization tests
# ──────────────────────────────────────────────

class TestVisualization:
    async def test_project_viz(self, client: AsyncClient):
        p = await client.post("/api/v1/projects?user_id=default", json={"name": "Viz"})
        pid = p.json()["id"]
        resp = await client.get(f"/api/v1/visualization/project/{pid}")
        assert resp.status_code == 200
        assert resp.json()["project"]["name"] == "Viz"

    async def test_user_activity(self, client: AsyncClient):
        resp = await client.get("/api/v1/visualization/activity/default?days=7")
        assert resp.status_code == 200
        assert resp.json()["period_days"] == 7


# ──────────────────────────────────────────────
# 7. Frontend component test example (Vitest)
#    Run with: npx vitest run
# ──────────────────────────────────────────────

"""
// File: frontend/src/components/__tests__/MemoryPanel.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import MemoryPanel from '../MemoryPanel'

vi.mock('../../services/memory', () => ({
  memoryService: {
    getRecent: vi.fn().mockResolvedValue([
      { key: 'k1', text: 'Python memory', agent_name: 'coder', score: 0.95, created_at: '2026-01-01' },
    ]),
    search: vi.fn().mockResolvedValue([]),
    delete: vi.fn().mockResolvedValue(undefined),
  },
}))

describe('MemoryPanel', () => {
  it('renders recent memories', async () => {
    render(<MemoryPanel />)
    expect(await screen.findByText('Python memory')).toBeTruthy()
    expect(screen.getByText('coder')).toBeTruthy()
  })

  it('shows empty state when no memories', async () => {
    vi.mocked(memoryService.getRecent).mockResolvedValueOnce([])
    render(<MemoryPanel />)
    expect(await screen.findByText('No memories yet')).toBeTruthy()
  })
})
"""
