"""
Authentication Manager for Expeta 2.0

This module manages authentication and authorization.
"""

import jwt
import logging
import time
from typing import Dict, Any, List, Optional

class AuthManager:
    """Manages authentication and authorization"""
    
    def __init__(self, secret_key: str = None, token_expiry: int = 3600):
        """Initialize authentication manager
        
        Args:
            secret_key: Secret key for JWT tokens
            token_expiry: Token expiry time in seconds
        """
        self.secret_key = secret_key or "default-secret-key-change-in-production"
        self.token_expiry = token_expiry
        self.users = {}
        self.roles = {}
        self.permissions = {}
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self, token: str) -> Dict[str, Any]:
        """Authenticate a user with a token
        
        Args:
            token: Authentication token
            
        Returns:
            Authentication result
        """
        if token.startswith("Bearer "):
            token = token[7:]
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            if "exp" in payload and payload["exp"] < time.time():
                return {
                    "authenticated": False,
                    "error": "Token expired"
                }
            
            user_id = payload.get("sub")
            if user_id not in self.users:
                return {
                    "authenticated": False,
                    "error": "User not found"
                }
            
            return {
                "authenticated": True,
                "user": self.users[user_id]
            }
        except jwt.InvalidTokenError as e:
            self.logger.error(f"Invalid token: {str(e)}")
            return {
                "authenticated": False,
                "error": "Invalid token"
            }
    
    def authorize(self, user_id: str, permission: str) -> bool:
        """Authorize a user for a permission
        
        Args:
            user_id: User ID
            permission: Permission to check
            
        Returns:
            True if user is authorized, False otherwise
        """
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        if "permissions" in user and permission in user["permissions"]:
            return True
        
        if "roles" in user:
            for role_id in user["roles"]:
                if role_id in self.roles:
                    role = self.roles[role_id]
                    if "permissions" in role and permission in role["permissions"]:
                        return True
        
        return False
    
    def generate_token(self, user_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """Generate a JWT token for a user
        
        Args:
            user_id: User ID
            additional_claims: Additional claims to include in the token
            
        Returns:
            JWT token
        """
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        payload = {
            "sub": user_id,
            "iat": int(time.time()),
            "exp": int(time.time()) + self.token_expiry
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def register_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Register a user
        
        Args:
            user_id: User ID
            user_data: User data
            
        Returns:
            True if user was registered, False if user already exists
        """
        if user_id in self.users:
            return False
        
        self.users[user_id] = user_data
        return True
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Update a user
        
        Args:
            user_id: User ID
            user_data: User data
            
        Returns:
            True if user was updated, False if user does not exist
        """
        if user_id not in self.users:
            return False
        
        self.users[user_id].update(user_data)
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user
        
        Args:
            user_id: User ID
            
        Returns:
            True if user was deleted, False if user does not exist
        """
        if user_id not in self.users:
            return False
        
        del self.users[user_id]
        return True
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user
        
        Args:
            user_id: User ID
            
        Returns:
            User data or None if not found
        """
        return self.users.get(user_id)
    
    def register_role(self, role_id: str, role_data: Dict[str, Any]) -> bool:
        """Register a role
        
        Args:
            role_id: Role ID
            role_data: Role data
            
        Returns:
            True if role was registered, False if role already exists
        """
        if role_id in self.roles:
            return False
        
        self.roles[role_id] = role_data
        return True
    
    def update_role(self, role_id: str, role_data: Dict[str, Any]) -> bool:
        """Update a role
        
        Args:
            role_id: Role ID
            role_data: Role data
            
        Returns:
            True if role was updated, False if role does not exist
        """
        if role_id not in self.roles:
            return False
        
        self.roles[role_id].update(role_data)
        return True
    
    def delete_role(self, role_id: str) -> bool:
        """Delete a role
        
        Args:
            role_id: Role ID
            
        Returns:
            True if role was deleted, False if role does not exist
        """
        if role_id not in self.roles:
            return False
        
        del self.roles[role_id]
        return True
    
    def get_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """Get role
        
        Args:
            role_id: Role ID
            
        Returns:
            Role data or None if not found
        """
        return self.roles.get(role_id)
    
    def register_permission(self, permission_id: str, permission_data: Dict[str, Any]) -> bool:
        """Register a permission
        
        Args:
            permission_id: Permission ID
            permission_data: Permission data
            
        Returns:
            True if permission was registered, False if permission already exists
        """
        if permission_id in self.permissions:
            return False
        
        self.permissions[permission_id] = permission_data
        return True
    
    def get_permission(self, permission_id: str) -> Optional[Dict[str, Any]]:
        """Get permission
        
        Args:
            permission_id: Permission ID
            
        Returns:
            Permission data or None if not found
        """
        return self.permissions.get(permission_id)
    
    def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Assign a role to a user
        
        Args:
            user_id: User ID
            role_id: Role ID
            
        Returns:
            True if role was assigned, False if user or role does not exist
        """
        if user_id not in self.users or role_id not in self.roles:
            return False
        
        if "roles" not in self.users[user_id]:
            self.users[user_id]["roles"] = []
        
        if role_id not in self.users[user_id]["roles"]:
            self.users[user_id]["roles"].append(role_id)
        
        return True
    
    def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Remove a role from a user
        
        Args:
            user_id: User ID
            role_id: Role ID
            
        Returns:
            True if role was removed, False if user does not exist or does not have the role
        """
        if user_id not in self.users:
            return False
        
        if "roles" not in self.users[user_id] or role_id not in self.users[user_id]["roles"]:
            return False
        
        self.users[user_id]["roles"].remove(role_id)
        return True
    
    def assign_permission_to_role(self, role_id: str, permission_id: str) -> bool:
        """Assign a permission to a role
        
        Args:
            role_id: Role ID
            permission_id: Permission ID
            
        Returns:
            True if permission was assigned, False if role or permission does not exist
        """
        if role_id not in self.roles or permission_id not in self.permissions:
            return False
        
        if "permissions" not in self.roles[role_id]:
            self.roles[role_id]["permissions"] = []
        
        if permission_id not in self.roles[role_id]["permissions"]:
            self.roles[role_id]["permissions"].append(permission_id)
        
        return True
    
    def remove_permission_from_role(self, role_id: str, permission_id: str) -> bool:
        """Remove a permission from a role
        
        Args:
            role_id: Role ID
            permission_id: Permission ID
            
        Returns:
            True if permission was removed, False if role does not exist or does not have the permission
        """
        if role_id not in self.roles:
            return False
        
        if "permissions" not in self.roles[role_id] or permission_id not in self.roles[role_id]["permissions"]:
            return False
        
        self.roles[role_id]["permissions"].remove(permission_id)
        return True
