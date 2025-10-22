# PyPDF Toolkit Web - Cross-Platform Setup Script (PowerShell Version)
# This script sets up the application on Windows systems

# Set execution policy for this session to allow script execution
try {
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force -ErrorAction SilentlyContinue
} catch {
    Write-Warning "Could not set execution policy. You may need to run PowerShell as Administrator."
    Write-Info "Alternatively, run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
}

param(
    [switch]$SkipVenv,
    [switch]$Force,
    [switch]$Help,
    [switch]$KeepVenv
)

# Color functions for Windows PowerShell
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║                          PyPDF Toolkit Web Setup                            ║" -ForegroundColor Magenta
    Write-Host "║                     Professional PDF Processing Platform                     ║" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

function Show-Help {
    Write-Host "PyPDF Toolkit Web - Setup Script"
    Write-Host ""
    Write-Host "USAGE:"
    Write-Host "    .\setup.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "OPTIONS:"
    Write-Host "    -SkipVenv     Skip virtual environment creation"
    Write-Host "    -Force        Force reinstall even if already set up"
    Write-Host "    -KeepVenv     Keep existing virtual environment (don't delete)"
    Write-Host "    -Help         Show this help message"
    Write-Host ""
    Write-Host "EXAMPLES:"
    Write-Host "    .\setup.ps1                 # Full setup with fresh virtual environment"
    Write-Host "    .\setup.ps1 -SkipVenv       # Setup without virtual environment"
    Write-Host "    .\setup.ps1 -Force          # Force complete reinstall"
    Write-Host "    .\setup.ps1 -KeepVenv       # Keep existing venv if it exists"
    Write-Host ""
    Write-Host "NOTE: By default, the script will delete and recreate the virtual environment"
    Write-Host "      to ensure a clean installation. Use -KeepVenv to preserve existing venv."
    Write-Host ""
    exit 0
}

# Show help if requested
if ($Help) {
    Show-Help
}

# Banner
Write-Banner

# Check if we're in the right directory
if (-not (Test-Path "requirements.txt")) {
    Write-Error "requirements.txt not found. Please run this script from the project root directory."
    Write-Host "Current directory: $(Get-Location)"
    Write-Host "Expected files: requirements.txt, app.py, modules/"
    exit 1
}

# Detect operating system
$OS = "Windows"
$PythonCmd = "python"
$PipCmd = "pip"

Write-Info "Detected Operating System: $OS"
Write-Info "Working directory: $(Get-Location)"
Write-Host ""

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to run command with error handling
function Invoke-Command {
    param(
        [string]$Command,
        [string]$Description,
        [bool]$Critical = $false
    )
    
    Write-Info "Running: $Description"
    Write-Host "Command: $Command" -ForegroundColor Gray
    
    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0) {
            Write-Success $Description
            return $true
        } else {
            Write-Error "$Description failed (Exit code: $LASTEXITCODE)"
            if ($Critical) {
                exit 1
            }
            return $false
        }
    }
    catch {
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
$PythonCommands = @($PythonCmd, "python3", "py")

foreach ($cmd in $PythonCommands) {
    if (Test-Command $cmd) {
        # Verify it's Python 3
        try {
            $version = & $cmd --version 2>&1
            if ($version -match "Python 3") {
                $PythonCmd = $cmd
                $PythonFound = $true
                break
            }
        }
        catch {
            continue
        }
    }
}

if (-not $PythonFound) {
    Write-Error "Python 3 is not installed or not in PATH"
    Write-Host "Please install Python 3.8+ from: https://www.python.org/downloads/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation"
    exit 1
}

# Check Python version
$PythonVersion = & $PythonCmd --version 2>&1
Write-Success "Found Python: $PythonVersion"

# Extract version numbers
if ($PythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
    $Major = [int]$Matches[1]
    $Minor = [int]$Matches[2]
    
    if ($Major -lt 3 -or ($Major -eq 3 -and $Minor -lt 8)) {
        Write-Error "Python 3.8+ is required. Found: $PythonVersion"
        exit 1
    }
}

# Check pip
$PipFound = $false
$PipCommands = @($PipCmd, "pip3")

foreach ($cmd in $PipCommands) {
    if (Test-Command $cmd) {
        $PipCmd = $cmd
        $PipFound = $true
        break
    }
}

if (-not $PipFound) {
    Write-Warning "pip not found, attempting to install..."
    if (Invoke-Command "curl https://bootstrap.pypa.io/get-pip.py | $PythonCmd" "Installing pip" $true) {
        $PipCmd = "$PythonCmd -m pip"
    } else {
        exit 1
    }
}

Write-Success "Found pip"

# Create directories
Write-Info "Creating project directories..."
$Directories = @("uploads", "outputs", "static\js")

foreach ($dir in $Directories) {
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
    
    # Default behavior: delete and recreate venv unless KeepVenv is specified
    if ((Test-Path "venv") -and -not $KeepVenv) {
        Write-Info "Removing existing virtual environment for fresh installation..."
        try {
            Remove-Item -Recurse -Force "venv" -ErrorAction Stop
            Write-Success "Removed existing virtual environment"
        } catch {
            Write-Warning "Could not remove existing virtual environment: $($_.Exception.Message)"
            Write-Info "Attempting to continue with existing environment..."
        }
    } elseif ((Test-Path "venv") -and $KeepVenv) {
        Write-Info "Keeping existing virtual environment as requested..."
    }
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path "venv")) {
        Invoke-Command "$PythonCmd -m venv venv" "Creating virtual environment" $true
    } else {
        Write-Info "Using existing virtual environment"
    }
    
    # Activate virtual environment and install dependencies
    Write-Info "Installing dependencies in virtual environment..."
    $ActivateScript = "venv\Scripts\Activate.ps1"
    if (Test-Path $ActivateScript) {
        # Use proper PowerShell syntax for command chaining
        $InstallCommand = "& `"$ActivateScript`"; pip install -r requirements.txt"
        if (-not (Invoke-Command $InstallCommand "Installing dependencies" $false)) {
            Write-Warning "Failed to install dependencies in virtual environment. Trying alternative method..."
            # Try using the batch file instead
            $BatchActivate = "venv\Scripts\activate.bat"
            if (Test-Path $BatchActivate) {
                $BatchCommand = "cmd /c `"$BatchActivate && pip install -r requirements.txt`""
                Invoke-Command $BatchCommand "Installing dependencies (batch method)" $true
            } else {
                Write-Error "Could not activate virtual environment or install dependencies"
                exit 1
            }
        }
    } else {
        Write-Error "Virtual environment activation script not found"
        exit 1
    }
} else {
    Write-Info "Skipping virtual environment setup..."
    Write-Info "Installing dependencies globally..."
    Invoke-Command "$PipCmd install -r requirements.txt" "Installing dependencies globally" $true
}

# Install Ghostscript and Poppler for enhanced PDF processing
Write-Info "Installing Ghostscript and Poppler for enhanced PDF processing..."

# Check if Chocolatey is available
if (Test-Command "choco") {
    Write-Info "Installing Ghostscript and Poppler via Chocolatey..."
    $gsResult = Invoke-Command "choco install ghostscript -y" "Installing Ghostscript via Chocolatey" $false
    $popplerResult = Invoke-Command "choco install poppler -y" "Installing Poppler via Chocolatey" $false
    
    if ($gsResult -and $popplerResult) {
        Write-Success "Ghostscript and Poppler installed successfully!"
    } else {
        Write-Warning "Some installations failed, but continuing..."
    }
} elseif (Test-Command "winget") {
    Write-Info "Installing Ghostscript and Poppler via winget..."
    $gsResult = Invoke-Command "winget install ArtifexSoftware.GhostScript" "Installing Ghostscript via winget" $false
    $popplerResult = Invoke-Command "winget install poppler" "Installing Poppler via winget" $false
    
    if ($gsResult -and $popplerResult) {
        Write-Success "Ghostscript and Poppler installed successfully!"
    } else {
        Write-Warning "Some installations failed, but continuing..."
    }
} else {
    Write-Warning "No package manager found (Chocolatey or winget)."
    Write-Host "Please install Ghostscript and Poppler manually:"
    Write-Host "  - Ghostscript: https://www.ghostscript.com/download/gsdnld.html"
    Write-Host "  - Poppler: https://poppler.freedesktop.org/"
    Write-Host "Or install a package manager:"
    Write-Host "  - Chocolatey: https://chocolatey.org/install"
    Write-Host "  - winget: Usually pre-installed on Windows 10/11"
}

# Verify installations
if (Test-Command "gs") {
    $GSVersion = & gs --version
    Write-Success "Ghostscript is available: version $GSVersion"
    Write-Info "PDF compression will use advanced Ghostscript compression for better results!"
} else {
    Write-Warning "Ghostscript not found. PDF compression will use alternative methods."
}

if (Test-Command "pdftoppm") {
    Write-Success "Poppler is available for PDF to image conversion!"
    Write-Info "PDF to image conversion will work properly."
} else {
    Write-Warning "Poppler not found. PDF to image conversion may not work properly."
}

# Verify installation
Write-Info "Verifying installation..."

# Create temporary test script
$TestScript = @"
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

$TestScript | Out-File -FilePath "temp_test.py" -Encoding UTF8

# Run test
if (-not $SkipVenv) {
    $ActivateScript = "venv\Scripts\Activate.ps1"
    if (Test-Path $ActivateScript) {
        # Use proper PowerShell syntax for command chaining
        $TestCommand = "& `"$ActivateScript`"; python temp_test.py"
        try {
            $TestResult = Invoke-Expression $TestCommand 2>&1
        } catch {
            Write-Warning "PowerShell activation failed, trying batch method..."
            $BatchActivate = "venv\Scripts\activate.bat"
            if (Test-Path $BatchActivate) {
                $BatchTestCommand = "cmd /c `"$BatchActivate && python temp_test.py`""
                $TestResult = Invoke-Expression $BatchTestCommand 2>&1
            } else {
                Write-Error "Could not activate virtual environment for testing"
                $TestResult = "ERROR: Could not activate virtual environment"
            }
        }
    } else {
        Write-Error "Virtual environment activation script not found for testing"
        $TestResult = "ERROR: Virtual environment not found"
    }
} else {
    $TestResult = & $PythonCmd temp_test.py 2>&1
}

# Clean up test file
Remove-Item "temp_test.py" -Force

if ($TestResult -match "SUCCESS") {
    Write-Success "Installation verification passed!"
} else {
    Write-Error "Installation verification failed!"
    Write-Host "Output: $TestResult"
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
    Write-Host "  1. Activate virtual environment:" -ForegroundColor Cyan
    Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  2. Start the application:" -ForegroundColor Cyan
    Write-Host "     python app.py" -ForegroundColor Yellow
} else {
    Write-Host "  Start the application:" -ForegroundColor Cyan
    Write-Host "     $PythonCmd app.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  3. Open your browser and navigate to:" -ForegroundColor Cyan
Write-Host "     http://localhost:5000" -ForegroundColor Yellow
Write-Host ""

Write-Info "For help and documentation, see:"
Write-Host "     README.md" -ForegroundColor Yellow
Write-Host "     PROJECT_SUMMARY.md" -ForegroundColor Yellow
Write-Host ""

Write-Success "Happy PDF processing! 🎉"