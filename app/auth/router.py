from app.db.config import SessionDep
from fastapi import APIRouter
from app.auth.response import RegistrationSuccess, register_responses
from app.auth.services import *
from app.auth.schemas import UserCreate, EmailVerification

router = APIRouter(prefix="/auth", tags=["User Login and authetication"])



@router.post("/register", status_code=201, response_model=RegistrationSuccess, responses=register_responses)
async def register(session: SessionDep, payload:UserCreate) -> RegistrationSuccess:
   return await register_user(session, payload)

@router.post("/send_email")
async def send_email(userInfo: EmailVerification):
   return await send_verification_email(userInfo)

@router.get("/verify")
async def verify(token: str, session: SessionDep):
   return await verify_email(token, session)