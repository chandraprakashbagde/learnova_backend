from app.admin.subjects.models import Subject
from app.admin.subjects.schemas import SubjectOut, CreateUpdateSubject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.api_response import ErrorResp, SuccessResp
from fastapi import status

async def get_all_subs(session: AsyncSession) -> list[SubjectOut]:
    stmt = select(Subject)
    result = await session.scalars(stmt)

    return result.fetchall()

async def create_sub(session: AsyncSession, sub:CreateUpdateSubject):
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
        data=subject
    )

async def update_sub(session: AsyncSession, id:int, sub:CreateUpdateSubject):
    subject = await session.get(Subject.id,id)

    if subject == None:
        return ErrorResp(
            status_code=status.HTTP_404_NOT_FOUND, 
            message="Subject Not Found"
        )

    subject.name = sub.name
    session.add(subject)
    await session.commit()
    await session.refresh(subject)

    return subject

async def delete_sub(session: AsyncSession, id:int):
    subject = await session.get(Subject.id,id)

    if subject == None:
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