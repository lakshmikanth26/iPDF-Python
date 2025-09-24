"""
PDF Splitter Module
Handles splitting PDF files into multiple documents by page ranges.
"""

import os
from pypdf import PdfWriter, PdfReader
from typing import List, Dict, Optional


class PDFSplitter:
    """Class to handle PDF splitting operations."""
    
    def split_pdf(self, pdf_path: str, output_dir: str, 
                  split_ranges: Optional[List[Dict]] = None) -> List[str]:
        """
        Split a PDF file into multiple files based on page ranges.
        
        Args:
            pdf_path: Path to the PDF file to split
            output_dir: Directory where split PDFs will be saved
            split_ranges: List of dictionaries with 'start', 'end', and 'name' keys
                         If None, splits into individual pages
        
        Returns:
            List of paths to created PDF files
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            created_files = []
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            if split_ranges:
                # Split based on provided ranges
                for i, range_info in enumerate(split_ranges):
                    start = max(0, range_info.get('start', 1) - 1)  # Convert to 0-based
                    end = min(total_pages, range_info.get('end', total_pages))
                    name = range_info.get('name', f'split_{i+1}')
                    
                    if start < end:
                        output_path = os.path.join(output_dir, f"{name}.pdf")
                        if self._create_pdf_from_pages(reader, start, end, output_path):
                            created_files.append(output_path)
            else:
                # Split into individual pages
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                for page_num in range(total_pages):
                    output_path = os.path.join(output_dir, f"{base_name}_page_{page_num + 1}.pdf")
                    if self._create_pdf_from_pages(reader, page_num, page_num + 1, output_path):
                        created_files.append(output_path)
            
            return created_files
            
        except Exception as e:
            print(f"Error splitting PDF: {str(e)}")
            return []
    
    def split_by_page_count(self, pdf_path: str, output_dir: str, pages_per_file: int) -> List[str]:
        """
        Split PDF into files with specified number of pages each.
        
        Args:
            pdf_path: Path to the PDF file to split
            output_dir: Directory where split PDFs will be saved
            pages_per_file: Number of pages per output file
        
        Returns:
            List of paths to created PDF files
        """
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            created_files = []
            
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            for start in range(0, total_pages, pages_per_file):
                end = min(start + pages_per_file, total_pages)
                file_num = (start // pages_per_file) + 1
                output_path = os.path.join(output_dir, f"{base_name}_part_{file_num}.pdf")
                
                if self._create_pdf_from_pages(reader, start, end, output_path):
                    created_files.append(output_path)
            
            return created_files
            
        except Exception as e:
            print(f"Error splitting PDF by page count: {str(e)}")
            return []
    
    def extract_pages(self, pdf_path: str, output_path: str, page_numbers: List[int]) -> bool:
        """
        Extract specific pages from a PDF and create a new PDF.
        
        Args:
            pdf_path: Path to the source PDF file
            output_path: Path for the output PDF file
            page_numbers: List of page numbers to extract (1-based)
        
        Returns:
            bool: True if extraction successful, False otherwise
        """
        try:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            for page_num in page_numbers:
                # Convert to 0-based indexing
                page_index = page_num - 1
                if 0 <= page_index < len(reader.pages):
                    writer.add_page(reader.pages[page_index])
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error extracting pages: {str(e)}")
            return False
    
    def _create_pdf_from_pages(self, reader: PdfReader, start: int, end: int, output_path: str) -> bool:
        """
        Create a PDF file from a range of pages.
        
        Args:
            reader: PdfReader object
            start: Start page index (0-based, inclusive)
            end: End page index (0-based, exclusive)
            output_path: Path for the output PDF file
        
        Returns:
            bool: True if creation successful, False otherwise
        """
        try:
            writer = PdfWriter()
            
            for page_index in range(start, end):
                if page_index < len(reader.pages):
                    writer.add_page(reader.pages[page_index])
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error creating PDF from pages: {str(e)}")
            return False
    
    def get_pdf_page_info(self, pdf_path: str) -> Dict:
        """
        Get detailed information about PDF pages.
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            Dictionary with page information
        """
        try:
            reader = PdfReader(pdf_path)
            pages_info = []
            
            for i, page in enumerate(reader.pages):
                page_info = {
                    'page_number': i + 1,
                    'width': float(page.mediabox.width),
                    'height': float(page.mediabox.height),
                    'rotation': page.get('/Rotate', 0)
                }
                pages_info.append(page_info)
            
            return {
                'total_pages': len(reader.pages),
                'pages': pages_info,
                'encrypted': reader.is_encrypted
            }
            
        except Exception as e:
            return {'error': str(e)}
