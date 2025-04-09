import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.memory_system import MemorySystem
from utils.env_loader import load_dotenv

load_dotenv()

def create_test_data():
    """Create test data in the memory system for testing file download functionality"""
    from memory.storage.file_storage import FileStorage
    storage = FileStorage()
    memory_system = MemorySystem(storage_provider=storage)
    
    test_expectation = {
        "name": "User Authentication System",
        "description": "A user authentication system with login and registration functionality",
        "acceptance_criteria": [
            "Users can register with email and password",
            "Users can login with email and password",
            "Users can reset their password",
            "System validates email format and password strength"
        ],
        "constraints": [
            "Must use secure password hashing",
            "Must implement rate limiting for login attempts"
        ],
        "interfaces": {
            "login": {
                "inputs": ["email", "password"],
                "outputs": ["auth_token", "user_info"]
            },
            "register": {
                "inputs": ["email", "password", "name"],
                "outputs": ["success", "user_id"]
            }
        }
    }
    
    expectation_id = "test123"
    test_expectation["id"] = expectation_id
    memory_system.record_expectations(test_expectation)
    print(f"Created test expectation with ID: {expectation_id}")
    
    test_generated_code = {
        "expectation_id": expectation_id,
        "files": [
            {
                "name": "auth.py",
                "content": """
import hashlib
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "placeholder-key-for-testing")
TOKEN_EXPIRY = 24  # hours

class AuthSystem:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def register(self, email, password, name):
        if self.db.users.find_one({"email": email}):
            return {"success": False, "error": "User already exists"}
            
        hashed_password = self._hash_password(password)
        
        user_id = self.db.users.insert_one({
            "email": email,
            "password": hashed_password,
            "name": name,
            "created_at": datetime.now()
        }).inserted_id
        
        return {"success": True, "user_id": str(user_id)}
    
    def login(self, email, password):
        user = self.db.users.find_one({"email": email})
        if not user:
            return {"success": False, "error": "Invalid credentials"}
            
        if not self._verify_password(password, user["password"]):
            return {"success": False, "error": "Invalid credentials"}
            
        token = self._generate_token(user)
        
        return {
            "success": True,
            "auth_token": token,
            "user_info": {
                "email": user["email"],
                "name": user["name"]
            }
        }
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
        
    def _verify_password(self, password, hashed_password):
        return self._hash_password(password) == hashed_password
        
    def _generate_token(self, user):
        payload = {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "exp": datetime.now() + timedelta(hours=TOKEN_EXPIRY)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
"""
            },
            {
                "name": "requirements.txt",
                "content": """
pyjwt==2.6.0
pymongo==4.3.3
"""
            }
        ]
    }
    
    memory_system.record_generation(test_generated_code)
    print(f"Created test generated code for expectation ID: {expectation_id}")

if __name__ == "__main__":
    create_test_data()
    print("Test data creation completed successfully")
