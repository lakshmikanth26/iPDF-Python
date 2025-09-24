# 🚀 PyPDF Toolkit Web - Quick Start Guide

Get up and running with PyPDF Toolkit Web in under 5 minutes! This guide provides simple setup instructions for all operating systems.

## 📋 Prerequisites

- **Python 3.8+** (Download from [python.org](https://www.python.org/downloads/))
- **Git** (Optional, for cloning)
- **Internet connection** (for downloading dependencies)

## 🖥️ Platform-Specific Setup

### 🪟 Windows Users

#### Option 1: PowerShell (Recommended)
```powershell
# Open PowerShell as Administrator (optional but recommended)
# Navigate to project directory
cd C:\path\to\iPDF-Python

# Run the setup script
.\setup.ps1

# Or with options:
.\setup.ps1 -SkipVenv    # Skip virtual environment
.\setup.ps1 -Force       # Force reinstall
```

#### Option 2: Command Prompt
```cmd
# Open Command Prompt
# Navigate to project directory
cd C:\path\to\iPDF-Python

# Run the setup script
setup.bat

# Or skip virtual environment:
setup.bat --skip-venv
```

### 🍎 macOS Users

#### Option 1: Terminal (Bash/Zsh)
```bash
# Open Terminal
# Navigate to project directory
cd /path/to/iPDF-Python

# Make script executable and run
chmod +x setup.sh
./setup.sh

# Or with options:
./setup.sh --skip-venv   # Skip virtual environment
./setup.sh --force       # Force reinstall
```

#### Option 2: PowerShell Core (if installed)
```powershell
# If you have PowerShell Core installed
./setup.ps1
```

### 🐧 Linux Users

#### Terminal (Bash)
```bash
# Open Terminal
# Navigate to project directory
cd /path/to/iPDF-Python

# Make script executable and run
chmod +x setup.sh
./setup.sh

# Or with options:
./setup.sh --skip-venv   # Skip virtual environment
./setup.sh --force       # Force reinstall
```

## 🎯 One-Command Setup

Choose the appropriate command for your system:

| Platform | Command |
|----------|---------|
| **Windows PowerShell** | `.\setup.ps1` |
| **Windows CMD** | `setup.bat` |
| **macOS/Linux** | `./setup.sh` |

## 🚀 Starting the Application

After setup completes, start the application:

### With Virtual Environment (Recommended)

**Windows:**
```cmd
# Activate virtual environment
venv\Scripts\activate

# Start application
python app.py
```

**macOS/Linux:**
```bash
# Activate virtual environment
source venv/bin/activate

# Start application
python app.py
```

### Without Virtual Environment

```bash
# All platforms
python app.py
```

## 🌐 Accessing the Application

1. **Open your web browser**
2. **Navigate to:** `http://localhost:5000` (or the port shown in the startup message)
3. **Start processing PDFs!** 🎉

> 💡 **Note:** If port 5000 is busy (common on macOS with AirPlay), the app will automatically find and use the next available port (5001, 5002, etc.)

## 🔧 Setup Script Options

All setup scripts support these options:

| Option | Description |
|--------|-------------|
| `--skip-venv` | Skip virtual environment creation |
| `--force` | Force reinstall even if already set up |
| `--help` | Show help message |

## 🐳 Alternative: Manual Setup

If you prefer manual setup:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create directories
mkdir uploads outputs

# 5. Start application
python app.py
```

## ☁️ Cloud Deployment

### Vercel (Serverless)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Docker (Coming Soon)
```bash
# Build Docker image
docker build -t pypdf-toolkit .

# Run container
docker run -p 5000:5000 pypdf-toolkit
```

## 🆘 Troubleshooting

### Common Issues

#### Python Not Found
- **Windows:** Install Python from [python.org](https://www.python.org/downloads/) and check "Add Python to PATH"
- **macOS:** Install via Homebrew: `brew install python`
- **Linux:** Install via package manager: `sudo apt install python3 python3-pip`

#### Permission Denied
- **Windows:** Run PowerShell as Administrator
- **macOS/Linux:** Use `chmod +x setup.sh` to make script executable

#### Module Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Try running setup script with `--force` option

#### Port Already in Use
- **Automatic Detection:** The app now automatically finds available ports (5000-5010)
- **macOS AirPlay:** Disable AirPlay Receiver in System Preferences → Sharing
- **Manual Override:** Set custom port with environment variable: `PORT=8000 python app.py`
- **Kill Process:** Find and kill process: `lsof -ti:5000 | xargs kill -9` (macOS/Linux)

### Getting Help

1. **Check logs:** Look at `app.log` file for detailed error messages
2. **Run tests:** Execute `python test_app.py` to verify installation
3. **Read documentation:** See `README.md` and `PROJECT_SUMMARY.md`
4. **Check requirements:** Ensure Python 3.8+ is installed

## 📱 Features Overview

Once running, you can access these features:

- **🔗 Merge PDFs** - Combine multiple PDFs into one
- **✂️ Split PDFs** - Split PDFs by pages or ranges  
- **🗜️ Compress PDFs** - Reduce file size with quality options
- **🔄 Convert Files** - Images ↔ PDF conversion
- **🔓 Unlock PDFs** - Remove password protection

## 🎊 Success!

If you see this message after setup:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                            SETUP COMPLETED SUCCESSFULLY!                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

You're ready to start processing PDFs! Open `http://localhost:5000` in your browser and enjoy! 🎉

---

**Need more help?** Check out the full documentation in `README.md` or `PROJECT_SUMMARY.md`.
