from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select 
from app.auth.models import User
from app.teacher.profile.models import TeacherProfile
from app.auth.schemas import UserCreate, UserOut, Role
from fastapi_response_handler import ConflictException, success_response
from app.auth.response import *
from app.auth.utilities import gen_password_hash


async def ensure_email_exists(session: AsyncSession, email: str):
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
     
    user = result.one_or_none()

    if user is not None:
        raise ConflictException.from_spec(USER_EMAIL_EXISTS)



async def register_user(session: AsyncSession, payload: UserCreate):
    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password=gen_password_hash(payload.password),
        role=payload.role,
    )

    await ensure_email_exists(session=session,email=payload.email)

    session.add(user)
    if payload.role.value == Role.TEACHER.value:
        user.teachers_profile = TeacherProfile(
            profile_image="0",
            exprience=0,
            bio=None
        )

    await session.commit()
    await session.refresh(user)
    return success_response(USERS_CREATED, UserOut.model_validate(user))