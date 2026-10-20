from app.admin.qaulifications.models import Qualifications
from app.admin.qaulifications.schemas import QualificationOut, CreateUpdateQualification
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.api_response import ErrorResp, SuccessResp
from fastapi import status


async def fetch_all_qaulifctns(session: AsyncSession) -> list[QualificationOut]:
    stmt = select(Qualifications)
    result = await session.scalars(stmt)

    return result.fetchall()

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
        data=new_qlfctn
    )

async def update_(session: AsyncSession, id:int, qlfctn:CreateUpdateQualification):
    qaulification = await session.get(Qualifications.id,id)

    if qaulification == None:
        return ErrorResp(
            status_code=status.HTTP_404_NOT_FOUND, 
            message="Qualifications Not Found"
        )

    qaulification.name = qlfctn.name
    session.add(qaulification)
    await session.commit()
    await session.refresh(qaulification)

    return qaulification

async def delete_(session: AsyncSession, id:int):
    qlfctn = await session.get(Qualifications.id,id)

    if qlfctn == None:
        return ErrorResp(
            status_code=status.HTTP_404_NOT_FOUND, 
            message="Qualifications Not Found"
        )

    qlfctn.deleted = True
    session.add(qlfctn)
    await session.commit()
    await session.refresh(qlfctn)

    return SuccessResp(
        message="Qualifications deleted successfully."
    )