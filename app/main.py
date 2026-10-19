from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from app.core.api_response import validation_exception_handler
from app.auth.router import router as auth_router

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def exceptionHandler(request: Request, exc: RequestValidationError):
    return await validation_exception_handler(exc)

app.include_router(auth_router) 