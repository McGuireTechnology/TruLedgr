# Core Entities

Core entities are the fundamental building blocks of the TruLedgr accounting system. They represent the primary objects and concepts used to record, organize, and report financial data. Each core entity models a real-world concept such as an account, transaction, institution, or user, and together they form the structure that supports double-entry bookkeeping, reporting, and collaboration within the platform.

## Accounts

### Ledger Accounts
Represents any account in the general ledger (e.g., cash, revenue, expense, liability, equity). Each ledger account has a type (asset, liability, equity, income, expense) and may include additional metadata such as subtype or category. All financial activity is ultimately posted to ledger accounts. Institution accounts and payees are specialized types of ledger accounts.

**Examples of Ledger Accounts:**
- Cash
- Checking Account
- Accounts Receivable
- Accounts Payable
- Sales Revenue
- Office Supplies Expense
- Owner’s Equity
- Credit Card Payable
- Rent Expense
- Interest Income

### Institution Accounts
Represents real-world accounts at financial institutions (e.g., checking, savings, credit card accounts at banks or credit unions). Institution accounts are a specialized type of ledger account, typically of type "asset" or "liability", and may include bank-specific metadata (bank name, account number, etc.). Used for reconciliation with bank feeds and statements.

**Examples of Institution Accounts:**
- Chase Checking Account
- Bank of America Savings Account
- Wells Fargo Credit Card
- PayPal Business Account
- American Express Platinum Card
- Local Credit Union Money Market Account

### Payees
Represents external parties or entities involved in transactions (e.g., vendors, customers, merchants like "Starbucks"). Payees are a specialized type of ledger account, allowing you to track who money is paid to or received from, and can be linked to transactions for reporting and categorization.

**Examples of Payees:**
- Starbucks
- Amazon
- ACME Corp.
- John Doe
- City of San Francisco

## Transactions
Represents a financial event, consisting of two or more entries (debits and credits). Transactions are the atomic unit of accounting activity.

**Examples of Transactions:**
- Starbucks purchase on 2025-06-05
- Payroll deposit for May 2025
- Rent payment for June 2025
- Invoice payment from ACME Corp.

## Special Core Entities

Special core entities are foundational to the TruLedgr system but serve unique roles that go beyond standard accounting records. They are essential for authentication, authorization, collaboration, and organizational structure. Teams and Users, for example, enable multi-user access, permissions, and group-based collaboration across the platform. These entities are linked to many records to manage ownership, access control, and participation in financial workflows.

### Teams
Represents groups of users who collaborate on the same set of ledgers, accounts, or financial data. Useful for organizations with multiple departments or business units.

**Examples of Teams:**
- Accounting Department
- Engineering Team
- Marketing Group
- Project Alpha Team

### Users
Individuals who use the system. Users may belong to teams, own accounts, and initiate or approve transactions.

**Examples of Users:**
- Alice Smith
- Bob Johnson
- Carol Lee
- David Kim

## Metadata Core Entities

Metadata core entities are supplemental objects that provide additional context, organization, or classification to the core accounting data. While not essential to the double-entry bookkeeping structure, they enhance the system by enabling flexible grouping, filtering, reporting, and documentation. Examples include categories for classifying transactions, tags for labeling records, and documents for attaching supporting files to financial activity.

### Categories
Used to classify or group accounts and transactions for reporting and analytics. Categories help organize financial data (e.g., "Utilities", "Payroll", "Office Supplies").

**Examples of Categories:**
- Utilities
- Payroll
- Office Supplies
- Meals & Entertainment
- Travel

### Documents
Represents files or digital records attached to transactions, accounts, or other entities in the system. Documents provide supporting evidence for financial activity, such as receipts, invoices, contracts, or statements. They help with auditing, compliance, and record-keeping by linking source materials to accounting records.

**Examples of Documents:**
- PDF receipt for a Starbucks purchase
- Scanned invoice from ACME Corp.
- Bank statement for May 2025
- Photo of a signed contract
- Payroll report in CSV format
- Image of a utility bill

### Tags
Labels that can be attached to accounts, transactions, or entries for flexible grouping, filtering, and reporting (e.g., "tax-deductible", "project-X").

**Examples of Tags:**
- tax-deductible
- project-X
- reimbursable
- recurring
- urgent