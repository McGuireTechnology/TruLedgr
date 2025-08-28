# Managing Finances

Learn how to effectively track your income and expenses, organize transactions, and maintain accurate financial records in TruLedgr.

## 💰 Transaction Management

### Understanding Transaction Types

TruLedgr supports three main transaction types:

#### 💸 Expenses
Money that flows out of your accounts:

- **Daily Expenses**: Groceries, coffee, gas, lunch
- **Bills**: Rent, utilities, phone, internet
- **Shopping**: Clothing, electronics, household items
- **Services**: Haircuts, repairs, subscriptions

#### 💵 Income  
Money that flows into your accounts:

- **Salary**: Regular paychecks from employment
- **Freelance**: Project-based or contract work
- **Investments**: Dividends, interest, capital gains
- **Other**: Gifts, refunds, side hustles

#### 🔄 Transfers
Moving money between your own accounts:

- **Savings**: Moving money to/from savings account
- **Credit Cards**: Paying off credit card balances
- **Investment**: Transferring to investment accounts
- **Cash**: ATM withdrawals or deposits

### Adding Transactions

#### Quick Entry Method

For fast transaction entry:

1. **Use the dashboard widget** for immediate access
2. **Fill essential fields only**:
   - Amount
   - Description (brief)
   - Category
3. **Save and continue** adding more transactions

#### Detailed Entry Method

For comprehensive tracking:

1. **Go to Transactions** → **Add New**
2. **Complete all fields**:
   - **Amount**: Exact transaction amount
   - **Description**: Detailed description
   - **Category**: Specific category
   - **Date & Time**: Exact transaction time
   - **Location**: Where the transaction occurred (optional)
   - **Notes**: Additional context or details
   - **Tags**: Custom labels for filtering (optional)

#### Bulk Import

For importing existing data:

1. **Go to Settings** → **Import Data**
2. **Download the CSV template**
3. **Fill in your transactions** following the format
4. **Upload your completed file**
5. **Review and confirm** the imported transactions

!!! tip "Import Tips"
    - Export data from your bank or previous app as CSV
    - Match the required column headers exactly
    - Review categories after import to ensure accuracy

### Editing and Managing Transactions

#### Editing Transactions

1. **Find the transaction** in your transaction list
2. **Click the transaction** to open details
3. **Click "Edit"** to modify fields
4. **Save changes** when complete

#### Deleting Transactions

1. **Open the transaction** you want to delete
2. **Click "Delete"** (usually a trash icon)
3. **Confirm deletion** when prompted

!!! warning "Deletion Warning"
    Deleted transactions cannot be recovered. Consider editing instead of deleting when possible.

#### Bulk Operations

Select multiple transactions to:

- **Change categories** for multiple transactions at once
- **Delete multiple transactions** 
- **Export selected transactions** to CSV
- **Apply tags** to multiple transactions

## 🏷️ Advanced Categorization

### Category Hierarchy

Organize categories with sub-categories:

```
🍕 Food & Dining
  ├── Restaurants
  ├── Groceries  
  ├── Coffee & Snacks
  └── Takeout

🚗 Transportation
  ├── Gas
  ├── Public Transit
  ├── Parking
  └── Car Maintenance
```

### Creating Sub-Categories

1. **Go to Settings** → **Categories**
2. **Select a parent category**
3. **Click "Add Sub-Category"**
4. **Name and configure** the sub-category

### Smart Categories

TruLedgr can suggest categories based on:

- **Transaction descriptions**: Recognizes common merchants
- **Amount patterns**: Similar amounts often have similar categories  
- **Previous categorization**: Learns from your patterns
- **Merchant data**: Recognizes common store names

### Category Rules

Set up automatic categorization:

1. **Go to Settings** → **Category Rules**
2. **Click "Add Rule"**
3. **Set conditions**:
   - Description contains "Starbucks" → Coffee & Snacks
   - Amount equals "1200.00" → Rent
   - Description contains "Shell" OR "Chevron" → Gas

## 🔍 Transaction Search and Filtering

### Basic Search

Use the search bar to find transactions by:

- **Description text**: "grocery", "coffee", "rent"
- **Amount**: "25.50", ">100", "<50"
- **Category names**: "food", "transport"
- **Date ranges**: "last month", "2024"

### Advanced Filters

Apply multiple filters simultaneously:

#### Date Filters
- **This Week/Month/Year**
- **Last 30/60/90 days**
- **Custom date range**
- **Specific dates**

#### Amount Filters
- **Exact amount**: $25.50
- **Amount range**: $20-$30
- **Greater than**: >$100
- **Less than**: <$50

#### Category Filters
- **Single category**: Food & Dining
- **Multiple categories**: Food + Entertainment
- **Exclude categories**: All except Income

#### Type Filters
- **Expenses only**
- **Income only**
- **Transfers only**
- **Multiple types**

### Saved Searches

Save frequently used search criteria:

1. **Apply your filters**
2. **Click "Save Search"**
3. **Name your search** (e.g., "Large Expenses", "Food Spending")
4. **Access saved searches** from the Quick Filters menu

## 📊 Transaction Organization

### Sorting Options

Sort transactions by:

- **Date**: Newest or oldest first
- **Amount**: Highest or lowest first
- **Category**: Alphabetical order
- **Description**: Alphabetical order
- **Type**: Expenses, income, transfers

### List Views

Choose your preferred transaction display:

#### Compact View
- Shows more transactions per page
- Essential information only
- Good for quick scanning

#### Detailed View  
- Shows all transaction fields
- Better for reviewing and editing
- Includes notes and tags

#### Card View
- Visual cards for each transaction
- Good for mobile devices
- Easy to scan and interact with

### Grouping Transactions

Group transactions by:

- **Date**: Daily, weekly, monthly groupings
- **Category**: All food expenses together
- **Amount**: Group by spending ranges
- **Type**: Separate expenses, income, transfers

## 📱 Mobile Transaction Management

### Mobile-Optimized Features

#### Quick Add Widget
- Large, thumb-friendly buttons
- Voice input for descriptions (browser dependent)
- Camera for receipt capture (planned feature)

#### Offline Capability
- Add transactions without internet
- Automatic sync when connection restored
- Local storage for reliability

#### Mobile-Specific Tips

!!! tip "Mobile Best Practices"
    - **Pin to home screen**: Add TruLedgr as a web app
    - **Use voice input**: Speak transaction descriptions
    - **Quick categories**: Set up favorite categories for faster entry
    - **Batch entry**: Add multiple transactions during downtime

### Receipt Management (Coming Soon)

Planned features for receipt handling:

- **Photo capture**: Take pictures of receipts
- **OCR text extraction**: Automatically extract amount and merchant
- **Receipt storage**: Keep digital copies organized
- **Expense verification**: Match receipts to transactions

## 🔄 Recurring Transactions

### Setting Up Recurring Transactions

For regular expenses like rent, subscriptions, or salary:

1. **Create the initial transaction**
2. **Click "Make Recurring"**
3. **Set recurrence pattern**:
   - **Frequency**: Daily, weekly, monthly, yearly
   - **End date**: When to stop recurring
   - **Amount changes**: Fixed or variable amounts

### Managing Recurring Transactions

#### Automatic Processing
- **Auto-create**: Transactions created automatically
- **Review queue**: Option to review before adding
- **Notifications**: Alerts when recurring transactions are created

#### Manual Overrides
- **Skip instances**: Skip specific occurrences
- **Modify amounts**: Change amount for specific instances
- **Update patterns**: Change frequency or end date

## 📈 Transaction Analytics

### Quick Insights

View immediate transaction insights:

- **Daily spending average**
- **Most expensive transaction this month**
- **Most frequent category**
- **Spending velocity**: How fast you're spending this month

### Spending Patterns

Identify patterns in your spending:

- **Day of week analysis**: When do you spend the most?
- **Time of day patterns**: Morning, afternoon, evening spending
- **Seasonal trends**: Monthly and yearly patterns
- **Category evolution**: How your spending categories change over time

### Merchant Analysis

Track spending by merchant:

- **Top merchants**: Where you spend the most money
- **Merchant frequency**: How often you shop at each place
- **Average transaction size**: Typical spending per merchant
- **Merchant trends**: Increasing or decreasing spending patterns

## 🎯 Transaction Best Practices

### Daily Habits

#### Immediate Entry
- **Add transactions right away**: Don't wait until end of day
- **Use your phone**: Mobile entry is quick and convenient
- **Set reminders**: Phone alerts to review daily spending

#### Consistency
- **Standard descriptions**: Use consistent naming for similar transactions
- **Regular categories**: Stick to your category system
- **Complete information**: Fill in all relevant fields

### Weekly Reviews

Set aside time each week to:

1. **Review all transactions** for accuracy
2. **Correct any categorization errors**
3. **Add missing transactions** from receipts or memory
4. **Check for duplicate entries**
5. **Update recurring transactions** if needed

### Monthly Maintenance

Each month:

1. **Export transaction data** for backup
2. **Review and update categories** based on spending patterns  
3. **Clean up merchant names** for consistency
4. **Archive old transactions** if desired
5. **Update recurring transaction amounts** (rent increases, etc.)

## 🛠️ Troubleshooting

### Common Issues

#### Transactions Not Saving
- **Check internet connection**
- **Verify all required fields are filled**
- **Clear browser cache and try again**
- **Disable browser extensions that might interfere**

#### Duplicate Transactions
- **Use the duplicate detection tool**
- **Check import data for duplicates before uploading**
- **Review recurring transactions for overlaps**

#### Missing Transactions
- **Check all date ranges and filters**
- **Verify the transaction wasn't accidentally deleted**
- **Look in different categories in case of miscategorization**

### Data Recovery

If you accidentally delete or lose data:

1. **Check recently deleted items** (if feature available)
2. **Restore from export backup** if you have one
3. **Contact support** for assistance with data recovery
4. **Re-import from bank data** if available

## 🎉 Next Steps

Now that you're managing transactions effectively:

1. **[Set up budgets](budgets-analytics.md)** to control spending
2. **[Explore analytics](budgets-analytics.md)** to understand patterns
3. **[Configure family sharing](family-household.md)** if needed
4. **[Review security settings](security-privacy.md)** for data protection

Master these transaction management techniques to build a solid foundation for your financial tracking! 💪
