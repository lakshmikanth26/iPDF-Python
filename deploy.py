#!/usr/bin/env python3
"""
Deployment script for PyPDF Toolkit Web
Handles environment setup and deployment tasks
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description=""):
    """Run a shell command and handle errors."""
    print(f"Running: {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    
    # Check pip
    if not run_command("pip --version", "Checking pip"):
        print("Error: pip is not installed")
        return False
    
    print("Dependencies check passed!")
    return True


def setup_virtual_environment():
    """Set up Python virtual environment."""
    print("Setting up virtual environment...")
    
    if os.path.exists("venv"):
        print("Virtual environment already exists")
        return True
    
    if not run_command("python -m venv venv", "Creating virtual environment"):
        return False
    
    print("Virtual environment created successfully!")
    return True


def install_requirements():
    """Install Python requirements."""
    print("Installing requirements...")
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_path = "venv/bin/pip"
    
    if not run_command(f"{pip_path} install -r requirements.txt", "Installing requirements"):
        return False
    
    print("Requirements installed successfully!")
    return True


def create_directories():
    """Create necessary directories."""
    print("Creating directories...")
    
    directories = ['uploads', 'outputs', 'static/js']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    return True


def run_tests():
    """Run basic application tests."""
    print("Running basic tests...")
    
    # Test imports
    try:
        import flask
        import pypdf
        import PIL
        import img2pdf
        print("All required packages imported successfully!")
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    
    # Test application startup
    try:
        from app import app
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("Application startup test passed!")
            else:
                print(f"Application startup test failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"Application test error: {e}")
        return False
    
    return True


def deploy_local():
    """Deploy application locally."""
    print("Starting local deployment...")
    
    if not check_dependencies():
        return False
    
    if not setup_virtual_environment():
        return False
    
    if not install_requirements():
        return False
    
    if not create_directories():
        return False
    
    if not run_tests():
        return False
    
    print("\n" + "="*50)
    print("LOCAL DEPLOYMENT SUCCESSFUL!")
    print("="*50)
    print("\nTo run the application:")
    if os.name == 'nt':  # Windows
        print("1. Activate virtual environment: venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("1. Activate virtual environment: source venv/bin/activate")
    print("2. Run application: python app.py")
    print("3. Open browser: http://localhost:5000")
    print("\nTo deploy to Vercel:")
    print("1. Install Vercel CLI: npm i -g vercel")
    print("2. Deploy: vercel --prod")
    
    return True


def deploy_vercel():
    """Deploy to Vercel."""
    print("Deploying to Vercel...")
    
    # Check if Vercel CLI is installed
    if not run_command("vercel --version", "Checking Vercel CLI"):
        print("Please install Vercel CLI: npm i -g vercel")
        return False
    
    # Deploy to Vercel
    if not run_command("vercel --prod", "Deploying to Vercel"):
        return False
    
    print("Vercel deployment completed!")
    return True


def main():
    """Main deployment function."""
    print("PyPDF Toolkit Web - Deployment Script")
    print("="*40)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "vercel":
            deploy_vercel()
        elif sys.argv[1] == "test":
            run_tests()
        else:
            print("Usage: python deploy.py [local|vercel|test]")
    else:
        deploy_local()


if __name__ == "__main__":
    main()
