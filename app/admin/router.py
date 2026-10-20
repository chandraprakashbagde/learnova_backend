from fastapi import APIRouter, Depends
from app.admin.subjects.router import router as subject_router
from app.auth.dependancies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin Routes"],dependencies=[Depends(require_admin)])

router.include_router(subject_router)