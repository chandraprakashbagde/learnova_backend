from fastapi import APIRouter, Depends
from app.auth.dependancies import require_teacher
from app.teacher.profile.router import router as profile_router


router = APIRouter(prefix="/teacher", tags=["Teacher Management"], dependencies=[Depends(require_teacher)])

router.include_router(profile_router)