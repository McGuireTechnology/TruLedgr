# TruLedgr-API

## Setup Instructions

**macOS/Linux (zsh/bash):**
```sh
# Clone the TruLedgr-API repository from GitHub
git clone https://github.com/TruLedgr/TruLedgr-API.git
cd TruLedgr-API
```

**Windows (PowerShell):**
```powershell
# Clone the TruLedgr-API repository from GitHub
git clone https://github.com/TruLedgr/TruLedgr-API.git
Set-Location TruLedgr-API
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

To start the FastAPI development server locally, activate your virtual environment and run:

```sh
uvicorn main:app --reload --port 8002
```

Note: The `--port` option is optional. If omitted, Uvicorn will use the default port 8000 (http://127.0.0.1:8000/).

This will start the API server with live reloading enabled. By default, it will be available at http://127.0.0.1:8002/.

You can access the interactive API documentation at:
- Swagger UI: http://127.0.0.1:8002/docs
- ReDoc: http://127.0.0.1:8002/redoc
