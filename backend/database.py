import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from datetime import datetime

# Load environment variables
load_dotenv()

# Get MongoDB connection URL from environment variables
MONGODB_URL = os.getenv("MONGODB_URL")

class DatabaseConnection:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        try:
            if not MONGODB_URL:
                raise ValueError("MONGODB_URL environment variable is not set")
                
            self._client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
            # Test the connection
            self._client.admin.command('ping')
            self._db = self._client.get_database()
            print("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def get_database(self):
        if not self._db:
            self._initialize_connection()
        return self._db

    def close_connection(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

def get_db():
    """
    Dependency function to get database instance.
    """
    db_connection = DatabaseConnection()
    return db_connection.get_database()

# Initialize the database connection when this module is imported
db = get_db()
