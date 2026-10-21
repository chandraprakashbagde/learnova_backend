from fastapi import APIRouter, Depends,HTTPException
from app.db.config import SessionDep
from app.auth.dependancies import get_logged_in_user_info
from app.teacher.profile.models import TeacherProfile, teachers_qualifications, teachers_subject
from sqlalchemy import select, insert
from app.core.api_response import SuccessResp, ErrorResp
from app.admin.qaulifications.models import Qualifications
from app.admin.subjects.models import Subject
from app.teacher.profile.schemas import TeacherProfileUpdate, VerificationStatus
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

async def get_account_status(session:SessionDep, user = Depends(get_logged_in_user_info)):
    stmt = select(TeacherProfile.verification_status).where(TeacherProfile.user_id == user["user_id"])
    result = await session.scalars(stmt)

    return SuccessResp(
        data=result.one_or_none()
    )

async def fetch_qaulifications(session:SessionDep):
    stmt = select(Qualifications.id, Qualifications.name)
    result = await session.execute(stmt)
    data = [dict(row) for row in result.mappings().all()]
    return SuccessResp(
            data=data
        )

async def fetch_subjects(session:SessionDep):
    stmt = select(Subject.id, Subject.name)
    result = await session.execute(stmt)
    data = [dict(row) for row in result.mappings().all()]
    return SuccessResp(
            data=data
        )

async def update_profile(session:SessionDep, teacher_profile_info:TeacherProfileUpdate, user = Depends(get_logged_in_user_info)):
    stmt = select(TeacherProfile).where(TeacherProfile.user_id == user["user_id"])
    teacher_profile = await session.scalar(stmt)

    if teacher_profile == None:
        return ErrorResp(message="Teacher profile not found")

    # Validate subject IDs
    subject_ids = list(set(teacher_profile_info.subjects))

    if subject_ids:
        result = await session.scalars(select(Subject.id).where(Subject.id.in_(subject_ids)))

        existing_subjects_ids = set(result.all()) 

        if existing_subjects_ids != set(subject_ids):
            return ErrorResp(message="One or more subject IDs are invalid")

    #validate qaulification IDs
    qaulification_ids = [ 
        item.qaulification_id
        for item in teacher_profile_info.qaulifications
    ]

    if len(qaulification_ids) != len(set(qaulification_ids)):
        return ErrorResp(message="Duplicate qaulification IDs are not allowed")
    
    if qaulification_ids:
        result = await session.scalars(select(Qualifications).where(Qualifications.id.in_(qaulification_ids)))
        existing_qaul_ids = set(result.all())

        if existing_qaul_ids != set(qaulification_ids):
            return ErrorResp(message="One or more qaulification IDs are invalid")

    try:
        teacher_profile.exprience = teacher_profile_info.exprience
        teacher_profile.bio = teacher_profile_info.bio
        teacher_profile.verification_status = VerificationStatus.DOCUMENTS_PENDING

        if subject_ids:
            await session.execute(
                insert(teachers_subject),
                [
                    {
                        "teacher_id": teacher_profile.id,
                        "subject_id": subject_id,
                    }
                    for subject_id in subject_ids
                ]
            )

        if qaulification_ids:
            await session.execute(
                insert(teachers_qualifications),
                [
                    {
                        "teacher_id":teacher_profile.id,
                        "qualifications_id":item.qualifications_id,
                        "specialization":item.specialization,
                        "institution_name":item.institution_name,
                        "passing_year":item.passing_year
                    }
                    for item in teacher_profile_info.qaulifications
                ]
            )

        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Profile update conflicts with existing data",
        )

    except Exception:
        await session.rollback()
        raise

    return SuccessResp(
        message="Teacher profile updated successfully"
    )