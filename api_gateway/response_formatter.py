"""
Response Formatter for Expeta 2.0

This module formats responses consistently.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

class ResponseFormatter:
    """Formats responses consistently"""
    
    def __init__(self, include_metadata: bool = True):
        """Initialize response formatter
        
        Args:
            include_metadata: Whether to include metadata in responses
        """
        self.include_metadata = include_metadata
        self.logger = logging.getLogger(__name__)
    
    def format_response(self, response: Dict[str, Any], path: str = None, method: str = None, version: str = None) -> Dict[str, Any]:
        """Format a response
        
        Args:
            response: Response to format
            path: Request path
            method: HTTP method
            version: API version
            
        Returns:
            Formatted response
        """
        formatted_response = response.copy()
        
        if self.include_metadata:
            formatted_response["_metadata"] = self._generate_metadata(path, method, version)
        
        return formatted_response
    
    def format_error(self, error: Dict[str, Any], path: str = None, method: str = None, version: str = None) -> Dict[str, Any]:
        """Format an error response
        
        Args:
            error: Error to format
            path: Request path
            method: HTTP method
            version: API version
            
        Returns:
            Formatted error response
        """
        formatted_error = error.copy()
        
        if "error" not in formatted_error:
            formatted_error["error"] = "Unknown error"
        
        if self.include_metadata:
            formatted_error["_metadata"] = self._generate_metadata(path, method, version)
        
        return formatted_error
    
    def format_list_response(self, items: list, total: int = None, page: int = None, page_size: int = None, path: str = None, method: str = None, version: str = None) -> Dict[str, Any]:
        """Format a list response
        
        Args:
            items: List of items
            total: Total number of items
            page: Current page
            page_size: Page size
            path: Request path
            method: HTTP method
            version: API version
            
        Returns:
            Formatted list response
        """
        formatted_response = {
            "items": items,
            "count": len(items)
        }
        
        if total is not None:
            formatted_response["total"] = total
        
        if page is not None:
            formatted_response["page"] = page
        
        if page_size is not None:
            formatted_response["page_size"] = page_size
        
        if self.include_metadata:
            formatted_response["_metadata"] = self._generate_metadata(path, method, version)
        
        return formatted_response
    
    def format_success_response(self, message: str = "Success", data: Dict[str, Any] = None, path: str = None, method: str = None, version: str = None) -> Dict[str, Any]:
        """Format a success response
        
        Args:
            message: Success message
            data: Optional data
            path: Request path
            method: HTTP method
            version: API version
            
        Returns:
            Formatted success response
        """
        formatted_response = {
            "success": True,
            "message": message
        }
        
        if data:
            formatted_response["data"] = data
        
        if self.include_metadata:
            formatted_response["_metadata"] = self._generate_metadata(path, method, version)
        
        return formatted_response
    
    def _generate_metadata(self, path: str = None, method: str = None, version: str = None) -> Dict[str, Any]:
        """Generate metadata
        
        Args:
            path: Request path
            method: HTTP method
            version: API version
            
        Returns:
            Metadata
        """
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "api_version": version or "v1"
        }
        
        if path:
            metadata["path"] = path
        
        if method:
            metadata["method"] = method
        
        return metadata
    
    def set_include_metadata(self, include_metadata: bool) -> None:
        """Set whether to include metadata in responses
        
        Args:
            include_metadata: Whether to include metadata
        """
        self.include_metadata = include_metadata
    
    def format_json_response(self, data: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
        """Format a JSON response for web frameworks
        
        Args:
            data: Response data
            status_code: HTTP status code
            
        Returns:
            Formatted JSON response
        """
        return {
            "data": data,
            "status_code": status_code
        }
    
    def format_xml_response(self, data: Dict[str, Any]) -> str:
        """Format an XML response
        
        Args:
            data: Response data
            
        Returns:
            Formatted XML response
        """
        try:
            import dicttoxml
            return dicttoxml.dicttoxml(data).decode()
        except ImportError:
            self.logger.warning("dicttoxml package not installed, returning empty XML")
            return "<response></response>"
    
    def format_csv_response(self, data: list) -> str:
        """Format a CSV response
        
        Args:
            data: Response data
            
        Returns:
            Formatted CSV response
        """
        if not data:
            return ""
        
        try:
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            
            return output.getvalue()
        except (ImportError, AttributeError):
            self.logger.warning("Error formatting CSV response")
            return ""
