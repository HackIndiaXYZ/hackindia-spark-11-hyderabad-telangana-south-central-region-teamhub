import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, AsyncGenerator
from app.core.database import get_db
from app.models.chat import Chat, Message
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistory, MessageSchema
from app.services.llm_service import llm_service
from app.services.memory_service import memory_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("")
async def send_message(data: ChatRequest, user_id: str = Query("default"), db: AsyncSession = Depends(get_db)):
    if data.stream:
        return await _stream_chat(data, user_id, db)
    return await _nonstream_chat(data, user_id, db)


async def _nonstream_chat(data: ChatRequest, user_id: str, db: AsyncSession) -> ChatResponse:
    if data.chat_id:
        result = await db.execute(select(Chat).where(Chat.id == data.chat_id, Chat.user_id == user_id))
        chat = result.scalar_one_or_none()
        if not chat:
            raise HTTPException(404, "Chat not found")
    else:
        chat = Chat(user_id=user_id, title=data.message[:50])
        db.add(chat)
        await db.flush()

    db.add(Message(chat_id=chat.id, role="user", content=data.message))
    await db.commit()

    msg_result = await db.execute(select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at))
    messages = [{"role": m.role, "content": m.content} for m in msg_result.scalars().all()]

    try:
        ai_result = await llm_service.chat(messages, stream=False)
        content = ai_result["content"] if isinstance(ai_result, dict) else ""
    except Exception as e:
        logger.error(f"LLM error: {e}")
        content = f"Sorry, I encountered an error: {e}"

    db.add(Message(chat_id=chat.id, role="assistant", content=content))
    await db.commit()

    if chat.title == "New Chat" and len(data.message) > 10:
        chat.title = data.message[:50]
        await db.commit()

    return ChatResponse(chat_id=chat.id, message=content)


async def _stream_chat(data: ChatRequest, user_id: str, db: AsyncSession):
    if data.chat_id:
        result = await db.execute(select(Chat).where(Chat.id == data.chat_id, Chat.user_id == user_id))
        chat = result.scalar_one_or_none()
        if not chat:
            raise HTTPException(404, "Chat not found")
    else:
        chat = Chat(user_id=user_id, title=data.message[:50])
        db.add(chat)
        await db.flush()

    db.add(Message(chat_id=chat.id, role="user", content=data.message))
    await db.commit()

    msg_result = await db.execute(select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at))
    messages = [{"role": m.role, "content": m.content} for m in msg_result.scalars().all()]

    try:
        context = await memory_service.get_context(data.message, user_id)
        if messages and context:
            messages[0]["content"] = f"Context:\n{context}\n\n---\n\n{messages[0]['content']}"
    except Exception as e:
        logger.warning(f"Memory context error: {e}")

    async def event_stream() -> AsyncGenerator[str, None]:
        full_content = ""
        try:
            ai_result = await llm_service.chat(messages, stream=True)
            if hasattr(ai_result, "__aiter__"):
                async for chunk in ai_result:
                    full_content += chunk
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            elif isinstance(ai_result, dict):
                content = ai_result.get("content", "")
                full_content = content
                yield f"data: {json.dumps({'content': content})}\n\n"
        except Exception as e:
            err_msg = f"Sorry, I encountered an error: {e}"
            full_content = err_msg
            yield f"data: {json.dumps({'content': err_msg})}\n\n"
        finally:
            db.add(Message(chat_id=chat.id, role="assistant", content=full_content))
            await db.commit()
            if chat.title == "New Chat" and len(data.message) > 10:
                chat.title = data.message[:50]
                await db.commit()
            yield f"data: {json.dumps({'done': True, 'chat_id': chat.id})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("", response_model=List[ChatHistory])
async def list_chats(user_id: str = Query("default"), skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Chat).where(Chat.user_id == user_id).offset(skip).limit(limit).order_by(Chat.updated_at.desc()))
    chats = result.scalars().all()
    output = []
    for chat in chats:
        msg_result = await db.execute(select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at).limit(1))
        msgs = [MessageSchema(role=m.role, content=m.content[:100], agent_name=m.agent_name) for m in msg_result.scalars().all()]
        output.append(ChatHistory(id=chat.id, title=chat.title, pinned=chat.pinned, created_at=chat.created_at, updated_at=chat.updated_at, messages=msgs))
    return output

@router.get("/{chat_id}", response_model=ChatHistory)
async def get_chat(chat_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(404, "Chat not found")
    msg_result = await db.execute(select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at))
    msgs = [MessageSchema(role=m.role, content=m.content, agent_name=m.agent_name) for m in msg_result.scalars().all()]
    return ChatHistory(id=chat.id, title=chat.title, pinned=chat.pinned, created_at=chat.created_at, updated_at=chat.updated_at, messages=msgs)

@router.delete("/{chat_id}", status_code=204)
async def delete_chat(chat_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(404, "Chat not found")
    await db.execute(Message.__table__.delete().where(Message.chat_id == chat_id))
    await db.delete(chat)
    await db.commit()
