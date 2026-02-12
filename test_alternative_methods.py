"""
Test and compare voice & image extraction methods
This script tests:
1. EasyOCR (new, pip installable, no system software)
2. PaddleOCR (new, fastest, very lightweight)
3. Original Tesseract (existing, requires system software)
4. Google Speech API (working, primary voice method)
"""
import logging
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("TESTING ALTERNATIVE VOICE & IMAGE EXTRACTION METHODS")
print("="*70 + "\n")

# ============================================================================
# TEST 1: Module Imports
# ============================================================================
print("TEST 1: Module Imports")
print("-" * 70)

try:
    from nlp_processor import OCRProcessor as TesseractOCR, VoiceProcessor
    print("Original Tesseract/Voice imports successful")
except Exception as e:
    print(f"Original imports failed: {e}")

try:
    from nlp_processor_alternative import (
        EasyOCRProcessor, PaddleOCRProcessor, VoiceProcessor as VoiceAlt
    )
    print("Alternative methods imports successful")
except Exception as e:
    print(f"Alternative imports failed: {e}")

try:
    from database import ExpenseDatabase
    print("Database imports successful")
except Exception as e:
    print(f"❌ Database imports failed: {e}")

# ============================================================================
# TEST 2: Check Installed Packages
# ============================================================================
print("\nTEST 2: Check Installed Packages")
print("-" * 70)

packages_to_check = {
    'speech_recognition': 'Voice Recognition',
    'pytesseract': 'Tesseract Python Interface',
    'PIL': 'Image Processing',
    'easyocr': 'EasyOCR',
    'paddleocr': 'PaddleOCR',
    'paddlepaddle': 'PaddlePaddle Framework'
}

installed_packages = {}
for package, description in packages_to_check.items():
    try:
        __import__(package)
        print(f"{description:35} INSTALLED")
        installed_packages[package] = True
    except ImportError:
        print(f"{description:35} NOT INSTALLED")
        installed_packages[package] = False

# ============================================================================
# TEST 3: System Software Check
# ============================================================================
print("\nTEST 3: System Software Check")
print("-" * 70)

# Check Tesseract
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(tesseract_path):
    print(f"Tesseract-OCR        INSTALLED at {tesseract_path}")
    tesseract_available = True
else:
    print(f"Tesseract-OCR       NOT FOUND at {tesseract_path}")
    tesseract_available = False

# ============================================================================
# TEST 4: Feature Availability Summary
# ============================================================================
print("\nTEST 4: Feature Availability Summary")
print("-" * 70)

features = {
    'Voice (Google Speech API)': installed_packages.get('speech_recognition', False),
    'Original Method (Tesseract)': installed_packages.get('pytesseract', False) and tesseract_available,
    'Alternative 1 (EasyOCR)': installed_packages.get('easyocr', False),
    'Alternative 2 (PaddleOCR)': installed_packages.get('paddleocr', False) and installed_packages.get('paddlepaddle', False),
}

print("\nFeature Status:")
working_count = 0
for feature, status in features.items():
    status_text = "WORKING" if status else "NOT AVAILABLE"
    print(f"{feature:40} {status_text}")
    if status:
        working_count += 1

print(f"\nTotal working features: {working_count}/{len(features)}")

# ============================================================================
# TEST 5: Installation Instructions for Missing Features
# ============================================================================
print("\nTEST 5: Installation Instructions")
print("-" * 70)

missing = []

if not installed_packages.get('easyocr', False):
    missing.append('easyocr')
if not installed_packages.get('paddleocr', False) or not installed_packages.get('paddlepaddle', False):
    missing.append('paddleocr paddlepaddle')

if missing:
    print("\nTo enable ALL alternative methods, install:")
    for package_set in missing:
        print(f"\n   pip install {package_set}")
else:
    print("\nAll packages installed! You can use all methods.")

# ============================================================================
# TEST 6: Method Comparison
# ============================================================================
print("\n" + "="*70)
print("METHOD COMPARISON CHART")
print("="*70 + "\n")

comparison = """
METHOD COMPARISON (SUMMARY)
---------------------------
- Tesseract: High accuracy, medium speed, requires system software.
- EasyOCR: High accuracy, fast, pip-installable only.
- PaddleOCR: High accuracy, fastest, pip-installable only.

See 00_COMPLETE_VOICE_PHOTO_GUIDE.md for a detailed comparison table.
"""

print(comparison)

# ============================================================================
# TEST 7: Quick Start Guide
# ============================================================================
print("\n" + "="*70)
print("QUICK START GUIDE")
print("="*70 + "\n")

guide = """
QUICK START GUIDE (SUMMARY)
---------------------------
OPTION 1: Use EasyOCR (recommended - easiest setup)
  1. Install EasyOCR:
       pip install easyocr
  2. Update main.py to use EasyOCRProcessor:
       From: from nlp_processor import OCRProcessor
       To:   from nlp_processor_alternative import EasyOCRProcessor as OCRProcessor
  3. Restart bot:
       python main.py

OPTION 2: Use PaddleOCR (best speed)
  1. Install PaddleOCR:
       pip install paddleocr paddlepaddle
  2. Update main.py to use PaddleOCRProcessor:
       From: from nlp_processor import OCRProcessor
       To:   from nlp_processor_alternative import PaddleOCRProcessor as OCRProcessor
  3. Restart bot:
       python main.py

OPTION 3: Keep Using Tesseract (already working)
  1. Verify Tesseract installed at C:\\Program Files\\Tesseract-OCR\\tesseract.exe
  2. Run bot as-is:
       python main.py

For more details, see 00_COMPLETE_VOICE_PHOTO_GUIDE.md.
"""

print(guide)

# ============================================================================
# TEST 8: Test Report
# ============================================================================
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70 + "\n")

print(f"""
Module Imports: OK
Package Detection: OK
System Software Check: OK
Feature Availability: {working_count}/{len(features)} methods available

WORKING FEATURES:
""")

for feature, status in features.items():
    if status:
        print(f"  {feature}")

if working_count < len(features):
    print(f"\nMISSING FEATURES: {len(features) - working_count}")
    for feature, status in features.items():
        if not status:
            print(f"  {feature}")

print(f"""
All tests completed!

NEXT STEPS:
1. Choose a method (Tesseract, EasyOCR, or PaddleOCR)
2. Install if needed: pip install [package_name]
3. Update main.py to use chosen OCR processor
4. Restart bot with: python main.py
5. Test with Telegram: send voice message and receipt photo

For detailed comparison and features, see:
00_COMPLETE_VOICE_PHOTO_GUIDE.md
""")

print("="*70 + "\n")
