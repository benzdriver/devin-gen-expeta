"""
Unit tests for Response Formatter
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api_gateway.response_formatter import ResponseFormatter

class TestResponseFormatter(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.formatter = ResponseFormatter()
    
    def test_format_response(self):
        """Test formatting a response"""
        response = {"data": "value"}
        formatted_response = self.formatter.format_response(response, "/test", "GET", "v1")
        
        self.assertEqual(formatted_response["data"], "value")
        self.assertIn("_metadata", formatted_response)
        self.assertEqual(formatted_response["_metadata"]["path"], "/test")
        self.assertEqual(formatted_response["_metadata"]["method"], "GET")
        self.assertEqual(formatted_response["_metadata"]["api_version"], "v1")
        self.assertIn("timestamp", formatted_response["_metadata"])
    
    def test_format_response_no_metadata(self):
        """Test formatting a response without metadata"""
        self.formatter.set_include_metadata(False)
        
        response = {"data": "value"}
        formatted_response = self.formatter.format_response(response)
        
        self.assertEqual(formatted_response["data"], "value")
        self.assertNotIn("_metadata", formatted_response)
    
    def test_format_error(self):
        """Test formatting an error response"""
        error = {"error": "Test error"}
        formatted_error = self.formatter.format_error(error, "/test", "GET", "v1")
        
        self.assertEqual(formatted_error["error"], "Test error")
        self.assertIn("_metadata", formatted_error)
        self.assertEqual(formatted_error["_metadata"]["path"], "/test")
        self.assertEqual(formatted_error["_metadata"]["method"], "GET")
        self.assertEqual(formatted_error["_metadata"]["api_version"], "v1")
    
    def test_format_error_no_error_message(self):
        """Test formatting an error response without an error message"""
        error = {}
        formatted_error = self.formatter.format_error(error)
        
        self.assertEqual(formatted_error["error"], "Unknown error")
        self.assertIn("_metadata", formatted_error)
    
    def test_format_list_response(self):
        """Test formatting a list response"""
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        formatted_response = self.formatter.format_list_response(
            items, total=10, page=1, page_size=3, path="/test", method="GET", version="v1"
        )
        
        self.assertEqual(formatted_response["items"], items)
        self.assertEqual(formatted_response["count"], 3)
        self.assertEqual(formatted_response["total"], 10)
        self.assertEqual(formatted_response["page"], 1)
        self.assertEqual(formatted_response["page_size"], 3)
        self.assertIn("_metadata", formatted_response)
    
    def test_format_list_response_minimal(self):
        """Test formatting a minimal list response"""
        items = [{"id": 1}, {"id": 2}]
        formatted_response = self.formatter.format_list_response(items)
        
        self.assertEqual(formatted_response["items"], items)
        self.assertEqual(formatted_response["count"], 2)
        self.assertNotIn("total", formatted_response)
        self.assertNotIn("page", formatted_response)
        self.assertNotIn("page_size", formatted_response)
        self.assertIn("_metadata", formatted_response)
    
    def test_format_success_response(self):
        """Test formatting a success response"""
        data = {"key": "value"}
        formatted_response = self.formatter.format_success_response(
            "Operation successful", data, "/test", "POST", "v1"
        )
        
        self.assertTrue(formatted_response["success"])
        self.assertEqual(formatted_response["message"], "Operation successful")
        self.assertEqual(formatted_response["data"], data)
        self.assertIn("_metadata", formatted_response)
    
    def test_format_success_response_no_data(self):
        """Test formatting a success response without data"""
        formatted_response = self.formatter.format_success_response("Operation successful")
        
        self.assertTrue(formatted_response["success"])
        self.assertEqual(formatted_response["message"], "Operation successful")
        self.assertNotIn("data", formatted_response)
        self.assertIn("_metadata", formatted_response)
    
    def test_generate_metadata(self):
        """Test generating metadata"""
        metadata = self.formatter._generate_metadata("/test", "GET", "v1")
        
        self.assertEqual(metadata["path"], "/test")
        self.assertEqual(metadata["method"], "GET")
        self.assertEqual(metadata["api_version"], "v1")
        self.assertIn("timestamp", metadata)
    
    def test_generate_metadata_minimal(self):
        """Test generating minimal metadata"""
        metadata = self.formatter._generate_metadata()
        
        self.assertEqual(metadata["api_version"], "v1")
        self.assertIn("timestamp", metadata)
        self.assertNotIn("path", metadata)
        self.assertNotIn("method", metadata)
    
    def test_set_include_metadata(self):
        """Test setting include_metadata"""
        self.formatter.set_include_metadata(False)
        
        self.assertFalse(self.formatter.include_metadata)
        
        response = {"data": "value"}
        formatted_response = self.formatter.format_response(response)
        
        self.assertNotIn("_metadata", formatted_response)
        
        self.formatter.set_include_metadata(True)
        
        self.assertTrue(self.formatter.include_metadata)
        
        formatted_response = self.formatter.format_response(response)
        
        self.assertIn("_metadata", formatted_response)
    
    def test_format_json_response(self):
        """Test formatting a JSON response"""
        data = {"key": "value"}
        formatted_response = self.formatter.format_json_response(data, 201)
        
        self.assertEqual(formatted_response["data"], data)
        self.assertEqual(formatted_response["status_code"], 201)
    
    @patch('dicttoxml.dicttoxml')
    def test_format_xml_response(self, mock_dicttoxml):
        """Test formatting an XML response"""
        mock_dicttoxml.return_value = b"<response><key>value</key></response>"
        
        data = {"key": "value"}
        xml_response = self.formatter.format_xml_response(data)
        
        self.assertEqual(xml_response, "<response><key>value</key></response>")
        mock_dicttoxml.assert_called_once_with(data)
    
    def test_format_xml_response_no_dicttoxml(self):
        """Test formatting an XML response without dicttoxml"""
        with patch('api_gateway.response_formatter.dicttoxml', None):
            with patch.object(self.formatter, 'logger') as mock_logger:
                data = {"key": "value"}
                xml_response = self.formatter.format_xml_response(data)
                
                self.assertEqual(xml_response, "<response></response>")
                mock_logger.warning.assert_called_once()
    
    @patch('csv.DictWriter')
    def test_format_csv_response(self, mock_dict_writer):
        """Test formatting a CSV response"""
        mock_writer = MagicMock()
        mock_dict_writer.return_value = mock_writer
        
        data = [{"key1": "value1", "key2": "value2"}, {"key1": "value3", "key2": "value4"}]
        
        with patch('io.StringIO') as mock_string_io:
            mock_string_io.return_value.getvalue.return_value = "key1,key2\nvalue1,value2\nvalue3,value4"
            csv_response = self.formatter.format_csv_response(data)
            
            self.assertEqual(csv_response, "key1,key2\nvalue1,value2\nvalue3,value4")
            mock_dict_writer.assert_called_once()
            mock_writer.writeheader.assert_called_once()
            mock_writer.writerows.assert_called_once_with(data)
    
    def test_format_csv_response_empty_data(self):
        """Test formatting a CSV response with empty data"""
        csv_response = self.formatter.format_csv_response([])
        
        self.assertEqual(csv_response, "")
    
    def test_format_csv_response_error(self):
        """Test formatting a CSV response with an error"""
        with patch('api_gateway.response_formatter.csv', None):
            with patch.object(self.formatter, 'logger') as mock_logger:
                data = [{"key": "value"}]
                csv_response = self.formatter.format_csv_response(data)
                
                self.assertEqual(csv_response, "")
                mock_logger.warning.assert_called_once()

if __name__ == "__main__":
    unittest.main()
