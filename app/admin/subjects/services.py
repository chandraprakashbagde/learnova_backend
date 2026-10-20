from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.schemas import MasterDataItemOut, MasterDataListOut
from app.admin.subjects.models import Subject
from app.admin.subjects.schemas import CreateUpdateSubject
from app.core.api_response import ErrorResp, SuccessResp
from app.teacher.profile.models import teachers_subject


def _teacher_count_subq():
    """Scalar subquery counting the teachers linked to each subject."""
    return (
        select(func.count())
        .select_from(teachers_subject)
        .where(teachers_subject.c.subject_id == Subject.id)
        .correlate(Subject)
        .scalar_subquery()
    )


def _like_pattern(term: str) -> str:
    """Lower-cased substring pattern with LIKE wildcards escaped."""
    escaped = term.strip().lower()
    for char in ("\\", "%", "_"):
        escaped = escaped.replace(char, f"\\{char}")
    return f"%{escaped}%"


async def get_all_subs(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    order_by: str = "name",
    order: str = "asc",
) -> MasterDataListOut:
    """Paginated, searchable subject list for GET /admin/subjects.

    Soft-deleted subjects are hidden, and each row carries the number of
    teachers referencing it so the admin table needs no extra requests.
    """
    filters = [Subject.deleted.is_(False)]
    if search and search.strip():
        filters.append(func.lower(Subject.name).like(_like_pattern(search), escape="\\"))

    total = (
        await session.scalar(select(func.count()).select_from(Subject).where(*filters))
    ) or 0

    order_column = {"name": Subject.name, "id": Subject.id}.get(order_by, Subject.name)
    ordering = order_column.desc() if order.lower() == "desc" else order_column.asc()

    stmt = (
        select(Subject, _teacher_count_subq().label("teacher_count"))
        .where(*filters)
        # Stable tiebreak so pagination never repeats or skips a row.
        .order_by(ordering, Subject.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await session.execute(stmt)).all()

    return MasterDataListOut(
        items=[
            MasterDataItemOut(id=row[0].id, name=row[0].name, teacher_count=row[1])
            for row in rows
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


async def create_sub(session: AsyncSession, sub: CreateUpdateSubject):
    stmt = select(Subject).where(Subject.name == sub.name)
    result = await session.scalars(stmt)

    if result.one_or_none():
        return ErrorResp(
            status_code=status.HTTP_409_CONFLICT,
            message="Subject is already present with this name"
        )

    subject = Subject(name=sub.name)

    session.add(subject)

    await session.commit()
    await session.refresh(subject)

    return SuccessResp(
        message="Subject created successfully",
        data=MasterDataItemOut(id=subject.id, name=subject.name, teacher_count=0)
    )

async def update_sub(session: AsyncSession, id:int, sub:CreateUpdateSubject):
    subject = await session.get(Subject, id)

    if subject is None or subject.deleted:
        return ErrorResp(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Subject Not Found"
        )

    duplicate = await session.scalar(
        select(Subject).where(Subject.name == sub.name, Subject.id != id)
    )
    if duplicate:
        return ErrorResp(
            status_code=status.HTTP_409_CONFLICT,
            message="Subject is already present with this name"
        )

    subject.name = sub.name
    session.add(subject)
    await session.commit()
    await session.refresh(subject)

    teacher_count = (
        await session.scalar(
            select(func.count())
            .select_from(teachers_subject)
            .where(teachers_subject.c.subject_id == id)
        )
    ) or 0

    return SuccessResp(
        message="Subject updated successfully",
        data=MasterDataItemOut(
            id=subject.id, name=subject.name, teacher_count=teacher_count
        )
    )

async def delete_sub(session: AsyncSession, id:int):
    subject = await session.get(Subject, id)

    if subject is None:
        return ErrorResp(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Subject Not Found"
        )

    subject.deleted = True
    session.add(subject)
    await session.commit()
    await session.refresh(subject)

    return SuccessResp(
        message="Subject deleted successfully."
    )
