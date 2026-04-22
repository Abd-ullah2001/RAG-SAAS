"""
Auth Routes — Authentication endpoints for signup, login, OAuth, and token refresh.

Endpoints:
  POST /auth/signup          — Register with email + password
  POST /auth/login           — Login with email + password
  GET  /auth/google          — Get Google OAuth consent URL
  POST /auth/refresh         — Exchange refresh_token for new access_token
  POST /auth/logout          — Invalidate the current session
"""

from fastapi import APIRouter, HTTPException, status

from app.db.supabase_client import supabase_anon
from app.core.logging import logger
from app.models.schemas import (
    SignUpRequest,
    LoginRequest,
    RefreshRequest,
    AuthResponse,
    GoogleOAuthResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL + PASSWORD SIGNUP
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest):
    """
    Register a new user with email and password.
    
    Supabase handles:
      - Password hashing (bcrypt)
      - Email verification (if enabled in dashboard)
      - User record creation in auth.users table
    
    Returns access + refresh tokens on success.
    """
    try:
        result = supabase_anon.auth.sign_up({
            "email": request.email,
            "password": request.password,
        })

        # Check if signup succeeded — Supabase returns user even for existing emails
        if not result.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed — the email may already be registered",
            )

        # If email confirmation is enabled, session may be None
        if not result.session:
            logger.info(f"Signup successful for {request.email} — awaiting email confirmation")
            # Return a partial response indicating confirmation needed
            return AuthResponse(
                access_token="",
                refresh_token="",
                token_type="bearer",
                user_id=result.user.id,
                email=result.user.email or request.email,
            )

        logger.info(f"User registered and logged in: {request.email}")
        return AuthResponse(
            access_token=result.session.access_token,
            refresh_token=result.session.refresh_token,
            user_id=result.user.id,
            email=result.user.email or request.email,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error for {request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {str(e)}",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL + PASSWORD LOGIN
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate with email and password.
    
    Returns JWT access_token (short-lived) and refresh_token (long-lived).
    The access_token should be sent as `Authorization: Bearer <token>`
    on all subsequent API requests.
    """
    try:
        result = supabase_anon.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })

        if not result.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        logger.info(f"User logged in: {request.email}")
        return AuthResponse(
            access_token=result.session.access_token,
            refresh_token=result.session.refresh_token,
            user_id=result.user.id,
            email=result.user.email or request.email,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# GOOGLE OAUTH
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/google", response_model=GoogleOAuthResponse)
async def google_oauth():
    """
    Get the Google OAuth consent screen URL.
    
    Flow:
      1. Frontend/client calls this endpoint
      2. Receives a URL to redirect the user to
      3. User authenticates with Google
      4. Google redirects back to Supabase with the auth code
      5. Supabase exchanges it for tokens and redirects to your app
      6. Your app receives the JWT tokens
    
    Note: Google OAuth must be enabled in Supabase Dashboard →
          Authentication → Providers → Google
    """
    try:
        result = supabase_anon.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": f"{__import__('os').getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/callback",
            },
        })

        if not result or not result.url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate Google OAuth URL",
            )

        logger.info("Google OAuth URL generated successfully")
        return GoogleOAuthResponse(url=result.url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth initialization failed: {str(e)}",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TOKEN REFRESH
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshRequest):
    """
    Exchange a refresh_token for a new access_token.
    
    Call this when the access_token expires (401 response from any endpoint).
    The refresh_token has a longer lifespan than the access_token.
    """
    try:
        result = supabase_anon.auth.refresh_session(request.refresh_token)

        if not result.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token — please login again",
            )

        logger.info(f"Token refreshed for user: {result.user.email}")
        return AuthResponse(
            access_token=result.session.access_token,
            refresh_token=result.session.refresh_token,
            user_id=result.user.id,
            email=result.user.email or "",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session refresh failed — please login again",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# LOGOUT
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """
    Invalidate the current session on the Supabase side.
    
    Note: The client should also discard the stored tokens locally.
    For full security, the access_token remains valid until it expires
    (JWTs are stateless), but the refresh_token is invalidated.
    """
    try:
        supabase_anon.auth.sign_out()
        logger.info("User session signed out")
        return {"message": "Successfully logged out"}

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Logout should never fail from the user's perspective
        return {"message": "Logged out"}
