import streamlit as st
import streamlit.components.v1 as components
from ocr import *
import PIL.Image
import json
import pathlib
from streamlit_lottie import st_lottie
from schema import MedicationResponse, Medication, Instructions, SpellCheckResponse
import logging
import pandas as pd
from dummydata import generate_dummy_data
from whatsapp_order import send_order_via_whatsapp, format_whatsapp_message

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

# Function to load Lottie animation files
def load_lottie_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

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
if 'whatsapp_message' not in st.session_state:
    st.session_state.whatsapp_message = ""
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0  # 0 for Prescription, 1 for Spell Check, 2 for Order

# Set page configuration
st.set_page_config(
    page_title="Pharmacist's Assistant",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== SIDEBAR =====
with st.sidebar:
    st.title("💊 Pharmacist's Assistant")
    st.markdown("---")
    
    st.subheader("Configuration")
    # Add a checkbox to toggle between real processing and dummy data
    use_dummy = st.checkbox("Use dummy data for testing", value=st.session_state.use_dummy_data)
    if use_dummy != st.session_state.use_dummy_data:
        st.session_state.use_dummy_data = use_dummy
        st.session_state.has_processed = False
        st.session_state.final_data = None
    
    st.markdown("---")
    
    # File uploader in sidebar
    st.subheader("Upload Prescription")
    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        logger.info("File uploaded: %s", uploaded_file.name)
        # Show a small preview in the sidebar
        image = PIL.Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
    
    st.markdown("---")
    
    # Process button
    process_button = st.button("Process Prescription", type="primary", use_container_width=True)
    
    # App information
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app helps pharmacists extract and verify medication information from prescription images.")
    st.markdown("© 2023 Pharmacist's Assistant")

# ===== MAIN CONTENT =====
# Main area title
st.title("Prescription Analysis")
st.markdown("Upload a prescription image in the sidebar, and we'll extract and verify the medicines for you.")

# Process the prescription if button is clicked or if using dummy data
if process_button or (st.session_state.use_dummy_data and not st.session_state.has_processed):
    if st.session_state.use_dummy_data:
        logger.info("Using dummy data for testing")
        with st.spinner("Generating dummy data..."):
            st.session_state.final_data, st.session_state.spell_check_data = generate_dummy_data()
    elif uploaded_file:
        logger.info("Processing image")
        uploaded_file.seek(0)
        
        with st.spinner("Extracting and verifying medicines..."):
            st.session_state.final_data, st.session_state.spell_check_data = process_prescription_with_spell_check(uploaded_file)
            logger.info("Image processing complete")
    
    st.session_state.has_processed = True
    
    # If we have data, update the WhatsApp message
    if st.session_state.final_data and hasattr(st.session_state.final_data, 'medications'):
        # Create a list to store the flattened medication data
        table_data = []
        
        for med in st.session_state.final_data.medications:
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
        
        # Initialize WhatsApp message
        st.session_state.whatsapp_message = format_whatsapp_message(table_data)

# Create tabs for different sections
if st.session_state.has_processed:
    # Use radio buttons to simulate tabs with better control
    tab_names = ["Prescription", "Spell Check", "Order"]
    
    # Create a horizontal container for the tab-like radio buttons
    tab_cols = st.columns(len(tab_names))
    
    # Style for the selected and unselected tabs
    selected_style = """
    <style>
    div[data-testid="stHorizontalBlock"] > div:nth-child({}) button {{
        background-color: #f0f2f6;
        border-bottom: 2px solid #4e8cff;
        font-weight: bold;
    }}
    </style>
    """
    
    # Function to handle tab selection
    def select_tab(tab_index):
        st.session_state.active_tab = tab_index
    
    # Create the tab-like radio buttons
    for i, (col, name) in enumerate(zip(tab_cols, tab_names)):
        with col:
            if st.button(
                name, 
                key=f"tab_{i}",
                use_container_width=True,
                on_click=select_tab,
                args=(i,)
            ):
                pass
    
    # Display the selected style for the active tab
    st.markdown(selected_style.format(st.session_state.active_tab + 1), unsafe_allow_html=True)
    
    # Display content based on the active tab
    active_tab = st.session_state.active_tab
    
    # === TAB 1: PRESCRIPTION DATA ===
    if active_tab == 0:
        st.header("Analyzed Prescription")
        
        if st.session_state.final_data and hasattr(st.session_state.final_data, 'medications'):
            data = st.session_state.final_data
            
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
            st.subheader("Medication Information")
            st.markdown("Review and edit the extracted medication information below:")
            
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
    
    # === TAB 2: SPELL CHECK ===
    elif active_tab == 1:
        st.header("Spell Check Results")
        
        if st.session_state.spell_check_data and hasattr(st.session_state.spell_check_data, 'drugs'):
            spell_check_data = st.session_state.spell_check_data
            
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
            st.markdown("Review the spell check results for medication names:")
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
    
    # === TAB 3: ORDER VIA WHATSAPP ===
    elif active_tab == 2:
        st.header("Send Order to Pharmacy")
        
        if st.session_state.edited_data is not None:
            # Pharmacy WhatsApp number input
            st.subheader("Pharmacy Information")
            pharmacy_number = st.text_input(
                "Pharmacy WhatsApp Number", 
                placeholder="+1234567890"
            )
            
            # Message preview and editing
            st.subheader("Message Preview")
            st.markdown("Edit your message before sending:")
            
            st.session_state.whatsapp_message = st.text_area(
                "Message content",
                value=st.session_state.whatsapp_message,
                height=200,
                label_visibility="collapsed"
            )
            
            # WhatsApp button
            st.subheader("Send Order")
            if pharmacy_number:
                medications_to_order = st.session_state.edited_data.to_dict('records')
                whatsapp_url = send_order_via_whatsapp(
                    medications_to_order, 
                    pharmacy_number, 
                    custom_message=st.session_state.whatsapp_message
                )
                
                # Create a custom HTML button with JavaScript to open in a new tab
                whatsapp_button_html = f"""
                <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                    <button style="
                        background-color: #25D366; 
                        color: white; 
                        padding: 10px 24px; 
                        border: none; 
                        border-radius: 4px; 
                        cursor: pointer;
                        font-weight: bold;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        margin: 10px 0;
                    ">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M13.601 2.326A7.854 7.854 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.933 7.933 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.898 7.898 0 0 0 13.6 2.326zM7.994 14.521a6.573 6.573 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.557 6.557 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592zm3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.346.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.729.729 0 0 0-.529.247c-.182.198-.691.677-.691 1.654 0 .977.71 1.916.81 2.049.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232z"/>
                        </svg>
                        Send Order via WhatsApp
                    </button>
                </a>
                """
                components.html(whatsapp_button_html, height=50)
                st.markdown("*Click the button above to open WhatsApp with your order*")
            else:
                st.error("Please enter a pharmacy WhatsApp number to send the order.")
        else:
            st.warning("Please process a prescription first to generate medication data.")
else:
    # Show instructions when no prescription has been processed
    st.info("👈 Please upload a prescription image in the sidebar and click 'Process Prescription' to begin.")
    
    # Placeholder for demonstration
    st.markdown("### How it works")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 1. Upload")
        st.markdown("Upload a prescription image through the sidebar")
        lottie_upload = load_lottie_file("/home/ciaokitty/pharma-autobot/public/Animation - Upload.json")
        st_lottie(lottie_upload, height=150, key="upload_animation")
    
    with col2:
        st.markdown("#### 2. Process")
        st.markdown("Our AI extracts and verifies medication information")
        lottie_upload = load_lottie_file("/home/ciaokitty/pharma-autobot/public/Animation - Process.json")
        st_lottie(lottie_upload, height=150, key="process_animation")
    
    with col3:
        st.markdown("#### 3. Order")
        st.markdown("Send the verified order to your pharmacy via WhatsApp")
        lottie_upload = load_lottie_file("/home/ciaokitty/pharma-autobot/public/Animation - Order.json")
        st_lottie(lottie_upload, height=150, key="order_animation")

