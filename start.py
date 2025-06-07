#!/usr/bin/env python3
"""
Startup script for Physics Before Newton - Proof Analyzer
"""

import os
import sys
import subprocess
import webbrowser
import threading
import time
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found")
        return False
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  .env file not found. Please create one from env_example.txt")
        print("   Copy env_example.txt to .env and add your OpenAI API key")
        return False
    
    # Check if React frontend exists
    if not Path("react-frontend").exists():
        print("❌ React frontend directory not found")
        return False
    
    # Check if Node.js is available
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Node.js is not installed or not available")
            return False
        print(f"✅ Node.js found: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js is not installed")
        return False
    
    print("✅ Requirements check passed")
    return True

def install_dependencies():
    """Install Python and Node.js dependencies"""
    print("📦 Installing dependencies...")
    
    # Install Python dependencies
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              check=True, capture_output=True, text=True)
        print("✅ Python dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    
    # Install Node.js dependencies
    react_frontend_path = Path("react-frontend")
    if react_frontend_path.exists():
        print("📦 Installing React dependencies...")
        try:
            result = subprocess.run(["npm", "install"], 
                                  cwd=react_frontend_path, 
                                  check=True, capture_output=True, text=True)
            print("✅ React dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install React dependencies: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return False
    
    return True

def start_backend_server():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    
    # Change to backend directory
    backend_path = Path("backend")
    if not backend_path.exists():
        print("❌ Backend directory not found")
        return False
    
    # Import and run the server
    sys.path.insert(0, str(backend_path))
    
    try:
        import uvicorn
        from main import app
        
        print("✅ Backend server starting on http://localhost:8000")
        
        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
    except ImportError as e:
        print(f"❌ Failed to import server modules: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Backend server error: {e}")
        return False

def start_react_frontend():
    """Start the React frontend development server"""
    print("⚛️  Starting React frontend...")
    
    react_frontend_path = Path("react-frontend")
    if not react_frontend_path.exists():
        print("❌ React frontend directory not found")
        return False
    
    try:
        # Start React development server
        result = subprocess.run(["npm", "start"], 
                              cwd=react_frontend_path,
                              check=False)  # Don't check return code as npm start runs indefinitely
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 React frontend stopped by user")
        return True
    except Exception as e:
        print(f"❌ React frontend error: {e}")
        return False

def start_servers():
    """Start both backend and frontend servers concurrently"""
    print("🚀 Starting both servers...")
    print("🌐 React app will be available at http://localhost:3000")
    print("🔧 Backend API available at http://localhost:8000")
    print("💡 Press Ctrl+C to stop both servers")
    print("\n" + "="*50)
    
    # Function to start backend in a thread
    def backend_thread():
        start_backend_server()
    
    # Function to start frontend in a thread
    def frontend_thread():
        start_react_frontend()
    
    # Start backend server in a separate thread
    backend_t = threading.Thread(target=backend_thread, daemon=True)
    backend_t.start()
    
    # Give backend time to start
    time.sleep(3)
    
    # Try to open browser automatically to React app
    try:
        webbrowser.open("http://localhost:3000")
    except:
        pass
    
    # Start frontend server in main thread
    try:
        start_react_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Servers stopped by user")
        return True

def main():
    """Main startup function"""
    print("🧪 Physics Before Newton - Proof Analyzer (React Version)")
    print("="*60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start both servers
    start_servers()

if __name__ == "__main__":
    main() 