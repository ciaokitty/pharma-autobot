class GeminiError(Exception):
    """
    Custom exception for errors related to the Gemini API.
    
    Attributes:
        message: The error message
    """
    def __init__(self, message="An error occurred in the Gemini application"):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"GeminiError: {self.message}"
    