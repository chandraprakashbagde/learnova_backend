from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.core.api_response import validation_exception_handler
from app.auth.router import router as auth_router
from app.admin.router import router as admin_router

app = FastAPI()

# Allow the frontend dev server to call the API (cookies included for the
# httpOnly refresh_token set by POST /auth/login).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def exceptionHandler(request: Request, exc: RequestValidationError):
    return await validation_exception_handler(exc)

app.include_router(auth_router) 
app.include_router(admin_router)