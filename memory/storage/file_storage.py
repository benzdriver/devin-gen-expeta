"""
File Storage Provider for Memory System

This module implements a file-based storage provider for the Memory System.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

class FileStorage:
    """File-based storage provider for Memory System"""
    
    def __init__(self, base_dir=None):
        """Initialize file storage
        
        Args:
            base_dir: Optional base directory for storage. If not provided, a default will be used.
        """
        self.base_dir = base_dir or self._get_default_base_dir()
        self._ensure_directories()
        
    def store(self, collection, data):
        """Store data in a collection
        
        Args:
            collection: Collection name
            data: Data to store
            
        Returns:
            Storage result with ID
        """
        if "id" not in data:
            data["id"] = self._generate_id()
            
        data["_timestamp"] = self._get_timestamp()
        
        file_path = self._get_file_path(collection, data["id"])
        
        self._write_json_file(file_path, data)
        
        return {
            "id": data["id"],
            "collection": collection,
            "timestamp": data["_timestamp"],
            "status": "stored"
        }
        
    def retrieve(self, collection, query=None):
        """Retrieve data from a collection
        
        Args:
            collection: Collection name
            query: Optional query dictionary
            
        Returns:
            Retrieved data matching the query
        """
        collection_dir = os.path.join(self.base_dir, collection)
        
        if not os.path.exists(collection_dir):
            return []
            
        if query and "id" in query:
            file_path = self._get_file_path(collection, query["id"])
            if os.path.exists(file_path):
                return [self._read_json_file(file_path)]
            return []
            
        results = []
        for file_name in os.listdir(collection_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(collection_dir, file_name)
                data = self._read_json_file(file_path)
                
                if query and not self._matches_query(data, query):
                    continue
                    
                results.append(data)
                
        return results
        
    def _ensure_directories(self):
        """Ensure storage directories exist"""
        os.makedirs(self.base_dir, exist_ok=True)
        
        collections = ["expectations", "generations", "validations", "llm_requests"]
        for collection in collections:
            os.makedirs(os.path.join(self.base_dir, collection), exist_ok=True)
            
    def _get_default_base_dir(self):
        """Get default base directory for storage
        
        Returns:
            Default base directory path
        """
        home_dir = str(Path.home())
        return os.path.join(home_dir, ".expeta", "storage")
        
    def _generate_id(self):
        """Generate a unique ID
        
        Returns:
            Unique ID string
        """
        timestamp = int(time.time() * 1000)
        random_suffix = os.urandom(4).hex()
        return f"{timestamp}-{random_suffix}"
        
    def _get_timestamp(self):
        """Get current timestamp
        
        Returns:
            ISO format timestamp string
        """
        return datetime.now().isoformat()
        
    def _get_file_path(self, collection, item_id):
        """Get file path for an item
        
        Args:
            collection: Collection name
            item_id: Item ID
            
        Returns:
            File path
        """
        return os.path.join(self.base_dir, collection, f"{item_id}.json")
        
    def _write_json_file(self, file_path, data):
        """Write data to JSON file
        
        Args:
            file_path: File path
            data: Data to write
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def _read_json_file(self, file_path):
        """Read data from JSON file
        
        Args:
            file_path: File path
            
        Returns:
            Data from file
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def _matches_query(self, data, query):
        """Check if data matches query
        
        Args:
            data: Data to check
            query: Query dictionary
            
        Returns:
            True if data matches query, False otherwise
        """
        for key, value in query.items():
            if key not in data or data[key] != value:
                return False
        return True
