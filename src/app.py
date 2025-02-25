import streamlit as st
from ocr import *
import PIL.Image
import json
from schema import MedicationResponse
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

# Initialize session state variables if they don't exist
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'has_processed' not in st.session_state:
    st.session_state.has_processed = False
if 'structured_data' not in st.session_state:
    st.session_state.structured_data = None

st.title("Pharmacist's Assistant")
logger.info("Application started")
st.write("Upload a prescription image, and we'll extract and verify the medicines for you.")

uploaded_file = st.file_uploader("Upload Prescription Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    logger.info("File uploaded: %s", uploaded_file.name)
    image = PIL.Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    # Only process the image if it hasn't been processed yet
    if not st.session_state.has_processed:
        logger.info("Processing image")
        uploaded_file.seek(0)
        
        with st.spinner("Extracting and verifying medicines..."):
            st.session_state.final_data =  process_prescription_with_spell_check(uploaded_file)
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
            
            # Display the table with styling
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Medication Name": st.column_config.TextColumn("Medication Name", help="Name of the prescribed medication"),
                    "Dosage": st.column_config.TextColumn("Dosage", help="Prescribed dosage"),
                    "Quantity": st.column_config.NumberColumn("Quantity", help="Number of units prescribed"),
                    "How to Take": st.column_config.TextColumn("How to Take", help="Instructions on how to take the medication"),
                    "How Much": st.column_config.TextColumn("How Much", help="Amount to take per dose"),
                    "When to Take": st.column_config.TextColumn("When to Take", help="Timing for taking the medication")
                }
            )
            
            # Add an expandable section with the raw data for reference
            with st.expander("View Raw Data"):
                st.json(json.loads(data.json()))
        else:
            st.warning("No medication data found in the processed results.")
    

