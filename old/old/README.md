# TruLedgr

TruLedgr is a modern, open-source personal finance management platform designed for clarity, accountability, and control. It combines the flexibility of custom tracking with the rigor of double-entry bookkeeping — built by developers, for individuals and families who want to own their financial data.

## 🚀 Key Features

- **Double-Entry Bookkeeping**  
  Accurate, auditable financial records using a proven accounting model.

- **Automatic Transaction Syncing**  
  Integrates with financial aggregators (Plaid, Finicity, OFX/QFX import) to keep your ledger up to date.

- **Budgeting & Projections**  
  Build a budget with real transaction data and see how your decisions affect the future.

- **Custom Categories & Tags**  
  Organize your financial world in a way that makes sense to you — not your bank.

- **Structured Notes & Attachments**  
  Attach receipts, notes, or contracts to specific entries. Build a financial paper trail.

- **Self-Host or Use the Cloud**  
  Host it yourself or use our managed version (coming soon) — your data, your choice.

## 📦 Tech Stack

- **Frontend:** Next.js + Tailwind CSS  
- **Backend:** FastAPI (Python)  
- **Database:** PostgreSQL (SQLite for local dev)  
- **Auth:** OAuth 2.0 (Google, Apple, etc.)  
- **Sync APIs:** FinanceKit, Plaid, OFX/QFX  

## 🛠 Installation (Local Dev)

```bash
git clone https://github.com/McGuireTechnology/TruLedgr.git
cd TruLedgr
cp .env.example .env
# Update with your keys and settings
docker-compose up --build
```

The app will be accessible at [http://localhost:3000](http://localhost:3000).


## 🔐 Security

TruLedgr is committed to secure financial data management. Key practices include:

- Minimal permissions for third-party integrations
- Encrypted secrets and vault-style credential storage
- Regular security audits planned as the platform matures

We welcome security-related issues and responsible disclosure.

## 📚 Documentation

Official documentation is hosted at:  
[https://docs.truledgr.app](https://docs.truledgr.app)

Contributions are welcome! Docs are powered by MkDocs and live in the `/docs` directory.

## 🤝 Contributing

We welcome contributors at any level.

- Fork the repo and make your changes
- Submit a PR with a clear title and description
- Respect coding standards and security practices

See `CONTRIBUTING.md` for more detail.

## 📜 License

This project is licensed under the MIT License.  
You're free to use, modify, and share — but attribution is appreciated.

## 🧭 Roadmap

- Income forecasting tools
- Multi-user shared ledgers
- Tax document vault
- iOS/Android app
- Managed cloud offering (TruLedgr Cloud)

Follow issues and milestones for progress.

## 👤 Maintainer

Built and maintained by McGuire Technology, LLC 
If TruLedgr helps you reclaim control of your finances, consider starring the repo!
