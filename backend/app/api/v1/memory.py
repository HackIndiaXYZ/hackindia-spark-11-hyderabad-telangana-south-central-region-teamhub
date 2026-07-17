from fastapi import APIRouter, Query, HTTPException
from app.services.memory_service import memory_service

router = APIRouter()


@router.post("")
async def save_memory(key: str, value: str, user_id: str = Query("default"), agent_name: str | None = Query(None)):
    result = await memory_service.save(user_id, key, value, agent_name)
    return result


@router.get("/search")
async def search_memory(query: str, user_id: str = Query("default"), top_k: int = Query(5, ge=1, le=20)):
    results = await memory_service.search(query, top_k, user_id)
    return results


@router.get("/recent")
async def recent_memories(user_id: str = Query("default"), limit: int = Query(10, ge=1, le=50)):
    results = await memory_service.get_recent(user_id, limit)
    return results


@router.get("/context")
async def memory_context(request: str, user_id: str = Query("default")):
    context = await memory_service.get_context(request, user_id)
    return {"context": context, "request": request}


@router.delete("/{key}")
async def delete_memory(key: str):
    success = await memory_service.delete(key)
    if not success:
        raise HTTPException(404, f"Memory with key '{key}' not found")
    return {"deleted": True}
