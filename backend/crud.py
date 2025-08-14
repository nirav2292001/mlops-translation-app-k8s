from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from .models import TranslationCreate, TranslationInDB, PyObjectId
from .database import get_db
from pymongo import ReturnDocument

class CRUDTranslation:
    def __init__(self, collection_name: str = "translations"):
        self.collection = get_db()[collection_name]
    
    async def create(self, translation: TranslationCreate) -> TranslationInDB:
        """
        Create a new translation record in the database.
        """
        translation_dict = translation.dict()
        # Convert datetime to string for MongoDB storage
        translation_dict["created_at"] = datetime.utcnow()
        
        result = self.collection.insert_one(translation_dict)
        return await self.get_by_id(str(result.inserted_id))
    
    async def get_by_id(self, id: str) -> Optional[TranslationInDB]:
        """
        Retrieve a translation by its ID.
        """
        try:
            doc = self.collection.find_one({"_id": ObjectId(id)})
            if doc:
                return TranslationInDB(**doc)
            return None
        except Exception as e:
            print(f"Error retrieving translation: {e}")
            return None
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[TranslationInDB]:
        """
        Retrieve multiple translations with optional filtering.
        """
        if filter_dict is None:
            filter_dict = {}
            
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
        return [TranslationInDB(**doc) for doc in cursor]
    
    async def update(
        self, 
        id: str, 
        update_data: dict,
    ) -> Optional[TranslationInDB]:
        """
        Update a translation record.
        """
        # Remove None values from update data
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        result = self.collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        
        if result:
            return TranslationInDB(**result)
        return None
    
    async def delete(self, id: str) -> bool:
        """
        Delete a translation record.
        """
        result = self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

# Create an instance of the CRUD operations
translation_crud = CRUDTranslation()
