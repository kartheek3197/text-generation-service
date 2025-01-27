# LLM Text Generation Service

Welcome to the **LLM Text Generation Service**, a containerized microservice that provides text generation capabilities using an opensource pretrained **GPT-2** (base) model from Hugging Face. This project is designed to showcase how a large language model can be deployed locally for real-time text generation.

---

## Key Highlights:

- **Model**: I have used **GPT-2** due to its small size and fewer parameters, making it lightweight and efficient for running on **CPU** without the need for specialized hardware like GPUs.
- **FastAPI**: I chose **FastAPI** because of its ability to auto-generated Swagger docs (`/docs`) and its high performance compared to frameworks like Flask. This makes it easier to create and test RESTful APIs.
- **Streamlit UI**: A simple **Streamlit-based UI** has been implemented to enable user-friendly interactions with the model. This UI can be run locally and provides sliders and inputs for customizing text generation parameters.
- **Dockerized**: The entire FastAPI application and its interaction with the GPT-2 model are fully containerized using **Docker**, making it easy to deploy in any environment.
- **Customizable**: 
  - The service allows dynamic control of text generation parameters such as `temperature`, `top_p`, `max_new_tokens`, and others, which can be passed via the **FastAPI endpoint** or adjusted interactively through the **Streamlit UI**.
  - The **text-generation model** itself can also be swapped. While **GPT-2** is used by default, you can easily change the model to any other Hugging Face-supported text-generation model (eg., **GPT-2 Medium**, **EleutherAI/gpt-neo-1.3B**, or **Flan-T5**) by modifying the `MODEL_NAME` environment variable.
- **Testing and Code Quality**: Performed basic **testing** and maintaining **code quality** with tools like **Pytest** and **Black**.
- **Lightweight and Portable**: The entire application, including the **Docker image**, is optimized for CPU execution, ensuring it can run efficiently in almost any environment without requiring specialized hardware.

---

## Disclaimer: Limitations of GPT-2:

The model used in this service is **GPT-2**, which is a **large language model** trained for **next-word prediction**. Unlike newer instruction-tuned models (e.g., **LLaMA 2**, **Flan-T5**, or **GPT-3.5**), **GPT-2 does not follow structured system/user prompts** in the same way as these advanced models.

Although I attempted to guide its responses using some basic prompt engineering, it only works sometimes. GPT-2 often fails to produce consistent or instruction-following output. For example, even when instructions like "You are a helpful AI assistant" were added to guide its behavior, the generated responses were still prone to **random, off-topic, or repetitive outputs**, especially for open-ended or vague queries.

---

## Architecture Overview:

The project consists of three key components:

1. **FastAPI Backend**:
   - Hosts the `/generate` endpoint to accept user prompts and return generated text.
   - Allows configuration of decoding parameters via request payload.
   - Handles model inference using Hugging Face's `transformers` library.

2. **Streamlit UI**:
   - Provides an interactive frontend for users to input prompts and adjust decoding parameters.
   - Sends requests to the FastAPI backend and displays generated text in real-time.

3. **Dockerized Setup**:
   - A containerized environment that bundles all dependencies and pre-downloads the Hugging Face model for faster startup.
   - Enables easy deployment across environments.

Here’s a high-level flow (local):
- **User Input** → Streamlit UI (local) → FastAPI `/generate` → Model Inference → Generated Text → **Response to UI** (local)

Here is the high-level flow (Docker):
- **Docker Image run** → FastAPI `/generate` [localhost 8000:8000](http://localhost:8000/docs) → Model Inference → **Generated Text**

---

## Prompt Engineering & Post-Processing:

### Prompt Engineering:

As discussed above GPT-2 is not instruction-tuned, it tries to find the next word based on the previous word, we can somewhat guide its outputs:

1. **System-Style Prefix**:  
   - Adding a prefix like "You are a helpful AI assistant. Respond clearly and concisely."  
   - This sometimes nudges GPT-2 toward more direct or "assistant-like" answers. But sometimes it gives some random answers:
        For the prefix: **You are a helpful AI assistant. Respond clearly and concisely.**, it gave the output as: `Do you have any other questions that I should know about or would like to ask me later on this process?`

2. **Few-Shot Examples**:
   - We could try this but need to keep in mind that GPT-2 1024-token context.
   - Provide short Q&A examples in the prompt. For instance:
     ```
     Q: What is 2 + 2?
     A: 4

     Q: {Your question}
     A:
     ```
   - This approach might change GPT-2’s behavior.

3. **Decoding Parameters**: 
   - Use `temperature`, `top_p`, and `repetition_penalty` to reduce repetitive outputs or random off-topic text. 
   - For more controlled results, lower `temperature` (0.5–0.7) and reduce `top_p` (0.8–0.9).

### Post Processing:

There are some post processing work has been done on the generated response:

1. **Removing Repeated Lines**:
   - GPT-2 typically produces repeated texts in the response. Removing the repeated lines by comparing each line generated from the response.
   - GPT-2 generally repeats the question in the response. Removed the question repetition from the generated response by comparing it with prompt.
   - Limiting the word counts to less than 200.

---

## Customizable Parameters Explanation:

There are some customizable parameters that users can control to influence the style and quality of text generation (All these parameters are optional):

1. **`max_new_tokens`**:
   - It helps us to tune the maximum number of tokens that we want the model to generate in the response.
   - So, it controls the length of the output.

2. **`temperature`**:
   - It controls randomness in token selection.
   - That is: if `temperature` is low (e.g., 0.1) then it produces more focused, deterministic results, while if `temperature` is high (e.g., 1.5) then it produces creative and diverse outputs.

3. **`top_p`**:
   - It performs Nucleus sampling, that is: It limits the token selection to the smallest set whose cumulative probability is ≥ `top_p`.
   - Keeps the output coherent while allowing some randomness.
   - For example: If `top_p=0.9`: Then it only considers tokens whose cumulative probability adds up to 90%.

4. **`repetition_penalty`**:
   - It penalizes tokens that have already appeared in the text to avoid redundancy.
   - So, higher the values (e.g., 1.5), discourage repetition more aggressively.

5. **`no_repeat_ngram_size`**:
   - It prevents the repetition of n-grams of the specified size (e.g., `2` for bigrams).
   - So, it ensures the output diversity without sacrificing the coherence.

These parameters allow users to fine-tune the balance between creativity, coherence, and precision.

---

## Run this service:

### Prerequisites
- IDE
- Python 3.8 or later

### Option 1: Running Locally

1. Clone the repository:
   ```
   git clone https://github.com/kartheek3197/text-generation-service.git
   cd text-generation-service
   ```

2. Installing all the required libraries:
    ```
    pip install -r requirements.txt
    ```

3. Starting the FastAPI:
    ```
    uvicorn text_generation_service.main:app --host 0.0.0.0 --port 8000 --reload
    ```

4. Starting the Streamlit UI (This is an optional step, but can be executed for UI interface):
    Open another terminal after starting the FastAPI:
    ```
    streamlit run text_generation_service/ui.py
    ```
    
5. Testing the API: 
   Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger docs.  
   Use a tool like **curl** or **Postman** to test the `/generate` endpoint:

   ```bash
   curl -X POST "http://localhost:8000/generate" \
   -H "Content-Type: application/json" \
   -d '{"prompt": "What is AI?", "max_new_tokens": 50}'

### Option 2: Running with Dockerfile:

1. **Clone the repository**:
   ```
   git clone https://github.com/kartheek3197/text-generation-service.git
   cd text-generation-service
   ```

2. **Building the Docker image**:
    ```
    docker build -t text-generator:latest .
    ```

3. **Running the Docker image**:
    If you want to run the Docker temporarily then:
   ```
    docker run --rm -p 8000:8000 -e MODEL_NAME=gpt2 -e PYTHONUNBUFFERED=1 text-generator:latest
   ```
   to stop the container: `docker stop <container_id>`
   
    If you want to run the Docker for long run:
    ```
    docker run -d -p 8000:8000 -e MODEL_NAME=gpt2 -e PYTHONUNBUFFERED=1 --name text_gen_container text-generator:latest
    ```
    to stop the container: Press `Ctrl+C`

    Here you could change the `MODEL_NAME` if you want.

4. **Starting the Streamlit UI** (This is an optional step, but can be executed for UI interface):
    Open another terminal after starting the FastAPI:
    ```
    streamlit run text_generation_service/ui.py
    ```

5. **Testing the API**:
   Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger docs.  
   Use a tool like **curl** or **Postman** to test the `/generate` endpoint:

   ```bash
   curl -X POST "http://localhost:8000/generate" \
   -H "Content-Type: application/json" \
   -d '{"prompt": "What is AI?", "max_new_tokens": 50}'


### Option 3: Running with Docker Desktop:

1. **Pulling the image**:
    ```bash
    docker pull kartheek3197/text-generator:latest

2. **Starting the Container**:
    Run the image in the docker desktop

3. **Testing the API**:
   Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger docs.  
   Use a tool like **curl** or **Postman** to test the `/generate` endpoint:

   ```bash
   curl -X POST "http://localhost:8000/generate" \
   -H "Content-Type: application/json" \
   -d '{"prompt": "What is AI?", "max_new_tokens": 50}'
   
---

## Testing:

Unit tests have been written for the FastAPI application to verify that the core functionality works as expected.

   1. Test Files: The test cases are located in the text_generation_service/tests directory.
   2. Framework: The tests are written using **Pytest**, a lightweight testing framework.

        You can run the tests using the following commands:
        - Clone the repository and run tests:
            ```bash
            git clone https://github.com/kartheek3197/text-generation-service.git
            cd text-generation-service
           
           pytest text_generation_service/tests --maxfail=1 --disable-warnings
          

---

## Improvements:

There is a lot of scope to improve this **Text-Generation Service**:
   1. **External Inference**: If you want to leverage a hosted inference API (e.g., Hugging Face Inference API or Ollama server) for larger models then more latest open source models like **Deepseek (R1)** which is comparable to GPT-O1 model. So, we can access bigger, more advanced models without local GPU.
   2. **Contextual Importance**: If there is more importance to the internal database, then a **RAG (Rretrieval-Augmented-Generation)** model can be built which gets more accurate response since it will be taken from the internal data.
   3. **Fine-Tuning**: Using Open-source models and fine-tuning with the internal data would give use more appropriate responses from the LLMs.
   4. **Conversational Buffer Memory and Few shot learning**: Using large contexual length LLMs can help us built conversational chatbots along with few shot learning which will drastically improve the response from the service.

---

## Contact:

This has been done for a demo purpose. Please do reach to kartheek3197@gmail.com for any queries.
