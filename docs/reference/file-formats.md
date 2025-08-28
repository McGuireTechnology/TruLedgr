# File Formats

Understanding the various file formats supported by TruLedgr for importing, exporting, and backing up your financial data.

## Import Formats

### CSV (Comma-Separated Values)

**File Extension:** `.csv`  
**Usage:** Most common format for importing transaction data  
**Compatibility:** Universal - works with all banks and financial software

#### Standard CSV Format

```csv
Date,Description,Amount,Category,Account
2024-01-15,Grocery Store,-85.42,Groceries,Checking
2024-01-15,Salary Deposit,2500.00,Income,Checking
2024-01-16,Gas Station,-35.20,Transportation,Credit Card
```

#### Required Fields
- **Date:** Transaction date (MM/DD/YYYY, YYYY-MM-DD, or DD/MM/YYYY)
- **Description:** Transaction description or merchant name
- **Amount:** Transaction amount (positive for income, negative for expenses)

#### Optional Fields
- **Category:** Expense or income category
- **Account:** Account name or identifier
- **Reference:** Check number or transaction ID
- **Notes:** Additional transaction details
- **Tags:** Comma-separated tags for organization

#### Bank-Specific Formats

**Chase Bank Format:**
```csv
Type,Trans Date,Post Date,Description,Amount
DEBIT,01/15/2024,01/15/2024,GROCERY STORE #123,-85.42
CREDIT,01/15/2024,01/15/2024,DIRECT DEPOSIT COMPANY,2500.00
```

**Bank of America Format:**
```csv
Date,Description,Amount,Running Bal.
01/15/2024,GROCERY STORE PURCHASE,-85.42,1234.56
01/15/2024,PAYROLL DEPOSIT,2500.00,3734.56
```

**Wells Fargo Format:**
```csv
"01/15/2024","-85.42","*","","GROCERY STORE #123 01/15"
"01/15/2024","2500.00","*","","DIRECT DEP COMPANY 01/15"
```

### Excel Formats

**File Extensions:** `.xlsx`, `.xls`  
**Usage:** Spreadsheet data with multiple sheets and formatting  
**Compatibility:** Microsoft Excel and compatible applications

#### Supported Excel Features
- Multiple worksheets (TruLedgr uses the first sheet by default)
- Header rows with column names
- Formatted dates and currency
- Merged cells (data extracted from top-left cell)
- Hidden rows and columns (ignored during import)

#### Excel Template
TruLedgr provides Excel templates for easy data entry:

| Date | Payee | Amount | Category | Account | Notes |
|------|-------|--------|----------|---------|-------|
| 1/15/2024 | Grocery Store | -85.42 | Groceries | Checking | Weekly shopping |
| 1/15/2024 | Employer | 2500.00 | Salary | Checking | Bi-weekly payroll |

### QIF (Quicken Interchange Format)

**File Extension:** `.qif`  
**Usage:** Legacy format from Quicken and other financial software  
**Compatibility:** Older financial applications

#### QIF Structure
```
!Type:Bank
D01/15/2024
T-85.42
PGrocery Store
LGroceries
^
D01/15/2024
T2500.00
PEmployer
LSalary
^
```

#### QIF Field Codes
- `D` - Date
- `T` - Amount
- `P` - Payee
- `L` - Category
- `M` - Memo
- `N` - Number (check number)
- `^` - End of transaction

### OFX (Open Financial Exchange)

**File Extension:** `.ofx`  
**Usage:** Bank download format for electronic statements  
**Compatibility:** Most financial institutions and software

#### OFX Benefits
- Includes account information and balances
- Standardized transaction codes
- Digital signatures for security
- Support for multiple account types

### QBO (QuickBooks Online)

**File Extension:** `.qbo`  
**Usage:** QuickBooks-specific format  
**Compatibility:** QuickBooks products and compatible software

### PDF Bank Statements

**File Extension:** `.pdf`  
**Usage:** Digital bank statements and credit card statements  
**Processing:** TruLedgr uses OCR technology to extract transaction data

#### PDF Processing Features
- Automatic table detection
- Text extraction and parsing
- Date and amount recognition
- Merchant name identification

#### Supported Statement Types
- Bank checking and savings statements
- Credit card statements
- Investment account statements
- Loan statements

### JSON Format

**File Extension:** `.json`  
**Usage:** API data exchange and backup files  
**Compatibility:** Web applications and APIs

#### JSON Transaction Format
```json
{
  "transactions": [
    {
      "date": "2024-01-15",
      "description": "Grocery Store",
      "amount": -85.42,
      "category": "Groceries",
      "account": "Checking",
      "id": "txn_123456"
    }
  ]
}
```

## Export Formats

### CSV Export

**Standard Export Format:**
```csv
Date,Payee,Amount,Category,Account,Notes,Tags,Reference
2024-01-15,Grocery Store,-85.42,Groceries,Checking,Weekly shopping,food,
2024-01-15,Employer,2500.00,Salary,Checking,Bi-weekly payroll,income,12345
```

**Custom Export Options:**
- Choose specific date ranges
- Select specific accounts or categories
- Include or exclude specific fields
- Apply filters before export

### Excel Export

**Features:**
- Multiple worksheets for different data types
- Formatted currency and dates
- Charts and summaries included
- Pivot table-ready data structure

**Worksheet Structure:**
- **Transactions:** All transaction data
- **Summary:** Monthly/yearly summaries
- **Categories:** Category breakdowns
- **Accounts:** Account summaries
- **Charts:** Visual representations

### PDF Reports

**Report Types:**
- Monthly statements
- Annual summaries
- Budget reports
- Tax summaries
- Net worth reports

**PDF Features:**
- Professional formatting
- Charts and graphs
- Print-ready layout
- Digital signatures available

### QIF Export

**Usage:** For importing into other financial software  
**Benefits:** Wide compatibility with legacy systems

### JSON Export

**Usage:** API integration and data backup  
**Benefits:** Complete data structure preservation

## Backup Formats

### Full Backup

**File Extension:** `.truledgr`  
**Content:** Complete account data including:
- All transactions
- Account settings
- Categories and rules
- Budget information
- Goals and targets
- User preferences

### Incremental Backup

**File Extension:** `.truledgr-inc`  
**Content:** Changes since last full backup  
**Benefits:** Smaller file size, faster backup process

### Cloud Backup

**Format:** Encrypted JSON  
**Storage:** Secure cloud storage  
**Features:**
- Automatic daily backups
- Version history (30 days)
- Cross-device synchronization
- Encryption at rest and in transit

## Data Validation

### Import Validation

TruLedgr performs automatic validation during import:

#### Date Validation
- Recognizes multiple date formats
- Handles leap years and month variations
- Flags invalid dates for review

#### Amount Validation
- Detects currency symbols and formatting
- Handles positive/negative conventions
- Identifies unusual amounts for review

#### Duplicate Detection
- Matches similar transactions
- Flags potential duplicates
- Allows manual override

### Export Validation

Before export, TruLedgr ensures:
- Data integrity
- Proper formatting
- Complete record sets
- Error-free output

## File Size Limits

### Import Limits
- **CSV files:** Up to 100MB
- **Excel files:** Up to 50MB
- **PDF files:** Up to 25MB
- **Other formats:** Up to 25MB

### Export Limits
- **Single export:** Up to 500,000 transactions
- **Date range:** No limit
- **File size:** Automatically split if needed

### Performance Optimization
- Large files processed in chunks
- Progress indicators for long operations
- Background processing available
- Resume capability for interrupted imports

## Troubleshooting

### Common Import Issues

**"Date format not recognized"**
- Ensure dates are in MM/DD/YYYY, DD/MM/YYYY, or YYYY-MM-DD format
- Check for extra spaces or characters
- Verify date column is properly identified

**"Amount format error"**
- Remove currency symbols ($ € £)
- Use periods for decimal separators
- Ensure negative numbers use minus sign or parentheses

**"File encoding error"**
- Save CSV files as UTF-8 encoding
- Avoid special characters in file names
- Check for hidden characters or formatting

### Export Issues

**"File too large"**
- Reduce date range
- Export specific accounts only
- Use incremental export feature

**"Permission denied"**
- Check file permissions
- Ensure file isn't open in another application
- Try different export location

### Performance Tips

**For Large Imports:**
- Split large files into smaller chunks
- Import during off-peak hours
- Close other applications during import
- Use wired internet connection for cloud uploads

**For Faster Processing:**
- Clean data before import
- Remove unnecessary columns
- Use standard date formats
- Eliminate duplicate headers

## Security Considerations

### File Security
- All files encrypted during transmission
- Temporary files securely deleted after processing
- No file data stored permanently on servers
- Local processing when possible

### Privacy Protection
- Personal data anonymized in error logs
- No account numbers included in support files
- Optional data masking for screenshots
- Secure file deletion after processing

---

*Having trouble with a specific file format? Check our [troubleshooting guide](../support/overview.md#troubleshooting) or [contact support](../support/overview.md#contacting-support).*
