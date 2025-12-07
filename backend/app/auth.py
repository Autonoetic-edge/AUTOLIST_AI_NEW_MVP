"""
JWT Authentication helpers and route handlers.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .config import settings
from .models import TokenResponse, UserCreate, UserLogin, UserResponse, TokenPayload

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Auth router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: The user ID to encode in the token
        expires_delta: Optional custom expiry time

    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)

    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT token string

    Returns:
        TokenPayload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenPayload(
            sub=payload["sub"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
        )
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependency to get the current authenticated user ID from token.

    Args:
        token: JWT token from Authorization header

    Returns:
        User ID string

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception

    # Check if token is expired
    if datetime.now(timezone.utc) > token_data.exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data.sub


# TODO: Replace with actual MongoDB user lookup
async def get_user_by_email(email: str) -> Optional[dict]:
    """
    Get user by email from database.

    TODO: Implement MongoDB lookup
    Example:
        from .database import get_db
        db = get_db()
        return await db.users.find_one({"email": email})
    """
    # Mock user for development
    if email == "demo@autolist.ai":
        return {
            "id": "user_demo_123",
            "email": "demo@autolist.ai",
            "name": "Demo User",
            "hashed_password": hash_password("password123"),
            "created_at": datetime.now(timezone.utc),
        }
    return None


# TODO: Replace with actual MongoDB user creation
async def create_user(user_data: UserCreate) -> dict:
    """
    Create a new user in the database.

    TODO: Implement MongoDB insert
    Example:
        from .database import get_db
        db = get_db()
        user_doc = {
            "email": user_data.email,
            "name": user_data.name,
            "hashed_password": hash_password(user_data.password),
            "created_at": datetime.now(timezone.utc),
        }
        result = await db.users.insert_one(user_doc)
        user_doc["id"] = str(result.inserted_id)
        return user_doc
    """
    return {
        "id": f"user_{datetime.now().timestamp()}",
        "email": user_data.email,
        "name": user_data.name,
        "hashed_password": hash_password(user_data.password),
        "created_at": datetime.now(timezone.utc),
    }


# ============================================================================
# Auth Routes
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await create_user(user_data)
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user.get("name"),
        created_at=user["created_at"],
    )


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token."""
    user = await get_user_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user["id"])
    expires_in = settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
    )


@router.post("/token", response_model=TokenResponse)
async def login_json(credentials: UserLogin):
    """Login with JSON body and get access token."""
    user = await get_user_by_email(credentials.email)

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(user["id"])
    expires_in = settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user_id: str = Depends(get_current_user)):
    """Get current user info."""
    # TODO: Look up user by ID from MongoDB
    # For now, return mock data
    return UserResponse(
        id=current_user_id,
        email="demo@autolist.ai",
        name="Demo User",
        created_at=datetime.now(timezone.utc),
    )
