import time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse

from open_webui.models.token_usage import (
    TokenUsageCreate,
    UserTokenLimitsCreate,
    UserTokenLimitsUpdate,
    TokenUsageSummary,
    token_usage_table,
    user_token_limits_table
)
from open_webui.models.users import Users
from open_webui.utils.auth import get_current_user, get_admin_user
from open_webui.utils.response import convert_ollama_usage_to_openai

router = APIRouter(prefix="/api/token-usage", tags=["token-usage"])


############################
# Token Usage Tracking
############################


@router.post("/track")
async def track_token_usage(
    usage_data: TokenUsageCreate,
    user=Depends(get_current_user)
):
    """Track token usage for a user"""
    try:
        # Verify the user is tracking their own usage or is admin
        if user.id != usage_data.user_id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only track your own token usage"
            )
        
        # Insert the usage record
        usage = token_usage_table.insert_token_usage(usage_data)
        if not usage:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to track token usage"
            )
        
        # Update usage counts in limits table
        user_token_limits_table.update_usage_counts(
            usage_data.user_id, 
            usage_data.total_tokens
        )
        
        return {"success": True, "usage_id": usage.id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/user/{user_id}")
async def get_user_token_usage(
    user_id: str,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    user=Depends(get_current_user)
):
    """Get token usage for a specific user"""
    try:
        # Verify the user is requesting their own usage or is admin
        if user.id != user_id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own token usage"
            )
        
        usage = token_usage_table.get_user_token_usage(
            user_id, start_time, end_time
        )
        
        return {"usage": usage}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/user/{user_id}/summary")
async def get_user_token_summary(
    user_id: str,
    user=Depends(get_current_user)
):
    """Get token usage summary for a specific user"""
    try:
        # Verify the user is requesting their own summary or is admin
        if user.id != user_id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own token summary"
            )
        
        # Get user limits
        limits = user_token_limits_table.get_user_limits(user_id)
        
        # Get total tokens used
        total_tokens = token_usage_table.get_total_tokens_by_user(user_id)
        
        # Get recent usage for daily/monthly
        current_time = int(time.time())
        day_ago = current_time - 86400
        month_ago = current_time - 2592000
        
        daily_usage = token_usage_table.get_user_token_usage(
            user_id, start_time=day_ago
        )
        monthly_usage = token_usage_table.get_user_token_usage(
            user_id, start_time=month_ago
        )
        
        daily_tokens = sum(u.total_tokens for u in daily_usage)
        monthly_tokens = sum(u.total_tokens for u in monthly_usage)
        
        # Calculate percentages
        daily_percentage = None
        monthly_percentage = None
        total_percentage = None
        
        if limits and limits.daily_token_limit:
            daily_percentage = (daily_tokens / limits.daily_token_limit) * 100
        
        if limits and limits.monthly_token_limit:
            monthly_percentage = (monthly_tokens / limits.monthly_token_limit) * 100
        
        if limits and limits.total_token_limit:
            total_percentage = (total_tokens / limits.total_token_limit) * 100
        
        summary = TokenUsageSummary(
            user_id=user_id,
            total_tokens=total_tokens,
            prompt_tokens=sum(u.prompt_tokens for u in monthly_usage),
            completion_tokens=sum(u.completion_tokens for u in monthly_usage),
            daily_tokens=daily_tokens,
            monthly_tokens=monthly_tokens,
            daily_limit=limits.daily_token_limit if limits else None,
            monthly_limit=limits.monthly_token_limit if limits else None,
            total_limit=limits.total_token_limit if limits else None,
            daily_usage_percentage=daily_percentage,
            monthly_usage_percentage=monthly_percentage,
            total_usage_percentage=total_percentage
        )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


############################
# Admin Token Limits Management
############################


@router.post("/admin/limits", response_model=dict)
async def create_user_token_limits(
    limits_data: UserTokenLimitsCreate,
    user=Depends(get_admin_user)
):
    """Create token limits for a user (admin only)"""
    try:
        # Verify user exists
        target_user = Users.get_user_by_id(limits_data.user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if limits already exist
        existing_limits = user_token_limits_table.get_user_limits(limits_data.user_id)
        if existing_limits:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token limits already exist for this user"
            )
        
        # Create limits
        limits = user_token_limits_table.create_user_limits(limits_data)
        if not limits:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create token limits"
            )
        
        return {"success": True, "limits": limits.model_dump()}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/admin/limits/{user_id}")
async def get_user_token_limits(
    user_id: str,
    user=Depends(get_admin_user)
):
    """Get token limits for a specific user (admin only)"""
    try:
        limits = user_token_limits_table.get_user_limits(user_id)
        if not limits:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token limits not found for this user"
            )
        
        return limits
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/admin/limits/{user_id}")
async def update_user_token_limits(
    user_id: str,
    update_data: UserTokenLimitsUpdate,
    user=Depends(get_admin_user)
):
    """Update token limits for a user (admin only)"""
    try:
        # Verify user exists
        target_user = Users.get_user_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update limits
        limits = user_token_limits_table.update_user_limits(user_id, update_data)
        if not limits:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update token limits"
            )
        
        return {"success": True, "limits": limits.model_dump()}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/admin/limits/{user_id}")
async def delete_user_token_limits(
    user_id: str,
    user=Depends(get_admin_user)
):
    """Delete token limits for a user (admin only)"""
    try:
        # Verify user exists
        target_user = Users.get_user_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Delete limits
        success = user_token_limits_table.delete_user_limits(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete token limits"
            )
        
        return {"success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/admin/limits")
async def get_all_user_token_limits(
    user=Depends(get_admin_user)
):
    """Get token limits for all users (admin only)"""
    try:
        limits = user_token_limits_table.get_all_user_limits()
        return {"limits": limits}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/admin/usage/summary")
async def get_all_users_token_summary(
    user=Depends(get_admin_user)
):
    """Get token usage summary for all users (admin only)"""
    try:
        # Get all users
        users_response = Users.get_users()
        users = users_response.get("users", [])
        
        summaries = []
        for user_info in users:
            user_id = user_info.id
            
            # Get user limits
            limits = user_token_limits_table.get_user_limits(user_id)
            
            # Get total tokens used
            total_tokens = token_usage_table.get_total_tokens_by_user(user_id)
            
            # Get recent usage for daily/monthly
            current_time = int(time.time())
            day_ago = current_time - 86400
            month_ago = current_time - 2592000
            
            daily_usage = token_usage_table.get_user_token_usage(
                user_id, start_time=day_ago
            )
            monthly_usage = token_usage_table.get_user_token_usage(
                user_id, start_time=month_ago
            )
            
            daily_tokens = sum(u.total_tokens for u in daily_usage)
            monthly_tokens = sum(u.total_tokens for u in monthly_usage)
            
            # Calculate percentages
            daily_percentage = None
            monthly_percentage = None
            total_percentage = None
            
            if limits and limits.daily_token_limit:
                daily_percentage = (daily_tokens / limits.daily_token_limit) * 100
            
            if limits and limits.monthly_token_limit:
                monthly_percentage = (monthly_tokens / limits.monthly_token_limit) * 100
            
            if limits and limits.total_token_limit:
                total_percentage = (total_tokens / limits.total_token_limit) * 100
            
            summary = TokenUsageSummary(
                user_id=user_id,
                total_tokens=total_tokens,
                prompt_tokens=sum(u.prompt_tokens for u in monthly_usage),
                completion_tokens=sum(u.completion_tokens for u in monthly_usage),
                daily_tokens=daily_tokens,
                monthly_tokens=monthly_tokens,
                daily_limit=limits.daily_token_limit if limits else None,
                monthly_limit=limits.monthly_token_limit if limits else None,
                total_limit=limits.total_token_limit if limits else None,
                daily_usage_percentage=daily_percentage,
                monthly_usage_percentage=monthly_percentage,
                total_usage_percentage=total_percentage
            )
            
            summaries.append(summary)
        
        return {"summaries": summaries}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


############################
# Utility Endpoints
############################


@router.post("/convert-ollama-usage")
async def convert_ollama_usage(ollama_usage: dict):
    """Convert Ollama usage format to OpenAI format"""
    try:
        converted = convert_ollama_usage_to_openai(ollama_usage)
        return converted
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert usage format: {str(e)}"
        ) 