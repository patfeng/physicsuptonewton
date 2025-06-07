#!/usr/bin/env python3
"""
Startup script for Physics Before Newton - Proof Analyzer
"""

import os
import sys
import subprocess
import webbrowser
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
    
    print("✅ Requirements check passed")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting server...")
    
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
        
        print("✅ Server starting on http://localhost:8000")
        print("🌐 Open http://localhost:8000/static/index.html in your browser")
        print("💡 Press Ctrl+C to stop the server")
        print("\n" + "="*50)
        
        # Try to open browser automatically
        try:
            webbrowser.open("http://localhost:8000/static/index.html")
        except:
            pass
        
        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
    except ImportError as e:
        print(f"❌ Failed to import server modules: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False

def main():
    """Main startup function"""
    print("🧪 Physics Before Newton - Proof Analyzer")
    print("="*50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 