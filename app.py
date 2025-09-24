"""
PyPDF Toolkit Web - Main Flask Application
A comprehensive PDF processing web application with merge, split, compress, convert, and unlock features.
"""

import os
import sys
import uuid
import tempfile
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import shutil

# Import our PDF processing modules
from modules.pdf_merger import PDFMerger
from modules.pdf_splitter import PDFSplitter
from modules.pdf_compressor import PDFCompressor
from modules.pdf_converter import PDFConverter
from modules.pdf_unlocker import PDFUnlocker
from modules.error_handler import ErrorHandler, PDFToolkitError, FileValidationError, ProcessingError

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production!

# Configure Flask for better error handling
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize PDF processing classes
pdf_merger = PDFMerger()
pdf_splitter = PDFSplitter()
pdf_compressor = PDFCompressor()
pdf_converter = PDFConverter()
pdf_unlocker = PDFUnlocker()


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files():
    """Clean up old uploaded and output files (older than 1 hour)."""
    try:
        current_time = datetime.now()
        for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                        if current_time - file_time > timedelta(hours=1):
                            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up files: {str(e)}")


@app.before_request
def before_request():
    """Run cleanup before each request."""
    cleanup_old_files()


@app.route('/')
def index():
    """Main page with feature selection."""
    return render_template('index.html')


@app.route('/merge')
def merge_page():
    """PDF merge page."""
    return render_template('merge.html')


@app.route('/split')
def split_page():
    """PDF split page."""
    return render_template('split.html')


@app.route('/compress')
def compress_page():
    """PDF compress page."""
    return render_template('compress.html')


@app.route('/convert')
def convert_page():
    """PDF convert page."""
    return render_template('convert.html')


@app.route('/unlock')
def unlock_page():
    """PDF unlock page."""
    return render_template('unlock.html')


@app.route('/api/merge', methods=['POST'])
def api_merge_pdfs():
    """API endpoint to merge PDF files."""
    try:
        ErrorHandler.log_operation("merge_pdfs_request", {"files_count": len(request.files.getlist('files'))})
        
        if 'files' not in request.files:
            return jsonify(ErrorHandler.create_error_response('No files uploaded', 'NO_FILES')[0])
        
        files = request.files.getlist('files')
        
        # Validate multiple files
        validation = ErrorHandler.validate_multiple_files(files, ErrorHandler.ALLOWED_PDF_EXTENSIONS, max_files=10)
        
        if not validation['valid']:
            return jsonify(ErrorHandler.create_error_response(
                '; '.join(validation['errors']), 
                validation.get('error_code', 'VALIDATION_ERROR')
            )[0])
        
        if len(validation['valid_files']) < 2:
            return jsonify(ErrorHandler.create_error_response(
                'At least 2 valid PDF files required', 
                'INSUFFICIENT_FILES'
            )[0])
        
        # Save uploaded files
        uploaded_paths = []
        for file_info in validation['valid_files']:
            filename = f"{uuid.uuid4()}_{file_info['filename']}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file_info['file'].save(file_path)
            uploaded_paths.append(file_path)
        
        # Generate output filename
        output_filename = f"merged_{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Get and validate page ranges if provided
        page_ranges_str = request.form.get('page_ranges', '').strip()
        page_ranges = None
        if page_ranges_str:
            page_ranges = [range.strip() if range.strip() else 'all' for range in page_ranges_str.split(',')]
        
        # Merge PDFs with error handling
        @ErrorHandler.handle_processing_error
        def perform_merge():
            return pdf_merger.merge_pdfs(uploaded_paths, output_path, page_ranges)
        
        result = perform_merge()
        if isinstance(result, dict) and not result.get('success', True):
            return jsonify(result)
        
        success = result if isinstance(result, bool) else result.get('success', False)
        
        if success:
            ErrorHandler.log_operation("merge_pdfs_success", {
                "files_merged": len(uploaded_paths),
                "output_file": output_filename
            })
            return jsonify({
                'success': True,
                'download_url': f'/download/{output_filename}',
                'filename': output_filename
            })
        else:
            return jsonify(ErrorHandler.create_error_response('Failed to merge PDFs', 'MERGE_FAILED')[0])
    
    except PDFToolkitError as e:
        return jsonify(ErrorHandler.create_error_response(e.message, e.error_code)[0])
    except Exception as e:
        return jsonify(ErrorHandler.create_error_response(f'Unexpected error: {str(e)}', 'INTERNAL_ERROR')[0])


@app.route('/api/split', methods=['POST'])
def api_split_pdf():
    """API endpoint to split PDF files."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if not file or not allowed_file(file.filename) or not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Please upload a valid PDF file'})
        
        # Save uploaded file
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Create output directory for split files
        output_dir = os.path.join(OUTPUT_FOLDER, f"split_{uuid.uuid4()}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Get split options
        split_type = request.form.get('split_type', 'pages')
        
        if split_type == 'pages':
            # Split by page count
            pages_per_file = int(request.form.get('pages_per_file', 1))
            created_files = pdf_splitter.split_by_page_count(file_path, output_dir, pages_per_file)
        elif split_type == 'ranges':
            # Split by custom ranges
            ranges_str = request.form.get('page_ranges', '')
            if not ranges_str:
                return jsonify({'success': False, 'error': 'Page ranges required'})
            
            # Parse ranges
            split_ranges = []
            for i, range_str in enumerate(ranges_str.split(',')):
                range_str = range_str.strip()
                if '-' in range_str:
                    start, end = map(int, range_str.split('-'))
                    split_ranges.append({'start': start, 'end': end, 'name': f'range_{i+1}'})
                else:
                    page = int(range_str)
                    split_ranges.append({'start': page, 'end': page, 'name': f'page_{page}'})
            
            created_files = pdf_splitter.split_pdf(file_path, output_dir, split_ranges)
        else:
            # Split into individual pages
            created_files = pdf_splitter.split_pdf(file_path, output_dir)
        
        if created_files:
            # Create a zip file with all split PDFs
            import zipfile
            zip_filename = f"split_pdfs_{uuid.uuid4()}.zip"
            zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for pdf_file in created_files:
                    zipf.write(pdf_file, os.path.basename(pdf_file))
            
            return jsonify({
                'success': True,
                'download_url': f'/download/{zip_filename}',
                'filename': zip_filename,
                'files_created': len(created_files)
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to split PDF'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/compress', methods=['POST'])
def api_compress_pdf():
    """API endpoint to compress PDF files."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if not file or not allowed_file(file.filename) or not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Please upload a valid PDF file'})
        
        # Save uploaded file
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Generate output filename
        output_filename = f"compressed_{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Get compression level
        compression_level = request.form.get('compression_level', 'medium')
        
        # Compress PDF
        result = pdf_compressor.compress_pdf(file_path, output_path, compression_level)
        
        if result['success']:
            result['download_url'] = f'/download/{output_filename}'
            result['filename'] = output_filename
            return jsonify(result)
        else:
            return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/convert', methods=['POST'])
def api_convert_files():
    """API endpoint to convert between PDF and images."""
    try:
        conversion_type = request.form.get('conversion_type')
        
        if conversion_type == 'images_to_pdf':
            if 'files' not in request.files:
                return jsonify({'success': False, 'error': 'No files uploaded'})
            
            files = request.files.getlist('files')
            if not files:
                return jsonify({'success': False, 'error': 'No image files provided'})
            
            # Save uploaded images
            uploaded_paths = []
            for file in files:
                if file and allowed_file(file.filename):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    if ext in ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif']:
                        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                        file_path = os.path.join(UPLOAD_FOLDER, filename)
                        file.save(file_path)
                        uploaded_paths.append(file_path)
            
            if not uploaded_paths:
                return jsonify({'success': False, 'error': 'No valid image files found'})
            
            # Generate output filename
            output_filename = f"converted_{uuid.uuid4()}.pdf"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            # Convert images to PDF
            result = pdf_converter.images_to_pdf(uploaded_paths, output_path)
            
            if result['success']:
                result['download_url'] = f'/download/{output_filename}'
                result['filename'] = output_filename
                return jsonify(result)
            else:
                return jsonify(result)
        
        elif conversion_type == 'pdf_to_images':
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file uploaded'})
            
            file = request.files['file']
            if not file or not file.filename.lower().endswith('.pdf'):
                return jsonify({'success': False, 'error': 'Please upload a valid PDF file'})
            
            # Save uploaded file
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Create output directory
            output_dir = os.path.join(OUTPUT_FOLDER, f"images_{uuid.uuid4()}")
            
            # Get conversion options
            image_format = request.form.get('image_format', 'PNG')
            dpi = int(request.form.get('dpi', 200))
            
            # Convert PDF to images
            result = pdf_converter.pdf_to_images(file_path, output_dir, image_format, dpi)
            
            return jsonify(result)
        
        else:
            return jsonify({'success': False, 'error': 'Invalid conversion type'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/unlock', methods=['POST'])
def api_unlock_pdf():
    """API endpoint to unlock password-protected PDF files."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if not file or not allowed_file(file.filename) or not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Please upload a valid PDF file'})
        
        # Save uploaded file
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Generate output filename
        output_filename = f"unlocked_{uuid.uuid4()}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Get password
        password = request.form.get('password', '')
        
        if password:
            # Try with provided password
            result = pdf_unlocker.unlock_pdf(file_path, output_path, password)
        else:
            # Try common passwords
            result = pdf_unlocker.try_common_passwords(file_path, output_path)
        
        if result['success']:
            result['download_url'] = f'/download/{output_filename}'
            result['filename'] = output_filename
            return jsonify(result)
        else:
            return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/download/<filename>')
def download_file(filename):
    """Download processed files."""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pdf-info', methods=['POST'])
def api_pdf_info():
    """API endpoint to get PDF file information."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if not file or not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Please upload a valid PDF file'})
        
        # Save uploaded file temporarily
        filename = secure_filename(f"temp_{uuid.uuid4()}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Get PDF info
        info = pdf_merger.get_pdf_info(file_path)
        encryption_info = pdf_unlocker.check_pdf_encryption(file_path)
        
        # Combine information
        combined_info = {**info, **encryption_info}
        
        # Clean up temp file
        os.remove(file_path)
        
        return jsonify({'success': True, 'info': combined_info})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# Global error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify(ErrorHandler.create_error_response(
        'File too large. Maximum size is 16MB', 
        'FILE_TOO_LARGE'
    )[0]), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify(ErrorHandler.create_error_response(
            'API endpoint not found', 
            'ENDPOINT_NOT_FOUND'
        )[0]), 404
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    ErrorHandler.log_operation("internal_server_error", {"error": str(error)})
    if request.path.startswith('/api/'):
        return jsonify(ErrorHandler.create_error_response(
            'Internal server error', 
            'INTERNAL_ERROR'
        )[0]), 500
    return render_template('index.html'), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle unexpected exceptions."""
    ErrorHandler.log_operation("unexpected_exception", {"error": str(e), "type": type(e).__name__})
    if request.path.startswith('/api/'):
        return jsonify(ErrorHandler.create_error_response(
            'An unexpected error occurred', 
            'UNEXPECTED_ERROR'
        )[0]), 500
    return render_template('index.html'), 500


def find_free_port(start_port=5000, max_port=5010):
    """Find a free port starting from start_port."""
    import socket
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None


if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Find available port (check environment variable first)
    env_port = os.environ.get('PORT')
    if env_port:
        try:
            port = int(env_port)
            print(f"🔧 Using port {port} from PORT environment variable")
        except ValueError:
            print(f"❌ Invalid PORT environment variable: {env_port}")
            sys.exit(1)
    else:
        port = find_free_port()
        if port is None:
            print("❌ No available ports found between 5000-5010")
            print("Please check running processes or specify a different port")
            print("💡 You can also set a custom port: PORT=8000 python app.py")
            sys.exit(1)
    
    # Log startup
    ErrorHandler.log_operation("application_startup", {
        "upload_folder": UPLOAD_FOLDER,
        "output_folder": OUTPUT_FOLDER,
        "max_file_size": MAX_FILE_SIZE,
        "port": port
    })
    
    if port != 5000:
        print(f"⚠️  Port 5000 is busy, using port {port} instead")
        print(f"💡 On macOS, you can disable AirPlay Receiver in System Preferences -> Sharing")
    
    print(f"🚀 Starting PyPDF Toolkit Web on http://localhost:{port}")
    print(f"📱 Also accessible at http://0.0.0.0:{port}")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print(f"\n👋 PyPDF Toolkit Web stopped gracefully")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
