import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

class TestHealth:
    async def test_health(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    async def test_root(self, client: AsyncClient):
        resp = await client.get("/")
        assert resp.status_code == 200
        assert resp.json()["name"] == "CODEBUDDY API"

class TestProjects:
    async def test_create_project(self, client: AsyncClient):
        resp = await client.post("/api/v1/projects?user_id=default", json={"name": "Test Project", "description": "A test", "language": "python"})
        assert resp.status_code == 201
        d = resp.json()
        assert d["name"] == "Test Project"
        assert d["language"] == "python"
        assert d["id"] is not None

    async def test_list_projects(self, client: AsyncClient):
        await client.post("/api/v1/projects?user_id=default", json={"name": "P1"})
        await client.post("/api/v1/projects?user_id=default", json={"name": "P2"})
        resp = await client.get("/api/v1/projects?user_id=default")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    async def test_get_project(self, client: AsyncClient):
        create = await client.post("/api/v1/projects?user_id=default", json={"name": "My Project"})
        pid = create.json()["id"]
        resp = await client.get(f"/api/v1/projects/{pid}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "My Project"

    async def test_get_project_404(self, client: AsyncClient):
        resp = await client.get("/api/v1/projects/nonexistent")
        assert resp.status_code == 404

    async def test_update_project(self, client: AsyncClient):
        create = await client.post("/api/v1/projects?user_id=default", json={"name": "Old Name"})
        pid = create.json()["id"]
        resp = await client.put(f"/api/v1/projects/{pid}", json={"name": "New Name", "language": "javascript"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"
        assert resp.json()["language"] == "javascript"

    async def test_delete_project(self, client: AsyncClient):
        create = await client.post("/api/v1/projects?user_id=default", json={"name": "Delete Me"})
        pid = create.json()["id"]
        resp = await client.delete(f"/api/v1/projects/{pid}")
        assert resp.status_code == 204
        resp = await client.get(f"/api/v1/projects/{pid}")
        assert resp.status_code == 404

    async def test_project_stats(self, client: AsyncClient):
        create = await client.post("/api/v1/projects?user_id=default", json={"name": "Stats"})
        pid = create.json()["id"]
        resp = await client.get(f"/api/v1/projects/{pid}/stats")
        assert resp.status_code == 200
        d = resp.json()
        assert d["name"] == "Stats"
        assert d["file_count"] == 0

class TestFiles:
    async def test_create_file(self, client: AsyncClient):
        proj = await client.post("/api/v1/projects?user_id=default", json={"name": "Files Project"})
        pid = proj.json()["id"]
        resp = await client.post(f"/api/v1/files/{pid}", json={"path": "src/main.py", "content": "print('hello')", "language": "python"})
        assert resp.status_code == 201
        assert resp.json()["path"] == "src/main.py"

    async def test_list_files(self, client: AsyncClient):
        proj = await client.post("/api/v1/projects?user_id=default", json={"name": "List Files"})
        pid = proj.json()["id"]
        await client.post(f"/api/v1/files/{pid}", json={"path": "f1.py"})
        await client.post(f"/api/v1/files/{pid}", json={"path": "f2.py"})
        resp = await client.get(f"/api/v1/files/{pid}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_update_file(self, client: AsyncClient):
        proj = await client.post("/api/v1/projects?user_id=default", json={"name": "Update File"})
        pid = proj.json()["id"]
        create = await client.post(f"/api/v1/files/{pid}", json={"path": "main.py", "content": "old"})
        fid = create.json()["id"]
        resp = await client.put(f"/api/v1/files/{pid}/{fid}", json={"content": "new content"})
        assert resp.status_code == 200
        assert resp.json()["content"] == "new content"

    async def test_delete_file(self, client: AsyncClient):
        proj = await client.post("/api/v1/projects?user_id=default", json={"name": "Delete File"})
        pid = proj.json()["id"]
        create = await client.post(f"/api/v1/files/{pid}", json={"path": "temp.txt"})
        fid = create.json()["id"]
        resp = await client.delete(f"/api/v1/files/{pid}/{fid}")
        assert resp.status_code == 204

class TestChat:
    async def test_send_message(self, client: AsyncClient):
        resp = await client.post("/api/v1/chat?user_id=default", json={"message": "Hello", "stream": False})
        assert resp.status_code == 200
        d = resp.json()
        assert d["chat_id"] is not None
        assert d["message"] is not None

    async def test_list_chats(self, client: AsyncClient):
        await client.post("/api/v1/chat?user_id=default", json={"message": "Chat 1"})
        await client.post("/api/v1/chat?user_id=default", json={"message": "Chat 2"})
        resp = await client.get("/api/v1/chat?user_id=default")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_chat(self, client: AsyncClient):
        create = await client.post("/api/v1/chat?user_id=default", json={"message": "Test chat"})
        cid = create.json()["chat_id"]
        resp = await client.get(f"/api/v1/chat/{cid}")
        assert resp.status_code == 200
        assert len(resp.json()["messages"]) >= 2

    async def test_delete_chat(self, client: AsyncClient):
        create = await client.post("/api/v1/chat?user_id=default", json={"message": "Delete me"})
        cid = create.json()["chat_id"]
        resp = await client.delete(f"/api/v1/chat/{cid}")
        assert resp.status_code == 204

    async def test_chat_with_existing_id(self, client: AsyncClient):
        create = await client.post("/api/v1/chat?user_id=default", json={"message": "First"})
        cid = create.json()["chat_id"]
        resp = await client.post("/api/v1/chat?user_id=default", json={"message": "Second", "chat_id": cid})
        assert resp.status_code == 200
        assert resp.json()["chat_id"] == cid

class TestAgents:
    async def test_list_agents(self, client: AsyncClient):
        resp = await client.get("/api/v1/agents/list")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 8
        keys = [a["key"] for a in data]
        assert "coder" in keys
        assert "debugger" in keys
        assert "architect" in keys
        assert "reviewer" in keys
        assert "documenter" in keys
        assert "tester" in keys
        assert "refactorer" in keys
        assert "explainer" in keys

    @pytest.mark.parametrize("agent_key", ["coder", "debugger", "architect", "reviewer", "documenter", "tester", "refactorer", "explainer"])
    async def test_each_agent_executes(self, client: AsyncClient, agent_key: str):
        resp = await client.post("/api/v1/agents/execute", json={"request": f"Act as {agent_key}", "agents": [agent_key]})
        assert resp.status_code == 200
        d = resp.json()
        assert d["status"] == "success"
        assert d["agent_name"] == agent_key
        assert d["execution_time_ms"] >= 0
        assert d["output"] is not None

    async def test_orchestrate(self, client: AsyncClient):
        resp = await client.post("/api/v1/agents/orchestrate", json={"request": "Build a web app", "agents": ["architect", "coder", "reviewer"]})
        assert resp.status_code == 200
        d = resp.json()
        assert d["request"] == "Build a web app"
        assert len(d["agents_used"]) >= 3
        assert len(d["results"]) >= 3
        assert d["total_time_ms"] >= 0

    async def test_unknown_agent(self, client: AsyncClient):
        resp = await client.post("/api/v1/agents/execute", json={"request": "test", "agents": ["unknown"]})
        assert resp.status_code == 200
        assert resp.json()["status"] == "error"

class TestVisualization:
    async def test_project_viz(self, client: AsyncClient):
        proj = await client.post("/api/v1/projects?user_id=default", json={"name": "Viz Project"})
        pid = proj.json()["id"]
        resp = await client.get(f"/api/v1/visualization/project/{pid}")
        assert resp.status_code == 200
        d = resp.json()
        assert d["project"]["name"] == "Viz Project"
        assert d["file_count"] == 0

    async def test_user_activity(self, client: AsyncClient):
        resp = await client.get("/api/v1/visualization/activity/default?days=7")
        assert resp.status_code == 200
        d = resp.json()
        assert d["period_days"] == 7
        assert "projects" in d
        assert "chats" in d
        assert "messages" in d
