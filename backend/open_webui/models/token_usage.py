import time
from typing import Optional, Dict, Any

from open_webui.internal.db import Base, JSONField, get_db
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, Integer, Boolean


####################
# Token Usage DB Schema
####################


class TokenUsage(Base):
    __tablename__ = "token_usage"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    model_id = Column(String, nullable=True)  # Optional: track per model
    session_id = Column(String, nullable=True)  # Optional: track per session
    chat_id = Column(String, nullable=True)  # Optional: track per chat
    
    # Token counts
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Metadata
    request_type = Column(String, nullable=True)  # e.g., "chat", "completion", "function_call"
    cost = Column(String, nullable=True)  # Optional: cost in currency
    
    # Timestamps
    created_at = Column(BigInteger, default=lambda: int(time.time()))
    updated_at = Column(BigInteger, default=lambda: int(time.time()))


class UserTokenLimits(Base):
    __tablename__ = "user_token_limits"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, unique=True)
    
    # Token limits
    daily_token_limit = Column(BigInteger, nullable=True)  # Daily limit in tokens
    monthly_token_limit = Column(BigInteger, nullable=True)  # Monthly limit in tokens
    total_token_limit = Column(BigInteger, nullable=True)  # Total lifetime limit
    
    # Usage tracking
    daily_tokens_used = Column(BigInteger, default=0)
    monthly_tokens_used = Column(BigInteger, default=0)
    total_tokens_used = Column(BigInteger, default=0)
    
    # Reset tracking
    last_daily_reset = Column(BigInteger, default=lambda: int(time.time()))
    last_monthly_reset = Column(BigInteger, default=lambda: int(time.time()))
    
    # Settings
    is_active = Column(Boolean, default=True)
    notify_at_percentage = Column(Integer, default=80)  # Notify when usage reaches this percentage
    
    # Timestamps
    created_at = Column(BigInteger, default=lambda: int(time.time()))
    updated_at = Column(BigInteger, default=lambda: int(time.time()))


####################
# Pydantic Models
####################


class TokenUsageModel(BaseModel):
    id: str
    user_id: str
    model_id: Optional[str] = None
    session_id: Optional[str] = None
    chat_id: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    request_type: Optional[str] = None
    cost: Optional[str] = None
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)


class UserTokenLimitsModel(BaseModel):
    id: str
    user_id: str
    daily_token_limit: Optional[int] = None
    monthly_token_limit: Optional[int] = None
    total_token_limit: Optional[int] = None
    daily_tokens_used: int = 0
    monthly_tokens_used: int = 0
    total_tokens_used: int = 0
    last_daily_reset: int
    last_monthly_reset: int
    is_active: bool = True
    notify_at_percentage: int = 80
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)


class TokenUsageCreate(BaseModel):
    user_id: str
    model_id: Optional[str] = None
    session_id: Optional[str] = None
    chat_id: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    request_type: Optional[str] = None
    cost: Optional[str] = None


class UserTokenLimitsCreate(BaseModel):
    user_id: str
    daily_token_limit: Optional[int] = None
    monthly_token_limit: Optional[int] = None
    total_token_limit: Optional[int] = None
    notify_at_percentage: int = 80


class UserTokenLimitsUpdate(BaseModel):
    daily_token_limit: Optional[int] = None
    monthly_token_limit: Optional[int] = None
    total_token_limit: Optional[int] = None
    is_active: Optional[bool] = None
    notify_at_percentage: Optional[int] = None


class TokenUsageSummary(BaseModel):
    user_id: str
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    daily_tokens: int
    monthly_tokens: int
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None
    total_limit: Optional[int] = None
    daily_usage_percentage: Optional[float] = None
    monthly_usage_percentage: Optional[float] = None
    total_usage_percentage: Optional[float] = None


####################
# Database Operations
####################


class TokenUsageTable:
    def insert_token_usage(self, usage_data: TokenUsageCreate) -> Optional[TokenUsageModel]:
        """Insert a new token usage record"""
        try:
            with get_db() as db:
                usage = TokenUsage(
                    id=f"{usage_data.user_id}_{int(time.time() * 1000)}",
                    **usage_data.model_dump()
                )
                db.add(usage)
                db.commit()
                db.refresh(usage)
                return TokenUsageModel.model_validate(usage)
        except Exception as e:
            print(f"Error inserting token usage: {e}")
            return None

    def get_user_token_usage(
        self, 
        user_id: str, 
        start_time: Optional[int] = None, 
        end_time: Optional[int] = None
    ) -> list[TokenUsageModel]:
        """Get token usage for a specific user within a time range"""
        try:
            with get_db() as db:
                query = db.query(TokenUsage).filter(TokenUsage.user_id == user_id)
                
                if start_time:
                    query = query.filter(TokenUsage.created_at >= start_time)
                if end_time:
                    query = query.filter(TokenUsage.created_at <= end_time)
                
                usages = query.order_by(TokenUsage.created_at.desc()).all()
                return [TokenUsageModel.model_validate(usage) for usage in usages]
        except Exception as e:
            print(f"Error getting user token usage: {e}")
            return []

    def get_total_tokens_by_user(self, user_id: str) -> int:
        """Get total tokens used by a user"""
        try:
            with get_db() as db:
                result = db.query(TokenUsage.total_tokens).filter(
                    TokenUsage.user_id == user_id
                ).all()
                return sum(row[0] for row in result) if result else 0
        except Exception as e:
            print(f"Error getting total tokens by user: {e}")
            return 0


class UserTokenLimitsTable:
    def create_user_limits(self, limits_data: UserTokenLimitsCreate) -> Optional[UserTokenLimitsModel]:
        """Create token limits for a user"""
        try:
            with get_db() as db:
                limits = UserTokenLimits(
                    id=limits_data.user_id,
                    **limits_data.model_dump()
                )
                db.add(limits)
                db.commit()
                db.refresh(limits)
                return UserTokenLimitsModel.model_validate(limits)
        except Exception as e:
            print(f"Error creating user token limits: {e}")
            return None

    def get_user_limits(self, user_id: str) -> Optional[UserTokenLimitsModel]:
        """Get token limits for a specific user"""
        try:
            with get_db() as db:
                limits = db.query(UserTokenLimits).filter(
                    UserTokenLimits.user_id == user_id
                ).first()
                return UserTokenLimitsModel.model_validate(limits) if limits else None
        except Exception as e:
            print(f"Error getting user token limits: {e}")
            return None

    def update_user_limits(
        self, 
        user_id: str, 
        update_data: UserTokenLimitsUpdate
    ) -> Optional[UserTokenLimitsModel]:
        """Update token limits for a user"""
        try:
            with get_db() as db:
                update_dict = update_data.model_dump(exclude_unset=True)
                update_dict["updated_at"] = int(time.time())
                
                result = db.query(UserTokenLimits).filter(
                    UserTokenLimits.user_id == user_id
                ).update(update_dict)
                
                if result:
                    db.commit()
                    return self.get_user_limits(user_id)
                return None
        except Exception as e:
            print(f"Error updating user token limits: {e}")
            return None

    def update_usage_counts(
        self, 
        user_id: str, 
        tokens_used: int
    ) -> bool:
        """Update usage counts for a user"""
        try:
            with get_db() as db:
                limits = db.query(UserTokenLimits).filter(
                    UserTokenLimits.user_id == user_id
                ).first()
                
                if limits:
                    current_time = int(time.time())
                    
                    # Check if daily reset is needed
                    if current_time - limits.last_daily_reset >= 86400:  # 24 hours
                        limits.daily_tokens_used = 0
                        limits.last_daily_reset = current_time
                    
                    # Check if monthly reset is needed
                    if current_time - limits.last_monthly_reset >= 2592000:  # 30 days
                        limits.monthly_tokens_used = 0
                        limits.last_monthly_reset = current_time
                    
                    # Update usage counts
                    limits.daily_tokens_used += tokens_used
                    limits.monthly_tokens_used += tokens_used
                    limits.total_tokens_used += tokens_used
                    limits.updated_at = current_time
                    
                    db.commit()
                    return True
                return False
        except Exception as e:
            print(f"Error updating usage counts: {e}")
            return False

    def get_all_user_limits(self) -> list[UserTokenLimitsModel]:
        """Get token limits for all users"""
        try:
            with get_db() as db:
                limits = db.query(UserTokenLimits).all()
                return [UserTokenLimitsModel.model_validate(limit) for limit in limits]
        except Exception as e:
            print(f"Error getting all user token limits: {e}")
            return []

    def delete_user_limits(self, user_id: str) -> bool:
        """Delete token limits for a user"""
        try:
            with get_db() as db:
                result = db.query(UserTokenLimits).filter(
                    UserTokenLimits.user_id == user_id
                ).delete()
                db.commit()
                return result > 0
        except Exception as e:
            print(f"Error deleting user token limits: {e}")
            return False


# Global instances
token_usage_table = TokenUsageTable()
user_token_limits_table = UserTokenLimitsTable() 