#!/usr/bin/env python3
"""
Development Server Orchestrator

Starts all development services for TruLedgr:
- FastAPI backend server
- Vue.js dashboard frontend
- Vue.js landing page frontend
- Documentation server (optional)
"""

import asyncio
import subprocess
import sys
import os
import signal
from pathlib import Path
from typing import List, Optional
import threading
import time

# Get the workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent

class DevServer:
    """Manages multiple development servers concurrently."""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.shutdown_event = threading.Event()
        
    def start_backend(self) -> subprocess.Popen:
        """Start the FastAPI backend server."""
        print("🔧 Starting FastAPI backend server...")
        
        # Use the virtual environment's uvicorn
        venv_uvicorn = WORKSPACE_ROOT / ".venv" / "bin" / "uvicorn"
        
        if venv_uvicorn.exists():
            cmd = [
                str(venv_uvicorn),
                "api.main:app",
                "--reload",
                "--host", "0.0.0.0",
                "--port", "8000"
            ]
        else:
            cmd = [
                sys.executable, "-m", "uvicorn",
                "api.main:app",
                "--reload",
                "--host", "0.0.0.0",
                "--port", "8000"
            ]
            
        return subprocess.Popen(
            cmd,
            cwd=WORKSPACE_ROOT,
            env={**os.environ, "PYTHONPATH": str(WORKSPACE_ROOT)}
        )
    
    def start_dashboard(self) -> Optional[subprocess.Popen]:
        """Start the Vue.js dashboard frontend."""
        print("📊 Starting dashboard frontend...")
        
        dashboard_dir = WORKSPACE_ROOT / "dash"
        if not dashboard_dir.exists():
            print("⚠️ Dashboard directory not found, skipping...")
            return None
            
        cmd = ["npm", "run", "dev:dash"]
        return subprocess.Popen(cmd, cwd=WORKSPACE_ROOT)
    
    def start_landing(self) -> Optional[subprocess.Popen]:
        """Start the Vue.js landing page frontend."""
        print("🌐 Starting landing page frontend...")
        
        landing_dir = WORKSPACE_ROOT / "landing"
        if not landing_dir.exists():
            print("⚠️ Landing page directory not found, skipping...")
            return None
            
        cmd = ["npm", "run", "dev:landing"]
        return subprocess.Popen(cmd, cwd=WORKSPACE_ROOT)
    
    def start_docs(self) -> Optional[subprocess.Popen]:
        """Start the MkDocs documentation server."""
        print("📚 Starting documentation server...")
        
        if not (WORKSPACE_ROOT / "mkdocs.yml").exists():
            print("⚠️ MkDocs config not found, skipping docs server...")
            return None
            
        cmd = [sys.executable, "-m", "mkdocs", "serve", "--dev-addr", "0.0.0.0:8001"]
        return subprocess.Popen(cmd, cwd=WORKSPACE_ROOT)
    
    def start_all(self, include_docs: bool = False):
        """Start all development servers."""
        print("🚀 Starting all development servers...")
        print("=" * 50)
        
        # Start backend
        backend_proc = self.start_backend()
        if backend_proc:
            self.processes.append(backend_proc)
        
        # Start frontend services
        dashboard_proc = self.start_dashboard()
        if dashboard_proc:
            self.processes.append(dashboard_proc)
            
        landing_proc = self.start_landing()
        if landing_proc:
            self.processes.append(landing_proc)
        
        # Optionally start docs
        if include_docs:
            docs_proc = self.start_docs()
            if docs_proc:
                self.processes.append(docs_proc)
        
        print("=" * 50)
        print("✅ Development servers started!")
        print("🔧 Backend API: http://localhost:8000")
        print("📊 Dashboard: http://localhost:5173")
        print("🌐 Landing Page: http://localhost:5174")
        if include_docs:
            print("📚 Documentation: http://localhost:8001")
        print("=" * 50)
        print("Press Ctrl+C to stop all servers...")
    
    def stop_all(self):
        """Stop all running processes."""
        print("\n🛑 Stopping all development servers...")
        
        for proc in self.processes:
            try:
                proc.terminate()
                # Give process a chance to terminate gracefully
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                proc.kill()
                proc.wait()
            except Exception as e:
                print(f"⚠️ Error stopping process: {e}")
        
        self.processes.clear()
        print("✅ All servers stopped.")
    
    def wait_for_interrupt(self):
        """Wait for keyboard interrupt and handle shutdown."""
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
                # Check if any processes have died
                for proc in self.processes[:]:  # Copy list to avoid modification during iteration
                    if proc.poll() is not None:
                        print(f"⚠️ Process {proc.pid} has exited")
                        self.processes.remove(proc)
                        
        except KeyboardInterrupt:
            self.stop_all()
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            self.stop_all()


def main():
    """Main entry point for development server orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Start TruLedgr development servers")
    parser.add_argument("--docs", action="store_true", help="Include documentation server")
    parser.add_argument("--backend-only", action="store_true", help="Start only the backend server")
    parser.add_argument("--frontend-only", action="store_true", help="Start only frontend servers")
    
    args = parser.parse_args()
    
    dev_server = DevServer()
    
    # Set up signal handling
    def signal_handler(signum, frame):
        dev_server.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.backend_only:
            print("🔧 Starting backend only...")
            proc = dev_server.start_backend()
            if proc:
                dev_server.processes.append(proc)
        elif args.frontend_only:
            print("🌐 Starting frontend only...")
            dashboard_proc = dev_server.start_dashboard()
            if dashboard_proc:
                dev_server.processes.append(dashboard_proc)
            landing_proc = dev_server.start_landing()
            if landing_proc:
                dev_server.processes.append(landing_proc)
        else:
            dev_server.start_all(include_docs=args.docs)
        
        dev_server.wait_for_interrupt()
        
    except Exception as e:
        print(f"💥 Failed to start development servers: {e}")
        dev_server.stop_all()
        sys.exit(1)


if __name__ == "__main__":
    main()
