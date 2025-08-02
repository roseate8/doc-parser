"""
PDFMiner parser implementation.
"""
from pathlib import Path
from typing import Dict, Any
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTFigure
from .base_parser import BaseParser, ParseResult


class PDFMinerParser(BaseParser):
    """Parser using PDFMiner library."""
    
    def __init__(self):
        super().__init__(
            name="PDFMiner",
            supported_formats=['.pdf']
        )
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse PDF using PDFMiner."""
        try:
            # Extract text using high-level API
            text = extract_text(str(file_path))
            
            # Extract additional information using lower-level API
            pages_info = []
            figures = []
            
            try:
                for page_layout in extract_pages(str(file_path)):
                    page_text = ""
                    page_figures = []
                    
                    for element in page_layout:
                        if isinstance(element, LTTextContainer):
                            page_text += element.get_text()
                        elif isinstance(element, LTFigure):
                            page_figures.append({
                                'bbox': element.bbox,
                                'width': element.width,
                                'height': element.height
                            })
                    
                    pages_info.append({
                        'text_length': len(page_text),
                        'figures_count': len(page_figures)
                    })
                    figures.extend(page_figures)
            except Exception:
                # If detailed parsing fails, use basic info
                pass
            
            # Extract metadata
            metadata = {
                'num_pages': len(pages_info) if pages_info else 0,
                'file_size': file_path.stat().st_size,
                'file_name': file_path.name,
                'text_length': len(text),
                'figures_count': len(figures)
            }
            
            result = ParseResult(
                text=text.strip(),
                metadata=metadata,
                tables=[],  # PDFMiner doesn't extract tables directly
                images=figures,
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