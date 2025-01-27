# --------------------
# Importing Libraries
# --------------------
import pytest  # Import the Pytest framework for writing and running test cases.
from fastapi.testclient import (
    TestClient,
)  # Import TestClient to simulate requests to the FastAPI app.
from text_generation_service.main import (
    app,
)  # Import the FastAPI app instance from the main application.

# --------------------
# Test Client Setup
# --------------------
# Creating a TestClient instance to interact with the FastAPI app.
client = TestClient(app)


# --------------------
# Root Endpoint Test
# --------------------
# Testing a case for the root endpoint (GET /)
def test_root():
    """
    It tests the root endpoint of the FastAPI service.

    This function checks:
    1. Whether the root endpoint ('/') is reachable (then it sends: status code 200).
    2. Whether the response contains the expected JSON welcome message or not.
    """
    # Makes a GET request to the root endpoint.
    response = client.get("/")

    # Assert the status code is 200 (OK).
    assert response.status_code == 200

    # Assert the JSON response matches the expected welcome message.
    assert response.json() == {"message": "Welcome to the Text Generation Service!"}


# ------------------------------
# Text Generation Endpoint Test
# ------------------------------
# Testing case for the text generation endpoint (POST /generate)
def test_generate():
    """
    It tests the text generation functionality of the FastAPI service.

    This function checks:
    1. Whether the /generate endpoint accepts valid input (then it sends: status code 200).
    2. Whether the response contains a 'generated_text' key in the JSON output or not.
    3. Whether the 'generated_text' value is not empty or not.
    """
    # Defines a payload for the POST request. This includes:
    # - "prompt": The input text prompt for the model.
    # - "max_new_tokens": It manages to give the maximum number of tokens to generate.
    payload = {"prompt": "Testing prompt", "max_new_tokens": 20}

    # Makes a POST request to the /generate endpoint with the payload.
    response = client.post("/generate", json=payload)

    # Asserts the status code is 200 (OK).
    assert response.status_code == 200

    # Extracts the JSON data from the response.
    data = response.json()

    # Asserts the 'generated_text' key exists in the response.
    assert "generated_text" in data

    # Asserts the 'generated_text' value is not empty (indicating a valid generation).
    assert len(data["generated_text"]) > 0
