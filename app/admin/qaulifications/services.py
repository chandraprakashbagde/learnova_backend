from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.qaulifications.models import Qualifications
from app.admin.qaulifications.schemas import CreateUpdateQualification
from app.admin.schemas import MasterDataItemOut, MasterDataListOut
from app.core.api_response import ErrorResp, SuccessResp
from app.teacher.profile.models import teachers_qualifications


def _teacher_count_subq():
    """Scalar subquery counting the teachers linked to each qualification."""
    return (
        select(func.count())
        .select_from(teachers_qualifications)
        .where(teachers_qualifications.c.qualifications_id == Qualifications.id)
        .correlate(Qualifications)
        .scalar_subquery()
    )


def _like_pattern(term: str) -> str:
    """Lower-cased substring pattern with LIKE wildcards escaped."""
    escaped = term.strip().lower()
    for char in ("\\", "%", "_"):
        escaped = escaped.replace(char, f"\\{char}")
    return f"%{escaped}%"


async def fetch_all_qaulifctns(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    order_by: str = "name",
    order: str = "asc",
) -> MasterDataListOut:
    """Paginated, searchable list for GET /admin/qualifications.

    Each row carries the number of teachers referencing it so the admin
    table needs no extra requests.
    """
    filters = []
    if search and search.strip():
        filters.append(
            func.lower(Qualifications.name).like(_like_pattern(search), escape="\\")
        )

    total = (
        await session.scalar(
            select(func.count()).select_from(Qualifications).where(*filters)
        )
    ) or 0

    order_column = {
        "name": Qualifications.name,
        "created_at": Qualifications.created_at,
        "id": Qualifications.id,
    }.get(order_by, Qualifications.name)
    ordering = order_column.desc() if order.lower() == "desc" else order_column.asc()

    stmt = (
        select(Qualifications, _teacher_count_subq().label("teacher_count"))
        .where(*filters)
        # Stable tiebreak so pagination never repeats or skips a row.
        .order_by(ordering, Qualifications.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await session.execute(stmt)).all()

    return MasterDataListOut(
        items=[
            MasterDataItemOut(
                id=row[0].id,
                name=row[0].name,
                created_at=row[0].created_at,
                teacher_count=row[1],
            )
            for row in rows
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


async def create_qaulifctns(session: AsyncSession, qlfctn:CreateUpdateQualification):
    stmt = select(Qualifications).where(Qualifications.name == qlfctn.name)
    result = await session.scalars(stmt)

    if result.one_or_none():
        return ErrorResp(
            status_code=status.HTTP_409_CONFLICT, 
            message="Qualifications is already present with this name"
        )

    new_qlfctn = Qualifications(name=qlfctn.name)

    session.add(new_qlfctn)

    await session.commit()
    await session.refresh(new_qlfctn)

    return SuccessResp(
        message="Qualifications created successfully",
        data=MasterDataItemOut(
            id=new_qlfctn.id,
            name=new_qlfctn.name,
            created_at=new_qlfctn.created_at,
            teacher_count=0,
        )
    )

async def update_(session: AsyncSession, id:int, qlfctn:CreateUpdateQualification):
    qaulification = await session.get(Qualifications, id)

    if qaulification is None:
        return ErrorResp(
            status_code=status.HTTP_404_NOT_FOUND, 
            message="Qualifications Not Found"
        )

    duplicate = await session.scalar(
        select(Qualifications).where(
            Qualifications.name == qlfctn.name, Qualifications.id != id
        )
    )
    if duplicate:
        return ErrorResp(
            status_code=status.HTTP_409_CONFLICT,
            message="Qualifications is already present with this name"
        )

    qaulification.name = qlfctn.name
    session.add(qaulification)
    await session.commit()
    await session.refresh(qaulification)

    teacher_count = (
        await session.scalar(
            select(func.count())
            .select_from(teachers_qualifications)
            .where(teachers_qualifications.c.qualifications_id == id)
        )
    ) or 0

    return SuccessResp(
        message="Qualifications updated successfully",
        data=MasterDataItemOut(
            id=qaulification.id,
            name=qaulification.name,
            created_at=qaulification.created_at,
            teacher_count=teacher_count,
        ),
    )

async def delete_(session: AsyncSession, id:int):
    qlfctn = await session.get(Qualifications, id)

    if qlfctn is None:
        return ErrorResp(
            status_code=status.HTTP_404_NOT_FOUND, 
            message="Qualifications Not Found"
        )

    # The qualifications table has no soft-delete flag, so only unlink-free
    # records may be removed; referenced ones must stay (409).
    in_use = await session.scalar(
        select(func.count())
        .select_from(teachers_qualifications)
        .where(teachers_qualifications.c.qualifications_id == id)
    ) or 0
    if in_use:
        return ErrorResp(
            status_code=status.HTTP_409_CONFLICT,
            message="Qualification is referenced by teachers and cannot be deleted"
        )

    await session.delete(qlfctn)
    await session.commit()

    return SuccessResp(
        message="Qualifications deleted successfully."
    )
