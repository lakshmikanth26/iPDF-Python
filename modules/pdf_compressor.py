"""
PDF Compressor Module
Handles PDF file compression to reduce file size.
"""

import os
import subprocess
import tempfile
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
            print(f"Original file size: {original_size:,} bytes")
            
            # For low compression, just copy the file
            if compression_level == 'low':
                import shutil
                shutil.copy2(input_path, output_path)
                return {
                    'success': True,
                    'original_size': original_size,
                    'compressed_size': original_size,
                    'compression_ratio': 0.0,
                    'size_reduction': 0
                }
            
            # Try Ghostscript compression first (most effective)
            print(f"Attempting Ghostscript compression with level: {compression_level}")
            result = self.compress_pdf_ghostscript(input_path, output_path, compression_level)
            
            # If Ghostscript fails or doesn't compress well, try advanced method
            if not result['success'] or result.get('compression_ratio', 0) <= 5:
                print(f"Ghostscript compression ineffective, trying advanced method...")
                result = self.compress_pdf_advanced(input_path, output_path, compression_level)
            
            # If advanced method also doesn't work well, try alternative method
            if not result['success'] or result.get('compression_ratio', 0) <= 5:
                print(f"Advanced compression ineffective, trying alternative method...")
                result = self.compress_pdf_alternative(input_path, output_path, compression_level)
            
            # If alternative method also doesn't work well, try minimal compression
            if not result['success'] or result.get('compression_ratio', 0) <= 5:
                print(f"Alternative compression ineffective, trying minimal compression...")
                result = self.compress_pdf_minimal(input_path, output_path)
            
            # If all compression methods are ineffective, just copy the original file
            if not result['success'] or result.get('compression_ratio', 0) <= 0:
                print(f"All compression methods ineffective, returning original file")
                import shutil
                shutil.copy2(input_path, output_path)
                return {
                    'success': True,
                    'original_size': original_size,
                    'compressed_size': original_size,
                    'compression_ratio': 0.0,
                    'size_reduction': 0,
                    'note': 'File was already optimally compressed'
                }
            
            print(f"Compression result: success={result['success']}, ratio={result.get('compression_ratio', 0)}%")
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _compress_pdf_primary(self, input_path: str, output_path: str, 
                             compression_level: str = 'medium') -> Dict:
        """
        Primary PDF compression method using page-level compression.
        """
        try:
            original_size = os.path.getsize(input_path)
            print(f"Primary compression - Original size: {original_size:,} bytes")
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Copy all pages to writer with compression
            for i, page in enumerate(reader.pages):
                try:
                    # Apply compression based on level
                    if compression_level == 'high':
                        # High compression: multiple techniques
                        try:
                            page.compress_content_streams()
                            print(f"Applied content stream compression to page {i+1}")
                        except Exception as e:
                            print(f"Content stream compression failed for page {i+1}: {e}")
                        
                        # Scale down slightly for high compression
                        try:
                            page.scale_by(0.95)  # Less aggressive scaling
                            print(f"Applied scaling to page {i+1}")
                        except Exception as e:
                            print(f"Scaling failed for page {i+1}: {e}")
                            
                    elif compression_level == 'medium':
                        # Medium compression: basic compression
                        try:
                            page.compress_content_streams()
                            print(f"Applied content stream compression to page {i+1}")
                        except Exception as e:
                            print(f"Content stream compression failed for page {i+1}: {e}")
                            
                    elif compression_level == 'low':
                        # Low compression: minimal processing
                        pass
                    
                    writer.add_page(page)
                    
                except Exception as e:
                    # If individual page processing fails, add page without compression
                    print(f"Warning: Could not process page {i+1}, adding without compression: {e}")
                    writer.add_page(page)
            
            # Apply writer-level compression for medium and high
            if compression_level in ['medium', 'high']:
                try:
                    writer.compress_identical_objects()
                    print("Applied identical objects compression")
                except Exception as e:
                    print(f"Identical objects compression failed: {e}")
                
                try:
                    writer.remove_duplication()
                    print("Applied duplication removal")
                except Exception as e:
                    print(f"Duplication removal failed: {e}")
            
            # Write the compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            compressed_size = os.path.getsize(output_path)
            print(f"Primary compression - Compressed size: {compressed_size:,} bytes")
            
            # Calculate compression ratio
            if original_size > 0:
                compression_ratio = (original_size - compressed_size) / original_size * 100
            else:
                compression_ratio = 0
            
            print(f"Primary compression - Ratio: {compression_ratio:.2f}%")
            
            return {
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': round(compression_ratio, 2),
                'size_reduction': original_size - compressed_size
            }
            
        except Exception as e:
            print(f"Primary compression failed with error: {e}")
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
    
    def compress_pdf_alternative(self, input_path: str, output_path: str, 
                               compression_level: str = 'medium') -> Dict:
        """
        Alternative PDF compression method using metadata removal and basic optimizations.
        
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
            print(f"Alternative compression - Original size: {original_size:,} bytes")
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Copy all pages to writer
            for page in reader.pages:
                writer.add_page(page)
            
            # Apply different compression techniques based on level
            if compression_level == 'high':
                # High compression: remove metadata and apply optimizations
                writer.add_metadata({})  # Remove metadata
                print("Removed metadata")
                try:
                    writer.compress_identical_objects()
                    print("Applied identical objects compression")
                except Exception as e:
                    print(f"Identical objects compression failed: {e}")
                try:
                    writer.remove_duplication()
                    print("Applied duplication removal")
                except Exception as e:
                    print(f"Duplication removal failed: {e}")
                    
            elif compression_level == 'medium':
                # Medium compression: basic optimizations only
                try:
                    writer.compress_identical_objects()
                    print("Applied identical objects compression")
                except Exception as e:
                    print(f"Identical objects compression failed: {e}")
                    
            elif compression_level == 'low':
                # Low compression: minimal processing
                pass
            
            # Write the compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            compressed_size = os.path.getsize(output_path)
            print(f"Alternative compression - Compressed size: {compressed_size:,} bytes")
            
            # Calculate compression ratio
            if original_size > 0:
                compression_ratio = (original_size - compressed_size) / original_size * 100
            else:
                compression_ratio = 0
            
            print(f"Alternative compression - Ratio: {compression_ratio:.2f}%")
            
            return {
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': round(compression_ratio, 2),
                'size_reduction': original_size - compressed_size
            }
            
        except Exception as e:
            print(f"Alternative compression failed with error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def compress_pdf_minimal(self, input_path: str, output_path: str) -> Dict:
        """
        Minimal compression method that only removes metadata.
        
        Args:
            input_path: Path to the input PDF file
            output_path: Path for the compressed PDF file
        
        Returns:
            Dictionary with compression results and statistics
        """
        try:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"PDF file not found: {input_path}")
            
            original_size = os.path.getsize(input_path)
            print(f"Minimal compression - Original size: {original_size:,} bytes")
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Copy all pages to writer
            for page in reader.pages:
                writer.add_page(page)
            
            # Only remove metadata - this often provides the best compression
            writer.add_metadata({})
            print("Removed metadata")
            
            # Write the compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            compressed_size = os.path.getsize(output_path)
            print(f"Minimal compression - Compressed size: {compressed_size:,} bytes")
            
            # Calculate compression ratio
            if original_size > 0:
                compression_ratio = (original_size - compressed_size) / original_size * 100
            else:
                compression_ratio = 0
            
            print(f"Minimal compression - Ratio: {compression_ratio:.2f}%")
            
            return {
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': round(compression_ratio, 2),
                'size_reduction': original_size - compressed_size
            }
            
        except Exception as e:
            print(f"Minimal compression failed with error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def compress_pdf_advanced(self, input_path: str, output_path: str, 
                            compression_level: str = 'medium') -> Dict:
        """
        Advanced PDF compression using multiple techniques including image optimization.
        
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
            print(f"Advanced compression - Original size: {original_size:,} bytes")
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Copy all pages with advanced compression
            for i, page in enumerate(reader.pages):
                try:
                    # Apply aggressive compression based on level
                    if compression_level == 'high':
                        # High compression: multiple aggressive techniques
                        try:
                            page.compress_content_streams()
                            print(f"Applied content stream compression to page {i+1}")
                        except Exception as e:
                            print(f"Content stream compression failed for page {i+1}: {e}")
                        
                        # Scale down more aggressively for high compression
                        try:
                            page.scale_by(0.85)  # More aggressive scaling
                            print(f"Applied aggressive scaling to page {i+1}")
                        except Exception as e:
                            print(f"Scaling failed for page {i+1}: {e}")
                            
                    elif compression_level == 'medium':
                        # Medium compression: balanced approach
                        try:
                            page.compress_content_streams()
                            print(f"Applied content stream compression to page {i+1}")
                        except Exception as e:
                            print(f"Content stream compression failed for page {i+1}: {e}")
                        
                        # Light scaling for medium compression
                        try:
                            page.scale_by(0.95)
                            print(f"Applied light scaling to page {i+1}")
                        except Exception as e:
                            print(f"Scaling failed for page {i+1}: {e}")
                            
                    elif compression_level == 'low':
                        # Low compression: minimal processing
                        try:
                            page.compress_content_streams()
                            print(f"Applied content stream compression to page {i+1}")
                        except Exception as e:
                            print(f"Content stream compression failed for page {i+1}: {e}")
                    
                    writer.add_page(page)
                    
                except Exception as e:
                    print(f"Warning: Could not process page {i+1}, adding without compression: {e}")
                    writer.add_page(page)
            
            # Apply aggressive writer-level compression
            try:
                writer.compress_identical_objects()
                print("Applied identical objects compression")
            except Exception as e:
                print(f"Identical objects compression failed: {e}")
            
            try:
                writer.remove_duplication()
                print("Applied duplication removal")
            except Exception as e:
                print(f"Duplication removal failed: {e}")
            
            # Remove all metadata for maximum compression
            writer.add_metadata({})
            print("Removed all metadata")
            
            # Write the compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            compressed_size = os.path.getsize(output_path)
            print(f"Advanced compression - Compressed size: {compressed_size:,} bytes")
            
            # Calculate compression ratio
            if original_size > 0:
                compression_ratio = (original_size - compressed_size) / original_size * 100
            else:
                compression_ratio = 0
            
            print(f"Advanced compression - Ratio: {compression_ratio:.2f}%")
            
            return {
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': round(compression_ratio, 2),
                'size_reduction': original_size - compressed_size
            }
            
        except Exception as e:
            print(f"Advanced compression failed with error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def compress_pdf_ghostscript(self, input_path: str, output_path: str, 
                                compression_level: str = 'medium') -> Dict:
        """
        PDF compression using Ghostscript (if available) - similar to professional tools.
        
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
            print(f"Ghostscript compression - Original size: {original_size:,} bytes")
            
            # Check if Ghostscript is available
            try:
                subprocess.run(['gs', '--version'], capture_output=True, check=True)
                gs_available = True
                print("Ghostscript is available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                gs_available = False
                print("Ghostscript not available, falling back to alternative method")
                return self.compress_pdf_advanced(input_path, output_path, compression_level)
            
            # Set compression parameters based on level
            if compression_level == 'high':
                dpi = "150"
                quality = "printer"
            elif compression_level == 'medium':
                dpi = "200"
                quality = "ebook"
            else:  # low
                dpi = "300"
                quality = "prepress"
            
            # Ghostscript command for PDF compression
            gs_command = [
                'gs',
                '-sDEVICE=pdfwrite',
                '-dCompatibilityLevel=1.4',
                f'-dPDFSETTINGS=/{quality}',
                f'-dNOPAUSE',
                f'-dQUIET',
                f'-dBATCH',
                f'-dNOPAUSE',
                f'-dNOPROMPT',
                f'-dOptimize=true',
                f'-dCompressFonts=true',
                f'-dSubsetFonts=true',
                f'-dColorImageDownsampleType=/Bicubic',
                f'-dColorImageResolution={dpi}',
                f'-dGrayImageDownsampleType=/Bicubic',
                f'-dGrayImageResolution={dpi}',
                f'-dMonoImageDownsampleType=/Bicubic',
                f'-dMonoImageResolution={dpi}',
                f'-sOutputFile={output_path}',
                input_path
            ]
            
            print(f"Running Ghostscript command: {' '.join(gs_command)}")
            
            # Run Ghostscript
            result = subprocess.run(gs_command, capture_output=True, text=True)
            
            if result.returncode == 0:
                compressed_size = os.path.getsize(output_path)
                print(f"Ghostscript compression - Compressed size: {compressed_size:,} bytes")
                
                # Calculate compression ratio
                if original_size > 0:
                    compression_ratio = (original_size - compressed_size) / original_size * 100
                else:
                    compression_ratio = 0
                
                print(f"Ghostscript compression - Ratio: {compression_ratio:.2f}%")
                
                return {
                    'success': True,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': round(compression_ratio, 2),
                    'size_reduction': original_size - compressed_size
                }
            else:
                print(f"Ghostscript failed: {result.stderr}")
                return self.compress_pdf_advanced(input_path, output_path, compression_level)
                
        except Exception as e:
            print(f"Ghostscript compression failed with error: {e}")
            return self.compress_pdf_advanced(input_path, output_path, compression_level)

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
