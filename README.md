# PyPDF Toolkit Web

A comprehensive Python Flask web application for PDF processing with professional-grade features including merge, split, compress, convert, and unlock capabilities.

## Features

### 🔗 PDF Merging
- Combine multiple PDF files into a single document
- Support for custom page ranges (e.g., "1-3", "all", "2,4,6")
- Preserve document metadata
- Drag-and-drop file upload interface

### ✂️ PDF Splitting
- Split PDF by page ranges or individual pages
- Extract specific pages from documents
- Split by number of pages per file
- Bulk processing with ZIP download

### 🗜️ PDF Compression
- Multiple compression levels (low, medium, high)
- Reduce file size while maintaining quality
- Image optimization within PDFs
- Metadata removal for privacy
- Real-time compression estimates

### 🔄 File Conversion
- **Images to PDF**: Convert JPG, PNG, BMP, TIFF, GIF to PDF
- **PDF to Images**: Extract pages as individual images
- Custom page sizes (A4, Letter, Legal)
- Adjustable image quality and DPI settings
- Batch image processing

### 🔓 PDF Unlocking
- Remove password protection from secured PDFs
- Try common passwords automatically
- Support for custom password lists
- Encryption status checking
- Security-conscious processing

## Technology Stack

- **Backend**: Python 3.8+ with Flask
- **PDF Processing**: PyPDF for core PDF operations
- **Image Processing**: Pillow (PIL) for image manipulation
- **Image to PDF**: img2pdf for efficient conversion
- **Frontend**: Modern HTML5, CSS3, and JavaScript
- **Deployment**: Vercel-ready configuration
- **UI/UX**: Responsive design with drag-and-drop functionality

## Installation & Setup

### 🚀 Quick Start (Recommended)

We provide cross-platform setup scripts that automatically detect your operating system and handle the entire setup process:

#### Windows Users
```powershell
# PowerShell (Recommended)
.\setup.ps1

# Command Prompt
setup.bat
```

#### macOS/Linux Users
```bash
# Make executable and run
chmod +x setup.sh
./setup.sh
```

#### Setup Options
- `--skip-venv` - Skip virtual environment creation
- `--force` - Force reinstall even if already set up
- `--help` - Show help message

### Manual Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/iPDF-Python.git
   cd iPDF-Python
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

> 📖 **Need help?** See the detailed [Quick Start Guide](QUICK_START.md) for platform-specific instructions and troubleshooting.

### Vercel Deployment

This application is configured for easy deployment on Vercel:

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy to Vercel**:
   ```bash
   vercel --prod
   ```

The `vercel.json` configuration file is already included for seamless deployment.

## Project Structure

```
iPDF-Python/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment configuration
├── modules/              # PDF processing modules
│   ├── __init__.py
│   ├── pdf_merger.py     # PDF merging functionality
│   ├── pdf_splitter.py   # PDF splitting functionality
│   ├── pdf_compressor.py # PDF compression functionality
│   ├── pdf_converter.py  # PDF/Image conversion functionality
│   └── pdf_unlocker.py   # PDF password removal functionality
├── templates/            # HTML templates
│   ├── base.html         # Base template with common elements
│   ├── index.html        # Home page
│   ├── merge.html        # PDF merge interface
│   ├── split.html        # PDF split interface
│   ├── compress.html     # PDF compression interface
│   ├── convert.html      # File conversion interface
│   └── unlock.html       # PDF unlock interface
├── static/               # Static assets
│   └── css/
│       └── style.css     # Modern CSS styling
├── uploads/              # Temporary upload directory
└── outputs/              # Processed files directory
```

## API Endpoints

### Core Processing APIs
- `POST /api/merge` - Merge multiple PDFs
- `POST /api/split` - Split PDF into multiple files
- `POST /api/compress` - Compress PDF file size
- `POST /api/convert` - Convert between PDF and image formats
- `POST /api/unlock` - Remove PDF password protection

### Utility APIs
- `POST /api/pdf-info` - Get PDF file information
- `GET /download/<filename>` - Download processed files

## Usage Examples

### PDF Merging
```python
from modules.pdf_merger import PDFMerger

merger = PDFMerger()
success = merger.merge_pdfs(
    pdf_paths=['file1.pdf', 'file2.pdf'],
    output_path='merged.pdf',
    page_ranges=['1-3', 'all']  # Optional
)
```

### PDF Splitting
```python
from modules.pdf_splitter import PDFSplitter

splitter = PDFSplitter()
created_files = splitter.split_by_page_count(
    pdf_path='large_file.pdf',
    output_dir='split_output/',
    pages_per_file=5
)
```

### PDF Compression
```python
from modules.pdf_compressor import PDFCompressor

compressor = PDFCompressor()
result = compressor.compress_pdf(
    input_path='large_file.pdf',
    output_path='compressed.pdf',
    compression_level='medium'
)
```

## Security Features

- **File Validation**: Strict file type checking and validation
- **Temporary Storage**: Automatic cleanup of uploaded and processed files
- **Privacy Protection**: Files are processed locally and deleted after 1 hour
- **Password Security**: Secure handling of PDF passwords
- **Error Handling**: Comprehensive error handling and user feedback

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PyPDF](https://pypdf.readthedocs.io/) for PDF processing capabilities
- [Pillow](https://pillow.readthedocs.io/) for image processing
- [img2pdf](https://gitlab.mister-muffin.de/josch/img2pdf) for efficient image to PDF conversion
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Vercel](https://vercel.com/) for deployment platform

## Support

For support, email support@example.com or create an issue in this repository.

---

**Built with ❤️ using Python and Flask**
