# Security
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
VALID_TOKEN = "buildops-secret-token-2025"  # Hardcoded for demo


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials
