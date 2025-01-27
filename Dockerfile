# -----------------------------
# Step 1: Use Python Slim Base
# -----------------------------
# Starting from a lightweight Python 3.9 slim image to keep the base image size small.
FROM python:3.9-slim

# ------------------------------
# Step 2: Set Working Directory
# ------------------------------
# Setting the working directory inside the container.
WORKDIR /text_generator_service

# -----------------------------
# Step 3: Install Dependencies
# -----------------------------
# Copy the requirements.txt file to leverage Docker's caching mechanism.
# This ensures that dependencies are installed only when requirements.txt changes.
COPY requirements.txt .

# Installing dependencies with pip:
# - `--no-cache-dir`: Preventing the pip from caching to reduce image size.
# - `--extra-index-url`: It ensures PyTorch is downloaded for CPU to keep the image size small.
# - `-r requirements.txt`: It installs the dependencies listed in requirements.txt.
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

# ------------------------------
# Step 4: Copy Application Code
# ------------------------------
# Copy the rest of the application code, including the `text_generation_service` folder, into the container.
COPY text_generation_service text_generation_service

# ----------------------------------
# Step 5: Download Model (Optional)
# ----------------------------------
# Here we are pre-downloading the Hugging Face model during the build process to:
# - Avoid downloading the model at runtime (first request latency).
# - Store the model directly in the Docker image.
# Note: This will increase the image size since the model will be embedded into the image.
ENV MODEL_NAME=gpt2
RUN python -c "from transformers import pipeline; pipeline('text-generation', model='${MODEL_NAME}')"

# ----------------------------
# Step 6: Expose FastAPI Port
# ----------------------------
# Expose port 8000 for the FastAPI app.
EXPOSE 8000

# --------------------------------
# Step 7: Set Up Gunicorn Command
# --------------------------------
# Use Gunicorn with Uvicorn workers for production readiness.
# - `-k uvicorn.workers.UvicornWorker`: It specifies Uvicorn workers.
# - `-w 2`: Configures 2 workers (increases for higher throughput in production).
# - `--bind 0.0.0.0:8000`: It binds the application to all interfaces on port 8000.
CMD ["gunicorn", "text_generation_service.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "--bind", "0.0.0.0:8000"]
