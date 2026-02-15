"""
Authentication and User Management API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import timedelta
from loguru import logger

from app.models import (
    LoginRequest, LoginResponse, UserResponse, CreateUserRequest,
    UpdateUserRequest, ChangePasswordRequest, UserUsageReportRequest,
    UserUsageReportResponse, UsageMonthlySummary, UsageDailyBreakdown
)
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_active_user, get_current_admin_user, TokenData,
    validate_password_strength, ACCESS_TOKEN_EXPIRE_DAYS
)
from app.services.database_service import db_service

router = APIRouter(prefix="/v1/auth", tags=["authentication"])
user_router = APIRouter(prefix="/v1/users", tags=["users"])


# ==================== AUTHENTICATION ENDPOINTS ====================

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """
    Login endpoint.
    
    Args:
        login_data: Email and password
    
    Returns:
        Access token and user info
    """
    try:
        # Get user from database
        user = db_service.get_user_by_email(login_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        # Verify password
        if not verify_password(login_data.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        # Check if user is active
        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled. Contact administrator.",
            )
        
        # Update last login
        db_service.update_last_login(user['id'])
        
        # Create access token
        token_expiry = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS) if login_data.remember_me else timedelta(days=1)
        access_token = create_access_token(
            data={
                "sub": str(user['id']),  # JWT 'sub' must be a string
                "email": user['email'],
                "username": user['username'],
                "is_admin": user['is_admin']
            },
            expires_delta=token_expiry
        )
        
        return LoginResponse(
            access_token=access_token,
            user=UserResponse(
            id=user['id'],
            email=user['email'],
            username=user['username'],
            full_name=user.get('full_name'),
            company=user.get('company'),
            profile_image_url=user.get('profile_image_url'),
            is_active=user['is_active'],
            is_admin=user['is_admin'],
            created_at=user['created_at'],
            last_login=user.get('last_login')
        )
    )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again.",
        )


@router.post("/token")
async def login_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token endpoint.
    
    Args:
        form_data: OAuth2 password form (username=email, password)
    
    Returns:
        Access token
    """
    # Get user from database (username field contains email)
    user = db_service.get_user_by_email(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    # Update last login
    db_service.update_last_login(user['id'])
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user['id'],
            "email": user['email'],
            "username": user['username'],
            "is_admin": user['is_admin']
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenData = Depends(get_current_active_user)):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User information
    """
    user = db_service.get_user_by_id(current_user.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse(
        id=user['id'],
        email=user['email'],
        username=user['username'],
        full_name=user.get('full_name'),
        company=user.get('company'),
        profile_image_url=user.get('profile_image_url'),
        is_active=user['is_active'],
        is_admin=user['is_admin'],
        created_at=user['created_at'],
        last_login=user.get('last_login')
    )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Change user password.
    
    Args:
        password_data: Old and new password
        current_user: Current authenticated user
    
    Returns:
        Success message
    """
    logger.info(f"User {current_user.username} (ID: {current_user.user_id}) attempting to change password")
    
    # Get user from database
    user = db_service.get_user_by_id(current_user.user_id)
    
    if not user:
        logger.error(f"User {current_user.user_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Verify old password
    if not verify_password(password_data.old_password, user['password_hash']):
        logger.warning(f"User {current_user.username} provided incorrect current password")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )
    
    # Validate new password strength
    is_valid, error_msg = validate_password_strength(password_data.new_password)
    if not is_valid:
        logger.warning(f"User {current_user.username} new password failed validation: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    
    # Update password
    password_hash = get_password_hash(password_data.new_password)
    logger.info(f"Updating password for user {current_user.username} (ID: {current_user.user_id})")
    updated = db_service.update_user(current_user.user_id, password_hash=password_hash)
    
    if not updated:
        logger.error(f"Failed to update password for user {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password",
        )
    
    logger.info(f"Password successfully changed for user {current_user.username} (ID: {current_user.user_id})")
    return {"message": "Password changed successfully"}


@router.put("/me", response_model=UserResponse)
async def update_own_profile(
    user_data: UpdateUserRequest,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Update own user profile (non-admin users can update their own profile).
    
    Args:
        user_data: Updated profile data
        current_user: Current authenticated user
    
    Returns:
        Updated user information
    """
    # Users can only update their own full_name, company, and profile_image_url
    # They cannot change email, username, is_active, or is_admin
    update_params = {}
    
    if user_data.full_name is not None:
        update_params['full_name'] = user_data.full_name
    
    if user_data.company is not None:
        update_params['company'] = user_data.company
    
    if user_data.profile_image_url is not None:
        update_params['profile_image_url'] = user_data.profile_image_url
    
    if not update_params:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update",
        )
    
    # Update user
    updated_user = db_service.update_user(current_user.user_id, **update_params)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or update failed",
        )
    
    logger.info(f"User {current_user.username} updated their profile")
    
    return UserResponse(**updated_user)


# ==================== USER MANAGEMENT ENDPOINTS (ADMIN ONLY) ====================

@user_router.get("/", response_model=List[UserResponse])
async def get_all_users(current_user: TokenData = Depends(get_current_admin_user)):
    """
    Get all users (admin only).
    
    Args:
        current_user: Current admin user
    
    Returns:
        List of all users
    """
    users = db_service.get_all_users()
    return [UserResponse(**user) for user in users]


@user_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: CreateUserRequest,
    current_user: TokenData = Depends(get_current_admin_user)
):
    """
    Create new user (admin only).
    
    Args:
        user_data: User data
        current_user: Current admin user
    
    Returns:
        Created user
    """
    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    
    # Hash password
    password_hash = get_password_hash(user_data.password)
    
    # Create user
    user = db_service.create_user(
        email=user_data.email,
        username=user_data.username,
        password_hash=password_hash,
        full_name=user_data.full_name,
        company=user_data.company,
        is_admin=user_data.is_admin
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )
    
    logger.info(f"Admin {current_user.username} created new user: {user['email']}")
    
    # TODO: Send email with credentials (future enhancement)
    
    return UserResponse(**user)


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: TokenData = Depends(get_current_admin_user)
):
    """
    Get user by ID (admin only).
    
    Args:
        user_id: User ID
        current_user: Current admin user
    
    Returns:
        User information
    """
    user = db_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse(
        id=user['id'],
        email=user['email'],
        username=user['username'],
        full_name=user.get('full_name'),
        company=user.get('company'),
        profile_image_url=user.get('profile_image_url'),
        is_active=user['is_active'],
        is_admin=user['is_admin'],
        created_at=user['created_at'],
        last_login=user.get('last_login')
    )


@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UpdateUserRequest,
    current_user: TokenData = Depends(get_current_admin_user)
):
    """
    Update user (admin only).
    
    Args:
        user_id: User ID
        user_data: Updated user data
        current_user: Current admin user
    
    Returns:
        Updated user
    """
    logger.info(f"Admin {current_user.username} updating user {user_id}")
    logger.info(f"Update data received: {user_data.model_dump(exclude_unset=True)}")
    
    # Prevent admin from deactivating themselves
    if user_id == current_user.user_id and user_data.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )
    
    # Prepare update parameters - only include fields that are actually set
    update_params = {}
    
    if user_data.email is not None:
        update_params['email'] = user_data.email
    
    if user_data.username is not None:
        update_params['username'] = user_data.username
    
    if user_data.full_name is not None:
        update_params['full_name'] = user_data.full_name
    
    if user_data.company is not None:
        update_params['company'] = user_data.company
    
    if user_data.profile_image_url is not None:
        update_params['profile_image_url'] = user_data.profile_image_url
    
    if user_data.is_active is not None:
        update_params['is_active'] = user_data.is_active
    
    # Hash password if provided
    if user_data.password:
        logger.info(f"Password provided for user {user_id}, hashing it")
        update_params['password_hash'] = get_password_hash(user_data.password)
    else:
        logger.info(f"No password provided for user {user_id}, keeping existing password")
    
    logger.info(f"Final update params: {list(update_params.keys())}")
    
    # Update user
    updated_user = db_service.update_user(user_id, **update_params)
    
    if not updated_user:
        logger.error(f"Failed to update user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or update failed",
        )
    
    logger.info(f"Admin {current_user.username} successfully updated user: {updated_user['email']}")
    
    return UserResponse(
        id=updated_user['id'],
        email=updated_user['email'],
        username=updated_user['username'],
        full_name=updated_user.get('full_name'),
        company=updated_user.get('company'),
        profile_image_url=updated_user.get('profile_image_url'),
        is_active=updated_user['is_active'],
        is_admin=updated_user['is_admin'],
        created_at=updated_user['created_at'],
        last_login=updated_user.get('last_login')
    )
    
    return UserResponse(**updated_user)


@user_router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: TokenData = Depends(get_current_admin_user)
):
    """
    Delete (deactivate) user (admin only).
    
    Args:
        user_id: User ID
        current_user: Current admin user
    
    Returns:
        Success message
    """
    # Prevent admin from deleting themselves
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    
    success = db_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or deletion failed",
        )
    
    logger.info(f"Admin {current_user.username} deactivated user ID: {user_id}")
    
    return {"message": "User deactivated successfully"}


# ==================== USAGE TRACKING ENDPOINTS ====================

@user_router.post("/usage-report", response_model=UserUsageReportResponse)
async def get_user_usage_report(
    request: UserUsageReportRequest,
    current_user: TokenData = Depends(get_current_admin_user)
):
    """
    Get user usage report for specific month (admin only).
    
    Args:
        request: User ID, year, month
        current_user: Current admin user
    
    Returns:
        Usage report with daily breakdown
    """
    # Get user
    user = db_service.get_user_by_id(request.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Get daily breakdown
    daily_usage = db_service.get_user_daily_usage(request.user_id, request.year, request.month)
    
    # Get monthly summary
    monthly_summary = db_service.get_user_monthly_summary(request.user_id, request.year, request.month)
    
    if not monthly_summary:
        monthly_summary = {
            'total_searches': 0,
            'youtube_searches': 0,
            'twitter_searches': 0,
            'facebook_searches': 0,
            'instagram_searches': 0,
            'google_searches': 0,
            'total_scrapings': 0,
            'total_analyses': 0,
            'google_api_calls': 0,
            'scrapecreators_credits': 0,
            'claude_tokens': 0,
            'monthly_cost_usd': 0.0
        }
    
    return UserUsageReportResponse(
        user=UserResponse(
            id=user['id'],
            email=user['email'],
            username=user['username'],
            full_name=user.get('full_name'),
            company=user.get('company'),
            profile_image_url=user.get('profile_image_url'),
            is_active=user['is_active'],
            is_admin=user['is_admin'],
            created_at=user['created_at'],
            last_login=user.get('last_login')
        ),
        usage=UsageMonthlySummary(
            year=request.year,
            month=request.month,
            **monthly_summary,
            daily_breakdown=[UsageDailyBreakdown(**day) for day in daily_usage]
        )
    )


@router.get("/my-usage", response_model=dict)
async def get_my_usage(current_user: TokenData = Depends(get_current_active_user)):
    """
    Get current user's total usage and cost.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Usage statistics
    """
    total_cost = db_service.get_user_total_cost(current_user.user_id)
    
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "total_cost_usd": total_cost
    }
