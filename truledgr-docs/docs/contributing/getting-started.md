## Getting Started

### Prerequisites

Before you begin, ensure you have the following tools installed:

- **Git** (version 2.0 or higher)
- **Python** (version 3.11 or higher)
- **Node.js** (version 18 or higher)
- **Docker** (for containerized development)
- **Xcode** (for iOS development, macOS only)
- **Android Studio** (for Android development)

### Initial Setup

1. **Fork the Repository**

   ```bash
   # Fork the repository on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/TruLedgr.git
   cd truledgr
   ```

2. **Set Up Remote Repositories**

   ```bash
   # Add the original repository as upstream
   git remote add upstream https://github.com/McGuireTechnology/TruLedgr.git
   
   # Verify your remotes
   git remote -v
   ```

3. **Install Dependencies**

   ```bash
   # API dependencies
   cd truledgr-api
   pip install -e ".[dev]"
   
   # Frontend dependencies
   cd ../truledgr-dash
   npm install
   
   # Landing page dependencies
   cd ../recycle/landing
   npm install
   
   # Documentation dependencies
   cd ../truledgr-docs
   pip install -r requirements.txt
   ```