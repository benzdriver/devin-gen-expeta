"""
Unit tests for Request Router
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api_gateway.request_router import RequestRouter

class TestRequestRouter(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.auth_manager = MagicMock()
        self.response_formatter = MagicMock()
        self.router = RequestRouter(
            auth_manager=self.auth_manager,
            response_formatter=self.response_formatter
        )
    
    def test_register_route(self):
        """Test registering a route"""
        handler = MagicMock()
        self.router.register_route("/test", "GET", handler, auth_required=True, version="v2")
        
        route_key = "v2:GET:/test"
        self.assertIn(route_key, self.router.routes)
        
        route = self.router.routes[route_key]
        self.assertEqual(route["path"], "/test")
        self.assertEqual(route["method"], "GET")
        self.assertEqual(route["handler"], handler)
        self.assertTrue(route["auth_required"])
        self.assertEqual(route["version"], "v2")
    
    def test_register_middleware(self):
        """Test registering middleware"""
        middleware = MagicMock()
        self.router.register_middleware(middleware)
        
        self.assertIn(middleware, self.router.middleware)
    
    def test_route_request(self):
        """Test routing a request"""
        handler = MagicMock(return_value={"result": "success"})
        self.router.register_route("/test", "GET", handler)
        
        request_data = {"param": "value"}
        headers = {"Content-Type": "application/json"}
        status_code, response = self.router.route_request("/test", "GET", request_data, headers)
        
        self.assertEqual(status_code, 200)
        
        handler.assert_called_once_with(request_data)
        
        self.response_formatter.format_response.assert_called_once_with(
            {"result": "success"}, "/test", "GET", "v1"
        )
    
    def test_route_request_not_found(self):
        """Test routing a request to a non-existent route"""
        status_code, response = self.router.route_request("/non-existent", "GET")
        
        self.assertEqual(status_code, 404)
        
        self.assertEqual(response, {"error": "Not found"})
    
    def test_route_request_with_auth(self):
        """Test routing a request that requires authentication"""
        handler = MagicMock(return_value={"result": "success"})
        self.router.register_route("/test", "GET", handler, auth_required=True)
        
        self.auth_manager.authenticate.return_value = {
            "authenticated": True,
            "user": {"id": "user-id"}
        }
        
        request_data = {"param": "value"}
        headers = {"Authorization": "Bearer token"}
        status_code, response = self.router.route_request("/test", "GET", request_data, headers)
        
        self.assertEqual(status_code, 200)
        
        self.auth_manager.authenticate.assert_called_once_with("Bearer token")
        
        handler.assert_called_once()
        self.assertEqual(handler.call_args[0][0]["param"], "value")
        self.assertEqual(handler.call_args[0][0]["user"]["id"], "user-id")
    
    def test_route_request_auth_required_no_token(self):
        """Test routing a request that requires authentication but has no token"""
        handler = MagicMock()
        self.router.register_route("/test", "GET", handler, auth_required=True)
        
        status_code, response = self.router.route_request("/test", "GET")
        
        self.assertEqual(status_code, 401)
        
        self.assertEqual(response, {"error": "Authentication required"})
        
        handler.assert_not_called()
    
    def test_route_request_auth_failed(self):
        """Test routing a request where authentication fails"""
        handler = MagicMock()
        self.router.register_route("/test", "GET", handler, auth_required=True)
        
        self.auth_manager.authenticate.return_value = {
            "authenticated": False,
            "error": "Invalid token"
        }
        
        headers = {"Authorization": "Bearer token"}
        status_code, response = self.router.route_request("/test", "GET", headers=headers)
        
        self.assertEqual(status_code, 401)
        
        self.assertEqual(response, {"error": "Invalid token"})
        
        handler.assert_not_called()
    
    def test_route_request_handler_exception(self):
        """Test routing a request where the handler raises an exception"""
        handler = MagicMock(side_effect=ValueError("Test exception"))
        self.router.register_route("/test", "GET", handler)
        
        status_code, response = self.router.route_request("/test", "GET")
        
        self.assertEqual(status_code, 500)
        
        self.response_formatter.format_error.assert_called_once()
        self.assertEqual(self.response_formatter.format_error.call_args[0][0]["error"], "Test exception")
    
    def test_apply_middleware(self):
        """Test applying middleware to a request"""
        middleware1 = MagicMock(return_value={"modified": "request1"})
        middleware2 = MagicMock(return_value={"modified": "request2"})
        self.router.register_middleware(middleware1)
        self.router.register_middleware(middleware2)
        
        request_data = {"original": "request"}
        headers = {"Content-Type": "application/json"}
        modified_request = self.router._apply_middleware("/test", "GET", request_data, headers, "v1")
        
        middleware1.assert_called_once_with("/test", "GET", request_data, headers, "v1")
        middleware2.assert_called_once_with("/test", "GET", {"modified": "request1"}, headers, "v1")
        
        self.assertEqual(modified_request, {"modified": "request2"})
    
    def test_apply_middleware_exception(self):
        """Test applying middleware that raises an exception"""
        middleware1 = MagicMock(side_effect=ValueError("Test exception"))
        middleware2 = MagicMock(return_value={"modified": "request"})
        self.router.register_middleware(middleware1)
        self.router.register_middleware(middleware2)
        
        request_data = {"original": "request"}
        headers = {"Content-Type": "application/json"}
        modified_request = self.router._apply_middleware("/test", "GET", request_data, headers, "v1")
        
        middleware1.assert_called_once_with("/test", "GET", request_data, headers, "v1")
        
        middleware2.assert_called_once_with("/test", "GET", request_data, headers, "v1")
        
        self.assertEqual(modified_request, {"modified": "request"})
    
    def test_get_routes(self):
        """Test getting all routes"""
        handler1 = MagicMock()
        handler2 = MagicMock()
        self.router.register_route("/route1", "GET", handler1)
        self.router.register_route("/route2", "POST", handler2)
        
        routes = self.router.get_routes()
        
        self.assertEqual(len(routes), 2)
        self.assertTrue(any(route["path"] == "/route1" for route in routes))
        self.assertTrue(any(route["path"] == "/route2" for route in routes))
    
    def test_get_route(self):
        """Test getting a route"""
        handler = MagicMock()
        self.router.register_route("/test", "GET", handler, version="v2")
        
        route = self.router.get_route("/test", "GET", "v2")
        
        self.assertEqual(route["path"], "/test")
        self.assertEqual(route["method"], "GET")
        self.assertEqual(route["handler"], handler)
        self.assertEqual(route["version"], "v2")
        
        non_existent_route = self.router.get_route("/non-existent", "GET")
        self.assertIsNone(non_existent_route)

if __name__ == "__main__":
    unittest.main()
