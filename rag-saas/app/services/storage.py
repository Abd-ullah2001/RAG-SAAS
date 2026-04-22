"""
Storage Service — File persistence via Supabase Storage.

Handles uploading, downloading, and deleting user files in the
Supabase Storage bucket. Files are stored under a user-scoped path:

    documents/{user_id}/{filename}

This ensures tenant isolation at the storage level even without RLS,
since each user's files are in their own "folder" prefix.
"""

from app.db.supabase_client import supabase
from app.core.config import settings
from app.core.logging import logger


def _build_storage_path(user_id: str, filename: str) -> str:
    """
    Build a consistent, user-scoped storage path.
    
    Pattern: {user_id}/{filename}
    Example: 550e8400-e29b-41d4-a716-446655440000/report.pdf
    """
    return f"{user_id}/{filename}"


async def upload_file_to_storage(
    user_id: str,
    filename: str,
    content: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    """
    Upload a file to Supabase Storage in the user's directory.
    
    If a file with the same name already exists, it will be overwritten (upsert).
    This is intentional — users re-uploading a file should update the version.
    
    Args:
        user_id: Authenticated user's UUID
        filename: Original filename (e.g., "report.pdf")
        content: Raw file bytes
        content_type: MIME type of the file
    
    Returns:
        The storage path that was used (for saving in the documents table)
    """
    storage_path = _build_storage_path(user_id, filename)

    try:
        # Upload with upsert=True to handle re-uploads gracefully
        supabase.storage.from_(settings.STORAGE_BUCKET).upload(
            path=storage_path,
            file=content,
            file_options={
                "content-type": content_type,
                "upsert": "true",  # overwrite if exists
            },
        )

        logger.info(f"File uploaded to storage: {storage_path}")
        return storage_path

    except Exception as e:
        logger.error(f"Storage upload failed for {storage_path}: {str(e)}")
        raise RuntimeError(f"Failed to upload file to storage: {str(e)}")


async def download_file_from_storage(user_id: str, filename: str) -> bytes:
    """
    Download a file from Supabase Storage.
    
    Args:
        user_id: Owner's UUID (for path construction)
        filename: Name of the file to download
    
    Returns:
        Raw file bytes
    """
    storage_path = _build_storage_path(user_id, filename)

    try:
        data = supabase.storage.from_(settings.STORAGE_BUCKET).download(storage_path)
        logger.info(f"File downloaded from storage: {storage_path}")
        return data

    except Exception as e:
        logger.error(f"Storage download failed for {storage_path}: {str(e)}")
        raise RuntimeError(f"Failed to download file: {str(e)}")


async def delete_file_from_storage(user_id: str, filename: str) -> bool:
    """
    Delete a file from Supabase Storage.
    
    Args:
        user_id: Owner's UUID
        filename: Name of the file to delete
    
    Returns:
        True if deletion succeeded
    """
    storage_path = _build_storage_path(user_id, filename)

    try:
        supabase.storage.from_(settings.STORAGE_BUCKET).remove([storage_path])
        logger.info(f"File deleted from storage: {storage_path}")
        return True

    except Exception as e:
        logger.error(f"Storage deletion failed for {storage_path}: {str(e)}")
        raise RuntimeError(f"Failed to delete file: {str(e)}")
