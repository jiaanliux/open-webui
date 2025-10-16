#!/usr/bin/env python3
"""
Setup script for the CasaBot Token Usage Tracking System

This script helps administrators set up initial token limits for users.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from open_webui.models.token_usage import user_token_limits_table, UserTokenLimitsCreate
    from open_webui.models.users import Users
    from open_webui.internal.db import get_db
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)


def setup_token_limits():
    """Set up initial token limits for all users"""
    
    print("Setting up token usage tracking system...")
    
    # Get all users
    try:
        users_response = Users.get_users()
        users = users_response.get("users", [])
        
        if not users:
            print("No users found in the system.")
            return
        
        print(f"Found {len(users)} users in the system.")
        
        # Set default limits for each user
        for user in users:
            print(f"\nSetting up limits for user: {user.name or user.email} (ID: {user.id})")
            
            # Check if limits already exist
            existing_limits = user_token_limits_table.get_user_limits(user.id)
            if existing_limits:
                print(f"  - Limits already exist for this user, skipping...")
                continue
            
            # Set default limits based on user role
            if user.role == "admin":
                # Admins get higher limits
                daily_limit = 50000
                monthly_limit = 500000
                total_limit = 5000000
            elif user.role == "user":
                # Regular users get moderate limits
                daily_limit = 10000
                monthly_limit = 100000
                total_limit = 1000000
            else:
                # Pending users get lower limits
                daily_limit = 1000
                monthly_limit = 10000
                total_limit = 100000
            
            # Create limits
            limits_data = UserTokenLimitsCreate(
                user_id=user.id,
                daily_token_limit=daily_limit,
                monthly_token_limit=monthly_limit,
                total_token_limit=total_limit,
                notify_at_percentage=80
            )
            
            try:
                limits = user_token_limits_table.create_user_limits(limits_data)
                if limits:
                    print(f"  - Created limits: Daily={daily_limit:,}, Monthly={monthly_limit:,}, Total={total_limit:,}")
                else:
                    print(f"  - Failed to create limits")
            except Exception as e:
                print(f"  - Error creating limits: {e}")
        
        print(f"\nToken usage system setup complete!")
        print(f"Processed {len(users)} users.")
        
    except Exception as e:
        print(f"Error setting up token limits: {e}")
        return False
    
    return True


def set_custom_limits(user_id, daily_limit=None, monthly_limit=None, total_limit=None):
    """Set custom token limits for a specific user"""
    
    print(f"Setting custom limits for user {user_id}...")
    
    # Check if user exists
    user = Users.get_user_by_id(user_id)
    if not user:
        print(f"User {user_id} not found.")
        return False
    
    print(f"User: {user.name or user.email}")
    
    # Check if limits already exist
    existing_limits = user_token_limits_table.get_user_limits(user_id)
    if existing_limits:
        print("User already has limits. Updating...")
        # Update existing limits
        from open_webui.models.token_usage import UserTokenLimitsUpdate
        
        update_data = UserTokenLimitsUpdate()
        if daily_limit is not None:
            update_data.daily_token_limit = daily_limit
        if monthly_limit is not None:
            update_data.monthly_token_limit = monthly_limit
        if total_limit is not None:
            update_data.total_token_limit = total_limit
        
        try:
            updated_limits = user_token_limits_table.update_user_limits(user_id, update_data)
            if updated_limits:
                print("Limits updated successfully!")
                return True
            else:
                print("Failed to update limits.")
                return False
        except Exception as e:
            print(f"Error updating limits: {e}")
            return False
    else:
        # Create new limits
        limits_data = UserTokenLimitsCreate(
            user_id=user_id,
            daily_token_limit=daily_limit,
            monthly_token_limit=monthly_limit,
            total_token_limit=total_limit,
            notify_at_percentage=80
        )
        
        try:
            limits = user_token_limits_table.create_user_limits(limits_data)
            if limits:
                print("Limits created successfully!")
                return True
            else:
                print("Failed to create limits.")
                return False
        except Exception as e:
            print(f"Error creating limits: {e}")
            return False


def list_user_limits():
    """List all users and their current token limits"""
    
    print("Current user token limits:")
    print("-" * 80)
    
    try:
        # Get all users
        users_response = Users.get_users()
        users = users_response.get("users", [])
        
        if not users:
            print("No users found in the system.")
            return
        
        # Get all limits
        all_limits = user_token_limits_table.get_all_user_limits()
        limits_dict = {limit.user_id: limit for limit in all_limits}
        
        for user in users:
            print(f"User: {user.name or user.email} (ID: {user.id})")
            print(f"Role: {user.role}")
            
            if user.id in limits_dict:
                limits = limits_dict[user.id]
                print(f"  Daily Limit: {limits.daily_token_limit:,} (Used: {limits.daily_tokens_used:,})")
                print(f"  Monthly Limit: {limits.monthly_token_limit:,} (Used: {limits.monthly_tokens_used:,})")
                print(f"  Total Limit: {limits.total_token_limit:,} (Used: {limits.total_tokens_used:,})")
                print(f"  Status: {'Active' if limits.is_active else 'Inactive'}")
            else:
                print("  No limits set")
            
            print()
        
    except Exception as e:
        print(f"Error listing user limits: {e}")


def main():
    parser = argparse.ArgumentParser(description="Setup CasaBot Token Usage Tracking System")
    parser.add_argument("--setup", action="store_true", help="Set up default token limits for all users")
    parser.add_argument("--list", action="store_true", help="List all users and their current limits")
    parser.add_argument("--user", type=str, help="User ID to set custom limits for")
    parser.add_argument("--daily", type=int, help="Daily token limit")
    parser.add_argument("--monthly", type=int, help="Monthly token limit")
    parser.add_argument("--total", type=int, help="Total token limit")
    
    args = parser.parse_args()
    
    if not any([args.setup, args.list, args.user]):
        parser.print_help()
        return
    
    try:
        if args.setup:
            setup_token_limits()
        elif args.list:
            list_user_limits()
        elif args.user:
            if not any([args.daily, args.monthly, args.total]):
                print("Please specify at least one limit (--daily, --monthly, or --total)")
                return
            
            set_custom_limits(args.user, args.daily, args.monthly, args.total)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main() 