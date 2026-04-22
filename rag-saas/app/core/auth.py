"""
Authentication & Authorization — JWT verification for all protected endpoints.

This module provides the `get_current_user` dependency that:
  1. Extracts the Bearer token from the Authorization header
  2. Decodes & validates the JWT using Supabase's JWT secret
  3. Returns the authenticated user's identity (user_id, email)
  4. Raises 401 if the token is missing, expired, or invalid

Usage in routes:
    @router.get("/protected")
    async def protected_route(user: dict = Depends(get_current_user)):
        user_id = user["user_id"]
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import settings
from app.core.logging import logger

# HTTPBearer scheme — extracts "Bearer <token>" from Authorization header
# auto_error=True means it raises 403 automatically if header is missing
security_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """
    FastAPI dependency: verifies the Supabase JWT and returns user info.
    
    Supabase JWTs contain these relevant claims:
        - sub: the user's UUID (our tenant_id)
        - email: the user's email address
        - aud: "authenticated" (for logged-in users)
        - exp: expiration timestamp
    
    Returns:
        dict with keys: user_id (str), email (str)
    
    Raises:
        HTTPException 401 if token is invalid or expired
    """
    token = credentials.credentials

    try:
        # Decode the JWT using Supabase's JWT secret
        # audience="authenticated" ensures only logged-in user tokens pass
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience="authenticated",
        )

        # Extract user identity from standard JWT claims
        user_id: str | None = payload.get("sub")
        email: str | None = payload.get("email")

        if not user_id:
            logger.warning("JWT decoded but missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user identity",
            )

        return {"user_id": user_id, "email": email}

    except ExpiredSignatureError:
        logger.info("JWT expired — client should refresh the token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired — please refresh your session",
        )
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
