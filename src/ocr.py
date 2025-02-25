import PIL.Image
from google import genai
from google.genai import types
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import json
from dotenv import load_dotenv
import os
from prompts import *
from schema import MedicationResponse

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

def extract_text_from_image(image) -> MedicationResponse:
    """
    Sends image to Google Gemini API and retrieves structured medication data.
    
    Args:
        image: The prescription image file
        
    Returns:
        MedicationResponse: A structured response containing medication information
    """
    client = genai.Client(api_key=API_KEY)
    image_bytes = image.read()
    
    # Create Gemini-compatible format
    b64_image = types.Part.from_bytes(
        data=image_bytes,
        mime_type=image.type
    )
    
    google_search_tool = Tool(
        google_search = GoogleSearch()
    )
    
    # First pass: Extract text from image
    response = client.models.generate_content(
        model="gemini-2.0-pro-exp-02-05",
        contents=[b64_image],
        config=GenerateContentConfig(
            system_instruction=ocr_system_prompt,
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        ),
    )
    #print(response.text)
    
    # Prevent NoneType errors
    if not response or not hasattr(response, "text"):
        # Return empty response if no text detected
        return MedicationResponse(medications=[])
    
    # Second pass: Structure the extracted text
    response2 = client.models.generate_content(
        model="gemini-2.0-pro-exp-02-05",
        contents=[ocr_structured_output_prompt, response.text],
        config={
            'response_mime_type': 'application/json',
            'response_schema': MedicationResponse,
        },
    )
    
    # Try to parse the structured response
    try:
        if hasattr(response2, "parsed"):
            # If the model returns a parsed object
            print(type(response2.parsed))
            print(response2.parsed)
            return response2.parsed
        else:
            # Fallback to empty response
            return MedicationResponse(medications=[])
    except Exception as e:
        print(f"Error parsing structured response: {e}")
        # Return the raw text as a fallback
        # return response.text

def get_medicine_names(data: MedicationResponse) -> list[str]:
    names = [i.medication_name for i in data.medications]
    return names


