import contextvars
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import logging

from app.database import get_user_by_token

# Store the authenticated user ID for the current async task
current_user_id = contextvars.ContextVar("current_user_id", default=None)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # We only care about authenticating MCP endpoints
        if request.url.path.startswith("/mcp"):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                logging.error("Authentication failed: Missing or invalid Authorization header")
                return JSONResponse({"error": "Unauthorized"}, status_code=401)
            
            token = auth_header.split(" ")[1]
            user = get_user_by_token(token)
            
            if not user:
                logging.error(f"Authentication failed: Invalid token used")
                return JSONResponse({"error": "Unauthorized"}, status_code=401)
            
            logging.info(f"Authentication success: User '{user['username']}' (ID: {user['id']}) authenticated")
            
            # Set the context variable so tools can access it
            current_user_id.set(user["id"])
            
        return await call_next(request)

def get_current_user_id() -> int:
    user_id = current_user_id.get()
    if user_id is None:
        raise RuntimeError("No authenticated user found in context.")
    return user_id
