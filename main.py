"""
Main Telegram Bot Handler for Expense Tracker
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.error import TelegramError

from config import BOT_TOKEN, CURRENCY
from database import ExpenseDatabase
from nlp_processor import ExpenseParser
from bot_commands import (
    start,
    help_command,
    summary,
    weekly_summary,
    monthly_summary,
    today_total,
    show_categories,
    list_expenses,
    delete_expense,
    statistics,
    export_all,
    export_monthly,
    export_weekly,
    export_today_data,
    set_daily_limit,
    set_weekly_limit,
    set_monthly_limit,
    check_limits,
    report_week,
    report_month,
    export_csv,
    export_pdf,
    export_graph,
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database and parser
db = ExpenseDatabase()
parser = ExpenseParser()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages for expense tracking"""
    
    if not update.message or not update.message.text:
        return
    
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    text = update.message.text.strip()
    
    # Skip if it's a command
    if text.startswith('/'):
        return
    
    # Check if it's multiple expenses (contains newlines)
    if '\n' in text:
        # Parse multiple expenses
        expenses = parser.parse_multiple_expenses(text)
        
        if not expenses:
            await update.message.reply_text(
                "❌ Could not parse any expenses from your input.\n\n"
                "Format: Each line should have amount and description\n"
                "Example:\n"
                "Coffee 30\n"
                "Apple 150\n"
                "Tea 40"
            )
            return
        
        # Store all expenses
        success_count = 0
        response_lines = ["✅ **Multiple Expenses Recorded!**\n"]
        
        for amount, category, description in expenses:
            if parser.is_valid_expense(amount, category):
                db.add_expense(user.id, amount, category, description, source="text")
                success_count += 1
                response_lines.append(f"✓ {description}")
                response_lines.append(f"  Amount: {CURRENCY}{amount:.2f} | Category: {category}")
        
        if success_count > 0:
            response_lines.append(f"\n📊 Total: {success_count} expenses recorded")
            response_lines.append("Use /summary to see your spending patterns!")
            confirmation = "\n".join(response_lines)
            await update.message.reply_text(confirmation, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Could not process any of the expenses. Please check the format.")
        
        return
    
    # Single expense parsing
    amount, category, description = parser.parse_expense(text)
    
    if not amount:
        await update.message.reply_text(
            "❌ I couldn't extract amount from your message.\n\n"
            "Try:\n"
            "• 'Spent 150 for biriyani'\n"
            "• '50 on transport'\n"
            "• '200 for movie'\n\n"
            "Or for multiple expenses, send each on a new line:\n"
            "Coffee 30\n"
            "Apple 150\n"
            "Tea 40"
        )
        return
    
    # Validate
    if not parser.is_valid_expense(amount, category):
        await update.message.reply_text("❌ Invalid expense data. Please try again.")
        return
    
    # Store in database
    db.add_expense(user.id, amount, category, description, source="text")
    
    # Send confirmation
    confirmation = (
        f"✅ **Expense Recorded!**\n\n"
        f"💰 Amount: {CURRENCY}{amount:.2f}\n"
        f"🏷️ Category: {category}\n"
        f"📝 Description: {description}\n\n"
        f"Use /summary to see your spending patterns!"
    )
    
    await update.message.reply_text(confirmation, parse_mode='Markdown')
    
    # Check budget limits and send warning if needed
    daily_limit, weekly_limit, monthly_limit = db.get_budget_limits(user.id)
    
    if any([daily_limit, weekly_limit, monthly_limit]):
        today_total = db.get_total_today(user.id)
        week_total = db.get_total_week(user.id)
        month_total = db.get_total_month(user.id)
        
        warnings = []
        
        # Check daily limit
        if daily_limit:
            daily_percentage = (today_total / daily_limit) * 100
            if daily_percentage >= 100:
                warnings.append(f"🔴 Daily limit EXCEEDED: {CURRENCY}{today_total:.2f} / {CURRENCY}{daily_limit:.2f}")
            elif daily_percentage >= 90:
                warnings.append(f"⚠️ Daily limit at 90%: {CURRENCY}{today_total:.2f} / {CURRENCY}{daily_limit:.2f}")
            elif daily_percentage >= 75:
                warnings.append(f"⚡ Daily limit at 75%: {CURRENCY}{today_total:.2f} / {CURRENCY}{daily_limit:.2f}")
        
        # Check weekly limit
        if weekly_limit:
            weekly_percentage = (week_total / weekly_limit) * 100
            if weekly_percentage >= 100:
                warnings.append(f"🔴 Weekly limit EXCEEDED: {CURRENCY}{week_total:.2f} / {CURRENCY}{weekly_limit:.2f}")
            elif weekly_percentage >= 90:
                warnings.append(f"⚠️ Weekly limit at 90%: {CURRENCY}{week_total:.2f} / {CURRENCY}{weekly_limit:.2f}")
            elif weekly_percentage >= 75:
                warnings.append(f"⚡ Weekly limit at 75%: {CURRENCY}{week_total:.2f} / {CURRENCY}{weekly_limit:.2f}")
        
        # Check monthly limit
        if monthly_limit:
            monthly_percentage = (month_total / monthly_limit) * 100
            if monthly_percentage >= 100:
                warnings.append(f"🔴 Monthly limit EXCEEDED: {CURRENCY}{month_total:.2f} / {CURRENCY}{monthly_limit:.2f}")
            elif monthly_percentage >= 90:
                warnings.append(f"⚠️ Monthly limit at 90%: {CURRENCY}{month_total:.2f} / {CURRENCY}{monthly_limit:.2f}")
            elif monthly_percentage >= 75:
                warnings.append(f"⚡ Monthly limit at 75%: {CURRENCY}{month_total:.2f} / {CURRENCY}{monthly_limit:.2f}")
        
        # Send warning if any
        if warnings:
            warning_text = "*Budget Alert:*\n" + "\n".join(warnings)
            await update.message.reply_text(warning_text, parse_mode='Markdown')


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo uploads for receipt processing - simple extraction"""
    
    if not update.message.photo:
        return
    
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    # Get the file
    photo = update.message.photo[-1]  # Get largest quality
    file = await context.bot.get_file(photo.file_id)
    
    try:
        # Download file
        await file.download_to_drive("temp_receipt.jpg")
        
        # Extract text from image using OCR
        ocr_text = None
        
        # Try configured method first
        try:
            from ocr_config import get_ocr_processor
            ocr = get_ocr_processor()
            if ocr:
                result = ocr.parse_receipt("temp_receipt.jpg")
                ocr_text = result.get('text') if result else None
        except Exception as e:
            logger.warning(f"⚠️ Configured OCR failed: {e}")
        
        # Fallback to EasyOCR
        if not ocr_text:
            try:
                from nlp_processor_alternative import EasyOCRProcessor
                ocr = EasyOCRProcessor()
                result = ocr.parse_receipt("temp_receipt.jpg")
                ocr_text = result.get('text') if result else None
                if ocr_text:
                    logger.info("✓ EasyOCR successful")
            except Exception as e:
                logger.warning(f"⚠️ EasyOCR failed: {e}")
        
        # Fallback to Tesseract
        if not ocr_text:
            try:
                from nlp_processor import OCRProcessor
                ocr = OCRProcessor()
                result = ocr.parse_receipt("temp_receipt.jpg")
                ocr_text = result.get('text') if result else None
                if ocr_text:
                    logger.info("✓ Tesseract successful")
            except Exception as e:
                logger.warning(f"⚠️ Tesseract failed: {e}")
        
        # If no OCR text extracted
        if not ocr_text:
            await update.message.reply_text(
                "⚠️ Could not extract text from image.\n\n"
                "Try:\n"
                "• Upload a clearer image\n"
                "• Ensure good lighting\n"
                "• Or manually type: 'Spent 500 for food'"
            )
            return
        
        # --- Advanced analysis: multi-item receipt with categories ---
        analysis = parser.analyze_receipt(ocr_text)
        items = analysis.get("items") or []

        saved_count = 0
        total_items_amount = 0.0
        food_total = 0.0

        for item in items:
            amount = item.get("total_price")
            category = item.get("category")
            name = (item.get("name") or "").strip() or "Receipt item"

            # Fallback category if missing
            if not category:
                category = parser._extract_category(name.lower())

            if parser.is_valid_expense(amount, category):
                db.add_expense(
                    user.id,
                    amount,
                    category,
                    f"Receipt - {name}",
                    source="image",
                )
                saved_count += 1
                total_items_amount += amount
                if category == "Food":
                    food_total += amount

        if saved_count > 0:
            lines = [
                "✅ **Receipt Processed!**",
                "",
                f"Items saved: {saved_count}",
                f"Total (items sum): {CURRENCY}{total_items_amount:.2f}",
                "Source: image receipt",
            ]
            if food_total > 0:
                lines.append(f"Food total: {CURRENCY}{food_total:.2f}")
            if analysis.get("final_amount"):
                lines.append(f"Bill total (receipt): {CURRENCY}{analysis['final_amount']:.2f}")
            lines.append("")
            lines.append("Use /summary or /export_monthly to see this in Excel.")

            await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
            return

        # --- Fallback: simple extraction (single total + category) ---
        simple_result = parser.extract_simple_receipt(ocr_text)
        
        final_amount = simple_result.get('final_amount')
        category = simple_result.get('category')
        
        if not final_amount:
            await update.message.reply_text(
                "❌ Could not find total amount in receipt.\n\n"
                "Please manually enter: 'Spent [amount] for [category]'\n"
                "Example: 'Spent 500 for food'"
            )
            return
        
        # Store the expense as a single entry
        db.add_expense(
            user.id,
            final_amount,
            category,
            f"Receipt - Amount: {final_amount}",
            source="image"
        )
        
        # Confirmation message
        confirmation = (
            f"✅ **Receipt Processed!**\n\n"
            f"💰 Amount: {CURRENCY}{final_amount:.2f}\n"
            f"🏷️ Category: {category}\n"
            f"📷 Source: image receipt\n\n"
            f"Use /summary to see your expenses!"
        )
        
        await update.message.reply_text(confirmation, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Error processing receipt: {str(e)}")
        await update.message.reply_text(
            f"Error processing receipt: {str(e)}\n"
            f"Please try again or manually enter the amount."
        )
    
    # Clean up temp file
    import os
    if os.path.exists("temp_receipt.jpg"):
        os.remove("temp_receipt.jpg")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages for bill tracking"""
    
    if not update.message.voice:
        return
    
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    await update.message.reply_text("🎤 Processing voice message...")
    
    try:
        # Get the voice file
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        
        # Download voice file
        await file.download_to_drive("temp_voice.ogg")
        
        # Convert to text using speech recognition
        from nlp_processor import VoiceProcessor
        voice_processor = VoiceProcessor()
        text = voice_processor.transcribe_voice("temp_voice.ogg")
        
        if not text:
            await update.message.reply_text(
                "Couldn't process voice message.\n\n"
                "1) **OGG conversion needs ffmpeg** – install and add to PATH:\n"
                "   https://ffmpeg.org (or: choco install ffmpeg)\n\n"
                "2) Internet required for Google Speech API.\n"
                "3) Speak clearly; or type: 'Spent 150 for food'"
            )
            return
        
        # Parse the transcribed text
        amount, category, description = parser.parse_expense(text)
        
        if not amount:
            await update.message.reply_text(
                f"📝 Transcribed: {text}\n\n"
                "❌ Couldn't extract amount. Please try saying:\n"
                "• 'Spent 150 for biriyani'\n"
                "• '50 on transport'\n"
                "• '200 for movie'"
            )
            return
        
        # Store expense
        db.add_expense(user.id, amount, category, description, source="voice")
        
        confirmation = (
            f"✅ **Voice Bill Recorded!**\n\n"
            f"🎤 Transcribed: {text}\n"
            f"💰 Amount: {CURRENCY}{amount:.2f}\n"
            f"🏷️ Category: {category}\n"
            f"📝 Description: {description}\n\n"
            f"Use /summary to see your spending!"
        )
        
        await update.message.reply_text(confirmation, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error processing voice: {str(e)}")
        await update.message.reply_text(
            f"❌ Error processing voice: {str(e)}\n"
            f"Please try again or manually enter the amount."
        )
    
    # Clean up
    import os
    if os.path.exists("temp_voice.ogg"):
        os.remove("temp_voice.ogg")


async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle screenshot uploads for online payment tracking"""
    
    if not update.message.photo:
        return
    
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    # Check if it's a screenshot (caption might indicate payment info)
    caption = update.message.caption or ""
    is_payment = "transaction" in caption.lower() or "payment" in caption.lower() or "upi" in caption.lower() or "bank" in caption.lower()
    
    if not is_payment:
        # Call the regular receipt handler for regular photos
        await handle_photo(update, context)
        return
    
    # Get the file
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    try:
        # Download file
        await file.download_to_drive("temp_payment.jpg")
        
        # Extract text from screenshot - try configured method first, fallback to others
        result = None
        
        # Try configured method first
        try:
            from ocr_config import get_ocr_processor
            ocr = get_ocr_processor()
            if ocr:
                result = ocr.parse_receipt("temp_payment.jpg")
        except Exception as e:
            logger.warning(f"⚠️ Configured OCR failed, trying fallback: {e}")
        
        # Fallback to EasyOCR if configured method failed
        if not result or not result.get('amount'):
            try:
                from nlp_processor_alternative import EasyOCRProcessor
                ocr = EasyOCRProcessor()
                result = ocr.parse_receipt("temp_payment.jpg")
                logger.info("✓ EasyOCR fallback successful")
            except Exception as e:
                logger.warning(f"⚠️ EasyOCR fallback failed: {e}")
        
        # Final fallback to original Tesseract
        if not result or not result.get('amount'):
            try:
                from nlp_processor import OCRProcessor
                ocr = OCRProcessor()
                result = ocr.parse_receipt("temp_payment.jpg")
                logger.info("✓ Tesseract fallback successful")
            except Exception as e:
                logger.warning(f"⚠️ Tesseract fallback failed: {e}")
        
        if not result or not result['amount']:
            await update.message.reply_text(
                "⚠️ Couldn't extract payment details.\n\n"
                "Please reply with transaction details in format:\n"
                "`TXID: ABC123\nAccount: MyBank\nAmount: 500`\n\n"
                "Or upload a clearer screenshot."
            )
            return
        
        # Extract transaction details from caption or OCR
        transaction_id = None
        account_name = None
        
        # Try to extract from caption
        if caption:
            lines = caption.split('\n')
            for line in lines:
                if 'tx' in line.lower() or 'id' in line.lower():
                    transaction_id = line.split(':')[-1].strip()
                if 'account' in line.lower():
                    account_name = line.split(':')[-1].strip()
        
        # Store with transaction details
        db.add_expense(
            user.id,
            result['amount'],
            result['category'],
            result['text'][:100],
            source="online_payment",
            transaction_id=transaction_id,
            account_name=account_name,
            payment_method="digital"
        )
        
        confirmation = (
            f"✅ **Online Payment Recorded!**\n\n"
            f"💰 Amount: {CURRENCY}{result['amount']:.2f}\n"
            f"🏷️ Category: {result['category']}\n"
        )
        
        if transaction_id:
            confirmation += f"🔑 Transaction ID: `{transaction_id}`\n"
        if account_name:
            confirmation += f"🏦 Account: {account_name}\n"
        
        confirmation += f"\n📱 Source: Online Payment/Screenshot\n\n"
        confirmation += f"Use /summary to track your spending!"
        
        await update.message.reply_text(confirmation, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error processing payment screenshot: {str(e)}")
        await update.message.reply_text(
            f"❌ Error processing screenshot: {str(e)}\n"
            f"Please try again with a clearer image or manually enter the details."
        )
    
    # Clean up
    import os
    if os.path.exists("temp_payment.jpg"):
        os.remove("temp_payment.jpg")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


def main():
    """Start the bot"""
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(CommandHandler("weekly", weekly_summary))
    application.add_handler(CommandHandler("monthly", monthly_summary))
    application.add_handler(CommandHandler("today", today_total))
    application.add_handler(CommandHandler("categories", show_categories))
    application.add_handler(CommandHandler("list", list_expenses))
    application.add_handler(CommandHandler("delete", delete_expense))
    application.add_handler(CommandHandler("stats", statistics))
    
    # Export commands
    application.add_handler(CommandHandler("export", export_all))
    application.add_handler(CommandHandler("export_monthly", export_monthly))
    application.add_handler(CommandHandler("export_weekly", export_weekly))
    application.add_handler(CommandHandler("export_today", export_today_data))
    application.add_handler(CommandHandler("export_csv", export_csv))
    application.add_handler(CommandHandler("pdf", export_pdf))
    application.add_handler(CommandHandler("graph", export_graph))
    
    # Budget limit commands
    application.add_handler(CommandHandler("setdaily", set_daily_limit))
    application.add_handler(CommandHandler("setweekly", set_weekly_limit))
    application.add_handler(CommandHandler("setmonthly", set_monthly_limit))
    application.add_handler(CommandHandler("limits", check_limits))
    
    # Report commands
    application.add_handler(CommandHandler("week", report_week))
    application.add_handler(CommandHandler("month", report_month))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start polling
    logger.info("Bot started polling...")
    print("[*] Expense Tracker Bot is running!")
    print("[*] Press Ctrl+C to stop.")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

