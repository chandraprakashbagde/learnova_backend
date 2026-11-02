from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.auth.router import router as auth_router
from app.core.validation import validation_handler

from fastapi_response_handler import register_handlers

import app.db.models  # noqa: F401 - registers all model classes with SQLAlchemy

app = FastAPI()

register_handlers(app, overrides={RequestValidationError: validation_handler})

app.include_router(auth_router)