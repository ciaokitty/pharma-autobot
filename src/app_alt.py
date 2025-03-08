from fastapi import FastAPI, File, UploadFile, Form, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import json
import logging
import uuid
from .ocr import *
from .schema import MedicationResponse, Medication, Instructions, SpellCheckResponse
import pandas as pd
from .dummydata import generate_dummy_data
from .whatsapp_order import send_order_via_whatsapp, format_whatsapp_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pharmacist's Assistant",
    description="Extract and verify medication information from prescription images",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up static files and templates
static_path = Path("public")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Store session data (in memory for demo purposes)
# In production, use a proper session management system
session_store = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Pharmacist's Assistant"}
    )

@app.post("/upload")
async def upload_prescription(
    file: UploadFile = File(None),
    use_dummy: bool = Form(False)
):
    """Handle prescription upload and processing"""
    try:
        if use_dummy:
            logger.info("Using dummy data for testing")
            final_data, spell_check_data = generate_dummy_data()
        elif file:
            # Validate file type
            if not file.content_type.startswith('image/'):
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid file type. Please upload an image file."}
                )
            
            logger.info(f"Processing image: {file.filename} ({file.content_type})")
            try:
                # Read file contents once and store in bytes
                file_bytes = await file.read()
                if not file_bytes:
                    raise ValueError("Empty file uploaded")
                
                final_data, spell_check_data = process_prescription_with_spell_check(file_bytes)
                if not final_data or not final_data.medications:
                    raise ValueError("No medications found in the prescription")
                
                logger.info("Image processing complete")
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to process image: {str(e)}"}
                )
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "No file uploaded and dummy data not selected"}
            )

        # Store results in session
        session_id = str(uuid.uuid4())
        session_store[session_id] = {
            "final_data": final_data,
            "spell_check_data": spell_check_data,
            "edited_data": None,
            "whatsapp_message": ""
        }

        return JSONResponse({
            "session_id": session_id,
            "message": "Prescription processed successfully"
        })
    except Exception as e:
        logger.error(f"Error processing prescription: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/prescription/{session_id}")
async def get_prescription_data(request: Request, session_id: str):
    """Get processed prescription data and render the prescription page"""
    if session_id not in session_store:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Session not found"}
        )
    
    return templates.TemplateResponse(
        "prescription.html",
        {"request": request, "session_id": session_id}
    )

@app.get("/api/prescription/{session_id}")
async def get_prescription_json(session_id: str):
    """Get processed prescription data as JSON"""
    if session_id not in session_store:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )
    
    session_data = session_store[session_id]
    final_data = session_data["final_data"]
    
    if not final_data or not hasattr(final_data, "medications"):
        return JSONResponse(
            status_code=404,
            content={"error": "No medication data found"}
        )
    
    # Convert medication data to table format
    table_data = []
    for med in final_data.medications:
        med_dict = {
            "Medication Name": med.medication_name,
            "Dosage": med.dosage,
            "Quantity": med.quantity,
            "How to Take": med.instructions.how,
            "How Much": med.instructions.how_much,
            "When to Take": med.instructions.when
        }
        table_data.append(med_dict)
    
    return JSONResponse({"medications": table_data})

@app.get("/api/spellcheck/{session_id}")
async def get_spellcheck_json(session_id: str):
    """Get spell check results as JSON"""
    if session_id not in session_store:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )
    
    spell_check_data = session_store[session_id]["spell_check_data"]
    
    if not spell_check_data or not hasattr(spell_check_data, "drugs"):
        return JSONResponse(
            status_code=404,
            content={"error": "No spell check data found"}
        )
    
    # Convert spell check data to table format
    spell_check_table = []
    for drug in spell_check_data.drugs:
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
    
    return JSONResponse({"spell_check": spell_check_table})

@app.post("/update-medications/{session_id}")
async def update_medications(session_id: str, medications: list):
    """Update medication data"""
    if session_id not in session_store:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )
    
    session_store[session_id]["edited_data"] = medications
    whatsapp_message = format_whatsapp_message(medications)
    session_store[session_id]["whatsapp_message"] = whatsapp_message
    
    return JSONResponse({
        "message": "Medications updated successfully",
        "whatsapp_message": whatsapp_message
    })

@app.get("/send-whatsapp/{session_id}")
async def send_whatsapp(
    session_id: str,
    phone_number: str = Query(...),
    custom_message: str = Query(None)
):
    """Send order via WhatsApp"""
    if session_id not in session_store:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )
    
    session_data = session_store[session_id]
    medications = session_data["edited_data"] or []
    message = custom_message or session_data["whatsapp_message"]
    
    whatsapp_url = send_order_via_whatsapp(
        medications,
        phone_number,
        custom_message=message
    )
    
    return RedirectResponse(url=whatsapp_url)

if __name__ == "__main__":
    uvicorn.run("app_alt:app", host="0.0.0.0", port=8000, reload=True)
