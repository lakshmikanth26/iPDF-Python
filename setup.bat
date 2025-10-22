@echo off
REM PyPDF Toolkit Web - Windows Batch Setup Script
REM Simple setup script for Windows Command Prompt users

setlocal EnableDelayedExpansion

REM Color codes (if supported)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "CYAN=[96m"
set "MAGENTA=[95m"
set "NC=[0m"

REM Banner
echo.
echo %MAGENTA%╔══════════════════════════════════════════════════════════════════════════════╗%NC%
echo %MAGENTA%║                          PyPDF Toolkit Web Setup                            ║%NC%
echo %MAGENTA%║                     Professional PDF Processing Platform                     ║%NC%
echo %MAGENTA%╚══════════════════════════════════════════════════════════════════════════════╝%NC%
echo.

echo %CYAN%ℹ Detected Operating System: Windows%NC%
echo %CYAN%ℹ Usage: setup.bat [--skip-venv] [--keep-venv] [--global]%NC%
echo %CYAN%ℹ By default, the script will delete and recreate the virtual environment%NC%
echo %CYAN%ℹ Use --keep-venv to preserve existing virtual environment%NC%
echo.

REM Check if Python is installed
echo %CYAN%ℹ Checking prerequisites...%NC%
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%✗ Python is not installed or not in PATH%NC%
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%✓ Found Python: %PYTHON_VERSION%%NC%

REM Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%✗ pip is not installed%NC%
    echo Installing pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo %RED%✗ Failed to install pip%NC%
        pause
        exit /b 1
    )
)
echo %GREEN%✓ Found pip%NC%

REM Create directories
echo %CYAN%ℹ Creating project directories...%NC%
if not exist "uploads" mkdir uploads && echo %GREEN%✓ Created directory: uploads%NC%
if not exist "outputs" mkdir outputs && echo %GREEN%✓ Created directory: outputs%NC%
if not exist "static\js" mkdir static\js && echo %GREEN%✓ Created directory: static\js%NC%

REM Check for virtual environment
set SKIP_VENV=0
set KEEP_VENV=0
if "%1"=="--skip-venv" set SKIP_VENV=1
if "%1"=="--global" set SKIP_VENV=1
if "%1"=="--keep-venv" set KEEP_VENV=1
if "%2"=="--keep-venv" set KEEP_VENV=1

if %SKIP_VENV%==0 (
    echo %CYAN%ℹ Setting up virtual environment...%NC%
    
    REM Default behavior: delete and recreate venv unless KeepVenv is specified
    if exist "venv" (
        if %KEEP_VENV%==0 (
            echo %CYAN%ℹ Removing existing virtual environment for fresh installation...%NC%
            rmdir /s /q venv
            if %errorlevel% neq 0 (
                echo %YELLOW%⚠ Could not remove existing virtual environment, continuing...%NC%
            ) else (
                echo %GREEN%✓ Removed existing virtual environment%NC%
            )
        ) else (
            echo %CYAN%ℹ Keeping existing virtual environment as requested...%NC%
        )
    )
    
    if not exist "venv" (
        echo Creating virtual environment...
        python -m venv venv
        if %errorlevel% neq 0 (
            echo %RED%✗ Failed to create virtual environment%NC%
            pause
            exit /b 1
        )
        echo %GREEN%✓ Created virtual environment%NC%
    ) else (
        echo %CYAN%ℹ Using existing virtual environment%NC%
    )
    
    echo %CYAN%ℹ Installing dependencies in virtual environment...%NC%
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo %RED%✗ Failed to install dependencies%NC%
        pause
        exit /b 1
    )
    echo %GREEN%✓ Dependencies installed successfully%NC%
) else (
    echo %CYAN%ℹ Installing dependencies globally...%NC%
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo %RED%✗ Failed to install dependencies%NC%
        pause
        exit /b 1
    )
    echo %GREEN%✓ Dependencies installed globally%NC%
)

REM Verify installation
echo %CYAN%ℹ Verifying installation...%NC%

REM Create temporary test script
echo try: > temp_test.py
echo     from modules.pdf_merger import PDFMerger >> temp_test.py
echo     from modules.pdf_splitter import PDFSplitter >> temp_test.py
echo     from modules.pdf_compressor import PDFCompressor >> temp_test.py
echo     from modules.pdf_converter import PDFConverter >> temp_test.py
echo     from modules.pdf_unlocker import PDFUnlocker >> temp_test.py
echo     from modules.error_handler import ErrorHandler >> temp_test.py
echo     import flask >> temp_test.py
echo     print('SUCCESS: All modules imported successfully') >> temp_test.py
echo except ImportError as e: >> temp_test.py
echo     print(f'ERROR: Import failed - {e}') >> temp_test.py
echo     exit(1) >> temp_test.py
echo except Exception as e: >> temp_test.py
echo     print(f'ERROR: Unexpected error - {e}') >> temp_test.py
echo     exit(1) >> temp_test.py

REM Run test
if %SKIP_VENV%==0 (
    call venv\Scripts\activate.bat && python temp_test.py
) else (
    python temp_test.py
)

set TEST_RESULT=%errorlevel%
del temp_test.py

if %TEST_RESULT%==0 (
    echo %GREEN%✓ Installation verification passed!%NC%
) else (
    echo %RED%✗ Installation verification failed!%NC%
    pause
    exit /b 1
)

REM Success message
echo.
echo %GREEN%╔══════════════════════════════════════════════════════════════════════════════╗%NC%
echo %GREEN%║                            SETUP COMPLETED SUCCESSFULLY!                    ║%NC%
echo %GREEN%╚══════════════════════════════════════════════════════════════════════════════╝%NC%
echo.

echo %GREEN%✓ PyPDF Toolkit Web has been set up successfully!%NC%
echo.

echo %CYAN%ℹ To start the application:%NC%
echo.

if %SKIP_VENV%==0 (
    echo %CYAN%  1. Activate virtual environment:%NC%
    echo %YELLOW%     venv\Scripts\activate%NC%
    echo.
    echo %CYAN%  2. Start the application:%NC%
    echo %YELLOW%     python app.py%NC%
) else (
    echo %CYAN%  Start the application:%NC%
    echo %YELLOW%     python app.py%NC%
)

echo.
echo %CYAN%  3. Open your browser and navigate to:%NC%
echo %YELLOW%     http://localhost:5000%NC%
echo.

echo %CYAN%ℹ For Vercel deployment:%NC%
echo %YELLOW%     npm i -g vercel%NC%
echo %YELLOW%     vercel --prod%NC%
echo.

REM Install Ghostscript and Poppler for enhanced PDF processing
echo %CYAN%ℹ Installing Ghostscript and Poppler for enhanced PDF processing...%NC%

REM Check if Chocolatey is available
choco --version >nul 2>&1
if %errorlevel%==0 (
    echo %CYAN%ℹ Installing Ghostscript and Poppler via Chocolatey...%NC%
    choco install ghostscript -y
    choco install poppler -y
    if %errorlevel%==0 (
        echo %GREEN%✓ Ghostscript and Poppler installed successfully!%NC%
    ) else (
        echo %YELLOW%⚠ Some installations failed, but continuing...%NC%
    )
) else (
    REM Check if winget is available
    winget --version >nul 2>&1
    if %errorlevel%==0 (
        echo %CYAN%ℹ Installing Ghostscript and Poppler via winget...%NC%
        winget install ArtifexSoftware.GhostScript
        winget install poppler
        if %errorlevel%==0 (
            echo %GREEN%✓ Ghostscript and Poppler installed successfully!%NC%
        ) else (
            echo %YELLOW%⚠ Some installations failed, but continuing...%NC%
        )
    ) else (
        echo %YELLOW%⚠ No package manager found (Chocolatey or winget).%NC%
        echo Please install Ghostscript and Poppler manually:
        echo   - Ghostscript: https://www.ghostscript.com/download/gsdnld.html
        echo   - Poppler: https://poppler.freedesktop.org/
        echo Or install a package manager:
        echo   - Chocolatey: https://chocolatey.org/install
        echo   - winget: Usually pre-installed on Windows 10/11
    )
)

REM Verify Ghostscript installation
gs --version >nul 2>&1
if %errorlevel%==0 (
    for /f "tokens=*" %%i in ('gs --version 2^>^&1') do set GS_VERSION=%%i
    echo %GREEN%✓ Ghostscript is available: version !GS_VERSION!%NC%
    echo %CYAN%ℹ PDF compression will use advanced Ghostscript compression for better results!%NC%
) else (
    echo %YELLOW%⚠ Ghostscript not found. PDF compression will use alternative methods.%NC%
)

REM Verify Poppler installation
pdftoppm --version >nul 2>&1
if %errorlevel%==0 (
    echo %GREEN%✓ Poppler is available for PDF to image conversion!%NC%
    echo %CYAN%ℹ PDF to image conversion will work properly.%NC%
) else (
    echo %YELLOW%⚠ Poppler not found. PDF to image conversion may not work properly.%NC%
)

echo.

echo %CYAN%ℹ For help and documentation, see:%NC%
echo %YELLOW%     README.md%NC%
echo %YELLOW%     PROJECT_SUMMARY.md%NC%
echo.

echo %GREEN%✓ Happy PDF processing! 🎉%NC%
echo.

pause
