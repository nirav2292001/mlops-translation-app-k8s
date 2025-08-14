from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uvicorn

# Import translator and database components
from translator import translate
from database import get_db
from models import TranslationCreate, TranslationInDB, PyObjectId
from crud import translation_crud

app = FastAPI(
    title="Translation API",
    description="API for translating text and storing translations in MongoDB",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to be translated")
    source_language: str = Field("auto", description="Source language code (default: auto-detect)")
    target_language: str = Field("en", description="Target language code (default: en)")
    metadata: Optional[dict] = Field(None, description="Additional metadata to store with the translation")

class TranslationResponse(TranslationInDB):
    pass

class ListTranslationsResponse(BaseModel):
    total: int
    translations: List[TranslationResponse]

# API Endpoints
@app.post(
    "/translate", 
    response_model=TranslationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Translate text and store the result",
    response_description="The created translation record"
)
async def translate_text(request: TranslationRequest):
    """
    Translate text from source language to target language and store the result in the database.
    """
    try:
        # Perform the translation
        translated_text = translate(request.text)
        
        # Create translation record
        translation_data = TranslationCreate(
            input_text=request.text,
            translated_text=translated_text,
            source_language=request.source_language,
            target_language=request.target_language,
            metadata=request.metadata or {},
            model_used="opus-mt-hi-en"  # Default model, adjust as needed
        )
        
        # Save to database
        translation = await translation_crud.create(translation_data)
        return translation
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during translation: {str(e)}"
        )

@app.get(
    "/translations",
    response_model=ListTranslationsResponse,
    summary="List all translations",
    response_description="List of all stored translations with pagination"
)
async def list_translations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, le=100, description="Maximum number of records to return")
):
    """
    Retrieve all stored translations with pagination.
    """
    try:
        translations = await translation_crud.get_multi(skip=skip, limit=limit)
        total = await translation_crud.collection.count_documents({})
        
        return {
            "total": total,
            "translations": translations
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving translations: {str(e)}"
        )

@app.get(
    "/translations/{translation_id}",
    response_model=TranslationResponse,
    summary="Get a specific translation by ID",
    responses={
        404: {"description": "Translation not found"}
    }
)
async def get_translation(translation_id: str):
    """
    Retrieve a specific translation by its ID.
    """
    translation = await translation_crud.get_by_id(translation_id)
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    return translation

@app.delete(
    "/translations/{translation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a translation by ID",
    responses={
        404: {"description": "Translation not found"}
    }
)
async def delete_translation(translation_id: str):
    """
    Delete a translation by its ID.
    """
    success = await translation_crud.delete(translation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    return None

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Run the application if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
