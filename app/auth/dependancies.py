from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.auth.utilities import decode_token
from app.auth.schemas import Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_logged_in_user_info(token = Depends(oauth2_scheme)):
    """
    Returns the decoded JWT claims for the authenticated user.

    Raises 401 when the token is missing, malformed, or expired so callers
    never receive `None` (previously an invalid token returned `None`, which
    surfaced as a 500 on /auth/role and a 200-with-null body on /auth/me).
    """
    user = decode_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_role(role: Role):
    """
    Dependency factory enforcing a specific role from the signed token claims.

    Frontend route guards are not security. Every protected endpoint must
    depend on this (or require_admin) so the server independently verifies the
    role — never from client-supplied data.

    Usage:
        @router.get("/teacher-only")
        async def endpoint(user = Depends(require_role(Role.TEACHER))): ...
    """
    async def _dependency(user = Depends(get_logged_in_user_info)):
        if user.get("role") != role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{role.value} access required",
            )
        return user

    return _dependency


# Require an Admin role. Equivalent to require_role(Role.ADMIN) but kept as a
# named dependency for readability at admin endpoints.
require_admin = require_role(Role.ADMIN)
