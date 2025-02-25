from pydantic import BaseModel, Field

class Instructions(BaseModel):
    """
    Medication instructions model.
    
    Attributes:
        how: How to take the medication (e.g., "Take with food")
        how_much: How much to take (e.g., "1 tablet")
        when: When to take the medication (e.g., "Every 8 hours")
    """
    how: str = Field(..., description="How to take the medication")
    how_much: str = Field(..., description="How much to take")
    when: str = Field(..., description="When to take the medication")

class Medication(BaseModel):
    """
    Medication information model.
    
    Attributes:
        medication_name: Name of the medication
        dosage: Dosage of the medication
        quantity: Quantity to be ordered
        instructions: Detailed instructions for taking the medication
    """
    medication_name: str = Field(..., description="Name of the medication")
    dosage: str = Field(..., description="Dosage of the medication")
    quantity: int = Field(..., description="Quantity to be ordered")
    instructions: Instructions = Field(..., description="Detailed instructions for taking the medication")

class MedicationResponse(BaseModel):
    """
    Response model containing a list of medications.
    
    Attributes:
        medications: List of medication information
    """
    medications: list[Medication] = Field(..., description="List of medication information")

class SpellCheckResponse(BaseModel):
    """
    Response model for spell-checked medication names.
    
    Attributes:
        input_name: Original input name
        corrected_name: Corrected name or original if correct
        generic_name: Generic drug name or 'N/A'
        brand_names: List of brand names
        is_correct: Whether the original spelling was correct
        is_generic: Whether the name is a generic name
        notes: Additional comments if needed
    """
    input_name: str = Field(..., description="Original input name")
    corrected_name: str = Field(..., description="Corrected name or original if correct")
    generic_name: str = Field(..., description="Generic drug name or 'N/A'")
    brand_names: list[str] = Field(..., description="List of brand names")
    is_correct: bool = Field(..., description="Whether the original spelling was correct")
    is_generic: bool = Field(..., description="Whether the name is a generic name")
    notes: str = Field(..., description="Additional comments if needed") 