from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def upload_to_gemini(file_path, mime_type=None):
    """Uploads the given file to Gemini and returns the file object."""
    # Upload the file to Gemini
    file = genai.upload_file(path=file_path, mime_type=mime_type)
    st.write(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def get_gemini_response(file, prompt):
    """Generates a response from the Gemini model using the uploaded image and prompt."""
    # Configure the model
    generation_config = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 1024,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config
    )

    # Start a chat session and send the prompt
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    file,  # Image file part
                    prompt  # Text prompt part
                ],
            },
        ]
    )
    response = chat_session.send_message(prompt)
    return response.text

# Streamlit app setup
st.set_page_config(page_title="Calorie Advisor App")
st.header("Calorie Advisor App")

input_prompt = """
You are an expert nutritionist. Analyze the food items in the image, calculate the total calories, 
and provide details of each food item with its calorie intake in the following format:

1. Item 1 - no of calories
2. Item 2 - no of calories
----
----
Finally you can also mention whether the food is healthy or notand also mention the percentage split of the ratio of carbohydrates, fats, fibres, sugar and other important things required in our diet
"""

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

submit = st.button("Tell me the total calories")

# Handle submit button click
if submit:
    if uploaded_file is not None:
        # Ensure the temp directory exists
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Save the uploaded file to the temp directory
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Upload the image and get a response
        file = upload_to_gemini(temp_path, mime_type=uploaded_file.type)
        response = get_gemini_response(file, input_prompt)
        
        st.subheader("The Response is")
        st.write(response)
        
        # Clean up the temporary file
        os.remove(temp_path)
    else:
        st.error("Please upload an image first.")
