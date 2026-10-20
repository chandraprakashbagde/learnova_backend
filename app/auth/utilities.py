from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from app.setting import setting
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from app.auth.models import User, RefreshToken

pwd_ctx = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

def gen_password_hash(passwod: str):
    return pwd_ctx.hash(passwod)

def verify_password(entered_password: str, hashed_password: str):
    return pwd_ctx.verify(entered_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta=None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM)

async def create_tokens(session: AsyncSession, user:User):
    access_token = create_access_token(data={
        "user_id":str(user.id),
        "email":user.email,
        "role":user.role.value
    })

    refresh_token_str = str(uuid4())

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=expires_at
    )

    session.add(refresh_token)

    await session.commit()

    return {
        "access_token":access_token,
        "refresh_token":refresh_token_str,
        "token_type":"bearer"
    }


def decode_token(token: str):
    try:
        return jwt.decode(token, setting.SECRET_KEY, algorithms=setting.ALGORITHM)
    except JWTError:
        return None