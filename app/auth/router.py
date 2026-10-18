from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from app.db.config import SessionDep
from app.auth.schemas import UserOut, UserCreate, LoginUser, RegSuccess
from app.auth.services import reg_user, autheticate_users
from app.auth.dependancies import validate_token
from app.auth.utilities import create_tokens

router = APIRouter(prefix="/auth", tags=["Authetication APIs"])

@router.post("/register", )
async def user(session:SessionDep, user: UserCreate):
    usr = await reg_user(session, user);

    if usr != None:
        return RegSuccess(user=usr)

@router.post("/login")
async def login(session: SessionDep, credentials:OAuth2PasswordRequestForm = Depends()):
    usr = await autheticate_users(session, credentials.username, credentials.password)

    token = await create_tokens(session, usr)

    response = JSONResponse(
        content={
            "access_token": token["access_token"]
        }
    )

    response.set_cookie(
        "refresh_token",
        token["refresh_token"],
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7
    )

    return response

@router.get("/me")
async def me(user = Depends(validate_token)):
    return user