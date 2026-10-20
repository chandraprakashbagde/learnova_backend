from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.schemas import UserCreate, UserOut, LoginUser
from app.auth.models import User
from app.auth.utilities import gen_password_hash, verify_password, create_tokens
from app.core.api_response import ErrorResp, SuccessResp

async def get_user_by_email(session: AsyncSession, email: str) -> UserOut | None:
    stmt = select(User).where(User.email==email)
    result = await session.scalars(stmt)
    return  result.one_or_none()

async def reg_user(session: AsyncSession, user: UserCreate) -> UserOut:

    ## Check User exists
    ext_usr = await get_user_by_email(session, email=user.email)

    if ext_usr != None:
       return ErrorResp("User with this email already exists", status_code=status.HTTP_409_CONFLICT)

    user = User(
        name=user.name, 
        email=user.email, 
        phone=user.phone,
        role=user.role.value,
        password=gen_password_hash(passwod=user.password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return SuccessResp(
        message="Registered successfully, verification link has been sent to your email.",
        data=UserOut.model_validate(user).model_dump()
    )

async def autheticate_users(session: AsyncSession, username: str, password: str):

    user = await get_user_by_email(session, username)

    if user is None or verify_password(password, user.password) == False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid crenderntials")

    return user