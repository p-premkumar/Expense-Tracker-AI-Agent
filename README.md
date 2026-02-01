# 💰 Telegram Expense Tracker AI Agent

An intelligent Telegram bot that automatically tracks your daily expenses using natural language processing and AI.

## 🎯 Features

- **Natural Language Processing**: Understands messages like "Spent 150 for biriyani"
- **Automatic Category Detection**: Intelligent expense categorization
- **Receipt OCR Processing**: Extract expenses from receipt photos
- **Weekly/Monthly Summaries**: Get detailed spending reports
- **Category Tracking**: Breakdown of expenses by category
- **SQLite Database**: Local storage of all expenses
- **📊 Excel Export**: Download expenses as professional Excel files
- **Multiple Input Methods**: 
  - Text messages
  - Screenshot uploads
  - Receipt photos

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Telegram account
- Bot token (already provided)

### Installation

1. **Clone/Setup the project:**
```bash
cd "Expense Tracer AI Agent"
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Download Tesseract (for OCR - optional but recommended):**
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`

4. **Run the bot:**
```bash
python main.py
```

## 📱 How to Use

### Start the Bot
Find @Expense_TrackerAI_Bot on Telegram or use the provided token.

### Adding Expenses
Simply send messages like:
- "Spent 150 for biriyani"
- "Transport - 50"
- "200 on movie tickets"
- "Electricity bill 1500"

### Available Commands
- `/start` - Welcome message
- `/help` - Show all commands
- `/summary` - Last 30 days summary
- `/weekly` - Last 7 days summary
- `/monthly` - Last 30 days summary
- `/today` - Today's total spending
- `/categories` - Show all expense categories
- `/list` - Last 10 expenses
- `/stats` - Detailed statistics
- `/delete` - Delete last expense

### Supported Categories
- Food
- Transport
- Entertainment
- Shopping
- Utilities
- Health
- Education
- Travel
- Work
- Other

## 📊 Supported Input Methods

### 1. Text Messages
```
"Today I spent 150 for biriyani"
"150 on transport"
"Coffee - 100"
```

### 2. Receipt Photos
Upload a clear receipt photo and the bot will:
- Extract text using OCR (Tesseract)
- Parse the amount and category
- Automatically store it

### 3. Screenshots
Take a screenshot of your expense and upload it.

## 🧠 AI Features

### NLP & Entity Extraction
- Keyword-based category matching
- Amount extraction from natural language
- Pattern recognition for common expense phrases

### Hybrid Approach
- Rule-based patterns for common categories
- Fallback to "Other" category
- Flexible amount parsing (handles ₹, $, €, etc.)

## 📁 Project Structure

```
Expense Tracer AI Agent/
├── main.py              # Main bot handler
├── config.py            # Configuration and settings
├── database.py          # Database management
├── nlp_processor.py     # NLP and entity extraction
├── bot_commands.py      # Command handlers
├── requirements.txt     # Python dependencies
├── expenses.db          # SQLite database (auto-created)
└── README.md           # This file
```

## 💾 Database Schema

### users
- user_id: Telegram user ID
- username: Telegram username
- first_name: User's first name
- created_at: Registration timestamp

### expenses
- id: Unique expense ID
- user_id: Reference to user
- amount: Expense amount
- category: Expense category
- description: Full text description
- date: Timestamp
- source: Input source (text/receipt)

### categories
- category_id: Category ID
- user_id: Reference to user
- name: Category name
- created_at: Creation timestamp

## 🔧 Configuration

Edit `config.py` to customize:
- Expense categories
- Currency symbol
- Expense patterns/keywords
- Database path

## 📈 Usage Examples

### Example 1: Simple text entry
```
User: "Spent 150 for biriyani"
Bot: ✅ Expense Recorded!
     💰 Amount: ₹150.00
     🏷️ Category: Food
```

### Example 2: Receipt upload
```
User: [Uploads receipt photo]
Bot: ✅ Receipt Processed!
     💰 Amount: ₹299.50
     🏷️ Category: Food
```

### Example 3: View summary
```
User: /summary
Bot: 📊 Expense Summary (Last 30 days)
     Food: ₹3,500.00 (15 items)
     Transport: ₹1,200.00 (8 items)
     ...
     💰 Total: ₹5,890.00
```

## 🔐 Security & Privacy

- All data stored locally in SQLite
- No data sent to external servers
- Bot token secured in config
- User data remains private

## 🐛 Troubleshooting

### Bot not responding
1. Check bot token in `config.py`
2. Ensure internet connection
3. Verify Telegram API is not blocked
4. Check logs for errors

### OCR not working
1. Verify Tesseract installation
2. Ensure image is clear and well-lit
3. Try uploading a different image
4. Manual entry as fallback

### Amount not detected
1. Include clear numbers in message
2. Use standard currency symbols
3. Example: "150 for food" works better than "approx 150-200"

## 📝 Example Phrases Bot Understands

```
"Spent 150 for food"
"150 on biriyani"
"Transport 50"
"₹100 for movie"
"Coffee - 50"
"Electricity bill 1500"
"Bought shoes 2000"
"Flight ticket 5000"
```

## 🚀 Future Enhancements

- [ ] Recurring expense tracking
- [ ] Budget alerts
- [ ] CSV export
- [ ] Multi-user households
- [ ] Bill splitting
- [ ] Voice notes support
- [ ] Integration with banks
- [ ] ML-based category prediction

## 📞 Support

For issues or questions:
1. Check this README
2. Review bot command logs
3. Verify all dependencies are installed
4. Check database integrity

## 📄 License

This project is open source and available for personal use.

## 🎉 Enjoy Tracking!

Start using the bot today to get better insights into your spending habits!

---

**Bot Status**: ✅ Active  
**Last Updated**: January 2026  
**Version**: 1.0.0
