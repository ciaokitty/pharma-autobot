import streamlit as st
from ocr import *
import PIL.Image
import json
from schema import MedicationResponse
import logging

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
            st.session_state.final_data =  asyncio.run(process_prescription_with_spell_check(uploaded_file))
            logger.info("Image processing complete")
            
            st.session_state.has_processed = True
    
    
    st.subheader("Analyzed Prescription:")
    
    # Display structured data in a more user-friendly format
    if st.session_state.final_data:
        logger.info("Displaying analyzed prescription data")
        data = st.session_state.final_data
        st.write(data)
        # names = get_medicine_names(data)
        # print(type(names))
        
        # st.write(names)
        
        # st.write(data)
    

