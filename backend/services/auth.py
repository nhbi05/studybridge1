"""Authentication utility functions."""
import os
from fastapi import HTTPException, Header
from supabase import create_client

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)


async def get_current_user(authorization: str = Header(None)):
    """Extract and verify Supabase auth token from header.
    
    Returns the authenticated user object from Supabase.
    Raises HTTPException 401 if token is invalid or missing.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.replace("Bearer ", "")
        
        # Verify and get user from Supabase
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_response.user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
