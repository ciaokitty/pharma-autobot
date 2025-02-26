import webbrowser

# Replace this with your extracted medicines list
medicines = ["Paracetamol 500mg", "Amoxicillin 250mg", "Cough Syrup"]

# Format message
message = f"Hello, I want to order the following medicines:\n\n" + "\n".join(medicines)

# Encode message for URL
message = message.replace(" ", "%20").replace("\n", "%0A")

# Replace with pharmacy WhatsApp number (with country code)
pharmacy_number = "9997703037"

# Generate WhatsApp Web/Mobile link
whatsapp_url = f"https://wa.me/{pharmacy_number}?text={message}"

# Open WhatsApp with the pre-filled message
webbrowser.open(whatsapp_url)
