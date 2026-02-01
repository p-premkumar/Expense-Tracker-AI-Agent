"""
Telegram bot command handlers
"""
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import ExpenseDatabase
from config import CURRENCY, EXPENSE_CATEGORIES
from datetime import datetime
from excel_exporter import ExcelExporter

db = ExpenseDatabase()
exporter = ExcelExporter()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    welcome_text = f"""
👋 Welcome to Expense Tracker AI Agent, {user.first_name}!

I help you track your expenses automatically. Just send me messages like:
• "Spent 150 for biriyani"
• "150 on transport"
• "200 for movie"

I'll extract the amount and category, then store it automatically.

🔍 **What I can do:**
• 📝 Parse text expenses
• 📸 Process receipt photos using OCR
• 📊 Generate weekly/monthly summaries
• 📈 Track expenses by category
• ✏️ Edit or delete expenses

Use /help for available commands.
    """
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command handler"""
    help_text = f"""
📋 **Available Commands:**

/start - Welcome message
/help - This help message
/summary - Show summary of last 30 days
/weekly - Weekly summary (last 7 days)
/monthly - Monthly summary (last 30 days)
/today - Today's total spending
/categories - Show all categories
/delete - Delete last expense
/edit - Edit last expense
/list - Show last 10 expenses
/stats - Detailed statistics

� **Export to Excel:**
/export - Export all expenses to Excel
/export_monthly - Export last 30 days to Excel
/export_weekly - Export last 7 days to Excel
/export_today - Export today's expenses to Excel

�📝 **How to Add Expenses:**
Just send natural language messages like:
• "Spent 150 for biriyani"
• "Transport - 50"
• "250 on movie"

📸 **Receipt Processing:**
Send a photo of your receipt and I'll extract amount and category automatically.

🎤 **Voice Bills:**
Send a voice message describing your bill/expense. I'll transcribe and record it automatically.

💳 **Online Payment Tracking:**
Upload a screenshot of online payment/transaction. Include caption with:
• TXID: [transaction_id]
• Account: [account_name]

I'll track transaction ID, account name, and amount separately.

💾 **Categories:**
{', '.join(EXPENSE_CATEGORIES)}

Use /summary to see your spending patterns!
    """
    
    await update.message.reply_text(help_text)

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE, days: int = 30) -> None:
    """Show expense summary"""
    user_id = update.effective_user.id
    expenses = db.get_summary(user_id, days)
    
    if not expenses:
        await update.message.reply_text("No expenses found for this period.")
        return
    
    summary_text = f"📊 **Expense Summary (Last {days} days)**\n\n"
    total = 0
    
    for category, amount, count in expenses:
        summary_text += f"🏷️ {category}: {CURRENCY}{amount:.2f} ({count} items)\n"
        total += amount
    
    summary_text += f"\n💰 **Total: {CURRENCY}{total:.2f}**"
    
    await update.message.reply_text(summary_text, parse_mode='Markdown')

async def weekly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show weekly summary"""
    await summary(update, context, days=7)

async def monthly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show monthly summary"""
    await summary(update, context, days=30)

async def today_total(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show today's total"""
    user_id = update.effective_user.id
    total = db.get_total_today(user_id)
    
    message = f"💸 **Today's Spending: {CURRENCY}{total:.2f}**"
    await update.message.reply_text(message, parse_mode='Markdown')

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all categories"""
    categories_text = "📂 **Expense Categories:**\n\n"
    for category in EXPENSE_CATEGORIES:
        categories_text += f"• {category}\n"
    
    await update.message.reply_text(categories_text, parse_mode='Markdown')

async def list_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List last 10 expenses"""
    user_id = update.effective_user.id
    expenses = db.get_expenses(user_id)[:10]
    
    if not expenses:
        await update.message.reply_text("No expenses found.")
        return
    
    list_text = "📝 **Last 10 Expenses:**\n\n"
    for idx, (exp_id, amount, category, description, date) in enumerate(expenses, 1):
        date_obj = datetime.fromisoformat(date)
        date_str = date_obj.strftime("%d-%m-%Y %H:%M")
        list_text += f"{idx}. {category} - {CURRENCY}{amount:.2f} ({date_str})\n"
    
    await update.message.reply_text(list_text, parse_mode='Markdown')

async def delete_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete last expense"""
    user_id = update.effective_user.id
    expenses = db.get_expenses(user_id)
    
    if not expenses:
        await update.message.reply_text("No expenses to delete.")
        return
    
    exp_id = expenses[0][0]
    db.delete_expense(exp_id, user_id)
    
    await update.message.reply_text("✅ Last expense deleted!")

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed statistics"""
    user_id = update.effective_user.id
    expenses_30 = db.get_summary(user_id, 30)
    expenses_7 = db.get_summary(user_id, 7)
    
    stats_text = "📈 **Detailed Statistics**\n\n"
    
    # Last 7 days
    stats_text += "**Last 7 Days:**\n"
    total_7 = 0
    if expenses_7:
        for category, amount, count in expenses_7:
            stats_text += f"  {category}: {CURRENCY}{amount:.2f}\n"
            total_7 += amount
        stats_text += f"  **Total: {CURRENCY}{total_7:.2f}**\n\n"
    else:
        stats_text += "  No expenses\n\n"
    
    # Last 30 days
    stats_text += "**Last 30 Days:**\n"
    total_30 = 0
    if expenses_30:
        for category, amount, count in expenses_30:
            stats_text += f"  {category}: {CURRENCY}{amount:.2f}\n"
            total_30 += amount
        stats_text += f"  **Total: {CURRENCY}{total_30:.2f}**\n"
    else:
        stats_text += "  No expenses\n"
    
    # Daily average
    if expenses_30:
        daily_avg = total_30 / 30
        stats_text += f"\n💡 **Daily Average: {CURRENCY}{daily_avg:.2f}**"
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')
async def export_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export all expenses to Excel file"""
    user_id = update.effective_user.id
    
    await update.message.reply_text("📊 Generating Excel file with all your expenses...", parse_mode='Markdown')
    
    try:
        # Generate Excel file
        filename = exporter.export_all_expenses(user_id)
        
        # Send file to user
        with open(filename, 'rb') as excel_file:
            await update.message.reply_document(
                document=excel_file,
                caption=f"📊 **All Expenses Report**\n\nGenerated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\nSheets included:\n• All Expenses\n• Summary\n• Monthly Breakdown",
                parse_mode='Markdown'
            )
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
        
        await update.message.reply_text("✅ Excel file exported successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating Excel file: {str(e)}")

async def export_monthly(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export monthly expenses to Excel file"""
    user_id = update.effective_user.id
    
    await update.message.reply_text("📊 Generating monthly expense report...", parse_mode='Markdown')
    
    try:
        # Generate Excel file
        filename = exporter.export_monthly_expenses(user_id)
        
        # Send file to user
        with open(filename, 'rb') as excel_file:
            await update.message.reply_document(
                document=excel_file,
                caption=f"📊 **Monthly Expense Report**\n\nGenerated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\nPeriod: Last 30 days\n\nSheets included:\n• Summary by Category\n• Detailed Transactions",
                parse_mode='Markdown'
            )
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
        
        await update.message.reply_text("✅ Monthly report exported successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating report: {str(e)}")

async def export_weekly(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export weekly expenses to Excel file"""
    user_id = update.effective_user.id
    
    await update.message.reply_text("📊 Generating weekly expense report...", parse_mode='Markdown')
    
    try:
        # Generate Excel file
        filename = exporter.export_custom_period(user_id, days=7)
        
        # Send file to user
        with open(filename, 'rb') as excel_file:
            await update.message.reply_document(
                document=excel_file,
                caption=f"📊 **Weekly Expense Report**\n\nGenerated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\nPeriod: Last 7 days",
                parse_mode='Markdown'
            )
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
        
        await update.message.reply_text("✅ Weekly report exported successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating report: {str(e)}")

async def export_today_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export today's expenses to Excel file"""
    user_id = update.effective_user.id
    
    await update.message.reply_text("📊 Generating today's expense report...", parse_mode='Markdown')
    
    try:
        # Generate Excel file
        filename = exporter.export_custom_period(user_id, days=1)
        
        # Send file to user
        with open(filename, 'rb') as excel_file:
            await update.message.reply_document(
                document=excel_file,
                caption=f"📊 **Today's Expense Report**\n\nGenerated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
                parse_mode='Markdown'
            )
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
        
        await update.message.reply_text("✅ Today's report exported successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating report: {str(e)}")