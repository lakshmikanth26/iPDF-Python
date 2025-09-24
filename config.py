"""
Configuration file for PyPDF Toolkit Web
Contains all configuration settings and constants for the application.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Application settings
class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    OUTPUT_FOLDER = BASE_DIR / 'outputs'
    MAX_FILES_PER_REQUEST = 10
    
    # Allowed file types
    ALLOWED_PDF_EXTENSIONS = {'.pdf'}
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/gif'
    }
    
    # Processing settings
    PDF_COMPRESSION_LEVELS = ['low', 'medium', 'high']
    IMAGE_DPI_OPTIONS = [150, 200, 300, 400]
    PAGE_SIZE_OPTIONS = ['A4', 'Letter', 'Legal']
    
    # Security settings
    FILE_CLEANUP_INTERVAL = 3600  # 1 hour in seconds
    MAX_FILENAME_LENGTH = 255
    DANGEROUS_PATTERNS = [
        '../', '..\\', '/etc/', '/proc/', '/sys/', 'C:\\Windows\\',
        '<script', 'javascript:', 'data:', 'vbscript:', 'onload=', 'onerror='
    ]
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = BASE_DIR / 'app.log'
    
    # API settings
    API_RATE_LIMIT = '100/hour'  # Rate limiting for API endpoints
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Ensure directories exist
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True)
        Config.OUTPUT_FOLDER.mkdir(exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    
    # Use temporary directories for testing
    import tempfile
    UPLOAD_FOLDER = Path(tempfile.mkdtemp())
    OUTPUT_FOLDER = Path(tempfile.mkdtemp())


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    return config[config_name]
