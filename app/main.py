from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import validation_exception_handler
from app.auth.router import router as auth_router

app = FastAPI()

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.include_router(auth_router) 