"""
Unit tests for Authentication Manager
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import jwt
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api_gateway.auth_manager import AuthManager

class TestAuthManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.secret_key = "test-secret-key"
        self.auth_manager = AuthManager(secret_key=self.secret_key)
    
    def test_authenticate_valid_token(self):
        """Test authenticating with a valid token"""
        user_data = {"name": "Test User", "email": "test@example.com"}
        self.auth_manager.register_user("user-id", user_data)
        
        token = self.auth_manager.generate_token("user-id")
        
        result = self.auth_manager.authenticate(token)
        
        self.assertTrue(result["authenticated"])
        self.assertEqual(result["user"]["name"], "Test User")
        self.assertEqual(result["user"]["email"], "test@example.com")
        
        result = self.auth_manager.authenticate(f"Bearer {token}")
        self.assertTrue(result["authenticated"])
    
    def test_authenticate_expired_token(self):
        """Test authenticating with an expired token"""
        user_data = {"name": "Test User"}
        self.auth_manager.register_user("user-id", user_data)
        
        payload = {
            "sub": "user-id",
            "iat": int(time.time()) - 3600,
            "exp": int(time.time()) - 1800
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        result = self.auth_manager.authenticate(token)
        
        self.assertFalse(result["authenticated"])
        self.assertEqual(result["error"], "Token expired")
    
    def test_authenticate_invalid_token(self):
        """Test authenticating with an invalid token"""
        result = self.auth_manager.authenticate("invalid-token")
        
        self.assertFalse(result["authenticated"])
        self.assertEqual(result["error"], "Invalid token")
    
    def test_authenticate_unknown_user(self):
        """Test authenticating with a token for an unknown user"""
        payload = {
            "sub": "unknown-user",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        result = self.auth_manager.authenticate(token)
        
        self.assertFalse(result["authenticated"])
        self.assertEqual(result["error"], "User not found")
    
    def test_authorize_direct_permission(self):
        """Test authorizing a user with a direct permission"""
        user_data = {
            "name": "Test User",
            "permissions": ["read", "write"]
        }
        self.auth_manager.register_user("user-id", user_data)
        
        result = self.auth_manager.authorize("user-id", "read")
        
        self.assertTrue(result)
        
        result = self.auth_manager.authorize("user-id", "delete")
        self.assertFalse(result)
    
    def test_authorize_role_permission(self):
        """Test authorizing a user with a permission granted through a role"""
        role_data = {
            "name": "Admin",
            "permissions": ["read", "write", "delete"]
        }
        self.auth_manager.register_role("admin-role", role_data)
        
        user_data = {
            "name": "Test User",
            "roles": ["admin-role"]
        }
        self.auth_manager.register_user("user-id", user_data)
        
        result = self.auth_manager.authorize("user-id", "delete")
        
        self.assertTrue(result)
        
        result = self.auth_manager.authorize("user-id", "admin")
        self.assertFalse(result)
    
    def test_authorize_unknown_user(self):
        """Test authorizing an unknown user"""
        result = self.auth_manager.authorize("unknown-user", "read")
        
        self.assertFalse(result)
    
    def test_generate_token(self):
        """Test generating a token"""
        user_data = {"name": "Test User"}
        self.auth_manager.register_user("user-id", user_data)
        
        token = self.auth_manager.generate_token("user-id", {"custom": "claim"})
        
        payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        
        self.assertEqual(payload["sub"], "user-id")
        self.assertEqual(payload["custom"], "claim")
        self.assertIn("iat", payload)
        self.assertIn("exp", payload)
        
        with self.assertRaises(ValueError):
            self.auth_manager.generate_token("unknown-user")
    
    def test_register_user(self):
        """Test registering a user"""
        user_data = {"name": "Test User"}
        result = self.auth_manager.register_user("user-id", user_data)
        
        self.assertTrue(result)
        
        self.assertIn("user-id", self.auth_manager.users)
        self.assertEqual(self.auth_manager.users["user-id"], user_data)
        
        result = self.auth_manager.register_user("user-id", {})
        self.assertFalse(result)
    
    def test_update_user(self):
        """Test updating a user"""
        self.auth_manager.register_user("user-id", {"name": "Test User"})
        
        user_data = {"email": "test@example.com"}
        result = self.auth_manager.update_user("user-id", user_data)
        
        self.assertTrue(result)
        
        self.assertEqual(self.auth_manager.users["user-id"]["name"], "Test User")
        self.assertEqual(self.auth_manager.users["user-id"]["email"], "test@example.com")
        
        result = self.auth_manager.update_user("unknown-user", {})
        self.assertFalse(result)
    
    def test_delete_user(self):
        """Test deleting a user"""
        self.auth_manager.register_user("user-id", {"name": "Test User"})
        
        result = self.auth_manager.delete_user("user-id")
        
        self.assertTrue(result)
        
        self.assertNotIn("user-id", self.auth_manager.users)
        
        result = self.auth_manager.delete_user("unknown-user")
        self.assertFalse(result)
    
    def test_get_user(self):
        """Test getting a user"""
        user_data = {"name": "Test User"}
        self.auth_manager.register_user("user-id", user_data)
        
        user = self.auth_manager.get_user("user-id")
        
        self.assertEqual(user, user_data)
        
        user = self.auth_manager.get_user("unknown-user")
        self.assertIsNone(user)
    
    def test_register_role(self):
        """Test registering a role"""
        role_data = {"name": "Admin"}
        result = self.auth_manager.register_role("admin-role", role_data)
        
        self.assertTrue(result)
        
        self.assertIn("admin-role", self.auth_manager.roles)
        self.assertEqual(self.auth_manager.roles["admin-role"], role_data)
        
        result = self.auth_manager.register_role("admin-role", {})
        self.assertFalse(result)
    
    def test_update_role(self):
        """Test updating a role"""
        self.auth_manager.register_role("admin-role", {"name": "Admin"})
        
        role_data = {"permissions": ["read", "write"]}
        result = self.auth_manager.update_role("admin-role", role_data)
        
        self.assertTrue(result)
        
        self.assertEqual(self.auth_manager.roles["admin-role"]["name"], "Admin")
        self.assertEqual(self.auth_manager.roles["admin-role"]["permissions"], ["read", "write"])
        
        result = self.auth_manager.update_role("unknown-role", {})
        self.assertFalse(result)
    
    def test_delete_role(self):
        """Test deleting a role"""
        self.auth_manager.register_role("admin-role", {"name": "Admin"})
        
        result = self.auth_manager.delete_role("admin-role")
        
        self.assertTrue(result)
        
        self.assertNotIn("admin-role", self.auth_manager.roles)
        
        result = self.auth_manager.delete_role("unknown-role")
        self.assertFalse(result)
    
    def test_get_role(self):
        """Test getting a role"""
        role_data = {"name": "Admin"}
        self.auth_manager.register_role("admin-role", role_data)
        
        role = self.auth_manager.get_role("admin-role")
        
        self.assertEqual(role, role_data)
        
        role = self.auth_manager.get_role("unknown-role")
        self.assertIsNone(role)
    
    def test_register_permission(self):
        """Test registering a permission"""
        permission_data = {"name": "Read", "description": "Read access"}
        result = self.auth_manager.register_permission("read", permission_data)
        
        self.assertTrue(result)
        
        self.assertIn("read", self.auth_manager.permissions)
        self.assertEqual(self.auth_manager.permissions["read"], permission_data)
        
        result = self.auth_manager.register_permission("read", {})
        self.assertFalse(result)
    
    def test_get_permission(self):
        """Test getting a permission"""
        permission_data = {"name": "Read"}
        self.auth_manager.register_permission("read", permission_data)
        
        permission = self.auth_manager.get_permission("read")
        
        self.assertEqual(permission, permission_data)
        
        permission = self.auth_manager.get_permission("unknown-permission")
        self.assertIsNone(permission)
    
    def test_assign_role_to_user(self):
        """Test assigning a role to a user"""
        self.auth_manager.register_user("user-id", {"name": "Test User"})
        self.auth_manager.register_role("admin-role", {"name": "Admin"})
        
        result = self.auth_manager.assign_role_to_user("user-id", "admin-role")
        
        self.assertTrue(result)
        
        self.assertIn("roles", self.auth_manager.users["user-id"])
        self.assertIn("admin-role", self.auth_manager.users["user-id"]["roles"])
        
        result = self.auth_manager.assign_role_to_user("unknown-user", "admin-role")
        self.assertFalse(result)
        
        result = self.auth_manager.assign_role_to_user("user-id", "unknown-role")
        self.assertFalse(result)
        
        result = self.auth_manager.assign_role_to_user("user-id", "admin-role")
        self.assertTrue(result)
    
    def test_remove_role_from_user(self):
        """Test removing a role from a user"""
        self.auth_manager.register_user("user-id", {"name": "Test User"})
        self.auth_manager.register_role("admin-role", {"name": "Admin"})
        
        self.auth_manager.assign_role_to_user("user-id", "admin-role")
        
        result = self.auth_manager.remove_role_from_user("user-id", "admin-role")
        
        self.assertTrue(result)
        
        self.assertNotIn("admin-role", self.auth_manager.users["user-id"]["roles"])
        
        result = self.auth_manager.remove_role_from_user("unknown-user", "admin-role")
        self.assertFalse(result)
        
        result = self.auth_manager.remove_role_from_user("user-id", "admin-role")
        self.assertFalse(result)
    
    def test_assign_permission_to_role(self):
        """Test assigning a permission to a role"""
        self.auth_manager.register_role("admin-role", {"name": "Admin"})
        self.auth_manager.register_permission("read", {"name": "Read"})
        
        result = self.auth_manager.assign_permission_to_role("admin-role", "read")
        
        self.assertTrue(result)
        
        self.assertIn("permissions", self.auth_manager.roles["admin-role"])
        self.assertIn("read", self.auth_manager.roles["admin-role"]["permissions"])
        
        result = self.auth_manager.assign_permission_to_role("unknown-role", "read")
        self.assertFalse(result)
        
        result = self.auth_manager.assign_permission_to_role("admin-role", "unknown-permission")
        self.assertFalse(result)
        
        result = self.auth_manager.assign_permission_to_role("admin-role", "read")
        self.assertTrue(result)
    
    def test_remove_permission_from_role(self):
        """Test removing a permission from a role"""
        self.auth_manager.register_role("admin-role", {"name": "Admin"})
        self.auth_manager.register_permission("read", {"name": "Read"})
        
        self.auth_manager.assign_permission_to_role("admin-role", "read")
        
        result = self.auth_manager.remove_permission_from_role("admin-role", "read")
        
        self.assertTrue(result)
        
        self.assertNotIn("read", self.auth_manager.roles["admin-role"]["permissions"])
        
        result = self.auth_manager.remove_permission_from_role("unknown-role", "read")
        self.assertFalse(result)
        
        result = self.auth_manager.remove_permission_from_role("admin-role", "read")
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
