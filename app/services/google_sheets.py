import json
import logging
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from app.core.config import settings
from app.db.supabase_client import supabase

logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly'
]

def get_google_auth_flow() -> Flow:
    """Initialize the Google OAuth flow."""
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "project_id": "rag-saas",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    return flow

class GoogleSheetsService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.supabase = supabase
        self.creds = self._load_credentials()

    def _load_credentials(self) -> Optional[Credentials]:
        """Load credentials from Supabase."""
        try:
            response = self.supabase.table("google_connections").select("credentials").eq("user_id", self.user_id).execute()
            if not response.data:
                return None
                
            creds_data = response.data[0]["credentials"]
            creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
            
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self.save_credentials(json.loads(creds.to_json()))
                
            return creds
        except Exception as e:
            logger.error(f"Error loading credentials for user {self.user_id}: {e}")
            return None

    def save_credentials(self, creds_dict: dict):
        """Save credentials to Supabase."""
        try:
            # Check if exists
            existing = self.supabase.table("google_connections").select("id").eq("user_id", self.user_id).execute()
            if existing.data:
                self.supabase.table("google_connections").update({
                    "credentials": creds_dict
                }).eq("user_id", self.user_id).execute()
            else:
                self.supabase.table("google_connections").insert({
                    "user_id": self.user_id,
                    "credentials": creds_dict
                }).execute()
        except Exception as e:
            logger.error(f"Error saving credentials for user {self.user_id}: {e}")
            raise e

    def get_service(self, service_name='sheets', version='v4'):
        if not self.creds:
            raise Exception("Google credentials not found or expired. Please reconnect.")
        return build(service_name, version, credentials=self.creds)

    def list_spreadsheets(self) -> List[Dict[str, Any]]:
        """List spreadsheets in the user's Google Drive."""
        drive_service = self.get_service('drive', 'v3')
        results = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.spreadsheet'",
            pageSize=10, fields="nextPageToken, files(id, name)"
        ).execute()
        return results.get('files', [])

    def get_sheet_data(self, spreadsheet_id: str, range_name: str) -> List[List[Any]]:
        """Read data from a specific sheet range."""
        service = self.get_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        return result.get('values', [])

    def append_row(self, spreadsheet_id: str, range_name: str, values: List[Any]) -> bool:
        """Append a row of data to a sheet."""
        service = self.get_service()
        body = {'values': [values]}
        try:
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error appending row: {e}")
            return False

    def update_cell(self, spreadsheet_id: str, range_name: str, value: Any) -> bool:
        """Update a specific cell or range."""
        service = self.get_service()
        body = {'values': [[value]]}
        try:
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating cell: {e}")
            return False
