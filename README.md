# Pharma-Autobot

Pharma-Autobot is a web application designed to help pharmacists and patients process prescriptions more efficiently. The application uses Google's Gemini AI to extract medication information from prescription images, verify drug names, and provides a user-friendly interface for managing medication orders.

## Features

- **Prescription OCR**: Extract medication information from uploaded prescription images
- **Drug Name Verification**: Automatically spell-check and verify medication names
- **Medication Management**: Edit and manage extracted medication information
- **WhatsApp Integration**: Send medication orders directly to pharmacies via WhatsApp
- **Testing Mode**: Use dummy data for testing the application without uploading images

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Google Gemini API key(s)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ciaokitty/pharma-autobot.git
   cd pharma-autobot
   ```

2. Create and activate a virtual environment:

   **Option 1: Using Python venv (standard)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

   **Option 2: Using uv (faster alternative)**
   ```bash
   # Install uv if you don't have it already
   pip install uv
   
   # Create and activate virtual environment with uv
   uv venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   
   # Install dependencies with uv (much faster than pip)
   uv pip install -r requirements.txt
   ```

3. If using standard pip, install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your Google Gemini API key(s):
   ```
   API_KEY=your_primary_api_key
   API_KEY1=your_backup_api_key1
   API_KEY2=your_backup_api_key2
   API_KEY3=your_backup_api_key3
   API_KEY4=your_backup_api_key4
   ```
   Note: You can use just one API key or multiple keys for rotation to avoid exhausting your requests.

### Running the Application

Start the Streamlit application:
```bash
streamlit run src/app.py
```

The application will be available at http://localhost:8501 in your web browser.

## Usage

1. Upload a prescription image or use the "Use dummy data for testing" option
2. The application will extract medication information and verify drug names
3. Review and edit the extracted information as needed
4. Enter a pharmacy's WhatsApp number to send the order
5. Customize the message if needed and click "Send Order via WhatsApp"

## Development

The project structure includes:
- `src/app.py`: Main Streamlit application
- `src/ocr.py`: Prescription OCR and text extraction functionality
- `src/schema.py`: Data models for medication information
- `src/prompts.py`: Prompts for the Gemini AI model
- `src/exceptions.py`: Custom exception handling

## Screenshots to show working of this application:

![Application Interface](screenshots/Screenshot%202025-02-26%20033943.png)

![Prescription Processing](screenshots/Screenshot%202025-02-26%20033958.png)

![Medication Extraction](screenshots/Screenshot%202025-02-26%20034018.png)

![Drug Verification](screenshots/Screenshot%202025-02-26%20034036.png)

![Medication Management](screenshots/Screenshot%202025-02-26%20034052.png)

![Order Customization](screenshots/Screenshot%202025-02-26%20034110.png)

![WhatsApp Integration](screenshots/Screenshot%202025-02-26%20034121.png)


