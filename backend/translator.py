from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import mlflow
import time

model_name = "Helsinki-NLP/opus-mt-en-de"

# MLflow tracking settings
mlflow.set_tracking_uri("file:./mlflow_logs")
mlflow.set_experiment("translation_service")

# Load tokenizer and model once
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def translate(text: str) -> str:
    with mlflow.start_run():
        # Log basic params
        mlflow.log_param("model", model_name)
        mlflow.log_param("input_length", len(text))

        # Inference timing
        start_time = time.time()
        inputs = tokenizer.encode(text, return_tensors="pt")
        outputs = model.generate(inputs, max_length=512, num_beams=4, early_stopping=True)
        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        end_time = time.time()

        # Log metrics and outputs
        mlflow.log_metric("inference_time_ms", (end_time - start_time) * 1000)
        mlflow.log_text(text, "input.txt")
        mlflow.log_text(translated_text, "output.txt")

        return translated_text
