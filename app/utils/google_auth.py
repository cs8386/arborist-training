"""Google OAuth2 flow for Slides/Drive access."""
import json
from pathlib import Path
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_SCOPES, BASE_URL

# OAuth redirect - must match Google Cloud Console
REDIRECT_URI = f"{BASE_URL.rstrip('/')}/auth/google/callback"


def get_oauth_flow():
    """Create OAuth flow for Google sign-in."""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=GOOGLE_SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    return flow


def credentials_to_dict(creds: Credentials) -> dict:
    """Convert Credentials to JSON-serializable dict for session storage."""
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else GOOGLE_SCOPES,
    }


def dict_to_credentials(data: dict) -> Credentials:
    """Restore Credentials from session dict."""
    return Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=data.get("client_id", GOOGLE_CLIENT_ID),
        client_secret=data.get("client_secret", GOOGLE_CLIENT_SECRET),
        scopes=data.get("scopes", GOOGLE_SCOPES),
    )
