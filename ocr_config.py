"""
OCR Method Configuration
Switch between different OCR methods easily
"""

# Available OCR methods:
# - "tesseract": Original Tesseract-OCR (system software required)
# - "easyocr": EasyOCR (pip installable, no system dependencies)
# - "paddleocr": PaddleOCR (fastest, very lightweight)

CURRENT_OCR_METHOD = "easyocr"  # ← Change this to switch methods

# Method details
OCR_METHODS = {
    "tesseract": {
        "class": "OCRProcessor",
        "module": "nlp_processor",
        "description": "Original Tesseract-OCR",
        "requires_system_software": True,
        "pip_installable": False,
        "speed": "Medium",
        "accuracy": "Excellent",
    },
    "easyocr": {
        "class": "EasyOCRProcessor",
        "module": "nlp_processor_alternative",
        "description": "EasyOCR (RECOMMENDED)",
        "requires_system_software": False,
        "pip_installable": True,
        "speed": "Fast",
        "accuracy": "Excellent",
    },
    "paddleocr": {
        "class": "PaddleOCRProcessor",
        "module": "nlp_processor_alternative",
        "description": "PaddleOCR (FASTEST)",
        "requires_system_software": False,
        "pip_installable": True,
        "speed": "Very Fast",
        "accuracy": "Excellent",
    },
}


def get_ocr_processor():
    """
    Dynamically load the configured OCR processor
    Usage: processor = get_ocr_processor()
    """
    if CURRENT_OCR_METHOD not in OCR_METHODS:
        raise ValueError(f"Unknown OCR method: {CURRENT_OCR_METHOD}")
    
    method_config = OCR_METHODS[CURRENT_OCR_METHOD]
    
    try:
        # Import the module and get the class
        module = __import__(method_config["module"], fromlist=[method_config["class"]])
        processor_class = getattr(module, method_config["class"])
        
        # Instantiate and return
        processor = processor_class()
        return processor
    
    except ImportError as e:
        print(f"❌ Failed to import {method_config['class']} from {method_config['module']}")
        print(f"   Error: {e}")
        print(f"   Install with: pip install {CURRENT_OCR_METHOD}")
        return None
    
    except Exception as e:
        print(f"❌ Failed to initialize OCR processor: {e}")
        return None


# Helper function to check method availability
def check_method_available(method_name):
    """Check if a specific OCR method is available"""
    if method_name not in OCR_METHODS:
        return False
    
    method_config = OCR_METHODS[method_name]
    
    try:
        # Try to import
        module = __import__(method_config["module"], fromlist=[method_config["class"]])
        getattr(module, method_config["class"])
        return True
    except:
        return False


# Get list of available methods
def get_available_methods():
    """Return list of available OCR methods"""
    available = []
    for method_name in OCR_METHODS.keys():
        if check_method_available(method_name):
            available.append({
                "name": method_name,
                "description": OCR_METHODS[method_name]["description"],
                "speed": OCR_METHODS[method_name]["speed"],
                "accuracy": OCR_METHODS[method_name]["accuracy"],
            })
    return available


if __name__ == "__main__":
    # Test the configuration
    print("="*70)
    print("OCR METHOD CONFIGURATION TEST")
    print("="*70 + "\n")
    
    print(f"Current OCR Method: {CURRENT_OCR_METHOD}")
    print(f"Description: {OCR_METHODS[CURRENT_OCR_METHOD]['description']}\n")
    
    available = get_available_methods()
    print(f"Available Methods: {len(available)}\n")
    
    for method in available:
        status = "✓" if method['name'] == CURRENT_OCR_METHOD else " "
        print(f"  {status} {method['name']:12} - {method['description']:25} (Speed: {method['speed']})")
    
    print("\n" + "="*70)
    print(f"Attempting to load: {CURRENT_OCR_METHOD}...")
    print("="*70 + "\n")
    
    processor = get_ocr_processor()
    if processor:
        print(f"✓ Successfully loaded {CURRENT_OCR_METHOD} OCR processor!")
    else:
        print(f"❌ Failed to load {CURRENT_OCR_METHOD} OCR processor")
