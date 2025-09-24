"""
PDF Unlocker Module
Handles removing password protection from secured PDF files.
"""

import os
from pypdf import PdfReader, PdfWriter
from typing import Dict, Optional


class PDFUnlocker:
    """Class to handle PDF unlocking operations."""
    
    def unlock_pdf(self, input_path: str, output_path: str, 
                   password: str) -> Dict:
        """
        Remove password protection from a PDF file.
        
        Args:
            input_path: Path to the encrypted PDF file
            output_path: Path for the unlocked PDF file
            password: Password to decrypt the PDF
        
        Returns:
            Dictionary with unlock results
        """
        try:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"PDF file not found: {input_path}")
            
            reader = PdfReader(input_path)
            
            # Check if PDF is encrypted
            if not reader.is_encrypted:
                return {
                    'success': False,
                    'error': 'PDF file is not password protected'
                }
            
            # Try to decrypt with provided password
            if not reader.decrypt(password):
                return {
                    'success': False,
                    'error': 'Incorrect password provided'
                }
            
            # Create writer and copy all pages
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            # Copy metadata if available
            if reader.metadata:
                writer.add_metadata(reader.metadata)
            
            # Write the unlocked PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return {
                'success': True,
                'input_file': input_path,
                'output_file': output_path,
                'pages_unlocked': len(reader.pages),
                'file_size': os.path.getsize(output_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def try_common_passwords(self, pdf_path: str, output_path: str,
                           custom_passwords: Optional[list] = None) -> Dict:
        """
        Try to unlock PDF using common passwords.
        
        Args:
            pdf_path: Path to the encrypted PDF file
            output_path: Path for the unlocked PDF file
            custom_passwords: Optional list of custom passwords to try
        
        Returns:
            Dictionary with unlock results
        """
        try:
            reader = PdfReader(pdf_path)
            
            if not reader.is_encrypted:
                return {
                    'success': False,
                    'error': 'PDF file is not password protected'
                }
            
            # Common passwords to try
            common_passwords = [
                '', '123456', 'password', '123456789', '12345678',
                'abc123', 'Password', '123123', 'admin', 'user',
                '1234', '12345', 'qwerty', 'letmein', 'welcome'
            ]
            
            # Add custom passwords if provided
            if custom_passwords:
                passwords_to_try = custom_passwords + common_passwords
            else:
                passwords_to_try = common_passwords
            
            # Try each password
            for password in passwords_to_try:
                try:
                    if reader.decrypt(password):
                        # Password found, unlock the PDF
                        writer = PdfWriter()
                        for page in reader.pages:
                            writer.add_page(page)
                        
                        if reader.metadata:
                            writer.add_metadata(reader.metadata)
                        
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                        
                        return {
                            'success': True,
                            'password_found': password if password else '[empty password]',
                            'output_file': output_path,
                            'pages_unlocked': len(reader.pages)
                        }
                except:
                    continue
            
            return {
                'success': False,
                'error': 'Could not unlock PDF with common passwords'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_pdf_encryption(self, pdf_path: str) -> Dict:
        """
        Check if a PDF file is encrypted and get encryption details.
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            Dictionary with encryption information
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            reader = PdfReader(pdf_path)
            
            encryption_info = {
                'is_encrypted': reader.is_encrypted,
                'file_size': os.path.getsize(pdf_path),
                'pages': len(reader.pages) if not reader.is_encrypted else 'Unknown (encrypted)'
            }
            
            if reader.is_encrypted:
                # Try to get more info about encryption (this might not work for all PDFs)
                try:
                    # Some basic info might be available even when encrypted
                    encryption_info['encryption_type'] = 'Standard PDF encryption'
                    encryption_info['can_extract_text'] = False
                    encryption_info['can_print'] = False
                    encryption_info['can_modify'] = False
                except:
                    pass
            else:
                encryption_info['metadata'] = dict(reader.metadata) if reader.metadata else {}
                encryption_info['can_extract_text'] = True
                encryption_info['can_print'] = True
                encryption_info['can_modify'] = True
            
            return encryption_info
            
        except Exception as e:
            return {'error': str(e)}
    
    def remove_restrictions(self, input_path: str, output_path: str,
                          password: Optional[str] = None) -> Dict:
        """
        Remove printing/editing restrictions from a PDF (if possible).
        
        Args:
            input_path: Path to the restricted PDF file
            output_path: Path for the unrestricted PDF file
            password: Optional password if the PDF is encrypted
        
        Returns:
            Dictionary with results
        """
        try:
            reader = PdfReader(input_path)
            
            # If encrypted, try to decrypt
            if reader.is_encrypted and password:
                if not reader.decrypt(password):
                    return {
                        'success': False,
                        'error': 'Incorrect password provided'
                    }
            elif reader.is_encrypted:
                return {
                    'success': False,
                    'error': 'PDF is encrypted, password required'
                }
            
            # Create new PDF without restrictions
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            # Add metadata but remove restrictions
            if reader.metadata:
                metadata = dict(reader.metadata)
                writer.add_metadata(metadata)
            
            # Write unrestricted PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return {
                'success': True,
                'input_file': input_path,
                'output_file': output_path,
                'message': 'Restrictions removed (if any existed)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
