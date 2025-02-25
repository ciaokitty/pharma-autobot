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