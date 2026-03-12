"""Google OAuth and app login endpoints."""
import base64
import json
import secrets
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.utils.google_auth import get_oauth_flow, credentials_to_dict
from app.config import ACCESS_PASSWORD
from app.auth_deps import create_token, verify_token
from app.linked_google import save_credentials, is_linked

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    password: str = ""


@router.post("/api/auth/login")
def login(data: LoginRequest):
    """Validate password and return JWT. No auth required."""
    if not ACCESS_PASSWORD:
        return {"token": create_token(), "ok": True}
    if data.password != ACCESS_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return {"token": create_token(), "ok": True}


@router.get("/api/settings/google-linked")
def get_google_linked(_=Depends(verify_token)):
    """Check if Google account is linked (for slides)."""
    return {"linked": is_linked()}


# Store Flow between redirect and callback (code_verifier lives in Flow)
_oauth_flows: dict = {}


@router.get("/auth/google")
def auth_google():
    """Legacy: redirect with credentials in URL (client-side)."""
    flow = get_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    _oauth_flows[state] = flow
    return RedirectResponse(url=authorization_url)


@router.get("/auth/google/link")
def auth_google_link():
    """Link Google account for slides - saves credentials server-side."""
    flow = get_oauth_flow()
    state = "link:" + secrets.token_urlsafe(16)
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )
    _oauth_flows[state] = flow
    return RedirectResponse(url=authorization_url)


@router.get("/auth/google/callback")
def auth_google_callback(code: str, state: str = None):
    """OAuth callback - exchange code for tokens."""
    if not state or state not in _oauth_flows:
        raise HTTPException(status_code=400, detail="Invalid OAuth state. Please try connecting again.")
    flow = _oauth_flows.pop(state)
    try:
        flow.fetch_token(code=code)
        creds = flow.credentials
        creds_dict = credentials_to_dict(creds)
        if state.startswith("link:"):
            save_credentials(creds_dict)
            return RedirectResponse(url="/#google_linked=1")
        encoded = base64.urlsafe_b64encode(json.dumps(creds_dict).encode()).decode()
        return RedirectResponse(url=f"/#credentials={encoded}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}")
