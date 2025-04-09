import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.memory_system import MemorySystem
from memory.storage.file_storage import FileStorage

def debug_storage():
    """Debug the file storage system to identify issues with test data retrieval"""
    storage = FileStorage()
    default_path = storage._get_default_base_dir()
    print(f"Default storage path: {default_path}")
    
    expectations_dir = os.path.join(default_path, "expectations")
    print(f"Expectations directory exists: {os.path.exists(expectations_dir)}")
    
    if os.path.exists(expectations_dir):
        files = os.listdir(expectations_dir)
        print(f"Files in expectations directory: {files}")
        
        test_file_path = os.path.join(expectations_dir, "test123.json")
        print(f"Test file exists: {os.path.exists(test_file_path)}")
        
        if os.path.exists(test_file_path):
            with open(test_file_path, 'r') as f:
                content = json.load(f)
                print(f"Test file content: {json.dumps(content, indent=2)}")
    
    memory_system = MemorySystem()
    result = memory_system.get_expectation("test123")
    print(f"Memory system retrieval result: {result}")
    
    explicit_storage = FileStorage()
    explicit_memory = MemorySystem(storage_provider=explicit_storage)
    explicit_result = explicit_memory.get_expectation("test123")
    print(f"Explicit storage retrieval result: {explicit_result}")
    
    api_storage_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "access", "rest_api", "src", ".expeta", "storage")
    print(f"API server storage path exists: {os.path.exists(api_storage_path)}")
    
    if os.path.exists(api_storage_path):
        api_expectations_dir = os.path.join(api_storage_path, "expectations")
        if os.path.exists(api_expectations_dir):
            api_files = os.listdir(api_expectations_dir)
            print(f"Files in API server expectations directory: {api_files}")

if __name__ == "__main__":
    debug_storage()
    print("Storage debugging completed")
