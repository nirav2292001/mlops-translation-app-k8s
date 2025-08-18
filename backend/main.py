from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from translator import translate, load_model
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Translation Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "de"

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    try:
        logger.info("Starting up translation service...")
        load_model()
        logger.info("Translation service ready!")
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "translation"}

@app.get("/ready")
def readiness_check():
    """Check if the service is ready to handle requests"""
    try:
        from translator import tokenizer, model
        if tokenizer is None or model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        return {"status": "ready", "model_loaded": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@app.post("/translate")
def translate_text(request: TranslationRequest):
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        translated = translate(request.text)
        return {"translated_text": translated}
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

# Run directly if this is the main file
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
