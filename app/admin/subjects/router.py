from typing import Annotated, Literal
from fastapi import APIRouter, Path, Query
from app.admin.subjects.services import *
from app.db.config import SessionDep
from app.admin.subjects.schemas import CreateUpdateSubject
router = APIRouter(prefix="/subjects")

# Routes are registered without a trailing slash so they match the paths the
# frontend calls (GET/POST /admin/subjects, PUT/DELETE /admin/subjects/{id}).
@router.get("")
async def get_all_subjects(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    search: Annotated[str | None, Query(max_length=100)] = None,
    order_by: Annotated[str, Query(pattern="^(name|id)$")] = "name",
    order: Annotated[Literal["asc", "desc"], Query()] = "asc",
):
    return await get_all_subs(
        session,
        page=page,
        page_size=page_size,
        search=search,
        order_by=order_by,
        order=order,
    )

@router.post("")
async def create_new_subject(session: SessionDep, sub: CreateUpdateSubject):
    return await create_sub(session, sub)

@router.put("/{id}")
async def update_subject(session: SessionDep, sub: CreateUpdateSubject, id = Annotated[int, Path()]):
    return await update_sub(session, id, sub)

@router.delete("/{id}")
async def delete_subject(session: SessionDep, id = Annotated[int, Path()]):
    return await delete_sub(session, id)
