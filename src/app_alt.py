from fastapi import FastAPI, File, UploadFile, Form, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import json
from loguru import logger
import uuid
from .ocr import *
from .schema import MedicationResponse, Medication, Instructions, SpellCheckResponse
import pandas as pd
from .dummydata import generate_dummy_data
from .whatsapp_order import send_order_via_whatsapp, format_whatsapp_message

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
async def upload_file(file: UploadFile = File(None), use_dummy: bool = Form(False)):
    """Handle file upload and process prescription"""
    try:
        session_id = str(uuid.uuid4())

        if use_dummy:
            logger.info("Using dummy data for testing")
            final_data, spell_check_data = generate_dummy_data()
            image_data = None
        else:
            if not file:
                raise HTTPException(status_code=400, detail="No file uploaded")

            # Read the file content
            file_content = await file.read()

            logger.info("Processing image")
            final_data, spell_check_data = process_prescription_with_spell_check(file_content)
            image_data = file_content

            logger.info("Image processing complete")

        # Store session data
        session_store[session_id] = {
            "final_data": final_data,
            "spell_check_data": spell_check_data,
            "edited_data": None,
            "whatsapp_message": "",
            "image_data": image_data
        }

        return JSONResponse({"session_id": session_id})
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prescription/{session_id}")
async def get_prescription_data(request: Request, session_id: str):
    """Get processed prescription data and render the prescription page"""
    if session_id not in session_store:
        logger.warning(f"Session not found: {session_id}")
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Session not found"}
        )

    return templates.TemplateResponse(
        "prescription.html",
        {"request": request, "session_id": session_id, "has_image": "image_data" in session_store[session_id]}
    )

@app.get("/api/prescription-image/{session_id}")
async def get_prescription_image(session_id: str):
    """Get the prescription image data"""
    if session_id not in session_store or "image_data" not in session_store[session_id]:
        return JSONResponse(
            status_code=404,
            content={"error": "Image not found"}
        )

    return Response(
        content=session_store[session_id]["image_data"],
        media_type="image/jpeg"
    )

@app.get("/reprocess-image/{session_id}")
async def reprocess_image(session_id: str):
    """Reprocess the prescription image for a given session"""
    if session_id not in session_store or "image_data" not in session_store[session_id]:
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # Get the stored image data
        image_data = session_store[session_id]["image_data"]
        
        # Reprocess the image
        final_data, spell_check_data = process_prescription_with_spell_check(image_data)
        
        # Update session data with new results
        session_store[session_id].update({
            "final_data": final_data,
            "spell_check_data": spell_check_data,
            "edited_data": None,
            "whatsapp_message": ""
        })
        
        return JSONResponse({"message": "Image reprocessed successfully"})
    except Exception as e:
        logger.error(f"Error reprocessing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prescription/{session_id}")
async def get_prescription_json(session_id: str):
    """Get processed prescription data as JSON"""
    if session_id not in session_store:
        logger.warning(f"Session not found: {session_id}")
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )

    session_data = session_store[session_id]
    final_data = session_data["final_data"]

    if not final_data or not hasattr(final_data, "medications"):
        logger.warning(f"No medication data found for session: {session_id}")
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
        logger.warning(f"Session not found for update: {session_id}")
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )

    session_store[session_id]["edited_data"] = medications
    whatsapp_message = format_whatsapp_message(medications)
    session_store[session_id]["whatsapp_message"] = whatsapp_message

    logger.info(f"Medications updated successfully for session: {session_id}")
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
