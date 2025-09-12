from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud, schemas
from app.core.security import create_access_token, verify_token, verify_password
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current authenticated user from cookie"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception
    
    try:
        user_id = verify_token(token)
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user

@router.post("/signup")
def signup(user: schemas.UserCreate, response: Response, db: Session = Depends(get_db)):
    """Create new user account"""
    try:
        # Check if user already exists
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        db_user = crud.create_user(db=db, user=user)
        
        # Create access token
        access_token = create_access_token(data={"sub": str(db_user.id)})
        
        # Set httpOnly cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=86400  # 24 hours
        )
        
        return {
            "message": "User created successfully",
            "user": {
                "id": str(db_user.id),
                "email": db_user.email,
                "name": db_user.name
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login")
def login(user_credentials: schemas.UserLogin, response: Response, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    try:
        # Get user by email
        user = crud.get_user_by_email(db, email=user_credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(user_credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Set httpOnly cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=86400  # 24 hours
        )
        
        return {
            "message": "Login successful",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout")
def logout(response: Response):
    """Logout user by clearing the authentication cookie"""
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}

@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user