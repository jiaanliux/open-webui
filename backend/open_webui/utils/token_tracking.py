import time
from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from open_webui.models.token_usage import token_usage_table, TokenUsageCreate
from open_webui.utils.auth import get_current_user_from_token


class TokenTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically track token usage from API responses"""
    
    async def dispatch(self, request: Request, call_next):
        # Get the response
        response = await call_next(request)
        
        # Only track token usage for successful responses
        if response.status_code != 200:
            return response
        
        # Try to extract token usage from response
        try:
            await self._track_token_usage(request, response)
        except Exception as e:
            # Don't fail the request if token tracking fails
            print(f"Token tracking failed: {e}")
        
        return response
    
    async def _track_token_usage(self, request: Request, response: Response):
        """Extract and track token usage from the response"""
        
        # Get user from token if available
        user = None
        try:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                user = get_current_user_from_token(token)
        except:
            pass
        
        if not user:
            return
        
        # Try to extract usage from response body
        usage_data = await self._extract_usage_from_response(response)
        if not usage_data:
            return
        
        # Create token usage record
        token_usage = TokenUsageCreate(
            user_id=user.id,
            model_id=usage_data.get("model_id"),
            session_id=usage_data.get("session_id"),
            chat_id=usage_data.get("chat_id"),
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
            request_type=usage_data.get("request_type", "api"),
            cost=usage_data.get("cost")
        )
        
        # Insert the usage record
        token_usage_table.insert_token_usage(token_usage)
    
    async def _extract_usage_from_response(self, response: Response) -> Optional[Dict[str, Any]]:
        """Extract token usage information from the response"""
        
        # Handle streaming responses
        if isinstance(response, StreamingResponse):
            return None
        
        # Try to get response body
        try:
            if hasattr(response, 'body'):
                body = response.body
                if isinstance(body, bytes):
                    body = body.decode('utf-8')
                
                # Parse JSON response
                import json
                data = json.loads(body)
                
                # Look for usage information in common patterns
                usage = data.get("usage") or data.get("token_usage") or data.get("tokens")
                if usage:
                    return {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                        "model_id": data.get("model"),
                        "request_type": "completion"
                    }
                
                # Look for chat-specific usage
                if "messages" in data:
                    return {
                        "prompt_tokens": data.get("prompt_tokens", 0),
                        "completion_tokens": data.get("completion_tokens", 0),
                        "total_tokens": data.get("total_tokens", 0),
                        "model_id": data.get("model"),
                        "chat_id": data.get("chat_id"),
                        "request_type": "chat"
                    }
                
        except Exception:
            pass
        
        return None


def track_token_usage_manually(
    user_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    model_id: Optional[str] = None,
    session_id: Optional[str] = None,
    chat_id: Optional[str] = None,
    request_type: str = "manual",
    cost: Optional[str] = None
):
    """Manually track token usage when automatic tracking isn't possible"""
    
    usage_data = TokenUsageCreate(
        user_id=user_id,
        model_id=model_id,
        session_id=session_id,
        chat_id=chat_id,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        request_type=request_type,
        cost=cost
    )
    
    return token_usage_table.insert_token_usage(usage_data)


def get_user_token_usage_summary(user_id: str) -> Dict[str, Any]:
    """Get a summary of token usage for a user"""
    
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
    
    return {
        "total_tokens": total_tokens,
        "daily_tokens": daily_tokens,
        "monthly_tokens": monthly_tokens,
        "daily_usage": daily_usage,
        "monthly_usage": monthly_usage
    } 