from fastapi import APIRouter, Path
from app.admin.subjects.services import *
from app.db.config import SessionDep
from app.admin.subjects.schemas import CreateUpdateSubject
from typing import Annotated
router = APIRouter(prefix="/subjects")

@router.get("/")
async def get_all_subjects(session: SessionDep):
    return await get_all_subs(session)

@router.post("/")
async def create_new_subject(session: SessionDep, sub: CreateUpdateSubject):
    return await create_sub(session, sub)

@router.put("/:{id}")
async def update_subject(session: SessionDep, sub: CreateUpdateSubject, id = Annotated[int, Path()]):
    return await update_sub(session, id, sub)

@router.delete("/:{id}")
async def delete_subject(session: SessionDep, id = Annotated[int, Path()]):
    return await delete_sub(session, id)