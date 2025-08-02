"""
PDFQuery parser implementation.
"""
from pathlib import Path
from typing import Dict, Any
import pdfquery
from .base_parser import BaseParser, ParseResult


class PDFQueryParser(BaseParser):
    """Parser using PDFQuery library."""
    
    def __init__(self):
        super().__init__(
            name="PDFQuery",
            supported_formats=['.pdf']
        )
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse PDF using PDFQuery."""
        try:
            pdf = pdfquery.PDFQuery(str(file_path))
            pdf.load()
            
            # Extract all text elements
            text_elements = pdf.tree.iter()
            text_content = ""
            
            for elem in text_elements:
                if elem.text and elem.text.strip():
                    text_content += elem.text.strip() + " "
            
            # Try to extract structured data
            # This is a basic implementation - PDFQuery is meant for more specific extractions
            try:
                # Get page count by checking LTPage elements
                pages = pdf.tree.xpath('//LTPage')
                num_pages = len(pages)
            except:
                num_pages = 0
            
            # Extract metadata
            metadata = {
                'num_pages': num_pages,
                'file_size': file_path.stat().st_size,
                'file_name': file_path.name,
                'text_length': len(text_content),
                'extraction_method': 'pdfquery'
            }
            
            result = ParseResult(
                text=text_content.strip(),
                metadata=metadata,
                tables=[],  # PDFQuery requires custom queries for table extraction
                images=[],  # PDFQuery requires custom queries for image extraction
                raw_data={},
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