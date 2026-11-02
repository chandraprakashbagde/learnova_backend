from app.db.config import SessionDep
from fastapi import APIRouter
from app.auth.response import RegistrationSuccess, register_responses
from app.auth.services import *
from app.auth.schemas import UserCreate

router = APIRouter(prefix="/auth", tags=["User Login and authetication"])



@router.post("/register", status_code=201, response_model=RegistrationSuccess, responses=register_responses)
async def register(session: SessionDep, payload:UserCreate) -> RegistrationSuccess:
   return await register_user(session, payload)