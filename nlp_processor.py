"""
NLP and entity extraction for expense parsing
"""
import re
from config import EXPENSE_PATTERNS, EXPENSE_CATEGORIES

class ExpenseParser:
    def __init__(self):
        self.amount_pattern = r'(\d+(?:[.,]\d{2})?)'
        self.currency_symbols = ['₹', '$', '€', '£', 'rs', 'rupees', 'dollars']
    
    def parse_expense(self, text):
        """
        Parse expense from natural language text
        Returns: (amount, category, description)
        """
        text_lower = text.lower()
        
        # Extract amount
        amount = self._extract_amount(text)
        if not amount:
            return None, None, None
        
        # Extract category
        category = self._extract_category(text_lower)
        
        # Description
        description = text
        
        return amount, category, description
    
    def _extract_amount(self, text):
        """Extract amount from text"""
        # Remove currency symbols
        cleaned = text
        for symbol in self.currency_symbols:
            cleaned = cleaned.lower().replace(symbol.lower(), '')
        
        # Find numbers
        matches = re.findall(r'(\d+(?:[.,]\d{2})?)', cleaned)
        
        if not matches:
            return None
        
        # Get the first significant number (usually the amount)
        for match in matches:
            amount_str = match.replace(',', '.')
            try:
                amount = float(amount_str)
                # Filter out very small or unreasonably large amounts
                if 0 < amount < 1000000:
                    return amount
            except ValueError:
                continue
        
        return None
    
    def _extract_category(self, text_lower):
        """Extract category from text using keyword matching"""
        
        for category, keywords in EXPENSE_PATTERNS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category.capitalize()
        
        return "Other"
    
    def is_valid_expense(self, amount, category):
        """Validate if parsed data is valid"""
        if not amount or amount <= 0:
            return False
        if not category or (category not in EXPENSE_CATEGORIES and category != "Other"):
            return False
        return True

class OCRProcessor:
    """Handle OCR processing for receipts and screenshots"""
    
    def __init__(self):
        self.parser = ExpenseParser()
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from image using OCR
        Requires pytesseract and Tesseract installation
        """
        try:
            import pytesseract
            from PIL import Image
            import os
            
            # Configure pytesseract to find Tesseract executable
            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.pytesseract_cmd = tesseract_path
            
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return text
        except ImportError:
            return "OCR not available. Please install pytesseract and Tesseract."
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def parse_receipt(self, image_path):
        """Parse receipt image and extract expenses"""
        text = self.extract_text_from_image(image_path)
        
        if "Error" in text or "not available" in text:
            return None
        
        # Parse the extracted text
        amount, category, description = self.parser.parse_expense(text)
        
        return {
            "text": text,
            "amount": amount,
            "category": category,
            "description": description
        }

class VoiceProcessor:
    """Process voice messages and convert to text"""
    
    def __init__(self):
        self.parser = ExpenseParser()
    
    def transcribe_voice(self, voice_path):
        """
        Convert voice to text using speech recognition
        Supports both Google Speech API and local recognition
        """
        try:
            # Try using speech_recognition library
            import speech_recognition as sr
            
            # Convert OGG to WAV if needed
            recognizer = sr.Recognizer()
            
            # Load audio
            with sr.AudioFile(voice_path) as source:
                audio = recognizer.record(source)
            
            # Try Google Speech API (free, online)
            try:
                text = recognizer.recognize_google(audio)
                return text
            except:
                # Fallback to other APIs if Google fails
                try:
                    text = recognizer.recognize_sphinx(audio)
                    return text
                except:
                    return "error"
                
        except ImportError:
            # speech_recognition not installed, use basic text extraction
            return self._extract_from_audio_metadata(voice_path)
        except Exception as e:
            print(f"Voice recognition error: {str(e)}")
            return "error"
    
    def _extract_from_audio_metadata(self, voice_path):
        """Fallback: extract text from audio metadata if available"""
        try:
            import wave
            with wave.open(voice_path, 'rb') as wav_file:
                # Get metadata (limited info from audio file)
                frames = wav_file.readframes(wav_file.getnframes())
                # This is a basic approach - returns error if no metadata
                return "error"
        except:
            return "error"