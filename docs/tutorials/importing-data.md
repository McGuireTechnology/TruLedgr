# Importing Data from Other Apps

Learn how to migrate your financial data from other personal finance applications into TruLedgr quickly and accurately.

## 💾 Supported Import Sources

TruLedgr supports importing data from many popular financial applications and file formats.

### Supported Applications

- **Mint** - Complete transaction and category import
- **YNAB (You Need A Budget)** - Budget and transaction import
- **Quicken** - Full financial data import
- **Personal Capital** - Investment and transaction data
- **PocketGuard** - Budget and spending data
- **Goodbudget** - Envelope budget import
- **EveryDollar** - Zero-based budget import

### Supported File Formats

- **CSV (Comma Separated Values)** - Most common format
- **QIF (Quicken Interchange Format)** - Legacy Quicken format
- **OFX (Open Financial Exchange)** - Bank standard format
- **Excel/XLSX** - Microsoft Excel files
- **JSON** - Structured data format

### Bank Export Formats

Most banks and financial institutions support:

- CSV exports from online banking
- OFX downloads for transactions
- PDF statements (with conversion)
- QIF exports from older systems

## 🚀 Import Process Overview

### Step 1: Export Your Data

#### From Mint

1. **Login to Mint**
   - Go to mint.com
   - Navigate to "Your Profile" → "Export Data"

2. **Export Transactions**
   - Select date range (recommend all-time)
   - Choose CSV format
   - Download transactions.csv

3. **Export Categories**
   - Export category assignments
   - Save custom category definitions

#### From YNAB

1. **Access YNAB Data**
   - Login to YNAB web or desktop app
   - Go to "File" → "Export Budget Data"

2. **Export Options**
   - Export register (transactions)
   - Export budget data
   - Save as CSV format

#### From Bank Websites

1. **Login to Online Banking**
   - Navigate to account statements
   - Select "Export" or "Download"

2. **Choose Format and Date Range**
   - Select CSV or OFX format
   - Choose comprehensive date range
   - Download separate files per account

### Step 2: Prepare Your Data

#### Clean Up CSV Files

Before importing, ensure your data is properly formatted:

**Required Columns**

```text
Date: YYYY-MM-DD format
Amount: Decimal number (negative for expenses)
Description: Transaction description
Category: Spending category
Account: Account name (if multiple accounts)
```

**Optional Columns**

```text
Notes: Additional transaction details
Tags: Custom transaction tags
Payee: Who the payment was to/from
Type: Income/Expense/Transfer
```

#### Example CSV Format

```csv
Date,Amount,Description,Category,Account
2024-01-15,-45.67,Grocery Store,Groceries,Checking
2024-01-16,3000.00,Salary Deposit,Income,Checking
2024-01-17,-25.00,Gas Station,Transportation,Checking
2024-01-18,-120.00,Electric Bill,Utilities,Checking
```

### Step 3: Import Into TruLedgr

#### Using the Import Wizard

1. **Access Import Tool**
   - Navigate to "Settings" → "Import Data"
   - Click "Import Transactions"

2. **Upload File**
   - Select your prepared CSV file
   - Choose file encoding (usually UTF-8)
   - Specify separator (comma, semicolon, tab)

3. **Map Columns**
   - Match CSV columns to TruLedgr fields
   - Set date format
   - Configure amount handling (positive/negative)

4. **Review and Import**
   - Preview first 10 transactions
   - Verify mapping is correct
   - Start import process

#### Import Configuration

**Date Format Options**

```text
MM/DD/YYYY (US format): 01/15/2024
DD/MM/YYYY (EU format): 15/01/2024
YYYY-MM-DD (ISO format): 2024-01-15
```

**Amount Format Options**

```text
Negative for expenses: -45.67
Positive for expenses: 45.67
Separate debit/credit columns
```

## 🗂️ Category Mapping

### Automatic Category Detection

TruLedgr can automatically map many common categories:

**Common Mappings**

```text
Original → TruLedgr
Food & Dining → Groceries, Restaurants
Auto & Transport → Transportation
Bills & Utilities → Utilities
Shopping → Shopping, Personal Care
Entertainment → Entertainment
Health & Fitness → Healthcare
```

### Custom Category Mapping

#### Create Mapping Rules

1. **Set Up Rules**
   - Map old categories to new ones
   - Handle subcategory consolidation
   - Create new categories as needed

2. **Keyword Matching**
   - Set up automatic categorization
   - Match by merchant name
   - Use description keywords

**Example Rules**

```text
If description contains "GROCERY" → Groceries
If description contains "GAS STATION" → Transportation
If description contains "NETFLIX" → Entertainment
If amount > 2000 AND description contains "SALARY" → Income
```

### Manual Category Review

After import, review and adjust categories:

1. **Bulk Category Changes**
   - Select multiple transactions
   - Apply category changes to all
   - Save for future auto-categorization

2. **Split Transactions**
   - Handle multi-category purchases
   - Split single transactions into parts
   - Maintain accurate category tracking

## 🏦 Account Setup

### Matching Imported Accounts

#### Create Accounts First

Before importing, set up your accounts in TruLedgr:

```text
Account Setup:
- Primary Checking: $2,500 starting balance
- Savings Account: $10,000 starting balance  
- Credit Card: -$1,250 starting balance
- Investment Account: $25,000 starting balance
```

#### Balance Reconciliation

After import, verify account balances:

1. **Check Starting Balances**
   - Compare with bank statements
   - Adjust for missing transactions
   - Account for pending transactions

2. **Verify Ending Balances**
   - Ensure math adds up correctly
   - Look for duplicate transactions
   - Check for missing transfers

## 📊 Budget Migration

### Transferring Budget Data

#### From Percentage-Based Apps

Convert percentage allocations to dollar amounts:

```text
Monthly Income: $5,000

Mint Percentages → TruLedgr Amounts:
Housing: 30% → $1,500
Food: 15% → $750
Transportation: 10% → $500
Savings: 20% → $1,000
```

#### From Envelope Systems

Convert envelope amounts directly:

```text
YNAB Envelopes → TruLedgr Categories:
Rent: $1,200 → Housing: $1,200
Groceries: $400 → Food: $400
Gas: $200 → Transportation: $200
```

### Historical Budget Performance

Import historical budget vs. actual data:

1. **Calculate Averages**
   - 6-month spending averages per category
   - Seasonal adjustment factors
   - Growth trend analysis

2. **Set Realistic Budgets**
   - Base on historical data
   - Adjust for life changes
   - Build in improvement goals

## 🔍 Data Validation

### Common Import Issues

#### Duplicate Transactions

**Detection Methods**

- Same date, amount, and description
- Similar amounts within 24 hours
- Identical merchant and amount

**Resolution Steps**

1. Review flagged duplicates
2. Merge or delete duplicates
3. Verify account balances remain correct

#### Missing Transactions

**Identification**

- Gaps in transaction dates
- Balance discrepancies
- Missing recurring transactions

**Resolution**

- Check original source for missing data
- Manually add missing transactions
- Verify with bank statements

#### Category Mismatches

**Common Issues**

- Personal vs. business expenses mixed
- Transfer vs. expense categorization
- Income vs. expense classification

**Fixes**

- Review large or unusual transactions
- Check transfer categorization
- Verify income classification

### Quality Assurance Checklist

#### Pre-Import Verification

- [ ] Data file opens correctly in spreadsheet
- [ ] All required columns present
- [ ] Date format consistent
- [ ] No obvious duplicates
- [ ] Amount format correct

#### Post-Import Verification

- [ ] Account balances match bank statements
- [ ] Transaction count makes sense
- [ ] No major category appears empty
- [ ] Income and expenses balanced
- [ ] Transfer transactions paired correctly

## 🛠️ Troubleshooting

### Common Problems and Solutions

#### File Format Issues

**Problem: File won't upload**

```text
Solutions:
- Check file size (max 50MB)
- Verify file format (CSV, XLSX, QIF)
- Remove special characters from filename
- Save as UTF-8 encoding
```

**Problem: Date parsing errors**

```text
Solutions:
- Standardize date format in spreadsheet
- Use YYYY-MM-DD format
- Remove any text in date columns
- Check for empty date cells
```

#### Data Mapping Issues

**Problem: Categories not mapping correctly**

```text
Solutions:
- Review category names for typos
- Create custom mapping rules
- Use bulk edit after import
- Set up keyword rules for future
```

**Problem: Amounts appearing wrong**

```text
Solutions:
- Check positive/negative settings
- Verify decimal point format
- Remove currency symbols
- Check for extra spaces in amounts
```

### Getting Help with Imports

#### Import Support Resources

- **Video Tutorials**: Step-by-step import guides
- **Template Files**: Properly formatted examples
- **Community Forum**: User-shared import tips
- **Direct Support**: Help with complex imports

#### Professional Import Service

For complex migrations:

- **Data Cleanup Service**: Professional data preparation
- **Custom Import Scripts**: Automated import solutions  
- **Migration Consulting**: Expert guidance for large datasets
- **Quality Assurance**: Professional data validation

## 📱 Mobile Import Options

### Mobile-Friendly Import

#### Photo Receipt Import

- Take photos of receipts
- Automatic text recognition
- Category suggestion
- Quick transaction creation

#### Email Import

- Forward bank notification emails
- Automatic transaction parsing
- Direct import to TruLedgr
- Category auto-assignment

### Sync with Mobile Banking

Set up automatic syncing:

- Bank API connections
- Real-time transaction updates
- Automatic categorization
- Balance synchronization

## 📈 Post-Import Optimization

### Data Enhancement

#### Transaction Enhancement

1. **Add Missing Details**
   - Expand transaction descriptions
   - Add location data where relevant
   - Include receipt photos
   - Add notes for context

2. **Category Refinement**
   - Split overly broad categories
   - Merge similar categories
   - Create subcategories
   - Set up auto-categorization rules

#### Budget Optimization

1. **Historical Analysis**
   - Review 6-12 months of spending
   - Identify spending patterns
   - Note seasonal variations
   - Calculate realistic averages

2. **Goal Setting**
   - Set reduction targets for overspent categories
   - Increase savings allocations gradually
   - Plan for irregular expenses
   - Set family financial goals

## 🎯 Success Tips

### Make the Most of Your Import

#### Start Fresh Mindset

- Use import as opportunity to review all spending
- Question old categorization systems
- Optimize for your current life situation
- Set new, realistic financial goals

#### Continuous Improvement

- Review categorization weekly for first month
- Adjust budgets based on imported data insights
- Set up automated rules to reduce manual work
- Regular data quality reviews

## 📚 Next Steps

After successful data import:

1. **[Budget Optimization](budget-optimization.md)** - Use historical data for better budgeting
2. **[Advanced Categorization](advanced-categories.md)** - Set up sophisticated category systems
3. **[Goal Setting](goal-setting.md)** - Use imported data to set realistic financial goals
4. **[Automation Setup](automation.md)** - Reduce manual transaction entry

Your financial history is now in TruLedgr - time to build your financial future! 📊
