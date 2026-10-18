from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.auth.utilities import decode_token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def validate_token(token = Depends(oauth2_scheme)):
    user = decode_token(token)

    return user