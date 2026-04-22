"""
Supabase Client — Singleton connection to Supabase services.

Two clients are initialized:
  1. `supabase` — uses the SERVICE_ROLE key (bypasses RLS, for backend operations)
  2. `supabase_anon` — uses the ANON key (respects RLS, for user-context operations)

The backend primarily uses the service_role client since we handle
authorization ourselves via JWT verification in the auth middleware.
"""

from supabase import create_client, Client
from app.core.config import settings
from app.core.logging import logger


def _create_supabase_client(key: str, label: str) -> Client:
    """Create and validate a Supabase client instance."""
    if not settings.SUPABASE_URL or not key:
        logger.error(f"Supabase {label} credentials missing — check .env or Railway variables")
        raise ValueError(f"SUPABASE_URL and {label} key are required")
    
    client = create_client(settings.SUPABASE_URL, key)
    logger.info(f"Supabase {label} client initialized → {settings.SUPABASE_URL}")
    return client


# ─── Primary client (service role) — bypasses RLS for backend operations ───
supabase: Client = _create_supabase_client(
    settings.SUPABASE_SERVICE_ROLE_KEY,
    "SERVICE_ROLE"
)

# ─── Anon client — used for auth operations that need to respect user context ─
supabase_anon: Client = _create_supabase_client(
    settings.SUPABASE_ANON_KEY,
    "ANON"
)
