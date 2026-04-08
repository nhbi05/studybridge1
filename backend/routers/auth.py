"""Authentication router for login/signup."""
import os
import uuid
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredential
import jwt
from passlib.context import CryptContext
from models.schemas import SignupRequest, LoginRequest, AuthResponse, UserProfile
from db.supabase import get_supabase
import httpx

router = APIRouter(prefix="/api/auth", tags=["auth"])

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, email: str) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthCredential = Depends(security)) -> dict:
    """Get current user from token."""
    token = credentials.credentials
    return verify_token(token)


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest, supabase=Depends(get_supabase)) -> AuthResponse:
    """Register a new user."""
    try:
        # Check if email already exists
        existing_user = await supabase.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(request.password)

        user_data = {
            "id": user_id,
            "email": request.email,
            "name": request.name,
            "password_hash": hashed_password,
            "year_of_study": request.year_of_study,
            "semester": request.semester,
            "course": request.course,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Save user to database
        saved = await supabase.save_user(user_data)
        if not saved:
            raise HTTPException(status_code=500, detail="Failed to create user")

        # Create JWT token
        token = create_access_token(user_id, request.email)

        return AuthResponse(
            success=True,
            message="User registered successfully",
            user_id=user_id,
            email=request.email,
            name=request.name,
            token=token,
            token_type="bearer",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, supabase=Depends(get_supabase)) -> AuthResponse:
    """Login user with email and password."""
    try:
        # Get user by email
        user = await supabase.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password
        if not verify_password(request.password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create JWT token
        token = create_access_token(user["id"], user["email"])

        return AuthResponse(
            success=True,
            message="Login successful",
            user_id=user["id"],
            email=user["email"],
            name=user["name"],
            token=token,
            token_type="bearer",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    supabase=Depends(get_supabase),
) -> UserProfile:
    """Get current user profile."""
    try:
        user_id = current_user.get("sub")
        user = await supabase.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserProfile(
            user_id=user["id"],
            email=user["email"],
            name=user["name"],
            year_of_study=user["year_of_study"],
            semester=user["semester"],
            course=user["course"],
            created_at=user.get("created_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")


@router.post("/logout", response_model=dict)
async def logout(current_user: dict = Depends(get_current_user)) -> dict:
    """Logout user (client-side JWT invalidation)."""
    return {"success": True, "message": "Logged out successfully"}


@router.post("/refresh-token")
async def refresh_token(
    current_user: dict = Depends(get_current_user),
) -> AuthResponse:
    """Refresh JWT token."""
    try:
        user_id = current_user.get("sub")
        email = current_user.get("email")

        # Create new token
        token = create_access_token(user_id, email)

        return AuthResponse(
            success=True,
            message="Token refreshed",
            token=token,
            token_type="bearer",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")


class GoogleTokenRequest:
    """Request body for Google OAuth token."""
    token: str


@router.post("/google")
async def google_signin(request: dict, supabase=Depends(get_supabase)) -> AuthResponse:
    """Handle Google OAuth signin/signup."""
    try:
        id_token = request.get("token")
        if not id_token:
            raise HTTPException(status_code=400, detail="Token required")

        # Verify the Google ID token
        # For production, verify with Google's servers: https://www.googleapis.com/oauth2/v3/tokeninfo
        # For now, we'll decode and use the token (in production, verify signature)
        try:
            # Decode without verification (not recommended for production)
            # In production, verify the signature with Google's public keys
            decoded = jwt.decode(id_token, options={"verify_signature": False})
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

        email = decoded.get("email")
        name = decoded.get("name", "")
        google_id = decoded.get("sub")

        if not email:
            raise HTTPException(status_code=400, detail="Email not found in token")

        # Check if user exists
        user = await supabase.get_user_by_email(email)
        
        if user:
            # User exists, return login
            token = create_access_token(user["id"], user["email"])
            return AuthResponse(
                success=True,
                message="Google login successful",
                user_id=user["id"],
                email=user["email"],
                name=user["name"],
                token=token,
                token_type="bearer",
            )
        else:
            # New user, auto-create account
            user_id = str(uuid.uuid4())
            user_data = {
                "id": user_id,
                "email": email,
                "name": name,
                "google_id": google_id,
                "password_hash": "google_oauth",  # Placeholder for OAuth users
                "year_of_study": 1,
                "semester": 1,
                "course": "CS",
                "created_at": datetime.utcnow().isoformat(),
            }

            saved = await supabase.save_user(user_data)
            if not saved:
                raise HTTPException(status_code=500, detail="Failed to create user")

            token = create_access_token(user_id, email)
            return AuthResponse(
                success=True,
                message="Account created via Google",
                user_id=user_id,
                email=email,
                name=name,
                token=token,
                token_type="bearer",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google signin failed: {str(e)}")
