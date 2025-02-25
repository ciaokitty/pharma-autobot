import streamlit as st
from ocr import *
import PIL.Image
import json
from schema import MedicationResponse, Medication, Instructions
import logging
import pandas as pd

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
    return MedicationResponse(
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
            )
        ]
    )

# Initialize session state variables if they don't exist
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'has_processed' not in st.session_state:
    st.session_state.has_processed = False
if 'structured_data' not in st.session_state:
    st.session_state.structured_data = None
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
            st.session_state.final_data = generate_dummy_data()
        else:
            logger.info("Processing image")
            uploaded_file.seek(0)
            
            with st.spinner("Extracting and verifying medicines..."):
                st.session_state.final_data = process_prescription_with_spell_check(uploaded_file)
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
    

