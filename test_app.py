#!/usr/bin/env python3
"""
Test Suite for PyPDF Toolkit Web
Comprehensive testing for all PDF processing modules and API endpoints.
"""

import os
import sys
import unittest
import tempfile
import shutil
from io import BytesIO
from unittest.mock import patch, MagicMock

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from modules.pdf_merger import PDFMerger
from modules.pdf_splitter import PDFSplitter
from modules.pdf_compressor import PDFCompressor
from modules.pdf_converter import PDFConverter
from modules.pdf_unlocker import PDFUnlocker
from modules.error_handler import ErrorHandler, FileValidationError, ProcessingError


class TestPDFModules(unittest.TestCase):
    """Test PDF processing modules."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.merger = PDFMerger()
        self.splitter = PDFSplitter()
        self.compressor = PDFCompressor()
        self.converter = PDFConverter()
        self.unlocker = PDFUnlocker()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_pdf_merger_initialization(self):
        """Test PDF merger initialization."""
        self.assertIsInstance(self.merger, PDFMerger)
        self.assertIsNotNone(self.merger.writer)
    
    def test_pdf_splitter_initialization(self):
        """Test PDF splitter initialization."""
        self.assertIsInstance(self.splitter, PDFSplitter)
    
    def test_pdf_compressor_initialization(self):
        """Test PDF compressor initialization."""
        self.assertIsInstance(self.compressor, PDFCompressor)
    
    def test_pdf_converter_initialization(self):
        """Test PDF converter initialization."""
        self.assertIsInstance(self.converter, PDFConverter)
        self.assertIsInstance(self.converter.supported_image_formats, list)
    
    def test_pdf_unlocker_initialization(self):
        """Test PDF unlocker initialization."""
        self.assertIsInstance(self.unlocker, PDFUnlocker)
    
    def test_page_range_parsing(self):
        """Test page range parsing in merger."""
        # Test valid ranges
        pages = self.merger._parse_page_range("1-3", 10)
        self.assertEqual(pages, [0, 1, 2])
        
        pages = self.merger._parse_page_range("1,3,5", 10)
        self.assertEqual(pages, [0, 2, 4])
        
        pages = self.merger._parse_page_range("1-3,5,7-9", 10)
        self.assertEqual(pages, [0, 1, 2, 4, 6, 7, 8])
    
    def test_file_validation_with_mock_file(self):
        """Test file validation with mock file object."""
        # Create a mock file object
        mock_file = MagicMock()
        mock_file.filename = 'test.pdf'
        mock_file.content_length = 1024
        mock_file.mimetype = 'application/pdf'
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=1024)
        
        validation = ErrorHandler.validate_file_upload(mock_file, {'.pdf'})
        self.assertTrue(validation['valid'])
        self.assertEqual(validation['filename'], 'test.pdf')


class TestErrorHandler(unittest.TestCase):
    """Test error handling functionality."""
    
    def test_file_validation_no_file(self):
        """Test file validation with no file."""
        validation = ErrorHandler.validate_file_upload(None)
        self.assertFalse(validation['valid'])
        self.assertEqual(validation['error_code'], 'NO_FILE')
    
    def test_file_validation_invalid_extension(self):
        """Test file validation with invalid extension."""
        mock_file = MagicMock()
        mock_file.filename = 'test.txt'
        mock_file.content_length = 1024
        
        validation = ErrorHandler.validate_file_upload(mock_file, {'.pdf'})
        self.assertFalse(validation['valid'])
        self.assertEqual(validation['error_code'], 'INVALID_EXTENSION')
    
    def test_page_range_validation(self):
        """Test page range validation."""
        # Valid ranges
        validation = ErrorHandler.validate_page_range("1-5", 10)
        self.assertTrue(validation['valid'])
        self.assertEqual(validation['pages'], [1, 2, 3, 4, 5])
        
        # Invalid range
        validation = ErrorHandler.validate_page_range("1-15", 10)
        self.assertFalse(validation['valid'])
        self.assertEqual(validation['error_code'], 'INVALID_PAGE_RANGE')
    
    def test_filename_sanitization(self):
        """Test filename sanitization."""
        dangerous_filename = "../../../etc/passwd"
        sanitized = ErrorHandler.sanitize_filename(dangerous_filename)
        self.assertNotIn('../', sanitized)
        self.assertNotIn('/etc/', sanitized)
    
    def test_error_response_creation(self):
        """Test error response creation."""
        response, status_code = ErrorHandler.create_error_response("Test error", "TEST_ERROR", 400)
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], "Test error")
        self.assertEqual(response['error_code'], "TEST_ERROR")
        self.assertEqual(status_code, 400)


class TestFlaskApp(unittest.TestCase):
    """Test Flask application endpoints."""
    
    def setUp(self):
        """Set up test client."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_index_page(self):
        """Test index page loads."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PyPDF Toolkit Web', response.data)
    
    def test_merge_page(self):
        """Test merge page loads."""
        response = self.app.get('/merge')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Merge PDFs', response.data)
    
    def test_split_page(self):
        """Test split page loads."""
        response = self.app.get('/split')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Split PDF', response.data)
    
    def test_compress_page(self):
        """Test compress page loads."""
        response = self.app.get('/compress')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Compress PDF', response.data)
    
    def test_convert_page(self):
        """Test convert page loads."""
        response = self.app.get('/convert')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Convert Files', response.data)
    
    def test_unlock_page(self):
        """Test unlock page loads."""
        response = self.app.get('/unlock')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Unlock PDF', response.data)
    
    def test_api_merge_no_files(self):
        """Test merge API with no files."""
        response = self.app.post('/api/merge')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'NO_FILES')
    
    def test_api_split_no_file(self):
        """Test split API with no file."""
        response = self.app.post('/api/split')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['success'])
    
    def test_api_compress_no_file(self):
        """Test compress API with no file."""
        response = self.app.post('/api/compress')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['success'])
    
    def test_api_convert_no_files(self):
        """Test convert API with no files."""
        response = self.app.post('/api/convert', data={'conversion_type': 'images_to_pdf'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['success'])
    
    def test_api_unlock_no_file(self):
        """Test unlock API with no file."""
        response = self.app.post('/api/unlock')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['success'])
    
    def test_404_api_endpoint(self):
        """Test 404 for non-existent API endpoint."""
        response = self.app.get('/api/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_code'], 'ENDPOINT_NOT_FOUND')
    
    def test_404_page(self):
        """Test 404 for non-existent page."""
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.app = app.test_client()
        self.app.testing = True
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up integration test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_mock_pdf_file(self, filename="test.pdf", size=1024):
        """Create a mock PDF file for testing."""
        return (BytesIO(b'%PDF-1.4\n%Mock PDF content' + b'0' * (size - 25)), filename)
    
    def test_file_upload_validation_integration(self):
        """Test file upload validation in API endpoints."""
        # Test with mock PDF file
        mock_pdf = self.create_mock_pdf_file()
        
        response = self.app.post('/api/merge', data={
            'files': [mock_pdf]
        })
        
        # Should fail because we need at least 2 files
        data = response.get_json()
        self.assertFalse(data['success'])


def run_tests():
    """Run all tests."""
    print("PyPDF Toolkit Web - Test Suite")
    print("=" * 40)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPDFModules,
        TestErrorHandler,
        TestFlaskApp,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 40)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nTest Result: {'PASSED' if success else 'FAILED'}")
    
    return success


if __name__ == '__main__':
    # Set up test environment
    os.environ['TESTING'] = '1'
    
    # Run tests
    success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
