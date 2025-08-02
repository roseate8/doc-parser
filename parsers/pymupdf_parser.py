"""
PyMuPDF parser implementation.
"""
from pathlib import Path
from typing import Dict, Any, List
import fitz  # PyMuPDF
from .base_parser import BaseParser, ParseResult


class PyMuPDFParser(BaseParser):
    """Parser using PyMuPDF (fitz) library."""
    
    def __init__(self):
        super().__init__(
            name="PyMuPDF",
            supported_formats=['.pdf']
        )
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse PDF using PyMuPDF."""
        try:
            doc = fitz.open(str(file_path))
            
            # Extract text from all pages
            text = ""
            tables = []
            images = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text() + "\n"
                
                # Extract tables (basic detection)
                try:
                    page_tables = page.find_tables()
                    for table in page_tables:
                        table_data = table.extract()
                        tables.append({
                            'page': page_num + 1,
                            'data': table_data
                        })
                except:
                    pass  # Table extraction might not be available in all versions
                
                # Extract image information
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    images.append({
                        'page': page_num + 1,
                        'index': img_index,
                        'width': img[2],
                        'height': img[3]
                    })
            
            # Extract metadata
            metadata = {
                'num_pages': len(doc),
                'file_size': file_path.stat().st_size,
                'file_name': file_path.name
            }
            
            # Add PDF-specific metadata
            doc_metadata = doc.metadata
            if doc_metadata:
                metadata.update({
                    'title': doc_metadata.get('title', ''),
                    'author': doc_metadata.get('author', ''),
                    'subject': doc_metadata.get('subject', ''),
                    'creator': doc_metadata.get('creator', ''),
                    'producer': doc_metadata.get('producer', ''),
                    'creation_date': doc_metadata.get('creationDate', ''),
                    'modification_date': doc_metadata.get('modDate', '')
                })
            
            doc.close()
            
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