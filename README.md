# Pharma-Autobot

Pharma-Autobot is a web application designed to help pharmacists and patients process prescriptions more efficiently. The application uses Google's Gemini AI to extract medication information from prescription images, verify drug names, and provides a user-friendly interface for managing medication orders.

### **Design Approach and Philosophy**  

Training a custom model for Handwritten Text Recognition (HTR) didn’t seem practical after testing some of the highest-ranked OCR models from [Papers with Code](https://paperswithcode.com/task/handwritten-text-recognition/). Even with well-written prescriptions, they struggled to produce meaningful results.  

Taking inspiration from [The Bitter Lesson by Rich Sutton](https://www.cs.utexas.edu/~eunsol/courses/data/bitter_lesson.pdf), it made more sense to leverage existing large-scale models rather than build something from scratch. Google Gemini’s vision models performed remarkably well at extracting text from handwritten notes, making them the best fit for this project. Instead of reinventing the wheel, the focus shifted to integrating and fine-tuning something that gets the job done efficiently.

## Features

- **Prescription OCR**: Extract medication information from uploaded prescription images
- **Drug Name Verification**: Automatically spell-check and verify medication names
- **Display common brand names**: Shows commonly available brand-name medications
- **Calculate dosage and quantity required**: Determines the required quantity based on dosage and frequency
- **Download Analysed Prrescription**: Download the extracted and analysed prescription in CSV format.
- **Medication Management**: Edit and manage extracted medication information
- **WhatsApp Integration**: Send medication orders directly to pharmacies via WhatsApp
- **Testing Mode**: Use dummy data for testing the application without uploading images again and again.

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
   Or alternatively you can directly run:
   ```bash
   uv sync
   source .venv/bin/activate
   ```

3. If using standard pip, install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the `/src` directory with your Google Gemini API key(s):
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

![Spell Check Results](screenshots/Screenshot%202025-02-26%20034121.png)

![WhatsApp Integration](screenshots/Screenshot%202025-02-26%20120034.png)


## Future Plan
 
### Drug Information Display  
- Fetches data from Tata 1mg and other sources.  
- Displays side effects and health warnings.  

### E-Commerce Integration  
- Supports one-click multi-platform "Add to Cart" functionality.  
- Uses APIs or web automation for orders.  
- Handles authentication and tracks cart status.

![Future plans](screenshots/future-pharma-bot.png)
