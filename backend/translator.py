from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import mlflow
import time
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model_name = "Helsinki-NLP/opus-mt-en-de"

# MLflow tracking settings
mlflow.set_tracking_uri("file:./mlflow_logs")
mlflow.set_experiment("translation_service")

# Global variables for lazy loading
tokenizer = None
model = None

def load_model():
    """Lazy load the model and tokenizer"""
    global tokenizer, model
    if tokenizer is None or model is None:
        logger.info(f"Loading model: {model_name}")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

def translate(text: str) -> str:
    # Load model if not already loaded
    load_model()
    
    try:
        with mlflow.start_run():
            # Log basic params
            mlflow.log_param("model", model_name)
            mlflow.log_param("input_length", len(text))

            # Inference timing
            start_time = time.time()
            inputs = tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)
            outputs = model.generate(inputs, max_length=512, num_beams=2, early_stopping=True)
            translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            end_time = time.time()

            # Log metrics and outputs
            mlflow.log_metric("inference_time_ms", (end_time - start_time) * 1000)
            mlflow.log_text(text, "input.txt")
            mlflow.log_text(translated_text, "output.txt")

            return translated_text
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return f"Translation failed: {str(e)}"
