"""
Error Handler Module
Provides comprehensive error handling and validation for the PyPDF Toolkit Web application.
"""

import os
import logging
import traceback
from functools import wraps
from typing import Dict, Any, Optional, List
from werkzeug.utils import secure_filename


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class PDFToolkitError(Exception):
    """Base exception class for PDF Toolkit errors."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code or 'UNKNOWN_ERROR'
        self.details = details or {}
        super().__init__(self.message)


class FileValidationError(PDFToolkitError):
    """Exception for file validation errors."""
    pass


class ProcessingError(PDFToolkitError):
    """Exception for PDF processing errors."""
    pass


class SecurityError(PDFToolkitError):
    """Exception for security-related errors."""
    pass


class ErrorHandler:
    """Comprehensive error handling and validation class."""
    
    # File validation constants
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    MAX_FILES_PER_REQUEST = 10
    ALLOWED_PDF_EXTENSIONS = {'.pdf'}
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/gif'
    }
    
    # Security patterns to check
    DANGEROUS_PATTERNS = [
        '../', '..\\', '/etc/', '/proc/', '/sys/', 'C:\\Windows\\',
        '<script', 'javascript:', 'data:', 'vbscript:', 'onload=', 'onerror='
    ]
    
    @staticmethod
    def validate_file_upload(file, allowed_extensions: set = None, max_size: int = None) -> Dict[str, Any]:
        """
        Validate uploaded file for security and format compliance.
        
        Args:
            file: Werkzeug FileStorage object
            allowed_extensions: Set of allowed file extensions
            max_size: Maximum file size in bytes
        
        Returns:
            Dict with validation results
        """
        try:
            if not file or not file.filename:
                raise FileValidationError("No file provided", "NO_FILE")
            
            filename = secure_filename(file.filename)
            if not filename:
                raise FileValidationError("Invalid filename", "INVALID_FILENAME")
            
            # Check file extension
            file_ext = os.path.splitext(filename)[1].lower()
            if allowed_extensions and file_ext not in allowed_extensions:
                raise FileValidationError(
                    f"File extension '{file_ext}' not allowed. Allowed: {', '.join(allowed_extensions)}",
                    "INVALID_EXTENSION"
                )
            
            # Check file size
            max_size = max_size or ErrorHandler.MAX_FILE_SIZE
            if hasattr(file, 'content_length') and file.content_length:
                file_size = file.content_length
            else:
                # Fallback: seek to end to get size
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
            
            if file_size > max_size:
                raise FileValidationError(
                    f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
                    "FILE_TOO_LARGE"
                )
            
            # Check for dangerous patterns in filename
            for pattern in ErrorHandler.DANGEROUS_PATTERNS:
                if pattern in filename.lower():
                    raise SecurityError(f"Dangerous pattern detected in filename: {pattern}", "SECURITY_VIOLATION")
            
            # Validate MIME type if available
            if hasattr(file, 'mimetype') and file.mimetype:
                if file.mimetype not in ErrorHandler.ALLOWED_MIME_TYPES:
                    logger.warning(f"Suspicious MIME type: {file.mimetype} for file: {filename}")
            
            return {
                'valid': True,
                'filename': filename,
                'size': file_size,
                'extension': file_ext
            }
            
        except (FileValidationError, SecurityError) as e:
            logger.error(f"File validation error: {e.message}")
            return {
                'valid': False,
                'error': e.message,
                'error_code': e.error_code
            }
        except Exception as e:
            logger.error(f"Unexpected error during file validation: {str(e)}")
            return {
                'valid': False,
                'error': "File validation failed",
                'error_code': "VALIDATION_ERROR"
            }
    
    @staticmethod
    def validate_multiple_files(files: List, allowed_extensions: set = None, max_files: int = None) -> Dict[str, Any]:
        """
        Validate multiple file uploads.
        
        Args:
            files: List of FileStorage objects
            allowed_extensions: Set of allowed file extensions
            max_files: Maximum number of files allowed
        
        Returns:
            Dict with validation results
        """
        try:
            if not files:
                raise FileValidationError("No files provided", "NO_FILES")
            
            max_files = max_files or ErrorHandler.MAX_FILES_PER_REQUEST
            if len(files) > max_files:
                raise FileValidationError(
                    f"Too many files ({len(files)}). Maximum allowed: {max_files}",
                    "TOO_MANY_FILES"
                )
            
            valid_files = []
            errors = []
            total_size = 0
            
            for i, file in enumerate(files):
                validation = ErrorHandler.validate_file_upload(file, allowed_extensions)
                
                if validation['valid']:
                    valid_files.append({
                        'file': file,
                        'filename': validation['filename'],
                        'size': validation['size'],
                        'extension': validation['extension']
                    })
                    total_size += validation['size']
                else:
                    errors.append(f"File {i+1}: {validation['error']}")
            
            # Check total size
            if total_size > ErrorHandler.MAX_FILE_SIZE * 2:  # Allow double for multiple files
                raise FileValidationError(
                    f"Total file size ({total_size} bytes) too large",
                    "TOTAL_SIZE_TOO_LARGE"
                )
            
            return {
                'valid': len(valid_files) > 0,
                'valid_files': valid_files,
                'errors': errors,
                'total_size': total_size
            }
            
        except FileValidationError as e:
            logger.error(f"Multiple file validation error: {e.message}")
            return {
                'valid': False,
                'valid_files': [],
                'errors': [e.message],
                'error_code': e.error_code
            }
        except Exception as e:
            logger.error(f"Unexpected error during multiple file validation: {str(e)}")
            return {
                'valid': False,
                'valid_files': [],
                'errors': ["File validation failed"],
                'error_code': "VALIDATION_ERROR"
            }
    
    @staticmethod
    def validate_page_range(page_range: str, total_pages: int) -> Dict[str, Any]:
        """
        Validate page range string.
        
        Args:
            page_range: Page range string (e.g., "1-5", "1,3,5", "all")
            total_pages: Total number of pages in the document
        
        Returns:
            Dict with validation results
        """
        try:
            if not page_range or page_range.strip().lower() == 'all':
                return {'valid': True, 'pages': list(range(1, total_pages + 1))}
            
            pages = set()
            parts = page_range.split(',')
            
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                
                if '-' in part:
                    # Handle range like "1-5"
                    try:
                        start, end = map(int, part.split('-', 1))
                        if start < 1 or end > total_pages or start > end:
                            raise ValueError(f"Invalid range: {part}")
                        pages.update(range(start, end + 1))
                    except ValueError:
                        raise FileValidationError(f"Invalid page range format: {part}", "INVALID_PAGE_RANGE")
                else:
                    # Handle single page like "5"
                    try:
                        page = int(part)
                        if page < 1 or page > total_pages:
                            raise ValueError(f"Page {page} out of range")
                        pages.add(page)
                    except ValueError:
                        raise FileValidationError(f"Invalid page number: {part}", "INVALID_PAGE_NUMBER")
            
            if not pages:
                raise FileValidationError("No valid pages specified", "NO_PAGES")
            
            return {'valid': True, 'pages': sorted(list(pages))}
            
        except FileValidationError as e:
            logger.error(f"Page range validation error: {e.message}")
            return {'valid': False, 'error': e.message, 'error_code': e.error_code}
        except Exception as e:
            logger.error(f"Unexpected error during page range validation: {str(e)}")
            return {'valid': False, 'error': "Page range validation failed", 'error_code': "VALIDATION_ERROR"}
    
    @staticmethod
    def handle_processing_error(func):
        """
        Decorator for handling processing errors in PDF operations.
        
        Args:
            func: Function to wrap
        
        Returns:
            Wrapped function with error handling
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                logger.error(f"File not found in {func.__name__}: {str(e)}")
                return {'success': False, 'error': 'File not found', 'error_code': 'FILE_NOT_FOUND'}
            except PermissionError as e:
                logger.error(f"Permission error in {func.__name__}: {str(e)}")
                return {'success': False, 'error': 'Permission denied', 'error_code': 'PERMISSION_DENIED'}
            except MemoryError as e:
                logger.error(f"Memory error in {func.__name__}: {str(e)}")
                return {'success': False, 'error': 'File too large to process', 'error_code': 'MEMORY_ERROR'}
            except ProcessingError as e:
                logger.error(f"Processing error in {func.__name__}: {e.message}")
                return {'success': False, 'error': e.message, 'error_code': e.error_code}
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return {'success': False, 'error': 'Processing failed', 'error_code': 'PROCESSING_ERROR'}
        
        return wrapper
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe storage.
        
        Args:
            filename: Original filename
        
        Returns:
            Sanitized filename
        """
        # Use werkzeug's secure_filename and add additional sanitization
        filename = secure_filename(filename)
        
        # Remove any remaining dangerous patterns
        for pattern in ErrorHandler.DANGEROUS_PATTERNS:
            filename = filename.replace(pattern, '')
        
        # Ensure filename is not empty and has reasonable length
        if not filename:
            filename = 'unnamed_file'
        
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def create_error_response(error_message: str, error_code: str = None, status_code: int = 400) -> tuple:
        """
        Create standardized error response.
        
        Args:
            error_message: Error message
            error_code: Error code
            status_code: HTTP status code
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        response = {
            'success': False,
            'error': error_message,
            'error_code': error_code or 'UNKNOWN_ERROR'
        }
        
        logger.error(f"API Error: {error_message} (Code: {error_code})")
        
        return response, status_code
    
    @staticmethod
    def log_operation(operation: str, details: Dict[str, Any] = None):
        """
        Log operation for monitoring and debugging.
        
        Args:
            operation: Operation name
            details: Additional details to log
        """
        log_message = f"Operation: {operation}"
        if details:
            log_message += f" | Details: {details}"
        
        logger.info(log_message)
