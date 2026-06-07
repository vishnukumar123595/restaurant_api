"""
Security: API Key authentication via X-API-Key header.

How it works in Swagger:
  1. Open http://127.0.0.1:8000/docs
  2. Click the green "Authorize" button (top right)
  3. Enter:  restaurant-secret-key-2025
  4. Click Authorize → Close
  5. All 🔒 endpoints will now send the key automatically

In production override the key via the API_KEY environment variable.
"""

from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
import os

API_KEY = os.getenv("API_KEY", "restaurant-secret-key-2025")
API_KEY_NAME = "X-API-Key"

# auto_error=True  →  FastAPI registers this as an OpenAPI security scheme,
# which makes the 🔒 lock icon and "Authorize" button appear in Swagger UI.
api_key_header = APIKeyHeader(
    name=API_KEY_NAME,
    auto_error=True,          # ← THIS was the Swagger bug (was False before)
    description="API key required for all protected endpoints. "
                "Dev key: `restaurant-secret-key-2025`",
)


async def require_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Dependency injected into every protected route.
    Raises 401 if key is missing or wrong.
    """
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Unauthorized",
                "message": "Invalid API Key. Check your X-API-Key header.",
                "hint": "Dev key is: restaurant-secret-key-2025",
            },
        )
    return api_key
