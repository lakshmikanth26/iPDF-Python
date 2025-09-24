"""
PDF Compressor Module
Handles PDF file compression to reduce file size.
"""

import os
from pypdf import PdfWriter, PdfReader
from typing import Optional, Dict


class PDFCompressor:
    """Class to handle PDF compression operations."""
    
    def compress_pdf(self, input_path: str, output_path: str, 
                    compression_level: str = 'medium') -> Dict:
        """
        Compress a PDF file to reduce its size.
        
        Args:
            input_path: Path to the input PDF file
            output_path: Path for the compressed PDF file
            compression_level: Compression level ('low', 'medium', 'high')
        
        Returns:
            Dictionary with compression results and statistics
        """
        try:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"PDF file not found: {input_path}")
            
            original_size = os.path.getsize(input_path)
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Copy all pages to writer
            for page in reader.pages:
                # Apply compression based on level
                if compression_level == 'high':
                    page.compress_content_streams()
                    page.scale_by(0.9)  # Slightly reduce page size
                elif compression_level == 'medium':
                    page.compress_content_streams()
                elif compression_level == 'low':
                    pass  # Minimal compression
                
                writer.add_page(page)
            
            # Apply writer-level compression
            if compression_level in ['medium', 'high']:
                writer.compress_identical_objects()
                writer.remove_duplication()
            
            # Write the compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (original_size - compressed_size) / original_size * 100
            
            return {
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': round(compression_ratio, 2),
                'size_reduction': original_size - compressed_size
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def optimize_images_in_pdf(self, input_path: str, output_path: str, 
                              image_quality: int = 85) -> Dict:
        """
        Optimize images within a PDF to reduce file size.
        
        Args:
            input_path: Path to the input PDF file
            output_path: Path for the optimized PDF file
            image_quality: Image quality percentage (1-100)
        
        Returns:
            Dictionary with optimization results
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                # This is a simplified approach - in a full implementation,
                # you would extract images, compress them, and reinsert them
                page.compress_content_streams()
                writer.add_page(page)
            
            writer.compress_identical_objects()
            writer.remove_duplication()
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            original_size = os.path.getsize(input_path)
            optimized_size = os.path.getsize(output_path)
            
            return {
                'success': True,
                'original_size': original_size,
                'optimized_size': optimized_size,
                'compression_ratio': round((original_size - optimized_size) / original_size * 100, 2)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def remove_metadata(self, input_path: str, output_path: str) -> Dict:
        """
        Remove metadata from PDF to reduce file size.
        
        Args:
            input_path: Path to the input PDF file
            output_path: Path for the cleaned PDF file
        
        Returns:
            Dictionary with cleaning results
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Copy pages without metadata
            for page in reader.pages:
                writer.add_page(page)
            
            # Don't copy metadata
            writer.add_metadata({})
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            original_size = os.path.getsize(input_path)
            cleaned_size = os.path.getsize(output_path)
            
            return {
                'success': True,
                'original_size': original_size,
                'cleaned_size': cleaned_size,
                'size_reduction': original_size - cleaned_size
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_compression_estimate(self, pdf_path: str) -> Dict:
        """
        Estimate potential compression for a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            Dictionary with compression estimates
        """
        try:
            reader = PdfReader(pdf_path)
            file_size = os.path.getsize(pdf_path)
            
            # Basic estimates based on PDF characteristics
            has_images = False
            has_metadata = bool(reader.metadata)
            page_count = len(reader.pages)
            
            # Simple heuristic for compression potential
            estimated_reduction = 0
            if has_metadata:
                estimated_reduction += 5  # 5% from metadata removal
            if page_count > 10:
                estimated_reduction += 15  # 15% from content compression
            if has_images:
                estimated_reduction += 25  # 25% from image compression
            else:
                estimated_reduction += 10  # 10% from general compression
            
            estimated_reduction = min(estimated_reduction, 60)  # Cap at 60%
            
            return {
                'current_size': file_size,
                'estimated_reduction_percent': estimated_reduction,
                'estimated_new_size': int(file_size * (100 - estimated_reduction) / 100),
                'page_count': page_count,
                'has_metadata': has_metadata
            }
            
        except Exception as e:
            return {'error': str(e)}
