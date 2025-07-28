#!/usr/bin/env python3
"""
Setup script for Agent System
Installs dependencies and sets up the environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Agent System...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Install dependencies
    if not run_command("pip install -r requirements-minimal.txt", "Installing Python dependencies"):
        print("❌ Failed with minimal requirements, trying with pip install individually...")
        packages = [
            "fastapi", "langchain", "langchain-openai", "sqlalchemy", "pyodbc",
            "python-jose[cryptography]", "passlib[bcrypt]", "cryptography", 
            "httpx", "pydantic", "pydantic-settings", "python-multipart",
            "uvicorn[standard]", "slowapi", "python-dotenv", "pytest", "pytest-asyncio"
        ]
        
        failed_packages = []
        for package in packages:
            if not run_command(f"pip install {package}", f"Installing {package}"):
                failed_packages.append(package)
        
        if failed_packages:
            print(f"❌ Failed to install: {', '.join(failed_packages)}")
            print("Please install them manually or check your Python environment")
            sys.exit(1)
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("\n📝 Creating .env file from template...")
        try:
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                content = src.read()
                # Generate some default keys
                import secrets
                import base64
                
                secret_key = secrets.token_urlsafe(32)
                encryption_key = base64.b64encode(secrets.token_bytes(32)).decode()
                
                content = content.replace("your_openai_key_here", "")
                content = content.replace("your-super-secret-jwt-key-change-in-production", secret_key)
                content = content.replace("your-aes-key-here-32-bytes-base64-encoded", encryption_key)
                
                dst.write(content)
            
            print("✅ .env file created")
            print("⚠️  Please edit .env file and add your OpenAI API key")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
    
    # Setup database
    print("\n📊 Setting up database...")
    print("Please run the database setup script:")
    print("python database/setup.py")
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python database/setup.py")
    print("3. Run: python -m uvicorn app.main:app --reload")
    print("4. Visit http://localhost:8000/docs for API documentation")

if __name__ == "__main__":
    main()