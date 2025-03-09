import PIL.Image
from google import genai
from google.genai import types
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import json
from dotenv import load_dotenv
import os
from .prompts import *
from .schema import MedicationResponse, SpellCheckResponse
from .exceptions import *
import logging

# Configure module-specific logger
logger = logging.getLogger(__name__)

class APIKeyRotator:
    """
    Rotates through a list of API keys to distribute API usage.

    Attributes:
        keys: List of API keys to rotate through
        index: Current index in the rotation
    """
    def __init__(self, keys: list[str]):
        self.keys = keys
        self.index = 0
        logger.info("APIKeyRotator initialized with %d keys", len(keys))

    def get_next_key(self) -> str:
        """
        Returns the next API key in the rotation.

        Returns:
            str: The next API key
        """
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        logger.info("API key rotated to index %d", self.index)
        return key

# Load API keys from .env file
load_dotenv()
api_keys = [os.getenv("API_KEY"), os.getenv("API_KEY1"), os.getenv("API_KEY2"), os.getenv("API_KEY3"), os.getenv("API_KEY4")]
api_key_rotator = APIKeyRotator(api_keys)

def extract_text_from_image(image) -> MedicationResponse:
    """
    Sends image to Google Gemini API and retrieves structured medication data.

    Args:
        image: The prescription image file (can be bytes or file-like object)

    Returns:
        MedicationResponse: A structured response containing medication information
    """
    logger.info("Extracting text from image")
    client = genai.Client(api_key=api_key_rotator.get_next_key())

    # Handle both bytes and file-like objects
    if isinstance(image, bytes):
        image_bytes = image
        mime_type = "image/jpeg"  # Default to JPEG if unknown
    else:
        image_bytes = image.read()
        mime_type = getattr(image, 'content_type', None) or getattr(image, 'type', 'image/jpeg')

    # Create Gemini-compatible format
    b64_image = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    google_search_tool = Tool(
        google_search = GoogleSearch()
    )

    # First pass: Extract text from image
    response = client.models.generate_content(
        model="gemini-2.0-pro-exp-02-05",
        contents=["this", b64_image],
        config=GenerateContentConfig(
            system_instruction=ocr_system_prompt,
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        ),
    )
    logger.info("Text extraction response received")

    # Prevent NoneType errors
    if not response or not hasattr(response, "text"):
        logger.warning("No text detected in image")
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
    logger.info("Structured text response received")

    # Try to parse the structured response
    try:
        if hasattr(response2, "parsed"):
            logger.info("Parsed structured response successfully")
            return response2.parsed
        else:
            logger.warning("Failed to parse structured response")
            return MedicationResponse(medications=[])
    except Exception as e:
        logger.error("Error parsing structured response: %s", e)
        return MedicationResponse(medications=[])

def get_medicine_names(data: MedicationResponse) -> list[str]:
    """
    Extracts all medication names from a MedicationResponse object.

    Args:
        data: MedicationResponse object containing medications

    Returns:
        list[str]: List of medication names
    """
    names = [i.medication_name for i in data.medications]
    return names

def spell_check_medicine_names(names: list[str], client) -> SpellCheckResponse:
    """
    Spell checks medicine names using Google Gemini.

    Args:
        names: List of medicine names to spell check
        client: The Google Gemini client

    Returns:
        SpellCheckResponse: A structured response containing spell check information
    """
    logger.info("Starting spell check for medicines: %s", names)
    google_search_tool = Tool(
        google_search = GoogleSearch()
    )

    logger.info("Initiating initial spell check request")
    spell_check_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[names],
        config=GenerateContentConfig(
            system_instruction=spell_system_prompt,
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        ),
    )

    # Get the initial response text
    if not spell_check_response or not hasattr(spell_check_response, "text"):
        logger.error("Initial spell check failed - no response text received")
        raise GeminiError("spell check failed")

    logger.info("Initial spell check completed, requesting brand name information")
    brand_name_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[spell_list_brand_name_prompt, spell_check_response.text],
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        ),
    )
    if not brand_name_response or not hasattr(brand_name_response, "text"):
        logger.error("Brand name retrieval failed - no response text received")
        raise GeminiError("brand name retrieval failed")

    logger.info("Brand name information received, generating structured response")
    # Structure the response
    structured_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[spell_structured_output_prompt, spell_check_response.text, brand_name_response.text],
        config={
            'response_mime_type': 'application/json',
            'response_schema': SpellCheckResponse,
        },
    )

    # Try to parse the structured response
    if hasattr(structured_response, "parsed"):
        logger.info("Successfully generated structured spell check response")
        return structured_response.parsed
    else:
        logger.error("Failed to generate structured output")
        raise GeminiError("structured output generation failed")

def fix_spellings(medication_response: MedicationResponse, spell_check_response: SpellCheckResponse) -> MedicationResponse:
    """
    Updates medication names with corrected spellings.

    Args:
        medication_response: Original medication data
        spell_check_response: Spell check results

    Returns:
        MedicationResponse: Updated medication data with corrected spellings
    """
    for spell_check in spell_check_response.drugs:
        if not spell_check.is_correct:
            for medicine in medication_response.medications:
                if medicine.medication_name == spell_check.input_name:
                    medicine.medication_name = spell_check.corrected_name
    return medication_response

def process_prescription_with_spell_check(image):
    """
    Process a prescription image and spell check all extracted medicine names.

    Args:
        image: The prescription image file

    Returns:
        tuple: (MedicationResponse, SpellCheckResponse) containing the
               fixed medication data and spell check results
    """
    # First extract medication data from the image
    medication_data = extract_text_from_image(image)

    # Get all medicine names
    medicine_names = get_medicine_names(medication_data)
    client = genai.Client(api_key=api_key_rotator.get_next_key())
    # Spell check all medicine names
    spell_check_results = spell_check_medicine_names(medicine_names, client)

    fixed_medication_data = fix_spellings(medication_data, spell_check_results)

    return fixed_medication_data, spell_check_results
