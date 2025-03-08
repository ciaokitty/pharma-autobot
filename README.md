# Pharma-Autobot

Pharma-Autobot is a web application designed to help pharmacists and patients process prescriptions more efficiently. The application uses Google's Gemini AI to extract medication information from prescription images, verify drug names, and provides a user-friendly interface for managing medication orders.

### **Design Approach and Philosophy**  

Training a custom model for Handwritten Text Recognition (HTR) didn't seem practical after testing some of the highest-ranked OCR models from [Papers with Code](https://paperswithcode.com/task/handwritten-text-recognition/). Even with well-written prescriptions, they struggled to produce meaningful results.  

Taking inspiration from [The Bitter Lesson by Rich Sutton](https://www.cs.utexas.edu/~eunsol/courses/data/bitter_lesson.pdf), it made more sense to leverage existing large-scale models rather than build something from scratch. Google Gemini's vision models performed remarkably well at extracting text from handwritten notes, making them the best fit for this project. Instead of reinventing the wheel, the focus shifted to integrating and fine-tuning something that gets the job done efficiently.

## Features

- **Prescription OCR**: Extract medication information from uploaded prescription images
- **Custom System Prompt**: Detailed custom system prompt that handles messy handwriting (e.g. striked out words), abbreviations, and dosage instructions to reduce errors
- **Drug Name Verification**: Automatically spell-check and verify medication names using Google Search Grounding
- **Display common brand names**: Shows commonly available brand-name medications
- **Display Dosage and Intake Instructions**: Deciphers common prescription notations and clearly presents how much, how often, and when to take each medication.
- **Calculate order quantity required**: Determines the required order quantity based on dosage and frequency
- **Download Analysed Prrescription**: Download the extracted and analysed prescription in CSV format
- **Medication Management**: Edit and manage extracted medication information
- **WhatsApp Integration**: Send medication orders directly to pharmacies via WhatsApp
- **Testing Mode**: Use dummy data for testing the application without uploading images again and again

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
   I had to use multiple API keys to avoid rate limits.

### Running the Application

You can run the application in two different ways:

#### 1. Streamlit Version (Original)
Start the Streamlit application locally on your browser:
```bash
streamlit run src/app.py
```

#### 2. FastHTML Version (Alternative)
Start the FastAPI application with Uvicorn:
```bash
uvicorn src.app_alt:app --reload
```

The FastHTML version provides a more traditional web application experience with:
- Faster page loads
- Better performance for large datasets
- More customizable UI
- Real-time updates without full page reloads

Both versions provide the same core functionality, so you can choose the one that best suits your needs.

## Project Structure

The project structure includes:
- `src/app.py`: Main Streamlit application
- `src/app_alt.py`: Alternative FastHTML application
- `src/ocr.py`: Prescription OCR and text extraction functionality
- `src/schema.py`: Data models for medication information
- `src/prompts.py`: Prompts for the Gemini AI model
- `src/exceptions.py`: Custom exception handling
- `templates/`: HTML templates for the FastHTML version
- `public/`: Static files and assets

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
