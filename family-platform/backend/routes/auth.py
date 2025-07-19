from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from database import get_db
from models.user import User, UserStatus
from utils.auth import (
    create_access_token, create_refresh_token, verify_password, 
    get_password_hash, create_email_verification_token, 
    verify_email_verification_token
)
from utils.email import send_verification_email, send_password_reset_email
from utils.validators import validate_email, validate_password

router = APIRouter()
security = HTTPBearer()

# Pydantic models for request/response
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class EmailVerification(BaseModel):
    token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str
    confirm_password: str

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from JWT token"""
    from utils.auth import verify_token
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if user.status not in [UserStatus.ACTIVE, UserStatus.PENDING_VERIFICATION]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or inactive"
        )
    
    return user

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account"""
    
    # Validate email format
    email_validation = validate_email(user_data.email)
    if not email_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": "email", "errors": email_validation["errors"]}
        )
    
    # Validate password
    password_validation = validate_password(user_data.password)
    if not password_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": "password", "errors": password_validation["errors"]}
        )
    
    # Check password confirmation
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": "confirm_password", "errors": ["Passwords do not match"]}
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address is already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    verification_token = create_email_verification_token(user_data.email.lower())
    
    new_user = User(
        email=user_data.email.lower(),
        hashed_password=hashed_password,
        email_verification_token=verification_token,
        status=UserStatus.PENDING_VERIFICATION
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send verification email
    try:
        await send_verification_email(user_data.email.lower(), verification_token)
    except Exception as e:
        # Log error but don't fail registration
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send verification email: {e}")
    
    return {
        "message": "Registration successful! Please check your email to verify your account.",
        "user_id": new_user.id,
        "email": new_user.email,
        "status": "pending_verification"
    }

@router.post("/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin, 
    response: Response,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email.lower()).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check user status
    if user.status == UserStatus.BANNED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been banned"
        )
    elif user.status == UserStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily suspended"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
    
    # Set refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Use in production with HTTPS
        samesite="strict",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60,  # 30 minutes
        user={
            "id": user.id,
            "email": user.email,
            "status": user.status.value,
            "is_email_verified": user.is_email_verified,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    )

@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerification, 
    db: Session = Depends(get_db)
):
    """Verify user email address with token"""
    
    # Verify token and get email
    email = verify_email_verification_token(verification_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already verified
    if user.is_email_verified:
        return {
            "message": "Email address is already verified",
            "status": "already_verified"
        }
    
    # Update user verification status
    user.is_email_verified = True
    user.email_verification_token = None
    user.status = UserStatus.ACTIVE
    
    db.commit()
    
    return {
        "message": "Email address verified successfully!",
        "status": "verified"
    }

@router.post("/resend-verification")
async def resend_verification(
    email_data: dict,
    db: Session = Depends(get_db)
):
    """Resend email verification"""
    
    email = email_data.get("email", "").lower()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is required"
        )
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't reveal if email exists for security
        return {
            "message": "If an account with this email exists, a verification email has been sent."
        }
    
    # Check if already verified
    if user.is_email_verified:
        return {
            "message": "Email address is already verified"
        }
    
    # Generate new verification token
    verification_token = create_email_verification_token(email)
    user.email_verification_token = verification_token
    db.commit()
    
    # Send verification email
    try:
        await send_verification_email(email, verification_token)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send verification email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )
    
    return {
        "message": "Verification email sent successfully"
    }

@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing refresh token"""
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "status": current_user.status.value,
        "role": current_user.role.value,
        "is_email_verified": current_user.is_email_verified,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
        "created_at": current_user.created_at.isoformat()
    }

@router.post("/refresh-token")
async def refresh_access_token(
    request: dict,
    response: Response,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    refresh_token = request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required"
        )
    
    # Verify refresh token
    from utils.auth import verify_token
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.status not in [UserStatus.ACTIVE, UserStatus.PENDING_VERIFICATION]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return {
        "access_token": access_token,
        "expires_in": 30 * 60  # 30 minutes
    }