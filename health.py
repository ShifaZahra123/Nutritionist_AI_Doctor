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
st.set_page_config(page_title="Gemini Health App")
st.header("Gemini Health App")

input_prompt = """
You are an expert nutritionist. Please analyze the food items in the image, and provide a detailed breakdown of the calorie content for each food item. Ensure that the response includes the following information:

1. List each food item with its name and calorie content.
2. Provide a total calorie count for all items combined.
3. Avoid vague statements, and if quantities are unclear, assume typical portion sizes.

Example response format:

1. Chicken Biryani - 600 calories
2. Mutton Curry - 300 calories
3. Egg Curry - 150 calories
4. Potato Fry - 200 calories
5. Raita - 100 calories
6. Banana - 100 calories
7. Buttermilk - 50 calories

Total calories: 1500 calories
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
        # Save the uploaded file to a temporary path
        temp_path = os.path.join("temp", uploaded_file.name)
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
