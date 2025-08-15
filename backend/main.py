from fastapi import FastAPI
from pydantic import BaseModel
from translator import translate
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationRequest(BaseModel):
    text: str

@app.post("/translate")
def translate_text(request: TranslationRequest):
    translated = translate(request.text)
    return {"translated_text": translated}

# Run directly if this is the main file
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
