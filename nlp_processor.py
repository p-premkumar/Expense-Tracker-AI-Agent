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
        Parse expense from receipt or text
        Priority: Explicit fields (amount:, category:) → Money symbols → Keywords
        Returns: (amount, category, description)
        """
        text_str = text or ""
        
        # STEP 1: Extract explicit "category:" field from receipt
        category = self._extract_explicit_category(text_str)
        
        # STEP 2: Extract amount using smart logic
        amount = self._extract_amount(text_str)
        if not amount:
            return None, None, None

        # STEP 3: Build description - clean full text
        description = text_str
        # Remove amount-related patterns to clean description
        amt_pattern = r"[\₹\$\€\£]?\s*\d+(?:[.,]\d{1,2})?\s*(?:rs|rupees|dollars)?"
        description = re.sub(amt_pattern, "", description, flags=re.IGNORECASE, count=1)
        # Remove explicit field labels (amount: 100, category: food, etc)
        description = re.sub(r'(?:amount|category|total|cost|price)\s*:?\s*[^\n]*', '', description, flags=re.IGNORECASE)
        # Collapse whitespace and strip
        description = re.sub(r"\s{2,}", " ", description).strip()
        description = description.strip(" -:;,.\n\t")

        # Fallback: if description is empty or too short, use original text
        if not description or len(description) < 3:
            description = text_str.strip()

        # If still no category from explicit field, extract from description/keywords
        if not category or category == "Other":
            category = self._extract_category(description.lower())

        return amount, category, description
    
    def _extract_explicit_category(self, text):
        """Extract category from explicit 'category:' field in receipt"""
        # Pattern: "category: biryani" or "category : biryani" or "category:biryani"
        pattern = r'category\s*:?\s*([^\n:,]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            category_text = match.group(1).lower().strip()
            
            # First, try direct match against category names
            for cat_name in EXPENSE_CATEGORIES:
                if category_text == cat_name.lower():
                    return cat_name
            
            # Second, try keyword matching in EXPENSE_PATTERNS
            for category, keywords in EXPENSE_PATTERNS.items():
                for keyword in keywords:
                    if keyword.lower() == category_text or keyword.lower() in category_text:
                        # Map pattern key to category name
                        for cat_name in EXPENSE_CATEGORIES:
                            if cat_name.lower() == category.lower():
                                return cat_name
        
        return None

    def parse_multiple_expenses(self, text):
        """
        Parse multiple expenses from receipt with multiple items
        Extracts items separated by newlines, each with category and amount
        Returns: list of (amount, category, description) tuples
        
        Handles formats:
        1. Explicit fields (Item: X, Amount: Y, Category: Z) with --- separators
        2. Line-by-line: "Biryani - 250" or "Biryani Rs 250"
        3. Double newlines: Blank lines between items
        """
        expenses = []
        
        # Try to detect item blocks separated by "---", "===", or blank lines
        item_blocks = []
        
        # Split by common separators first (strongest signal)
        if "---" in text or "===" in text:
            blocks = re.split(r'---+|===+', text)
            item_blocks = [block.strip() for block in blocks if block.strip()]
        else:
            # Check if this looks like line-by-line format (each line has amount)
            lines = text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            # Count how many lines have numbers (potential items)
            lines_with_numbers = sum(1 for line in lines if re.search(r'\d+', line))
            
            # If multiple lines have numbers, treat each as a separate item
            if lines_with_numbers >= 2 and len(lines) >= 2:
                item_blocks = lines
            else:
                # Single item or blank lines as separators
                current_block = []
                for line in lines:
                    if not line:
                        if current_block:
                            item_blocks.append('\n'.join(current_block))
                            current_block = []
                    else:
                        current_block.append(line)
                
                if current_block:
                    item_blocks.append('\n'.join(current_block))
        
        # Process each block
        for block in item_blocks:
            if not block:
                continue
            
            # Try to parse the block as a single expense
            amount, category, description = self.parse_expense(block)
            
            if amount:  # Only add if we found an amount
                expenses.append((amount, category, description))
        
        return expenses
    
    def _extract_amount(self, text):
        """Extract amount from text - prioritizes 'amount:' field, then money symbols"""
        text_lower = text.lower()
        
        # HIGHEST PRIORITY: Look for explicit "amount:" field in receipt
        # Pattern: "amount : 100" or "amount: 100" or "amount 100"
        amount_pattern = r'amount\s*:?\s*([₹\$\€\£])?\s*(\d+(?:[.,]\d{2})?)'
        match = re.search(amount_pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(2) if match.group(2) else match.group(1)
            amount = self._parse_amount_string(amount_str)
            if amount:
                return amount
        
        # PRIORITY 2: Look for "total" or "grand total" fields (common in receipts)
        total_keywords = ['total', 'grand total', 'final amount', 'amount due', 'total amount', 'total cost']
        for keyword in total_keywords:
            pattern = rf'{keyword}\s*:?\s*([₹\$\€\£])?\s*(\d+(?:[.,]\d{{2}}))'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(2) if match.group(2) else match.group(1)
                amount = self._parse_amount_string(amount_str)
                if amount:
                    return amount
        
        # PRIORITY 3: Look for money symbols (₹, $, €, £, Rs, rupees, dollars)
        has_currency = bool(re.search(r'[₹\$\€\£]|Rs\.|Rs |rupee|rupees|dollar', text, re.IGNORECASE))
        
        if has_currency:
            # RECEIPT MODE: Extract from lines with currency
            money_lines = []
            lines = text.split('\n')
            
            for line in lines:
                if re.search(r'[₹\$\€\£]|Rs\.|Rs |rupee|rupees|dollar', line, re.IGNORECASE):
                    money_lines.append(line)
            
            amounts_found = []
            for line in money_lines:
                # Skip item/product lines (these are not totals)
                if re.search(r'item|product|qty|quantity|x\d|each|piece', line, re.IGNORECASE):
                    continue
                
                # Pattern 1: Currency symbol followed by number
                match = re.search(r'[₹\$\€\£]\s*(\d+(?:[.,]\d{2})?)', line)
                if match:
                    amount = self._parse_amount_string(match.group(1))
                    if amount:
                        amounts_found.append(amount)
                
                # Pattern 2: Rs/rupees/dollars followed by number
                match = re.search(r'(?:Rs\.|Rs|rupees?|dollars?)\s*:?\s*(\d+(?:[.,]\d{2})?)', line, re.IGNORECASE)
                if match:
                    amount = self._parse_amount_string(match.group(1))
                    if amount:
                        amounts_found.append(amount)
            
            if amounts_found:
                # Return the largest amount (usually the total)
                return max(amounts_found)
        
        # PRIORITY 4: TEXT MODE (simple text input like "Spent 500 for biryani")
        # Look for numbers with 2 decimal places first
        decimal_pattern = r'(\d+[.,]\d{2})'
        matches = re.findall(decimal_pattern, text)
        if matches:
            for match in sorted(matches, key=lambda x: float(x.replace(',', '.')), reverse=True):
                amount = self._parse_amount_string(match)
                if amount:
                    return amount
        
        # PRIORITY 5: Look for any number (but skip obvious pincodes at start)
        all_matches = re.findall(r'(\d+(?:[.,]\d{2})?)', text)
        for idx, match in enumerate(all_matches):
            amount = self._parse_amount_string(match)
            if amount:
                # Skip likely pincodes: 5-6 digit integers without decimals at start
                is_pincode = (len(match) in [5, 6] and '.' not in match and ',' not in match and idx == 0)
                if not is_pincode:
                    return amount
        
        return None
    
    def _parse_amount_string(self, amount_str):
        """Helper to parse amount string to float"""
        try:
            amount_str = amount_str.replace(',', '.')
            amount = float(amount_str)
            # Valid range for expenses
            if 0 < amount < 1000000:
                return amount
        except (ValueError, TypeError):
            pass
        return None
    
    def _extract_category(self, text_lower):
        """Extract category from text using keyword matching"""
        
        for category, keywords in EXPENSE_PATTERNS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Match category name from EXPENSE_CATEGORIES (case-insensitive)
                    for cat_name in EXPENSE_CATEGORIES:
                        if cat_name.lower() == category.lower():
                            return cat_name
        
        return "Other"
    
    def is_valid_expense(self, amount, category):
        """Validate if parsed data is valid"""
        if not amount or amount <= 0:
            return False
        if not category or (category not in EXPENSE_CATEGORIES and category != "Other"):
            return False
        return True
    
    def extract_simple_receipt(self, text):
        """
        Simple receipt extraction - only category and final amount
        Returns: dict with 'category' and 'final_amount' only
        """
        text = (text or "").strip()
        
        if not text:
            return {
                'category': 'Other',
                'final_amount': None,
                'error': 'Empty receipt text'
            }
        
        # Extract final amount (total)
        final_amount = self._extract_final_amount_simple(text)
        
        # Extract category from text keywords
        category = self._extract_category(text.lower())
        
        return {
            'category': category,
            'final_amount': final_amount
        }
    
    def _extract_final_amount_simple(self, text):
        """Extract final/total amount from receipt text"""
        # Look for common total patterns
        patterns = [
            r'(?:grand\s+)?total\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:[.,]\d{1,2})?)',
            r'(?:final|payable|amount|due)\s*:?\s*(?:Rs\.?|₹)?\s*(\d+(?:[.,]\d{1,2})?)',
            r'(?:Rs\.?|₹)\s*(\d+(?:[.,]\d{1,2})?)\s*$',  # Amount at end
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '.')
                    amount = float(amount_str)
                    if 0 < amount < 1000000:
                        return amount
                except (ValueError, IndexError):
                    pass
        
        # Fallback: get the largest number in text
        numbers = re.findall(r'(\d+(?:[.,]\d{1,2})?)', text)
        if numbers:
            try:
                amounts = [float(n.replace(',', '.')) for n in numbers if 0 < float(n.replace(',', '.')) < 1000000]
                if amounts:
                    return max(amounts)  # Return largest amount as final total
            except (ValueError, TypeError):
                pass
        
        return None
    
    def analyze_receipt(self, receipt_text):
        """
        Advanced receipt analysis for structured data extraction.
        Extracts: restaurant details, items, quantities, prices, taxes, totals.
        
        Returns: dict with fields for restaurant, items, subtotal, tax, service_charge, discount, final_amount, currency, payment_method, confidence
        """
        text = (receipt_text or "").strip()
        
        if not text:
            return {
                'restaurant': {'name': None, 'address': None, 'phone': None},
                'items': [],
                'subtotal': None,
                'tax': {'gst': None, 'other': None},
                'service_charge': None,
                'discount': None,
                'final_amount': None,
                'currency': 'INR',
                'payment_method': None,
                'confidence': 'low',
                'error': 'Empty receipt text'
            }
        
        result = {
            'restaurant': {'name': None, 'address': None, 'phone': None},
            'items': [],
            'subtotal': None,
            'tax': {'gst': None, 'other': None},
            'service_charge': None,
            'discount': None,
            'final_amount': None,
            'currency': 'INR',
            'payment_method': None,
            'confidence': 'medium'
        }
        
        # Extract restaurant details
        lines = text.split('\n')[:5]
        for line in lines:
            clean_line = line.strip()
            if clean_line and len(clean_line) > 3 and len(clean_line) < 50:
                if not any(char.isdigit() for char in clean_line[:5]):
                    result['restaurant']['name'] = clean_line
                    break
        
        # Extract phone
        phone_match = re.search(r'\b\d{10}\b', text)
        if phone_match:
            result['restaurant']['phone'] = phone_match.group()
        
        # Extract items - look for lines with prices; support "Qty x Unit" or single price
        text_lines = [line.strip() for line in text.split('\n') if line.strip()]
        skip_names = {'subtotal', 'total', 'tax', 'gst', 'service', 'discount', 'grand total', 'amount', 'payable', 'phone', 'gstin', 'address'}
        item_pattern = r'^([a-zA-Z\s]+?)\s+(?:[\-\.]|x\s*)?\s*(₹|Rs|rs|\$|€|£)?\s*(\d+(?:[.,]\d{1,2})?)\s*(?:\(.*?\))?$'
        qty_pattern = r'^([a-zA-Z\s]+?)\s+(\d+)\s+(?:x\s*)?\s*(\d+(?:[.,]\d{1,2})?)\s+(?:[\-\.]|x\s*)?\s*(\d+(?:[.,]\d{1,2})?)\s*$'
        for line in text_lines:
            line_lower = line.lower()
            if any(s in line_lower for s in ('phone', 'gstin', 'address', 'tin')) and not re.search(r'\d+\s*(?:x|)\s*\d+', line):
                continue
            match_qty = re.match(qty_pattern, line, re.IGNORECASE)
            if match_qty:
                item_name = match_qty.group(1).strip()
                if item_name.lower() in skip_names or len(item_name) < 2:
                    continue
                try:
                    qty = int(match_qty.group(2))
                    unit = float(match_qty.group(3).replace(',', '.'))
                    total_price = float(match_qty.group(4).replace(',', '.'))
                    if total_price <= 0 or total_price > 999999:
                        continue
                    category = self._extract_category(item_name.lower())
                    result['items'].append({
                        'name': item_name,
                        'quantity': qty,
                        'unit_price': unit,
                        'total_price': total_price,
                        'category': category
                    })
                except (ValueError, IndexError):
                    pass
                continue
            match = re.match(item_pattern, line, re.IGNORECASE)
            if match:
                item_name = match.group(1).strip()
                if item_name.lower() in skip_names or len(item_name) < 2:
                    continue
                price_str = match.group(3)
                if price_str:
                    try:
                        price = float(price_str.replace(',', '.'))
                        if price <= 0 or price > 999999:
                            continue
                        category = self._extract_category(item_name.lower())
                        result['items'].append({
                            'name': item_name,
                            'quantity': None,
                            'unit_price': None,
                            'total_price': price,
                            'category': category
                        })
                    except ValueError:
                        pass
        
        # Extract subtotal
        subtotal_patterns = [
            r'subtotal\s*:?\s*(₹|Rs|rs|\$|€|£)?\s*(\d+(?:[.,]\d{1,2})?)',
            r'sub[\s-]?total\s*:?\s*(₹|Rs|rs|\$|€|£)?\s*(\d+(?:[.,]\d{1,2})?)',
        ]
        for pattern in subtotal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result['subtotal'] = float(match.group(2).replace(',', '.'))
                    break
                except (ValueError, IndexError):
                    pass
        
        # Extract taxes
        gst_patterns = [
            r'(?:sgst|cgst|gst)\s*(?:\d+%?)?\s*:?\s*(₹|Rs|rs|\$|€|£)?\s*(\d+(?:[.,]\d{1,2})?)',
            r'gst\s*:?\s*(₹|Rs|rs|\$|€|£)?\s*(\d+(?:[.,]\d{1,2})?)',
        ]
        for pattern in gst_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result['tax']['gst'] = float(match.group(2).replace(',', '.'))
                    break
                except (ValueError, IndexError):
                    pass
        
        # Extract service charge
        service_patterns = [
            r'service\s*charge\s*:?\s*(₹|Rs|rs|\$|€|£)?\s*(\d+(?:[.,]\d{1,2})?)',
            r'service\s*:?\s*(₹|Rs|rs|\$|€|£)?\s*(\d+(?:[.,]\d{1,2})?)',
        ]
        for pattern in service_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result['service_charge'] = float(match.group(2).replace(',', '.'))
                    break
                except (ValueError, IndexError):
                    pass
        
        # Extract discount
        discount_patterns = [
            r'discount\s*:?\s*[-]?\s*(₹|Rs|rs|\$|€|£)?\s*(\d+(?:[.,]\d{1,2})?)',
            r'offer\s*:?\s*[-]?\s*(₹|Rs|rs|\$|€|£)?\s*(\d+(?:[.,]\d{1,2})?)',
        ]
        for pattern in discount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result['discount'] = float(match.group(2).replace(',', '.'))
                    break
                except (ValueError, IndexError):
                    pass
        
        # Extract final amount
        total_patterns = [
            r'(?:total|final|payable)\s*:?\s*(₹|Rs|rs|\$|€|£)?\s*(\d+(?:[.,]\d{1,2})?)',
            r'grand\s+total\s*:?\s*(₹|Rs|rs|\$|€|£)?\s*(\d+(?:[.,]\d{1,2})?)',
        ]
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result['final_amount'] = float(match.group(2).replace(',', '.'))
                    break
                except (ValueError, IndexError):
                    pass
        
        # Detect payment method
        payment_patterns = {
            'Cash': r'\bcash\b',
            'Card': r'\bcard\b',
            'UPI': r'\bupi\b',
        }
        for method, pattern in payment_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                result['payment_method'] = method
                break
        
        # Detect currency
        if '₹' in text or 'Rs' in text.upper() or 'INR' in text.upper():
            result['currency'] = 'INR'
        elif '$' in text or 'USD' in text.upper():
            result['currency'] = 'USD'
        elif '€' in text:
            result['currency'] = 'EUR'
        
        # Confidence level
        if result['items'] and result['final_amount']:
            result['confidence'] = 'high'
        elif result['items'] or result['final_amount']:
            result['confidence'] = 'medium'
        else:
            result['confidence'] = 'low'
        
        return result

    def format_receipt_plain_text(self, analysis):
        """
        Format receipt analysis as plain text (NOT JSON).
        Output: Food Items list, Subtotal, Tax, Total Amount.
        """
        lines = ["Food Items:"]
        items = analysis.get('items') or []
        for i, it in enumerate(items, 1):
            name = (it.get('name') or '').strip()
            price = it.get('total_price')
            if name and price is not None and price > 0:
                lines.append(f"{i}. {name} - {price:.2f}")
        subtotal = analysis.get('subtotal')
        tax_gst = (analysis.get('tax') or {}).get('gst')
        tax_other = (analysis.get('tax') or {}).get('other')
        tax_val = tax_gst if tax_gst is not None else tax_other
        final = analysis.get('final_amount')
        lines.append("")
        if subtotal is not None:
            lines.append(f"Subtotal: {subtotal:.2f}")
        if tax_val is not None:
            lines.append(f"Tax: {tax_val:.2f}")
        elif final is not None:
            lines.append("Tax: (not available)")
        if final is not None:
            lines.append(f"Total Amount: {final:.2f}")
        return "\n".join(lines)

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
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Configure pytesseract to find Tesseract executable
            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.pytesseract_cmd = tesseract_path
                logger.info(f"✓ Tesseract found at: {tesseract_path}")
            else:
                logger.warning(f"⚠️ Tesseract not found at expected path: {tesseract_path}")
            
            # Validate image file exists
            if not os.path.exists(image_path):
                logger.error(f"❌ Image file not found: {image_path}")
                return ""
            
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            logger.info(f"✓ OCR extraction successful. Text length: {len(text)}")
            return text
        except ImportError as ie:
            logger.error(f"❌ pytesseract or PIL import error: {ie}")
            return ""
        except FileNotFoundError:
            logger.error(f"❌ Image file not found: {image_path}")
            return ""
        except Exception as e:
            logger.error(f"❌ OCR error: {str(e)}")
            return ""
    
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
    
    def _ogg_to_wav(self, voice_path):
        """Convert OGG/Opus (Telegram voice) to WAV for speech_recognition.
        Requires: pydub + ffmpeg on PATH. Install ffmpeg: https://ffmpeg.org
        """
        import os
        try:
            from pydub import AudioSegment
        except ImportError:
            return None
        base, ext = os.path.splitext(voice_path)
        wav_path = base + "_converted.wav"
        ext = (ext or ".ogg").lstrip(".").lower()
        try:
            audio = AudioSegment.from_file(voice_path, format=ext or "ogg")
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(wav_path, format="wav")
            return wav_path
        except Exception:
            return None

    def transcribe_voice(self, voice_path):
        """
        Convert voice to text using speech recognition.
        Converts OGG/Opus (Telegram) to WAV first; supports Google Speech API.
        """
        try:
            import speech_recognition as sr
            import os
            import logging

            logger = logging.getLogger(__name__)

            if not os.path.exists(voice_path):
                logger.error("Voice file not found: %s", voice_path)
                return None

            logger.info("Starting voice transcription from: %s", voice_path)
            recognizer = sr.Recognizer()

            # Use WAV for speech_recognition (it does not support raw OGG/Opus)
            audio_path = voice_path
            temp_wav = None
            if voice_path.lower().endswith(".ogg") or voice_path.lower().endswith(".opus"):
                temp_wav = self._ogg_to_wav(voice_path)
                if temp_wav and os.path.exists(temp_wav):
                    audio_path = temp_wav
                else:
                    logger.error("Failed to convert OGG/Opus to WAV (install pydub)")
                    return None

            try:
                with sr.AudioFile(audio_path) as source:
                    audio = recognizer.record(source)
                logger.info("Audio file loaded successfully")
            except Exception as e:
                logger.error("Failed to load audio file: %s", e)
                if temp_wav and os.path.exists(temp_wav):
                    try:
                        os.remove(temp_wav)
                    except OSError:
                        pass
                return None
            finally:
                if temp_wav and os.path.exists(temp_wav):
                    try:
                        os.remove(temp_wav)
                    except OSError:
                        pass
            
            # Try Google Speech API (free, online) - requires internet
            try:
                text = recognizer.recognize_google(audio)
                logger.info(f"✓ Google Speech API transcription successful: {len(text)} chars")
                return text
            except sr.UnknownValueError:
                logger.warning("⚠️ Google Speech API could not understand audio")
            except sr.RequestError as e:
                logger.warning(f"⚠️ Google Speech API request failed: {e}")
            except Exception as e:
                logger.warning(f"⚠️ Google Speech API error: {e}")
            
            # Fallback to Sphinx (offline recognition)
            try:
                logger.info("🔄 Attempting Sphinx offline recognition...")
                text = recognizer.recognize_sphinx(audio)
                logger.info(f"✓ Sphinx transcription successful: {len(text)} chars")
                return text
            except Exception as e:
                logger.error(f"❌ Sphinx recognition failed: {e}")
                return None
                
        except ImportError as ie:
            logger.error(f"❌ speech_recognition library not installed: {ie}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected voice recognition error: {str(e)}")
            return None
    
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