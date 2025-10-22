#!/bin/bash

# PyPDF Toolkit Web - Cross-Platform Setup Script (Bash Version)
# This script sets up the application on Mac/Linux systems

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Output functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

print_banner() {
    echo -e "${MAGENTA}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                          PyPDF Toolkit Web Setup                            ║"
    echo "║                     Professional PDF Processing Platform                     ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
}

# Help function
show_help() {
    echo "PyPDF Toolkit Web - Setup Script"
    echo
    echo "USAGE:"
    echo "    ./setup.sh [OPTIONS]"
    echo
    echo "OPTIONS:"
    echo "    --skip-venv     Skip virtual environment creation"
    echo "    --force         Force reinstall even if already set up"
    echo "    --help          Show this help message"
    echo
    echo "EXAMPLES:"
    echo "    ./setup.sh                 # Full setup with virtual environment"
    echo "    ./setup.sh --skip-venv     # Setup without virtual environment"
    echo "    ./setup.sh --force         # Force complete reinstall"
    echo
    exit 0
}

# Parse command line arguments
SKIP_VENV=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-venv)
            SKIP_VENV=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Banner
print_banner

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    OS="Unknown"
    PYTHON_CMD="python3"
    PIP_CMD="pip"
fi

print_info "Detected Operating System: $OS"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run command with error handling
run_command() {
    local cmd="$1"
    local description="$2"
    local critical="${3:-false}"
    
    print_info "Running: $description"
    echo -e "${NC}Command: $cmd"
    
    if eval "$cmd"; then
        print_success "$description"
        return 0
    else
        print_error "$description failed"
        if [[ "$critical" == "true" ]]; then
            exit 1
        fi
        return 1
    fi
}

# Check prerequisites
print_info "Checking prerequisites..."

# Check Python - prioritize python3
PYTHON_FOUND=false
for cmd in "python3" "$PYTHON_CMD" "python"; do
    if command_exists "$cmd"; then
        # Verify it's Python 3
        if $cmd --version 2>&1 | grep -q "Python 3"; then
            PYTHON_CMD="$cmd"
            PYTHON_FOUND=true
            break
        fi
    fi
done

if [[ "$PYTHON_FOUND" != "true" ]]; then
    print_error "Python is not installed or not in PATH"
    echo "Please install Python 3.8+ from: https://www.python.org/downloads/"
    if [[ "$OS" == "macOS" ]]; then
        echo "Or install via Homebrew: brew install python"
    elif [[ "$OS" == "Linux" ]]; then
        echo "Or install via package manager: sudo apt install python3 python3-pip"
    fi
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
print_success "Found Python: $PYTHON_VERSION"

# Extract version numbers
if [[ $PYTHON_VERSION =~ Python\ ([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
    MAJOR=${BASH_REMATCH[1]}
    MINOR=${BASH_REMATCH[2]}
    
    if [[ $MAJOR -lt 3 ]] || [[ $MAJOR -eq 3 && $MINOR -lt 8 ]]; then
        print_error "Python 3.8+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi
fi

# Check pip - prioritize pip3
PIP_FOUND=false
for cmd in "pip3" "$PIP_CMD" "pip"; do
    if command_exists "$cmd"; then
        PIP_CMD="$cmd"
        PIP_FOUND=true
        break
    fi
done

if [[ "$PIP_FOUND" != "true" ]]; then
    print_warning "pip not found, attempting to install..."
    if run_command "curl https://bootstrap.pypa.io/get-pip.py | $PYTHON_CMD" "Installing pip" "true"; then
        PIP_CMD="$PYTHON_CMD -m pip"
    else
        exit 1
    fi
fi

print_success "Found pip"

# Create directories
print_info "Creating project directories..."
DIRECTORIES=("uploads" "outputs" "static/js")
for dir in "${DIRECTORIES[@]}"; do
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir"
        print_success "Created directory: $dir"
    else
        print_info "Directory already exists: $dir"
    fi
done

# Virtual environment setup
if [[ "$SKIP_VENV" != "true" ]]; then
    print_info "Setting up virtual environment..."
    
    if [[ -d "venv" && "$FORCE" != "true" ]]; then
        print_info "Virtual environment already exists. Use --force to recreate."
    else
        if [[ -d "venv" ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf venv
        fi
        
        run_command "$PYTHON_CMD -m venv venv" "Creating virtual environment" "true"
    fi
    
    # Activate virtual environment and install dependencies
    print_info "Installing dependencies in virtual environment..."
    run_command "source venv/bin/activate && pip install -r requirements.txt" "Installing dependencies" "true"
else
    print_info "Skipping virtual environment setup..."
    print_info "Installing dependencies globally..."
    run_command "$PIP_CMD install -r requirements.txt" "Installing dependencies globally" "true"
fi

# Verify installation
print_info "Verifying installation..."

# Create temporary test script
cat > temp_test.py << 'EOF'
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
EOF

# Run test
if [[ "$SKIP_VENV" != "true" ]]; then
    TEST_RESULT=$(source venv/bin/activate && python temp_test.py 2>&1)
else
    TEST_RESULT=$($PYTHON_CMD temp_test.py 2>&1)
fi

# Clean up test file
rm temp_test.py

if [[ "$TEST_RESULT" == *"SUCCESS"* ]]; then
    print_success "Installation verification passed!"
else
    print_error "Installation verification failed!"
    echo "Output: $TEST_RESULT"
    exit 1
fi

# Success message and instructions
echo
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                            SETUP COMPLETED SUCCESSFULLY!                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo

print_success "PyPDF Toolkit Web has been set up successfully!"
echo

print_info "To start the application:"
echo

if [[ "$SKIP_VENV" != "true" ]]; then
    echo -e "${CYAN}  1. Activate virtual environment:${NC}"
    echo -e "${YELLOW}     source venv/bin/activate${NC}"
    echo
    echo -e "${CYAN}  2. Start the application:${NC}"
    echo -e "${YELLOW}     python app.py${NC}"
else
    echo -e "${CYAN}  Start the application:${NC}"
    echo -e "${YELLOW}     $PYTHON_CMD app.py${NC}"
fi

echo
echo -e "${CYAN}  3. Open your browser and navigate to:${NC}"
echo -e "${YELLOW}     http://localhost:5000${NC}"
echo

print_info "For Vercel deployment:"
echo -e "${YELLOW}     npm i -g vercel${NC}"
echo -e "${YELLOW}     vercel --prod${NC}"
echo

print_info "For help and documentation, see:"
echo -e "${YELLOW}     README.md${NC}"
echo -e "${YELLOW}     PROJECT_SUMMARY.md${NC}"
echo

# Install Ghostscript and Poppler for enhanced PDF processing
print_info "Installing Ghostscript and Poppler for enhanced PDF processing..."

if [[ "$OS" == "macOS" ]]; then
    if command -v brew &> /dev/null; then
        print_info "Installing Ghostscript and Poppler via Homebrew..."
        if brew install ghostscript poppler; then
            print_success "Ghostscript and Poppler installed successfully!"
        else
            print_warning "Ghostscript/Poppler installation failed, but continuing..."
        fi
    else
        print_warning "Homebrew not found. Please install Ghostscript and Poppler manually:"
        echo -e "${YELLOW}     Visit: https://www.ghostscript.com/download/gsdnld.html${NC}"
        echo -e "${YELLOW}     Visit: https://poppler.freedesktop.org/${NC}"
    fi
elif [[ "$OS" == "Linux" ]]; then
    if command -v apt &> /dev/null; then
        print_info "Installing Ghostscript and Poppler via apt..."
        if sudo apt update && sudo apt install -y ghostscript poppler-utils; then
            print_success "Ghostscript and Poppler installed successfully!"
        else
            print_warning "Ghostscript/Poppler installation failed, but continuing..."
        fi
    elif command -v yum &> /dev/null; then
        print_info "Installing Ghostscript and Poppler via yum..."
        if sudo yum install -y ghostscript poppler-utils; then
            print_success "Ghostscript and Poppler installed successfully!"
        else
            print_warning "Ghostscript/Poppler installation failed, but continuing..."
        fi
    else
        print_warning "Package manager not found. Please install Ghostscript and Poppler manually:"
        echo -e "${YELLOW}     Visit: https://www.ghostscript.com/download/gsdnld.html${NC}"
        echo -e "${YELLOW}     Visit: https://poppler.freedesktop.org/${NC}"
    fi
else
    print_warning "Unsupported OS for automatic installation."
    echo -e "${YELLOW}     Please install Ghostscript and Poppler manually:${NC}"
    echo -e "${YELLOW}     - Ghostscript: https://www.ghostscript.com/download/gsdnld.html${NC}"
    echo -e "${YELLOW}     - Poppler: https://poppler.freedesktop.org/${NC}"
fi

# Verify installations
if command -v gs &> /dev/null; then
    GS_VERSION=$(gs --version)
    print_success "Ghostscript is available: version $GS_VERSION"
    print_info "PDF compression will use advanced Ghostscript compression for better results!"
else
    print_warning "Ghostscript not found. PDF compression will use alternative methods."
fi

if command -v pdftoppm &> /dev/null; then
    print_success "Poppler is available for PDF to image conversion!"
    print_info "PDF to image conversion will work properly."
else
    print_warning "Poppler not found. PDF to image conversion may not work properly."
fi
echo

print_success "Happy PDF processing! 🎉"
