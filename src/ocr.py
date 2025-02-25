import PIL.Image
from google import genai
from google.genai import types
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import json
from dotenv import load_dotenv
import os
from prompts import *
from schema import MedicationResponse, SpellCheckResponse
import asyncio
from exceptions import *

# Function to rotate API keys
class APIKeyRotator:
    def __init__(self, keys: list[str]):
        self.keys = keys
        self.index = 0

    def get_next_key(self) -> str:
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key

# Load API keys from .env file
load_dotenv()
api_keys = [os.getenv("API_KEY"), os.getenv("API_KEY1"), os.getenv("API_KEY2"), os.getenv("API_KEY3"), os.getenv("API_KEY4")]
api_key_rotator = APIKeyRotator(api_keys)

def extract_text_from_image(image) -> MedicationResponse:
    """
    Sends image to Google Gemini API and retrieves structured medication data.
    
    Args:
        image: The prescription image file
        
    Returns:
        MedicationResponse: A structured response containing medication information
    """
    client = genai.Client(api_key=api_key_rotator.get_next_key())
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

async def spell_check_medicine_name(name: str, client) -> SpellCheckResponse:
    """
    Asynchronously spell checks a medicine name using Google Gemini.
    
    Args:
        name: The medicine name to spell check
        client: The Google Gemini client
        
    Returns:
        SpellCheckResponse: A structured response containing spell check information
    """
    google_search_tool = Tool(
        google_search = GoogleSearch()
    )
    
    spell_check_response = await client.models.generate_content(
        model="gemini-1.5-flash-8b",
        contents=[name],
        config=GenerateContentConfig(
            system_instruction=spell_system_prompt,
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        ),
    )
    
    # Get the initial response text
    if not spell_check_response or not hasattr(spell_check_response, "text"):
        # Return a default response if no text detected
        raise GeminiError("spell check failed")
    
    brand_name_response = client.models.generate_content(
    model="gemini-1.5-flash-8b",
    contents=[spell_list_brand_name_prompt, spell_check_response.text],
    config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        ),
    )
    if not brand_name_response or not hasattr(brand_name_response, "text"):
    # Return a default response if no text detected
        raise GeminiError("brand name retrieval failed")

    # Structure the response
    structured_response = await client.models.generate_content(
        model="gemini-1.5-flash-8b",
        contents=[spell_structured_output_prompt, spell_check_response.text, brand_name_response.text],
        config={
            'response_mime_type': 'application/json',
            'response_schema': SpellCheckResponse,
        },
    )
    
    # Try to parse the structured response
    
    if hasattr(structured_response, "parsed"):
        return structured_response.parsed
    else:
        # Fallback to default response
        raise GeminiError("structured output generation failed")
   

async def spell_check_all_medicines(names: list[str]) -> list[SpellCheckResponse]:
    """
    Asynchronously spell checks multiple medicine names using Google Gemini.
    
    Args:
        names: List of medicine names to spell check
        
    Returns:
        list[SpellCheckResponse]: A list of structured responses for each medicine name
    """
    client = genai.Client(api_key=api_key_rotator.get_next_key())
    tasks = [spell_check_medicine_name(name, client) for name in names]
    results = await asyncio.gather(*tasks)
    return results

def fix_spellings(medication_response: MedicationResponse, spell_check_responses: list[SpellCheckResponse]) -> MedicationResponse:
    for spell_check_response in spell_check_responses:
        if not spell_check_response.is_correct:
            for medicine in medication_response.medications:
                if medicine.medication_name == spell_check_response.input_name:
                    medicine.medication_name = spell_check_response.corrected_name
    return medication_response

async def process_prescription_with_spell_check(image):
    """
    Process a prescription image and spell check all extracted medicine names.
    
    Args:
        image: The prescription image file
        
    Returns:
        tuple: (MedicationResponse, list[SpellCheckResponse]) containing the 
               original medication data and spell check results
    """
    # First extract medication data from the image
    medication_data = extract_text_from_image(image)
    
    # Get all medicine names
    medicine_names = get_medicine_names(medication_data)
    
    # Spell check all medicine names asynchronously
    spell_check_results = await spell_check_all_medicines(medicine_names)

    fixed_medication_data = fix_spellings(medication_data, spell_check_results)
    print(fixed_medication_data)

    return fixed_medication_data
    
    



