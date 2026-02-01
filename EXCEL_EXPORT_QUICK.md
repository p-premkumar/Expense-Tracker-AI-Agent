# Excel Export - Quick Reference

## Commands

```
/export          → Download ALL expenses as Excel
/export_monthly  → Download LAST 30 DAYS as Excel  
/export_weekly   → Download LAST 7 DAYS as Excel
/export_today    → Download TODAY'S expenses as Excel
```

## What You Get

✅ Professional Excel spreadsheets  
✅ Multiple sheets with different views  
✅ Formatted with colors and borders  
✅ Currency symbols and calculations  
✅ Category summaries and breakdowns  
✅ Detailed transaction lists  

## File Format

```
Format: XLSX (Excel 2007+)
Opens in: Excel, Google Sheets, LibreOffice
Size: 50-300 KB typical
Time: 2-5 seconds to generate
```

## Usage Example

```
1. Send: /export_monthly
2. Bot replies: "📊 Generating monthly expense report..."
3. Wait 3-5 seconds
4. Receive: expenses_monthly_USERID_YYYYMM_timestamp.xlsx
5. Click to download
6. Open in Excel/Sheets
```

## Sheet Contents

### Summary Sheet
- Category breakdown
- Total amounts
- Transaction counts
- Averages per category
- **Total row** (highlighted)

### Details Sheet
- Date & Time
- Category
- Amount (with currency)
- Description
- Source (text/photo)

### Monthly Breakdown (All-in-one only)
- Month-wise totals
- Year overview
- Spending by month

## Features

| Feature | Included |
|---------|----------|
| Color formatting | ✅ Yes |
| Currency symbol | ✅ Yes |
| Borders | ✅ Yes |
| Formulas | ✅ Yes |
| Sorting ready | ✅ Yes |
| Multiple sheets | ✅ Yes |

## Common Uses

```
📊 Track spending     → /export_monthly
📈 Weekly review      → /export_weekly
✅ Daily verification → /export_today
💾 Complete backup    → /export
💰 Budget planning    → /export_monthly
📋 Tax prep          → /export
```

## Tips

```
💡 Export weekly for trend tracking
💡 Use monthly for budgeting  
💡 Create pivot tables in Excel for analysis
💡 Save to cloud for backup
💡 Share with accountant if needed
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| File won't open | Use Google Sheets or LibreOffice |
| No data in file | Add expenses first with natural language |
| Columns too narrow | Double-click column header divider |
| Export taking long | Wait, or try with fewer days |

## Tips for Analysis

### In Excel:
1. **Sort** - Click header → Data → Sort
2. **Filter** - Select data → Data → AutoFilter
3. **Sum** - =SUM(column)
4. **Average** - =AVERAGE(column)
5. **Count** - =COUNTIF(column, criteria)

### Create Charts:
1. Select data
2. Insert → Chart
3. Choose type (pie, bar, line)
4. Analyze visually

## All Commands

```
📊 Export Commands:
/export              - All expenses
/export_monthly      - Last 30 days
/export_weekly       - Last 7 days
/export_today        - Today only

📋 Other Commands:
/start              - Welcome
/help               - Full help
/summary            - Text summary
/list               - Last 10
/stats              - Statistics
/categories         - Show categories
```

---

**Quick Start:** Send `/export_monthly` now! 📊
