from fastapi import APIRouter, Path
from app.admin.qaulifications.services import *
from app.db.config import SessionDep
from app.admin.qaulifications.schemas import CreateUpdateQualification
from typing import Annotated
router = APIRouter(prefix="/qaulifications")

@router.get("/")
async def get_all_qaulfctns(session: SessionDep):
    return await fetch_all_qaulifctns(session)

@router.post("/")
async def create_new_qaulfctn(session: SessionDep, qlfctn: CreateUpdateQualification):
    return await create_qaulifctns(session, qlfctn)

@router.put("/:{id}")
async def update_qaulfctns(session: SessionDep, qlfctn: CreateUpdateQualification, id = Annotated[int, Path()]):
    return await update_(session, id, qlfctn)

@router.delete("/:{id}")
async def delete_qaulfctns(session: SessionDep, id = Annotated[int, Path()]):
    return await delete_(session, id)