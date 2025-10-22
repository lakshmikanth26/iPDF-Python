"""
PDF Converter Module
Handles conversion between PDF and image formats (JPG/PNG).
"""

import os
import img2pdf
from PIL import Image
from pypdf import PdfReader
from typing import List, Dict, Optional, Tuple
import tempfile

# Import pdf2image for PDF to image conversion
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


class PDFConverter:
    """Class to handle PDF conversion operations."""
    
    def __init__(self):
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    
    def images_to_pdf(self, image_paths: List[str], output_path: str, 
                     page_size: Optional[Tuple[float, float]] = None,
                     fit_mode: str = 'fit') -> Dict:
        """
        Convert multiple images to a single PDF file.
        
        Args:
            image_paths: List of paths to image files
            output_path: Path for the output PDF file
            page_size: Optional tuple (width, height) in points for page size
            fit_mode: How to fit images ('fit', 'fill', 'exact')
        
        Returns:
            Dictionary with conversion results
        """
        try:
            if not image_paths:
                raise ValueError("No image paths provided")
            
            # Validate image files
            valid_images = []
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    continue
                ext = os.path.splitext(img_path)[1].lower()
                if ext in self.supported_image_formats:
                    valid_images.append(img_path)
            
            if not valid_images:
                raise ValueError("No valid image files found")
            
            # Convert images to PDF using img2pdf
            with open(output_path, "wb") as f:
                if page_size:
                    # Custom page size
                    layout = img2pdf.get_layout_fun(page_size)
                    f.write(img2pdf.convert(valid_images, layout_fun=layout))
                else:
                    # Auto-size based on images
                    f.write(img2pdf.convert(valid_images))
            
            return {
                'success': True,
                'images_processed': len(valid_images),
                'output_file': output_path,
                'file_size': os.path.getsize(output_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def image_to_pdf(self, image_path: str, output_path: str, 
                    page_size: Optional[str] = None) -> Dict:
        """
        Convert a single image to PDF.
        
        Args:
            image_path: Path to the image file
            output_path: Path for the output PDF file
            page_size: Page size ('A4', 'Letter', 'Legal', or None for auto)
        
        Returns:
            Dictionary with conversion results
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Define page sizes in points (72 points = 1 inch)
            page_sizes = {
                'A4': (595, 842),
                'Letter': (612, 792),
                'Legal': (612, 1008)
            }
            
            with open(output_path, "wb") as f:
                if page_size and page_size in page_sizes:
                    layout = img2pdf.get_layout_fun(page_sizes[page_size])
                    f.write(img2pdf.convert([image_path], layout_fun=layout))
                else:
                    f.write(img2pdf.convert([image_path]))
            
            return {
                'success': True,
                'input_file': image_path,
                'output_file': output_path,
                'file_size': os.path.getsize(output_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def pdf_to_images(self, pdf_path: str, output_dir: str, 
                     image_format: str = 'PNG', dpi: int = 200,
                     page_range: Optional[List[int]] = None) -> Dict:
        """
        Convert PDF pages to image files.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory where images will be saved
            image_format: Output image format ('PNG', 'JPEG')
            dpi: Resolution for the output images
            page_range: Optional list of page numbers to convert (1-based)
        
        Returns:
            Dictionary with conversion results
        """
        try:
            if not PDF2IMAGE_AVAILABLE:
                return {
                    'success': False,
                    'error': 'PDF to image conversion requires pdf2image library. Please install: pip install pdf2image'
                }
            
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Convert PDF to images
            if page_range:
                images = convert_from_path(pdf_path, dpi=dpi, 
                                         first_page=min(page_range),
                                         last_page=max(page_range))
            else:
                images = convert_from_path(pdf_path, dpi=dpi)
            
            output_files = []
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            for i, image in enumerate(images):
                if page_range and (i + 1) not in page_range:
                    continue
                    
                page_num = i + 1
                if page_range:
                    # Find the actual page number in the range
                    actual_page = page_range[i] if i < len(page_range) else page_num
                else:
                    actual_page = page_num
                
                filename = f"{base_name}_page_{actual_page:03d}.{image_format.lower()}"
                filepath = os.path.join(output_dir, filename)
                
                # Convert to specified format
                if image_format.upper() == 'JPEG':
                    image = image.convert('RGB')
                
                image.save(filepath, format=image_format.upper(), quality=95)
                output_files.append(filepath)
            
            return {
                'success': True,
                'output_files': output_files,
                'page_count': len(output_files),
                'total_pages': len(images)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_image_info(self, image_path: str) -> Dict:
        """
        Get information about an image file.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Dictionary with image information
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_bytes': os.path.getsize(image_path)
                }
        except Exception as e:
            return {'error': str(e)}
    
    def resize_image(self, image_path: str, output_path: str, 
                    max_width: int = 1920, max_height: int = 1080,
                    quality: int = 85) -> Dict:
        """
        Resize an image while maintaining aspect ratio.
        
        Args:
            image_path: Path to the input image
            output_path: Path for the resized image
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            quality: JPEG quality (1-100)
        
        Returns:
            Dictionary with resize results
        """
        try:
            with Image.open(image_path) as img:
                # Calculate new size maintaining aspect ratio
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Save with specified quality
                save_kwargs = {}
                if img.format == 'JPEG' or output_path.lower().endswith('.jpg'):
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True
                
                img.save(output_path, **save_kwargs)
                
                return {
                    'success': True,
                    'original_size': os.path.getsize(image_path),
                    'resized_size': os.path.getsize(output_path),
                    'new_dimensions': img.size
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
