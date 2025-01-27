# --------------------
# Importing Libraries
# --------------------
import os  # This is for interacting with environment variables (to get MODEL_NAME).
from fastapi import (
    FastAPI,
    HTTPException,
)  # FastAPI framework for building APIs and HTTP error handling.
from pydantic import BaseModel  # This is to validate the input data to the API.
from transformers import (
    pipeline,
)  # This library is for using Hugging Face's pre-trained text-generation pipeline.


# -----------------------
# Data model for request
# -----------------------
class GenerateRequest(BaseModel):
    """
    This is GenerateRequest class that defines the expected structure of the API request payload.
    Each field here corresponds to a parameter for text generation.
    """

    prompt: str  # The user-provided text input for the model to generate text from.
    max_new_tokens: int = 200  # Maximum number of tokens the model should generate.
    temperature: float = (
        0.7  # Controls the randomness of the model's output. Higher = more diverse.
    )
    top_p: float = (
        0.9  # Nucleus sampling parameter: limits token selection to the top p cumulative probability.
    )
    repetition_penalty: float = 1.2  # Penalizes repeating tokens to avoid redundancy.
    no_repeat_ngram_size: int = (
        2  # Prevents repetition of n-grams (e.g., bigrams for value `2`).
    )


# -------------------------
# Initializing the FastAPI
# -------------------------
# Initializing FastAPI app with metadata for auto-generated documentation.
# The reason why I have opted for FastAPI is it gives auto-generated swagger docs, which will be easy to test the API.
app = FastAPI(
    title="Text Generation Service",  # This is the title of the API shown in the Swagger docs.
    description="A Dockerized text-generation microservice using Hugging Face Transformers",  # This is the description shown in the docs.
    version="1.0.0",  # This is the version number of the API.
)

# -------------------------------
# Collecting the MODEL_NAME from env
# -------------------------------
# Get the model name from the environment variable or we  are using "gpt2" as the default.
MODEL_NAME = os.getenv("MODEL_NAME", "gpt2")

# Trying to load the text-generation pipeline with the specified model name.
try:
    generator = pipeline(
        "text-generation",  # specifying the task type (text generation), there are differnet types which can be found in hugging face site.
        model=MODEL_NAME,  # Giving the mdoel name from the environment variable.
        device=-1,  # Since we are using CPU (device=-1) or else (device=0) for GPU if available.
        framework="pt",  # Forcing to use PyTorch as the framework.
    )
except Exception as e:
    # Printing the error and raise it if the model loading fails.
    print(f"Error loading model {MODEL_NAME}: {e}")
    raise e


# -----------------------
# Root Endpoint (GET /)
# -----------------------
@app.get("/")
def root():
    """
    This is the root endpoint that provides a welcome message.
    This would be useful to check if the API is up and running.
    """
    return {"message": "Welcome to the Text Generation Service!"}


# -----------------------
# Creating POST Endpoint
# -----------------------
@app.post("/generate")
def generate_text(req: GenerateRequest):
    """
    POST endpoint is to generate text from a user-provided prompt and parameters. Here parameters are optional. The user may or may not give the parameters.
    Accepts a JSON payload matching the GenerateRequest schema and returns the generated text.
    """
    # -------------------------
    # Step 1: Input Validation
    # -------------------------
    # It ensures the user prompt is not empty or only whitespace. If so, it produces 400 error.
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    # ----------------------------
    # Step 2: Prepares the Prompt
    # ----------------------------

    # Here I have commented out this system like prompt, if want to test please uncomment this.
    # final_prompt = f"You are a helpful AI assistant. Respond clearly to the following question: {prompt}"
    final_prompt = prompt

    # ----------------------------
    # Step 3: Run Model Inference
    # ----------------------------
    # It uses the generator pipeline to generate text based on the prompt and user-provided parameters.
    outputs = generator(
        final_prompt,  # This will be the input prompt for the model.
        max_new_tokens=req.max_new_tokens,  # Maximum number of tokens the model should generate.
        do_sample=True,  # Use sampling (rather than greedy decoding) for more diverse responses.
        temperature=req.temperature,  # Controls the randomness of the model's output. Higher = more diverse.
        top_p=req.top_p,  # Nucleus sampling parameter: limits token selection to the top p cumulative probability.
        repetition_penalty=req.repetition_penalty,  # Penalizes repeating tokens to avoid redundancy.
        no_repeat_ngram_size=req.no_repeat_ngram_size,  # Prevents repetition of n-grams (e.g., bigrams for value `2`).
    )

    # Extracts the generated text from the model's output.
    generated_text = outputs[0]["generated_text"]

    # ------------------------
    # Step 4: Post-Processing
    # ------------------------

    # Removes the repeated lines from the output by checking uniqueness.
    lines = generated_text.split("\n")  # It splits the output into lines.
    unique_lines = []  # It will store all the unique lines.
    seen = set()  # It tracks the lines that already been processed.
    for line in lines:
        line_stripped = line.strip()  # It removes the leading/trailing whitespace.
        if line_stripped not in seen:
            unique_lines.append(line)  # It adds the unique line to the list.
            seen.add(line_stripped)  # Marks this line as seen.

    # Here we are combining the unique lines back into the final text.
    final_text = "\n".join(unique_lines)

    # Removing the repeated prompt from the beginning of the output (if present).
    if prompt in final_text:
        final_text = final_text.replace(prompt, "").strip()

    # Clampping the output length to ~200 words for conciseness.
    words = final_text.split()
    if len(words) > 200:
        final_text = " ".join(words[:200])

    # ------------------------
    # Step 5: Return Response
    # ------------------------
    # Returning the cleaned-up generated text as a JSON response.
    return {"generated_text": final_text}
