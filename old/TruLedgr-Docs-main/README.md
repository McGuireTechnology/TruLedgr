# TruLedgr-Docs

> **Live Documentation:** [https://docs.truledgr.app](https://docs.truledgr.app)

TruLedgr-Docs is the documentation repository for the TruLedgr project. It contains all the guides, API references, and setup instructions for users and developers working with TruLedgr. The documentation is built using MkDocs and is intended to provide clear, accessible, and up-to-date information about the TruLedgr ecosystem.


## Setup Instructions

**macOS/Linux (zsh/bash):**
```sh
# Clone the TruLedgr-Docs repository from GitHub
git clone https://github.com/TruLedgr/TruLedgr-Docs.git
cd TruLedgr-Docs
```

**Windows (PowerShell):**
```powershell
# Clone the TruLedgr-Docs repository from GitHub
git clone https://github.com/TruLedgr/TruLedgr-Docs.git
Set-Location TruLedgr-Docs
```

## Python Environment Setup

**macOS/Linux (zsh/bash):**
```sh
# Create a Python virtual environment in the .venv folder
python3 -m venv .venv
# Activate the virtual environment
source .venv/bin/activate
# Install required Python packages
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
# Create a Python virtual environment in the .venv folder
python -m venv .venv
# Activate the virtual environment
.venv\Scripts\Activate.ps1
# Install required Python packages
pip install -r requirements.txt
```

## Running the Local Development Server

To preview the documentation locally, activate your virtual environment and run:

```sh
mkdocs serve -a 127.0.0.1:8001
```

Note: The `-a` option sets the address and port. It is optional—if omitted, MkDocs will use the default port 8000 (http://127.0.0.1:8000/).

This will start a local server (usually at http://127.0.0.1:8001/) where you can view your docs in your browser.

## Building Static Documentation

To generate a static site from your Markdown files, activate your virtual environment and run:

```sh
mkdocs build
```

This will create a `site/` directory containing the static HTML files for your documentation, which you can deploy to any web server or GitHub Pages.

## Deployment with GitHub Actions

The documentation is automatically deployed to [https://docs.truledgr.app](https://docs.truledgr.app) using GitHub Actions and GitHub Pages.

### How it works

- On every push to the `main` branch, a GitHub Actions workflow builds the documentation using MkDocs.
- The generated static site is deployed to the `gh-pages` branch and published via GitHub Pages.
- The live documentation is available at: [https://docs.truledgr.app](https://docs.truledgr.app)

No manual deployment steps are required—just push your changes to `main` and they will be published automatically.
