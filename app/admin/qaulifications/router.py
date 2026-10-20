from typing import Annotated, Literal
from fastapi import APIRouter, Path, Query
from app.admin.qaulifications.services import *
from app.db.config import SessionDep
from app.admin.qaulifications.schemas import CreateUpdateQualification

# The URL is `/admin/qualifications` (correct spelling) to match the contract
# the frontend calls — see features/admin/api/adminMasterData.api.ts.
router = APIRouter(prefix="/qualifications")

# Routes are registered without a trailing slash so they match the paths the
# frontend calls (GET/POST /admin/qualifications, PUT/DELETE .../{id}).
@router.get("")
async def get_all_qaulfctns(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    search: Annotated[str | None, Query(max_length=100)] = None,
    order_by: Annotated[str, Query(pattern="^(name|created_at|id)$")] = "name",
    order: Annotated[Literal["asc", "desc"], Query()] = "asc",
):
    return await fetch_all_qaulifctns(
        session,
        page=page,
        page_size=page_size,
        search=search,
        order_by=order_by,
        order=order,
    )

@router.post("")
async def create_new_qaulfctn(session: SessionDep, qlfctn: CreateUpdateQualification):
    return await create_qaulifctns(session, qlfctn)

@router.put("/{id}")
async def update_qaulfctns(session: SessionDep, qlfctn: CreateUpdateQualification, id = Annotated[int, Path()]):
    return await update_(session, id, qlfctn)

@router.delete("/{id}")
async def delete_qaulfctns(session: SessionDep, id = Annotated[int, Path()]):
    return await delete_(session, id)
