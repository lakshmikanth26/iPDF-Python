# PyPDF Toolkit Web - Cross-Platform Setup Script
# This script automatically detects the operating system and sets up the application

param(
    [switch]$SkipVenv,
    [switch]$Force,
    [switch]$Help
)

# Color functions for better output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    if ($PSVersionTable.PSVersion.Major -ge 5) {
        Write-Host $Message -ForegroundColor $Color
    } else {
        Write-Host $Message
    }
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" "Yellow"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ $Message" "Cyan"
}

# Help function
function Show-Help {
    Write-Host @"
PyPDF Toolkit Web - Setup Script

USAGE:
    PowerShell:
        .\setup.ps1 [OPTIONS]
    
    Bash/Zsh (Mac/Linux):
        chmod +x setup.ps1
        ./setup.ps1 [OPTIONS]

OPTIONS:
    -SkipVenv       Skip virtual environment creation
    -Force          Force reinstall even if already set up
    -Help           Show this help message

EXAMPLES:
    .\setup.ps1                 # Full setup with virtual environment
    .\setup.ps1 -SkipVenv      # Setup without virtual environment
    .\setup.ps1 -Force         # Force complete reinstall

"@
    exit 0
}

# Show help if requested
if ($Help) {
    Show-Help
}

# Banner
Write-Host @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                          PyPDF Toolkit Web Setup                            ║
║                     Professional PDF Processing Platform                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Magenta

Write-Host ""

# Detect operating system
$IsWindows = $false
$IsMac = $false
$IsLinux = $false

if ($PSVersionTable.PSVersion.Major -ge 6) {
    # PowerShell Core (6+)
    $IsWindows = $IsWindows -or ($PSVersionTable.OS -like "*Windows*")
    $IsMac = $PSVersionTable.OS -like "*Darwin*"
    $IsLinux = $PSVersionTable.OS -like "*Linux*"
} else {
    # Windows PowerShell (5.1 and below)
    $IsWindows = $true
}

# Fallback detection for cross-platform compatibility
if (-not $IsWindows -and -not $IsMac -and -not $IsLinux) {
    if ($env:OS -eq "Windows_NT") {
        $IsWindows = $true
    } elseif (Test-Path "/System/Library/CoreServices/SystemVersion.plist") {
        $IsMac = $true
    } else {
        $IsLinux = $true
    }
}

# Display detected OS
if ($IsWindows) {
    Write-Info "Detected Operating System: Windows"
    $PythonCmd = "python"
    $PipCmd = "pip"
    $VenvActivate = "venv\Scripts\Activate.ps1"
    $VenvActivateBat = "venv\Scripts\activate.bat"
} elseif ($IsMac) {
    Write-Info "Detected Operating System: macOS"
    $PythonCmd = "python3"
    $PipCmd = "pip3"
    $VenvActivate = "venv/bin/activate"
} else {
    Write-Info "Detected Operating System: Linux"
    $PythonCmd = "python3"
    $PipCmd = "pip3"
    $VenvActivate = "venv/bin/activate"
}

Write-Host ""

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    
    try {
        if (Get-Command $Command -ErrorAction SilentlyContinue) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Function to run command with error handling
function Invoke-SafeCommand {
    param(
        [string]$Command,
        [string]$Description,
        [switch]$Critical = $false
    )
    
    Write-Info "Running: $Description"
    Write-Host "Command: $Command" -ForegroundColor Gray
    
    try {
        if ($IsWindows) {
            $result = cmd /c $Command 2>&1
        } else {
            $result = bash -c $Command 2>&1
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success $Description
            return $true
        } else {
            Write-Error "$Description failed with exit code: $LASTEXITCODE"
            if ($result) {
                Write-Host "Output: $result" -ForegroundColor Red
            }
            if ($Critical) {
                exit 1
            }
            return $false
        }
    } catch {
        Write-Error "$Description failed: $($_.Exception.Message)"
        if ($Critical) {
            exit 1
        }
        return $false
    }
}

# Check prerequisites
Write-Info "Checking prerequisites..."

# Check Python
$PythonFound = $false
foreach ($cmd in @($PythonCmd, "python", "python3")) {
    if (Test-Command $cmd) {
        $PythonCmd = $cmd
        $PythonFound = $true
        break
    }
}

if (-not $PythonFound) {
    Write-Error "Python is not installed or not in PATH"
    Write-Host "Please install Python 3.8+ from: https://www.python.org/downloads/"
    exit 1
}

# Check Python version
try {
    $pythonVersion = & $PythonCmd --version 2>&1
    Write-Success "Found Python: $pythonVersion"
    
    # Extract version number
    if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Error "Python 3.8+ is required. Found: $pythonVersion"
            exit 1
        }
    }
} catch {
    Write-Error "Failed to check Python version"
    exit 1
}

# Check pip
$PipFound = $false
foreach ($cmd in @($PipCmd, "pip", "pip3")) {
    if (Test-Command $cmd) {
        $PipCmd = $cmd
        $PipFound = $true
        break
    }
}

if (-not $PipFound) {
    Write-Warning "pip not found, attempting to install..."
    if ($IsWindows) {
        Invoke-SafeCommand "$PythonCmd -m ensurepip --upgrade" "Installing pip" -Critical
    } else {
        Invoke-SafeCommand "curl https://bootstrap.pypa.io/get-pip.py | $PythonCmd" "Installing pip" -Critical
    }
    $PipCmd = "$PythonCmd -m pip"
}

Write-Success "Found pip"

# Create directories
Write-Info "Creating project directories..."
$directories = @("uploads", "outputs", "static/js")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Success "Created directory: $dir"
    } else {
        Write-Info "Directory already exists: $dir"
    }
}

# Virtual environment setup
if (-not $SkipVenv) {
    Write-Info "Setting up virtual environment..."
    
    if ((Test-Path "venv") -and -not $Force) {
        Write-Info "Virtual environment already exists. Use -Force to recreate."
    } else {
        if (Test-Path "venv") {
            Write-Info "Removing existing virtual environment..."
            Remove-Item -Recurse -Force "venv"
        }
        
        if (-not (Invoke-SafeCommand "$PythonCmd -m venv venv" "Creating virtual environment" -Critical)) {
            exit 1
        }
    }
    
    # Activate virtual environment and install dependencies
    Write-Info "Installing dependencies in virtual environment..."
    
    if ($IsWindows) {
        # Windows activation
        $activateCmd = "venv\Scripts\activate && pip install -r requirements.txt"
        if (-not (Invoke-SafeCommand $activateCmd "Installing dependencies" -Critical)) {
            # Try with PowerShell activation
            Write-Info "Trying PowerShell activation method..."
            try {
                & "venv\Scripts\Activate.ps1"
                & pip install -r requirements.txt
                Write-Success "Dependencies installed successfully"
            } catch {
                Write-Error "Failed to install dependencies: $($_.Exception.Message)"
                exit 1
            }
        }
    } else {
        # Mac/Linux activation
        $activateCmd = "source venv/bin/activate && pip install -r requirements.txt"
        if (-not (Invoke-SafeCommand $activateCmd "Installing dependencies" -Critical)) {
            exit 1
        }
    }
} else {
    Write-Info "Skipping virtual environment setup..."
    Write-Info "Installing dependencies globally..."
    if (-not (Invoke-SafeCommand "$PipCmd install -r requirements.txt" "Installing dependencies globally" -Critical)) {
        exit 1
    }
}

# Verify installation
Write-Info "Verifying installation..."

$testScript = @"
try:
    from modules.pdf_merger import PDFMerger
    from modules.pdf_splitter import PDFSplitter
    from modules.pdf_compressor import PDFCompressor
    from modules.pdf_converter import PDFConverter
    from modules.pdf_unlocker import PDFUnlocker
    from modules.error_handler import ErrorHandler
    import flask
    print('SUCCESS: All modules imported successfully')
except ImportError as e:
    print(f'ERROR: Import failed - {e}')
    exit(1)
except Exception as e:
    print(f'ERROR: Unexpected error - {e}')
    exit(1)
"@

$testScript | Out-File -FilePath "temp_test.py" -Encoding UTF8

if ($SkipVenv) {
    $testResult = & $PythonCmd temp_test.py 2>&1
} else {
    if ($IsWindows) {
        $testResult = cmd /c "venv\Scripts\activate && python temp_test.py" 2>&1
    } else {
        $testResult = bash -c "source venv/bin/activate && python temp_test.py" 2>&1
    }
}

Remove-Item "temp_test.py" -Force

if ($testResult -like "*SUCCESS*") {
    Write-Success "Installation verification passed!"
} else {
    Write-Error "Installation verification failed!"
    Write-Host "Output: $testResult" -ForegroundColor Red
    exit 1
}

# Success message and instructions
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                            SETUP COMPLETED SUCCESSFULLY!                    ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Success "PyPDF Toolkit Web has been set up successfully!"
Write-Host ""

Write-Info "To start the application:"
Write-Host ""

if (-not $SkipVenv) {
    if ($IsWindows) {
        Write-Host "  1. Activate virtual environment:" -ForegroundColor Cyan
        Write-Host "     venv\Scripts\activate" -ForegroundColor Yellow
        Write-Host "     # OR in PowerShell:" -ForegroundColor Gray
        Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  2. Start the application:" -ForegroundColor Cyan
        Write-Host "     python app.py" -ForegroundColor Yellow
    } else {
        Write-Host "  1. Activate virtual environment:" -ForegroundColor Cyan
        Write-Host "     source venv/bin/activate" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  2. Start the application:" -ForegroundColor Cyan
        Write-Host "     python app.py" -ForegroundColor Yellow
    }
} else {
    Write-Host "  Start the application:" -ForegroundColor Cyan
    Write-Host "     $PythonCmd app.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  3. Open your browser and navigate to:" -ForegroundColor Cyan
Write-Host "     http://localhost:5000" -ForegroundColor Yellow
Write-Host ""

Write-Info "For Vercel deployment:"
Write-Host "     npm i -g vercel" -ForegroundColor Yellow
Write-Host "     vercel --prod" -ForegroundColor Yellow
Write-Host ""

Write-Info "For help and documentation, see:"
Write-Host "     README.md" -ForegroundColor Yellow
Write-Host "     PROJECT_SUMMARY.md" -ForegroundColor Yellow
Write-Host ""

Write-Success "Happy PDF processing! 🎉"
