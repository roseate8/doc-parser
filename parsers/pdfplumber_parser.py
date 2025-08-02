"""
pdfplumber parser implementation.
"""
from pathlib import Path
from typing import Dict, Any, List
import pdfplumber
from .base_parser import BaseParser, ParseResult


class PDFPlumberParser(BaseParser):
    """Parser using pdfplumber library."""
    
    def __init__(self):
        super().__init__(
            name="pdfplumber",
            supported_formats=['.pdf']
        )
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse PDF using pdfplumber."""
        try:
            with pdfplumber.open(str(file_path)) as pdf:
                # Extract text from all pages
                text = ""
                tables = []
                images = []
                
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    # Extract tables
                    page_tables = page.extract_tables()
                    for table_index, table in enumerate(page_tables):
                        tables.append({
                            'page': page_num + 1,
                            'table_index': table_index,
                            'data': table,
                            'rows': len(table),
                            'columns': len(table[0]) if table else 0
                        })
                    
                    # Extract image information
                    if hasattr(page, 'images'):
                        for img_index, img in enumerate(page.images):
                            images.append({
                                'page': page_num + 1,
                                'index': img_index,
                                'x0': img.get('x0'),
                                'y0': img.get('y0'),
                                'x1': img.get('x1'),
                                'y1': img.get('y1'),
                                'width': img.get('width'),
                                'height': img.get('height')
                            })
                
                # Extract metadata
                metadata = {
                    'num_pages': len(pdf.pages),
                    'file_size': file_path.stat().st_size,
                    'file_name': file_path.name,
                    'num_tables': len(tables),
                    'num_images': len(images)
                }
                
                # Add PDF-specific metadata if available
                if hasattr(pdf, 'metadata') and pdf.metadata:
                    metadata.update({
                        'title': pdf.metadata.get('Title', ''),
                        'author': pdf.metadata.get('Author', ''),
                        'subject': pdf.metadata.get('Subject', ''),
                        'creator': pdf.metadata.get('Creator', ''),
                        'producer': pdf.metadata.get('Producer', ''),
                        'creation_date': str(pdf.metadata.get('CreationDate', '')),
                        'modification_date': str(pdf.metadata.get('ModDate', ''))
                    })
                
                result = ParseResult(
                    text=text.strip(),
                    metadata=metadata,
                    tables=tables,
                    images=images,
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