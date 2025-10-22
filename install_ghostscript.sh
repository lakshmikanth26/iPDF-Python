#!/bin/bash

# Ghostscript Installation Script for PDF Compression
# This script installs Ghostscript for better PDF compression results

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info "Installing Ghostscript for enhanced PDF compression..."

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    print_info "Detected macOS"
    
    # Check if Homebrew is installed
    if command -v brew &> /dev/null; then
        print_info "Installing Ghostscript via Homebrew..."
        brew install ghostscript
        print_success "Ghostscript installed successfully!"
    else
        print_error "Homebrew not found. Please install Homebrew first:"
        echo "Visit: https://brew.sh/"
        exit 1
    fi
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    print_info "Detected Linux"
    
    # Check if apt is available
    if command -v apt &> /dev/null; then
        print_info "Installing Ghostscript via apt..."
        sudo apt update
        sudo apt install -y ghostscript
        print_success "Ghostscript installed successfully!"
    elif command -v yum &> /dev/null; then
        print_info "Installing Ghostscript via yum..."
        sudo yum install -y ghostscript
        print_success "Ghostscript installed successfully!"
    else
        print_error "Package manager not found. Please install Ghostscript manually."
        echo "Visit: https://www.ghostscript.com/download/gsdnld.html"
        exit 1
    fi
    
else
    print_error "Unsupported operating system: $OSTYPE"
    echo "Please install Ghostscript manually from: https://www.ghostscript.com/download/gsdnld.html"
    exit 1
fi

# Verify installation
print_info "Verifying Ghostscript installation..."
if command -v gs &> /dev/null; then
    GS_VERSION=$(gs --version)
    print_success "Ghostscript is installed: version $GS_VERSION"
    print_info "PDF compression will now use advanced Ghostscript compression for better results!"
else
    print_error "Ghostscript installation verification failed"
    exit 1
fi

echo
print_success "Ghostscript installation completed!"
print_info "You can now use the PDF compression feature with enhanced results."
