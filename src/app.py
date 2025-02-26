import streamlit as st
from ocr import *
import PIL.Image
import json
from schema import MedicationResponse, Medication, Instructions, SpellCheckResponse
import logging
import pandas as pd
import webbrowser
from urllib.parse import quote

# Configure logging for the entire application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output to console
    ]
)

# Configure logger for this module
logger = logging.getLogger(__name__)

# Function to generate dummy data for testing
def generate_dummy_data():
    """Generate dummy prescription data for testing purposes"""
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

# Function to send order via WhatsApp
def send_order_via_whatsapp(medications, pharmacy_number):
    """
    Send medication list to a pharmacy via WhatsApp
    
    Args:
        medications: List of medication dictionaries
        pharmacy_number: WhatsApp number of the pharmacy
    """
    # Format message with medication details
    message = "Hello, I want to order the following medicines:\n\n"
    
    for med in medications:
        med_line = f"• {med['Medication Name']} {med['Dosage']} - Qty: {med['Quantity']}"
        message += med_line + "\n"
    
    # Encode message for URL
    encoded_message = quote(message)
    
    # Generate WhatsApp Web/Mobile link
    whatsapp_url = f"https://wa.me/{pharmacy_number}?text={encoded_message}"
    
    # Open WhatsApp with the pre-filled message
    webbrowser.open(whatsapp_url)
    
    return message

# Initialize session state variables if they don't exist
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'has_processed' not in st.session_state:
    st.session_state.has_processed = False
if 'structured_data' not in st.session_state:
    st.session_state.structured_data = None
if 'spell_check_data' not in st.session_state:
    st.session_state.spell_check_data = None
if 'edited_data' not in st.session_state:
    st.session_state.edited_data = None
if 'final_data' not in st.session_state:
    st.session_state.final_data = None
if 'use_dummy_data' not in st.session_state:
    st.session_state.use_dummy_data = False

st.title("Pharmacist's Assistant")
logger.info("Application started")
st.write("Upload a prescription image, and we'll extract and verify the medicines for you.")

# Add a checkbox to toggle between real processing and dummy data
use_dummy = st.checkbox("Use dummy data for testing", value=st.session_state.use_dummy_data)
if use_dummy != st.session_state.use_dummy_data:
    st.session_state.use_dummy_data = use_dummy
    st.session_state.has_processed = False
    st.session_state.final_data = None

uploaded_file = st.file_uploader("Upload Prescription Image", type=["png", "jpg", "jpeg"])

if uploaded_file or st.session_state.use_dummy_data:
    if uploaded_file and not st.session_state.use_dummy_data:
        logger.info("File uploaded: %s", uploaded_file.name)
        image = PIL.Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
    
    # Only process the image if it hasn't been processed yet
    if not st.session_state.has_processed:
        if st.session_state.use_dummy_data:
            logger.info("Using dummy data for testing")
            st.session_state.final_data, st.session_state.spell_check_data = generate_dummy_data()
        else:
            logger.info("Processing image")
            uploaded_file.seek(0)
            
            with st.spinner("Extracting and verifying medicines..."):
                st.session_state.final_data, st.session_state.spell_check_data = process_prescription_with_spell_check(uploaded_file)
                logger.info("Image processing complete")
        
        st.session_state.has_processed = True
    
    
    st.subheader("Analyzed Prescription:")
    
    # Display structured data in a more user-friendly format
    if st.session_state.final_data:
        logger.info("Displaying analyzed prescription data")
        data = st.session_state.final_data
        
        # Create a table to display medication information
        if hasattr(data, 'medications') and data.medications:
            # Create a list to store the flattened medication data
            table_data = []
            
            for med in data.medications:
                # Flatten the nested structure for tabular display
                med_dict = {
                    "Medication Name": med.medication_name,
                    "Dosage": med.dosage,
                    "Quantity": med.quantity,
                    "How to Take": med.instructions.how,
                    "How Much": med.instructions.how_much,
                    "When to Take": med.instructions.when
                }
                table_data.append(med_dict)
            
            # Convert to DataFrame for display
            df = pd.DataFrame(table_data)
            
            # Display the table with editing capabilities
            edited_df = st.data_editor(
                df,
                key="medication_editor",
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "Medication Name": st.column_config.TextColumn("Medication Name", help="Name of the prescribed medication"),
                    "Dosage": st.column_config.TextColumn("Dosage", help="Prescribed dosage"),
                    "Quantity": st.column_config.NumberColumn("Quantity", help="Number of units prescribed"),
                    "How to Take": st.column_config.TextColumn("How to Take", help="Instructions on how to take the medication"),
                    "How Much": st.column_config.TextColumn("How Much", help="Amount to take per dose"),
                    "When to Take": st.column_config.TextColumn("When to Take", help="Timing for taking the medication")
                }
            )
            
            # Store the edited dataframe in session state
            st.session_state.edited_data = edited_df
            
            # Add WhatsApp order button
            pharmacy_number = st.text_input("Pharmacy WhatsApp Number ", value="")
            
            # Format the message for preview
            if "whatsapp_message" not in st.session_state:
                # Initialize with default message
                medications_to_order = edited_df.to_dict('records')
                message = "Hello, I want to order the following medicines:\n\n"
                for med in medications_to_order:
                    message += f"-- {med['Medication Name']} {med['Dosage']} - Qty: {med['Quantity']}\n"
                st.session_state.whatsapp_message = message
            
            # Show message preview with editing capability
            st.subheader("Message Preview")
            st.session_state.whatsapp_message = st.text_area(
                "Edit your message before sending:",
                value=st.session_state.whatsapp_message,
                height=200
            )
            
            # Send button
            if st.button("Send Order via WhatsApp"):
                # Encode message for URL
                encoded_message = quote(st.session_state.whatsapp_message)
                
                # Generate WhatsApp Web/Mobile link
                whatsapp_url = f"https://wa.me/{pharmacy_number}?text={encoded_message}"
                
                # Open WhatsApp with the pre-filled message
                webbrowser.open(whatsapp_url)
                
                # Show confirmation
                st.success("Opening WhatsApp with your order!")
            
            # Show information about edits
            with st.expander("View Edit Information"):
                st.write("### Changes Made to the Table")
                if "medication_editor" in st.session_state:
                    edit_info = st.session_state["medication_editor"]
                    st.write("#### Edited Rows")
                    st.json(edit_info.get("edited_rows", {}))
                    
                    st.write("#### Added Rows")
                    st.json(edit_info.get("added_rows", []))
                    
                    st.write("#### Deleted Rows")
                    st.json(edit_info.get("deleted_rows", []))
                else:
                    st.write("No edits made yet.")
            
            # Add an expandable section with the raw data for reference
            with st.expander("View Raw Data"):
                st.json(json.loads(data.json()))
        else:
            st.warning("No medication data found in the processed results.")
    
    # Display spell check data
    if st.session_state.spell_check_data:
        st.subheader("Spell Check Results:")
        spell_check_data = st.session_state.spell_check_data
        
        if hasattr(spell_check_data, 'drugs') and spell_check_data.drugs:
            # Create a list to store the spell check data
            spell_check_table = []
            
            for drug in spell_check_data.drugs:
                # Create a dictionary for each drug
                drug_dict = {
                    "Original Name": drug.input_name,
                    "Corrected Name": drug.corrected_name,
                    "Generic Names": ", ".join(drug.generic_name),
                    "Brand Names": ", ".join(drug.brand_names),
                    "Correctly Spelled": "✓" if drug.is_correct else "✗",
                    "Is Generic": "Yes" if drug.is_generic else "No",
                    "Notes": drug.notes
                }
                spell_check_table.append(drug_dict)
            
            # Convert to DataFrame for display
            spell_check_df = pd.DataFrame(spell_check_table)
            
            # Display the table
            st.dataframe(
                spell_check_df,
                use_container_width=True,
                column_config={
                    "Original Name": st.column_config.TextColumn("Original Name", help="Original medication name from prescription"),
                    "Corrected Name": st.column_config.TextColumn("Corrected Name", help="Corrected medication name"),
                    "Generic Names": st.column_config.TextColumn("Generic Names", help="Generic names of the medication"),
                    "Brand Names": st.column_config.TextColumn("Brand Names", help="Common brand names"),
                    "Correctly Spelled": st.column_config.TextColumn("Correctly Spelled", help="Whether the original spelling was correct"),
                    "Is Generic": st.column_config.TextColumn("Is Generic", help="Whether the name is a generic drug name"),
                    "Notes": st.column_config.TextColumn("Notes", help="Additional information")
                }
            )
            
            # Add an expandable section with the raw spell check data
            with st.expander("View Raw Spell Check Data"):
                st.json(json.loads(spell_check_data.json()))
        else:
            st.warning("No spell check data found in the processed results.")

