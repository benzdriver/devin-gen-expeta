"""
Request Router for Expeta 2.0

This module routes requests to appropriate handlers.
"""

import logging
from typing import Dict, Any, List, Callable, Optional, Tuple

class RequestRouter:
    """Routes requests to appropriate handlers"""
    
    def __init__(self, auth_manager=None, response_formatter=None):
        """Initialize request router
        
        Args:
            auth_manager: Optional authentication manager
            response_formatter: Optional response formatter
        """
        self.routes = {}
        self.middleware = []
        self.auth_manager = auth_manager
        self.response_formatter = response_formatter
        self.logger = logging.getLogger(__name__)
    
    def register_route(self, path: str, method: str, handler: Callable, auth_required: bool = False, version: str = "v1") -> None:
        """Register a route
        
        Args:
            path: Route path
            method: HTTP method
            handler: Handler function
            auth_required: Whether authentication is required
            version: API version
        """
        route_key = self._get_route_key(path, method, version)
        
        self.routes[route_key] = {
            "path": path,
            "method": method,
            "handler": handler,
            "auth_required": auth_required,
            "version": version
        }
    
    def register_middleware(self, middleware: Callable) -> None:
        """Register middleware
        
        Args:
            middleware: Middleware function
        """
        self.middleware.append(middleware)
    
    def route_request(self, path: str, method: str, request_data: Dict[str, Any] = None, headers: Dict[str, str] = None, version: str = "v1") -> Tuple[int, Dict[str, Any]]:
        """Route a request to the appropriate handler
        
        Args:
            path: Request path
            method: HTTP method
            request_data: Request data
            headers: Request headers
            version: API version
            
        Returns:
            Tuple of (status_code, response_data)
        """
        route_key = self._get_route_key(path, method, version)
        
        if route_key not in self.routes:
            return 404, {"error": "Not found"}
        
        route = self.routes[route_key]
        
        modified_request = self._apply_middleware(path, method, request_data, headers, version)
        if modified_request:
            request_data = modified_request
        
        if route["auth_required"] and self.auth_manager:
            auth_token = headers.get("Authorization") if headers else None
            if not auth_token:
                return 401, {"error": "Authentication required"}
            
            auth_result = self.auth_manager.authenticate(auth_token)
            if not auth_result["authenticated"]:
                return 401, {"error": auth_result.get("error", "Authentication failed")}
            
            if request_data is None:
                request_data = {}
            
            request_data["user"] = auth_result.get("user")
        
        try:
            response = route["handler"](request_data)
            
            if self.response_formatter:
                response = self.response_formatter.format_response(response, path, method, version)
            
            return 200, response
        except Exception as e:
            self.logger.error(f"Error handling request {path} {method}: {str(e)}")
            
            error_response = {"error": str(e)}
            
            if self.response_formatter:
                error_response = self.response_formatter.format_error(error_response, path, method, version)
            
            return 500, error_response
    
    def _get_route_key(self, path: str, method: str, version: str) -> str:
        """Get route key
        
        Args:
            path: Route path
            method: HTTP method
            version: API version
            
        Returns:
            Route key
        """
        return f"{version}:{method.upper()}:{path}"
    
    def _apply_middleware(self, path: str, method: str, request_data: Dict[str, Any], headers: Dict[str, str], version: str) -> Optional[Dict[str, Any]]:
        """Apply middleware to request
        
        Args:
            path: Request path
            method: HTTP method
            request_data: Request data
            headers: Request headers
            version: API version
            
        Returns:
            Modified request data or None if no modifications
        """
        modified_request = request_data
        
        for middleware in self.middleware:
            try:
                result = middleware(path, method, modified_request, headers, version)
                if result:
                    modified_request = result
            except Exception as e:
                self.logger.error(f"Error in middleware for {path} {method}: {str(e)}")
        
        return modified_request
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get all routes
        
        Returns:
            List of routes
        """
        return list(self.routes.values())
    
    def get_route(self, path: str, method: str, version: str = "v1") -> Optional[Dict[str, Any]]:
        """Get route
        
        Args:
            path: Route path
            method: HTTP method
            version: API version
            
        Returns:
            Route or None if not found
        """
        route_key = self._get_route_key(path, method, version)
        return self.routes.get(route_key)
