# --------------------
# Importing Libraries
# --------------------
import streamlit as st  # Streamlit library is used to build the user interface.
import requests  # For making HTTP requests to the FastAPI backend.


# --------------------
# Main Function
# --------------------
def main():
    """
    This Main function runs the Streamlit application.
    This provides a user interface to interact with the FastAPI-based text generation service.
    The end-user can customize the parameters and give the input to get the response.
    """

    # Setting the title of the Streamlit application.
    st.title("Local LLM Text Generation Service")

    # it Provides a brief description of the application.
    st.write(
        """
    This is a simple UI to interact with the local text generation API (FastAPI).
    """
    )

    # --------------------
    # Form for User Input
    # --------------------
    with st.form("GenerationForm"):
        """
        It creates a form that allows the user to:
        - Input a text prompt.
        - Adjust various decoding parameters (e.g., max_new_tokens, temperature, etc.).
        - Submit the form to generate text.
        """

        # This is to input text prompt for the model.
        prompt = st.text_area("Prompt", "Once upon a time, ")

        # Slider for max_new_tokens (controls the length of the generated text).
        max_new_tokens = st.slider("max_new_tokens", 10, 200, 50)

        # Slider for temperature (controls randomness; higher = more diverse).
        temperature = st.slider("temperature", 0.1, 2.0, 0.7, 0.1)

        # Slider for top_p (Nucleus sampling; limits sampling to cumulative probability p).
        top_p = st.slider("top_p", 0.1, 1.0, 0.9, 0.05)

        # Slider for repetition_penalty (penalizes repeated tokens; higher = less repetition).
        repetition_penalty = st.slider("repetition_penalty", 1.0, 2.0, 1.2, 0.1)

        # Slider for no_repeat_ngram_size (prevents repetition of n-grams of the specified size).
        no_repeat_ngram_size = st.slider("no_repeat_ngram_size", 0, 5, 2)

        # Submit button to trigger text generation.
        submitted = st.form_submit_button("Generate")

    # --------------------
    # API Call on Form Submission
    # --------------------
    if submitted:
        """
        If the form is submitted:
        1. It first collects all user input parameters.
        2. Then it make a POST request to the FastAPI `/generate` endpoint with the parameters.
        3. Fially it display the generated text or an error message.
        """

        # Defines the URL for the FastAPI backend endpoint.
        url = "http://localhost:8000/generate"

        # Creates the payload for the API request based on the user's input.
        payload = {
            "prompt": prompt,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "repetition_penalty": repetition_penalty,
            "no_repeat_ngram_size": no_repeat_ngram_size,
        }

        # Trying to send the request to the API and handle the response.
        try:
            # Makes a POST request to the API with the payload.
            resp = requests.post(url, json=payload)

            # If the request is successful (status code 200), display the generated text.
            if resp.status_code == 200:
                # It parses the JSON response from the API.
                data = resp.json()

                # Displays the generated text in the Streamlit app.
                st.subheader("Generated Text:")
                st.write(data["generated_text"])

            # If the API returns an error, display the error message and status code.
            else:
                st.error(f"Error: {resp.status_code}, {resp.text}")

        # If there is a connection issue or other exception, display an error message.
        except Exception as e:
            st.error(f"Could not connect to the API: {e}")


# --------------------
# Run the Streamlit App
# --------------------
if __name__ == "__main__":
    """
    This is the entry point for the Streamlit application.
    When the script is executed, it runs the `main` function.
    """
    main()
