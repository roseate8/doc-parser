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
                
                # Extract text - handle potential encoding issues
                try:
                    page_text = page.get_text()
                    text += page_text + "\n"
                except Exception as e:
                    print(f"Warning: Text extraction failed for page {page_num + 1}: {e}")
                    text += f"[Text extraction failed for page {page_num + 1}]\n"
                
                # Extract tables with improved error handling
                try:
                    page_tables = page.find_tables()
                    if page_tables:
                        for table_idx, table in enumerate(page_tables):
                            try:
                                table_data = table.extract()
                                if table_data:  # Only add if we got actual data
                                    tables.append({
                                        'page': page_num + 1,
                                        'table_index': table_idx,
                                        'data': table_data,
                                        'rows': len(table_data),
                                        'columns': len(table_data[0]) if table_data else 0
                                    })
                            except Exception as e:
                                print(f"Warning: Table extraction failed on page {page_num + 1}, table {table_idx}: {e}")
                except Exception as e:
                    print(f"Warning: Table detection failed for page {page_num + 1}: {e}")
                
                # Extract image information with safer indexing
                try:
                    image_list = page.get_images()
                    for img_index, img in enumerate(image_list):
                        try:
                            # Safely extract image info with bounds checking
                            img_info = {
                                'page': page_num + 1,
                                'index': img_index,
                                'xref': img[0] if len(img) > 0 else None,
                            }
                            # Add dimensions if available
                            if len(img) > 2:
                                img_info['width'] = img[2]
                            if len(img) > 3:
                                img_info['height'] = img[3]
                            
                            images.append(img_info)
                        except Exception as e:
                            print(f"Warning: Image info extraction failed on page {page_num + 1}, image {img_index}: {e}")
                except Exception as e:
                    print(f"Warning: Image detection failed for page {page_num + 1}: {e}")
            
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
            error_msg = f"PyMuPDF parsing failed: {str(e)}"
            print(f"Error in PyMuPDF parser: {error_msg}")
            return {
                'text': '',
                'metadata': {
                    'error': error_msg, 
                    'file_name': file_path.name if file_path else 'unknown',
                    'parser': 'PyMuPDF'
                },
                'tables': [],
                'images': [],
                'parser_name': self.name,
                'raw_data': None
            }
    
    def is_supported(self, file_path: Path) -> bool:
        """Check if file is a supported PDF."""
        return self.get_file_extension(file_path) in self.supported_formats