from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from pydantic_core import core_schema

# Custom Pydantic type for MongoDB ObjectId
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type, _handler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.no_info_plain_validator_function(cls.validate),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

class TranslationBase(BaseModel):
    """Base model for translation data."""
    input_text: str = Field(..., description="The original input text to be translated")
    translated_text: str = Field(..., description="The translated text")
    source_language: str = Field(default="auto", description="Source language code (default: auto-detect)")
    target_language: str = Field(default="en", description="Target language code (default: en)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of creation")
    model_used: str = Field(default="opus-mt-hi-en", description="Name/ID of the translation model used")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

class TranslationCreate(TranslationBase):
    """Model for creating a new translation."""
    pass

class TranslationInDB(TranslationBase):
    """Model for translation data stored in the database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
