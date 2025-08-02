"""
PyPDF parser implementation.
"""
from pathlib import Path
from typing import Dict, Any
from pypdf import PdfReader
from .base_parser import BaseParser, ParseResult


class PyPDFParser(BaseParser):
    """Parser using PyPDF library."""
    
    def __init__(self):
        super().__init__(
            name="PyPDF",
            supported_formats=['.pdf']
        )
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse PDF using PyPDF."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Extract text from all pages
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                # Extract metadata
                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'file_size': file_path.stat().st_size,
                    'file_name': file_path.name
                }
                
                # Add PDF-specific metadata if available
                if pdf_reader.metadata:
                    metadata.update({
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                        'modification_date': str(pdf_reader.metadata.get('/ModDate', ''))
                    })
                
                result = ParseResult(
                    text=text.strip(),
                    metadata=metadata,
                    tables=[],  # PyPDF doesn't extract tables directly
                    images=[],  # PyPDF doesn't extract images directly
                    raw_data={'pdf_reader': None},  # Don't store the reader object
                    parser_name=self.name
                )
                
                return result.to_dict()
                
        except Exception as e:
            return {
                'text': '',
                'metadata': {'error': str(e), 'file_name': file_path.name},
                'tables': [],
                'images': [],
                'parser_name': self.name,
                'raw_data': None
            }
    
    def is_supported(self, file_path: Path) -> bool:
        """Check if file is a supported PDF."""
        return self.get_file_extension(file_path) in self.supported_formats