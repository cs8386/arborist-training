"""App login auth - JWT verification for API protection."""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import SECRET_KEY, ACCESS_PASSWORD

security = HTTPBearer(auto_error=False)


def create_token() -> str:
    """Create a JWT for authenticated access."""
    import datetime
    return jwt.encode(
        {"sub": "user", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)},
        SECRET_KEY,
        algorithm="HS256",
    )


def verify_token(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> bool:
    """Verify JWT from Authorization header. Raises 401 if invalid."""
    if not ACCESS_PASSWORD:
        return True  # No password set = no protection
    if not credentials:
        raise HTTPException(status_code=401, detail="Login required")
    try:
        jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return True
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
