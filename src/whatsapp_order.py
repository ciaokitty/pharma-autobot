from urllib.parse import quote

def format_whatsapp_message(medications):
    """
    Format a message for WhatsApp with medication details.
    
    Args:
        medications: List of medication dictionaries
        
    Returns:
        str: The formatted message
    """
    message = "Hello, I want to order the following medicines:\n\n"
    for med in medications:
        med_line = f"• {med['Medication Name']} {med['Dosage']} - Qty: {med['Quantity']}"
        message += med_line + "\n"
    return message

def get_whatsapp_url(message, phone_number):
    """
    Generate a WhatsApp URL for the given message and phone number.
    
    Args:
        message: The message to send
        phone_number: The recipient's phone number
        
    Returns:
        str: WhatsApp URL with encoded message
    """
    encoded_message = quote(message)
    return f"https://wa.me/{phone_number}?text={encoded_message}"

def send_order_via_whatsapp(medications, pharmacy_number, custom_message=None):
    """
    Generate WhatsApp URL for medication order.
    
    Args:
        medications: List of medication dictionaries
        pharmacy_number: WhatsApp number of the pharmacy
        custom_message: Optional custom message to use instead of the default format
        
    Returns:
        str: The WhatsApp URL to open
    """
    message = custom_message if custom_message else format_whatsapp_message(medications)
    whatsapp_url = get_whatsapp_url(message, pharmacy_number)
    return whatsapp_url
