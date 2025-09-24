"""
PDF Merger Module
Handles merging multiple PDF files into a single PDF document.
"""

import os
from pypdf import PdfWriter, PdfReader
from typing import List, Optional


class PDFMerger:
    """Class to handle PDF merging operations."""
    
    def __init__(self):
        self.writer = PdfWriter()
    
    def merge_pdfs(self, pdf_paths: List[str], output_path: str, 
                   page_ranges: Optional[List[str]] = None) -> bool:
        """
        Merge multiple PDF files into one.
        
        Args:
            pdf_paths: List of paths to PDF files to merge
            output_path: Path where the merged PDF will be saved
            page_ranges: Optional list of page ranges for each PDF (e.g., ["1-3", "all", "2,4,6"])
        
        Returns:
            bool: True if merge successful, False otherwise
        """
        try:
            for i, pdf_path in enumerate(pdf_paths):
                if not os.path.exists(pdf_path):
                    raise FileNotFoundError(f"PDF file not found: {pdf_path}")
                
                reader = PdfReader(pdf_path)
                
                # Determine which pages to include
                if page_ranges and i < len(page_ranges) and page_ranges[i] != "all":
                    pages_to_add = self._parse_page_range(page_ranges[i], len(reader.pages))
                else:
                    pages_to_add = list(range(len(reader.pages)))
                
                # Add specified pages to the writer
                for page_num in pages_to_add:
                    if 0 <= page_num < len(reader.pages):
                        self.writer.add_page(reader.pages[page_num])
            
            # Write the merged PDF
            with open(output_path, 'wb') as output_file:
                self.writer.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error merging PDFs: {str(e)}")
            return False
    
    def _parse_page_range(self, page_range: str, total_pages: int) -> List[int]:
        """
        Parse page range string into list of page indices (0-based).
        
        Args:
            page_range: String like "1-3", "1,3,5", or "1-3,5,7-9"
            total_pages: Total number of pages in the PDF
        
        Returns:
            List of 0-based page indices
        """
        pages = []
        parts = page_range.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Handle range like "1-3"
                start, end = map(int, part.split('-'))
                # Convert to 0-based indexing
                start = max(0, start - 1)
                end = min(total_pages, end)
                pages.extend(range(start, end))
            else:
                # Handle single page like "5"
                page = int(part) - 1  # Convert to 0-based
                if 0 <= page < total_pages:
                    pages.append(page)
        
        return sorted(list(set(pages)))  # Remove duplicates and sort
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get information about a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            Dictionary with PDF information
        """
        try:
            reader = PdfReader(pdf_path)
            return {
                'pages': len(reader.pages),
                'encrypted': reader.is_encrypted,
                'title': reader.metadata.get('/Title', 'Unknown') if reader.metadata else 'Unknown',
                'author': reader.metadata.get('/Author', 'Unknown') if reader.metadata else 'Unknown'
            }
        except Exception as e:
            return {'error': str(e)}
