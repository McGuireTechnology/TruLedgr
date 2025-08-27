#!/usr/bin/env python3
"""
TruLedgr Component Launchers

Individual launchers for TruLedgr components:
- API server (FastAPI backend)
- Documentation server (MkDocs)
- dash (Vue.js frontend via npm)
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

# Get the workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent


def start_api():
    """Launch the FastAPI backend server with uvicorn and auto-reload."""
    print("🔧 Starting TruLedgr API Server...")
    print("=" * 40)
    
    # Use the virtual environment's uvicorn if available
    venv_uvicorn = WORKSPACE_ROOT / ".venv" / "bin" / "uvicorn"
    
    if venv_uvicorn.exists():
        cmd = [str(venv_uvicorn)]
    else:
        cmd = [sys.executable, "-m", "uvicorn"]
    
    # Default command: uvicorn api.main:app --reload
    cmd.extend([
        "api.main:app",
        "--reload"
    ])
    
    print(f"🚀 API Server: http://127.0.0.1:8000")
    print(f"📖 API Docs: http://127.0.0.1:8000/docs")
    print("=" * 40)
    
    try:
        subprocess.run(
            cmd,
            cwd=WORKSPACE_ROOT,
            env={**os.environ, "PYTHONPATH": str(WORKSPACE_ROOT)}
        )
    except KeyboardInterrupt:
        print("\n🛑 API server stopped.")
    except Exception as e:
        print(f"💥 Failed to start API server: {e}")
        sys.exit(1)


def start_docs():
    """Launch the MkDocs documentation server."""
    print("📚 Starting TruLedgr Documentation Server...")
    print("=" * 45)
    
    # Check if MkDocs is available
    try:
        subprocess.run([sys.executable, "-c", "import mkdocs"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️ MkDocs not found. Installing documentation dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[docs]"], 
                          cwd=WORKSPACE_ROOT, check=True)
            print("✅ Documentation dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"💥 Failed to install documentation dependencies: {e}")
            sys.exit(1)
    
    # Simple command: mkdocs serve
    cmd = [sys.executable, "-m", "mkdocs", "serve"]
    
    print(f"🚀 Documentation Server: http://127.0.0.1:8000")
    print("=" * 45)
    
    try:
        subprocess.run(cmd, cwd=WORKSPACE_ROOT)
    except KeyboardInterrupt:
        print("\n🛑 Documentation server stopped.")
    except Exception as e:
        print(f"💥 Failed to start documentation server: {e}")
        sys.exit(1)


def start_dash():
    """Launch the Vue.js dash frontend."""
    print("📊 Starting TruLedgr dash...")
    print("=" * 35)
    
    # Check if package.json exists in workspace root
    package_json = WORKSPACE_ROOT / "package.json"
    if not package_json.exists():
        print("💥 package.json not found in workspace root!")
        sys.exit(1)
    
    # Check if dash directory exists
    dash_dir = WORKSPACE_ROOT / "dash"
    if not dash_dir.exists():
        print("💥 dash directory not found!")
        print(f"Expected: {dash_dir}")
        sys.exit(1)
    
    # Run npm dev from workspace root (where node_modules is)
    cmd = ["npm", "run", "dev:dash"]
    
    print("🚀 dash: http://localhost:5173")
    print("=" * 35)
    
    try:
        subprocess.run(cmd, cwd=WORKSPACE_ROOT)
    except KeyboardInterrupt:
        print("\n🛑 dash stopped.")
    except Exception as e:
        print(f"💥 Failed to start dash: {e}")
        sys.exit(1)


def start_landing():
    """Launch the Vue.js landing page frontend."""
    print("🌐 Starting TruLedgr Landing Page...")
    print("=" * 37)
    
    # Check if package.json exists in workspace root
    package_json = WORKSPACE_ROOT / "package.json"
    if not package_json.exists():
        print("💥 package.json not found in workspace root!")
        sys.exit(1)
    
    # Check if landing directory exists
    landing_dir = WORKSPACE_ROOT / "landing"
    if not landing_dir.exists():
        print("💥 Landing directory not found!")
        print(f"Expected: {landing_dir}")
        sys.exit(1)
    
    # Run npm dev from workspace root (where node_modules is)
    # Note: You may need to add a specific script for landing in package.json
    cmd = ["npm", "run", "dev:landing"]  # Assuming you'll add this script
    
    print("🚀 Landing Page: http://localhost:5174")
    print("=" * 37)
    
    try:
        subprocess.run(cmd, cwd=WORKSPACE_ROOT)
    except KeyboardInterrupt:
        print("\n🛑 Landing page stopped.")
    except Exception as e:
        print(f"💥 Failed to start landing page: {e}")
        print("💡 Make sure you have a 'dev:landing' script in package.json")
        sys.exit(1)


if __name__ == "__main__":
    # This allows the script to be called directly for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python launchers.py [api|docs|dash|landing]")
        sys.exit(1)
    
    component = sys.argv[1]
    sys.argv = sys.argv[1:]  # Remove the component name from argv
    
    if component == "api":
        start_api()
    elif component == "docs":
        start_docs()
    elif component == "dash":
        start_dash()
    elif component == "landing":
        start_landing()
    else:
        print(f"Unknown component: {component}")
        print("Available components: api, docs, dash, landing")
        sys.exit(1)
