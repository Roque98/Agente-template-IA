# 🔧 Installation Guide

## ⚠️ Dependency Installation Fix

If you're getting cryptography version errors, try these alternatives:

### Option 1: Auto Setup (Recommended)
```bash
python setup.py
```

### Option 2: Manual Installation
```bash
# Install core dependencies first
pip install fastapi uvicorn sqlalchemy pyodbc python-dotenv

# Install security packages
pip install "python-jose[cryptography]" "passlib[bcrypt]"

# Install AI/ML packages
pip install langchain langchain-openai

# Install remaining packages
pip install httpx pydantic pydantic-settings python-multipart slowapi

# Install testing packages (optional)
pip install pytest pytest-asyncio
```

### Option 3: Using conda (if pip fails)
```bash
# Create conda environment
conda create -n agent-system python=3.11
conda activate agent-system

# Install packages via conda where possible
conda install fastapi uvicorn sqlalchemy
conda install cryptography
pip install langchain langchain-openai pyodbc python-jose passlib httpx pydantic pydantic-settings python-multipart slowapi python-dotenv pytest pytest-asyncio
```

### Option 4: Alternative cryptography
```bash
# If cryptography is the problem, try without version pinning
pip install cryptography --upgrade
pip install -r requirements-minimal.txt
```

### Option 5: Virtual Environment
```bash
# Create fresh virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip first
pip install --upgrade pip

# Install packages
pip install -r requirements-minimal.txt
```

## 🐍 Python Version Requirements

- **Minimum:** Python 3.11
- **Recommended:** Python 3.11 or 3.12
- **Not supported:** Python 3.10 or lower

### Check your Python version:
```bash
python --version
```

## 📦 Core Dependencies Explained

| Package | Purpose | Alternative |
|---------|---------|-------------|
| `fastapi` | Web framework | `flask` |
| `langchain` | LLM framework | Direct OpenAI API |
| `sqlalchemy` | Database ORM | Direct SQL |
| `pyodbc` | SQL Server driver | `pymssql` |
| `cryptography` | Encryption | Built-in `hashlib` |
| `pydantic` | Data validation | Manual validation |

## 🔧 Troubleshooting

### Error: "Microsoft Visual C++ 14.0 is required"
**Windows only:**
```bash
# Install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### Error: "Failed building wheel for cryptography"
```bash
# Option 1: Use conda
conda install cryptography

# Option 2: Use pre-compiled wheel
pip install --only-binary=cryptography cryptography

# Option 3: Alternative crypto library
pip install pycryptodome
```

### Error: "No module named 'pyodbc'"
```bash
# On Ubuntu/Debian:
sudo apt-get install unixodbc-dev

# On macOS:
brew install unixodbc

# On Windows: Usually works out of the box
```

### Error: SQL Server connection issues
```bash
# Install SQL Server ODBC Driver
# Windows: Download from Microsoft
# Linux: Follow Microsoft's guide
# macOS: brew install msodbcsql17
```

## ✅ Verify Installation

After installation, test if everything works:

```bash
python -c "
import fastapi
import langchain
import sqlalchemy
import pyodbc
import cryptography
import httpx
import pydantic
print('✅ All dependencies installed successfully!')
"
```

## 🚀 Quick Start After Installation

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 2. Setup database
python database/setup.py

# 3. Run application
python run.py

# 4. Test
curl http://localhost:8000/health
```

## 📞 Still Having Issues?

1. **Check Python version:** `python --version`
2. **Check pip version:** `pip --version`
3. **Update pip:** `pip install --upgrade pip`
4. **Clear pip cache:** `pip cache purge`
5. **Use virtual environment:** Always recommended
6. **Check system dependencies:** ODBC drivers, C++ compiler

## 🐳 Docker Alternative

If local installation keeps failing, use Docker:

```bash
# Just run with Docker
docker-compose up -d

# No local Python setup needed!
```