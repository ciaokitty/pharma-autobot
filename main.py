import streamlit as st
import pathlib
import PIL.Image
from google import genai
from google.genai import types
#from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

def extract_text_from_image(image):
    """Sends image to Google Gemini API and retrieves extracted text with grounding."""

    class Medicine(BaseModel):
        drug_name: str
        dosage: list[str]

    client = genai.Client(api_key=API_KEY)

    
    

    # Convert uploaded file to bytes
    image_bytes = image.read()
    
    # Create Gemini-compatible format
    b64_image = types.Part.from_bytes(
        data=image_bytes,
        mime_type=image.type
    )
    
    prompt = """
    Extract the names of medicines and their dosages from this prescription image.
    For each medicine found:
    1. Search and verify the medicine name
    2. List the dosage as written in the prescription, if no dosage is interpreted list "dosage not clear"
    3. If found through search, include basic information about the medicine's purpose
    
    
    """
    
    response = client.models.generate_content(
        # model="gemini-2.0-pro-exp-02-05",
        model="gemini-2.0-flash-lite-preview-02-05"
        contents=[prompt, b64_image],
        config={
        'response_mime_type': 'application/json',
        'response_schema': list[Medicine],
    },
    )
    
    # Prevent NoneType errors
    if not response or not hasattr(response, "text"):
        return "No text detected"

    return response.text

# Streamlit UI
st.title("Pharmacist's Assistant")
st.write("Upload a prescription image, and we'll extract and verify the medicines for you.")

uploaded_file = st.file_uploader("Upload Prescription Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = PIL.Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    uploaded_file.seek(0)
    
    with st.spinner("Extracting and verifying medicines..."):
        extracted_text = extract_text_from_image(uploaded_file)

    #st.write(extracted_text.model_json_schema)
    
    st.subheader("Analyzed Prescription:")
    st.markdown(extracted_text)  # Using markdown to properly render formatted text
    
    # Add a download button for the analysis
    st.download_button(
        label="Download Analysis",
        data=extracted_text,
        file_name="prescription_analysis.txt",
        mime="text/plain"
    )
