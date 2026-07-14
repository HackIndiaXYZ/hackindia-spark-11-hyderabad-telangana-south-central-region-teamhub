from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.models.file import File as FileModel
from app.schemas.file import FileCreate, FileUpdate, FileResponse

router = APIRouter()

@router.get("/{project_id}", response_model=List[FileResponse])
async def list_files(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileModel).where(FileModel.project_id == project_id).order_by(FileModel.path))
    return result.scalars().all()

@router.post("/{project_id}", response_model=FileResponse, status_code=201)
async def create_file(project_id: str, data: FileCreate, db: AsyncSession = Depends(get_db)):
    file = FileModel(project_id=project_id, **data.model_dump())
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return file

@router.get("/{project_id}/{file_id}", response_model=FileResponse)
async def get_file(project_id: str, file_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileModel).where(FileModel.id == file_id, FileModel.project_id == project_id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(404, "File not found")
    return file

@router.put("/{project_id}/{file_id}", response_model=FileResponse)
async def update_file(project_id: str, file_id: str, data: FileUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileModel).where(FileModel.id == file_id, FileModel.project_id == project_id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(404, "File not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(file, k, v)
    await db.commit()
    await db.refresh(file)
    return file

@router.delete("/{project_id}/{file_id}", status_code=204)
async def delete_file(project_id: str, file_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileModel).where(FileModel.id == file_id, FileModel.project_id == project_id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(404, "File not found")
    await db.delete(file)
    await db.commit()
