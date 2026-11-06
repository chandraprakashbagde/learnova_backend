from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from fastapi import HTTPException

from app.auth.models import User
from app.teacher.profile.models import TeacherProfile
from app.auth.schemas import UserCreate, UserOut, Role, EmailVerification
from app.auth.response import (
    REG_SUCCESSFULL,
    USERS_CREATED,
    USER_EMAIL_EXISTS,
    VALIDATION_FAILED,
    INTERNAL_ERROR,
    SuccessResponse,
    ErrorResponse,
    ErrorDetail,
)


async def ensure_email_exists(session: AsyncSession, email: str):
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)

    user = result.one_or_none()

    if user is not None:
        raise HTTPException(
            status_code=USER_EMAIL_EXISTS.status_code,
            detail=USER_EMAIL_EXISTS.detail,
        )


async def send_verification_email(userInfo: EmailVerification):
    """Render and send email verification email."""

    from app.core.sendemails.send_email import render_email_template, send_email

    try:
        html_content = render_email_template(
            template_name="email_verification.html",
            context={
                "user_name": userInfo.user_name,
                "user_role": userInfo.user_role.value,
                "verification_url": f"localhost:8000/auth/verify?token={await create_email_verification_token(userInfo.user_id)}",
                "expiry_minutes": 15,
            },
        )

        response = await send_email(
            to_email=userInfo.user_email,
            subject="Verify your Learnova account",
            html_content=html_content,
            to_name=userInfo.user_name,
        )

        return response

    except Exception as exc:
        print(f"Verification email error: {exc}")
        raise


async def register_user(session: AsyncSession, payload: UserCreate):
    try:
        user = User(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            password=gen_password_hash(payload.password),
            role=payload.role,
        )

        await ensure_email_exists(session=session, email=payload.email)

        session.add(user)
        if payload.role.value == Role.TEACHER.value:
            user.teachers_profile = TeacherProfile(
                profile_image="0",
                exprience=0,
                bio=None,
            )

        await session.commit()
        await session.refresh(user)
        await send_verification_email(EmailVerification(
            user_name=user.name,
            user_role=user.role.value,
            user_id=user.id
        ))
        return SuccessResponse(message=REG_SUCCESSFULL, data=UserOut.model_validate(user))
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=INTERNAL_ERROR.detail,
        )


async def verify_email(token: str, session: AsyncSession):
    from app.auth.utilities import verify_email_token

    tokenize_info = await verify_email_token(token)
    print("tokenize_info")
    print(tokenize_info)
    if tokenize_info is None:
        raise HTTPException(
            status_code=403,
            detail="Invalid EMAIL TOKEN",
        )
    user = await session.get(User, tokenize_info)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.email_verified = True
    user.email_verified_at = datetime.now(timezone.utc)

    session.add(user)

    await session.commit()

    return SuccessResponse(message="Email verified successfully", data=None)