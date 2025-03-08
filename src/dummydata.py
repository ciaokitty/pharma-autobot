from .schema import MedicationResponse, Medication, Instructions, SpellCheckResponse

def generate_dummy_data():
    """
    Generate dummy prescription data for testing purposes.
    
    Returns:
        tuple: (MedicationResponse, SpellCheckResponse) containing sample medication
               and spell check data
    """
    medication_data = MedicationResponse(
        medications=[
            Medication(
                medication_name="Amoxicillin",
                dosage="500mg",
                quantity=30,
                instructions=Instructions(
                    how="Take with food",
                    how_much="1 tablet",
                    when="Every 8 hours for 7 days"
                )
            ),
            Medication(
                medication_name="Ibuprofen",
                dosage="200mg",
                quantity=15,
                instructions=Instructions(
                    how="Take as needed",
                    how_much="1 tablet",
                    when="Every 6 hours if pain persists"
                )
            ),
            Medication(
                medication_name="Lorazepam",
                dosage="1mg",
                quantity=30,
                instructions=Instructions(
                    how="Take at bedtime",
                    how_much="1 tablet",
                    when="Every night for anxiety"
                )
            ),
            Medication(
                medication_name="Paracetamol",
                dosage="500mg",
                quantity=15,
                instructions=Instructions(
                    how="Take with water",
                    how_much="1 tablet",
                    when="Every 4-6 hours for pain"
                )
            ),
            Medication(
                medication_name="Amoxicillin + Clavulanate",
                dosage="500mg + 125mg",
                quantity=21,
                instructions=Instructions(
                    how="Take with food",
                    how_much="1 tablet",
                    when="Every 8 hours for 7 days"
                )
            ),
            Medication(
                medication_name="Sertraline",
                dosage="50mg",
                quantity=30,
                instructions=Instructions(
                    how="Take with water",
                    how_much="1 tablet",
                    when="Every morning"
                )
            )
        ]
    )
    
    spell_check_data = SpellCheckResponse(
        drugs=[
            {
                "input_name": "Amoxicillin",
                "corrected_name": "Amoxicillin",
                "generic_name": ["Amoxicillin"],
                "brand_names": ["Amoxil", "Trimox"],
                "is_correct": True,
                "is_generic": True,
                "notes": "No spelling errors detected."
            },
            {
                "input_name": "Ibuprofen",
                "corrected_name": "Ibuprofen",
                "generic_name": ["Ibuprofen"],
                "brand_names": ["Advil", "Motrin", "Nurofen"],
                "is_correct": True,
                "is_generic": True,
                "notes": "No spelling errors detected."
            },
            {
                "input_name": "Lorazepam",
                "corrected_name": "Lorazepam",
                "generic_name": ["Lorazepam"],
                "brand_names": ["Ativan"],
                "is_correct": True,
                "is_generic": True,
                "notes": "No spelling errors detected."
            },
            {
                "input_name": "Paracetomol",
                "corrected_name": "Paracetamol",
                "generic_name": ["Paracetamol"],
                "brand_names": ["Tylenol", "Panadol"],
                "is_correct": False,
                "is_generic": True,
                "notes": "Common misspelling corrected."
            },
            {
                "input_name": "Amoxicillin + Clavulanate",
                "corrected_name": "Amoxicillin + Clavulanate",
                "generic_name": ["Amoxicillin", "Clavulanic Acid"],
                "brand_names": ["Augmentin", "Clavamox"],
                "is_correct": True,
                "is_generic": True,
                "notes": "Combination drug verified."
            },
            {
                "input_name": "Sertraline",
                "corrected_name": "Sertraline",
                "generic_name": ["Sertraline"],
                "brand_names": ["Zoloft"],
                "is_correct": True,
                "is_generic": True,
                "notes": "No spelling errors detected."
            },
            {
                "input_name": "Enzoflam",
                "corrected_name": "Enzoflam",
                "generic_name": ["Diclofenac", "Paracetamol", "Serratiopeptidase"],
                "brand_names": ["Enzoflam MR", "Enzoflam SP", "Enzoflam CT", "Enzoflam P", "Enzoflam Gel"],
                "is_correct": True,
                "is_generic": False,
                "notes": "Brand name verified. It's a combination drug."
            },
            {
                "input_name": "Advilv",
                "corrected_name": "Advil",
                "generic_name": ["Ibuprofen"],
                "brand_names": ["Advil", "Motrin", "Nurofen"],
                "is_correct": False,
                "is_generic": False,
                "notes": "Likely intended to be 'Advil'."
            },
            {
                "input_name": "Xytrnex",
                "corrected_name": "Unknown",
                "generic_name": [],
                "brand_names": [],
                "is_correct": False,
                "is_generic": False,
                "notes": "Unable to confidently determine the intended medicine."
            }
        ]
    )
    
    return medication_data, spell_check_data
