"""
Parser manager to handle all available parsers.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

from .pypdf_parser import PyPDFParser
from .pymupdf_parser import PyMuPDFParser
from .pdfplumber_parser import PDFPlumberParser
from .pdfminer_parser import PDFMinerParser
from .tabula_parser import TabulaParser
from .pdfquery_parser import PDFQueryParser
from .llamaparse_parser import LlamaParseParser


class ParserManager:
    """Manages all available document parsers."""
    
    def __init__(self, llamaparse_api_key: str = None):
        self.parsers = {
            'PyPDF': PyPDFParser(),
            'PyMuPDF': PyMuPDFParser(),
            'pdfplumber': PDFPlumberParser(),
            'PDFMiner': PDFMinerParser(),
            'tabula': TabulaParser(),
            'PDFQuery': PDFQueryParser(),
            'LlamaParse': LlamaParseParser(llamaparse_api_key)
        }
    
    def get_available_parsers(self) -> List[str]:
        """Get list of available parser names."""
        return list(self.parsers.keys())
    
    def get_parser(self, parser_name: str):
        """Get a specific parser by name."""
        return self.parsers.get(parser_name)
    
    def get_supported_parsers(self, file_path: Path) -> List[str]:
        """Get list of parsers that support the given file format."""
        supported = []
        for name, parser in self.parsers.items():
            if parser.is_supported(file_path):
                supported.append(name)
        return supported
    
    def parse_document(self, file_path: Path, parser_name: str) -> Dict[str, Any]:
        """
        Parse a document using the specified parser.
        
        Args:
            file_path: Path to the document to parse
            parser_name: Name of the parser to use
            
        Returns:
            Dictionary containing parsed data
        """
        parser = self.get_parser(parser_name)
        if not parser:
            return {
                'text': '',
                'metadata': {'error': f'Parser "{parser_name}" not found', 'file_name': file_path.name},
                'tables': [],
                'images': [],
                'parser_name': parser_name,
                'raw_data': None
            }
        
        if not parser.is_supported(file_path):
            return {
                'text': '',
                'metadata': {'error': f'File format not supported by {parser_name}', 'file_name': file_path.name},
                'tables': [],
                'images': [],
                'parser_name': parser_name,
                'raw_data': None
            }
        
        return parser.parse(file_path)
    
    def get_parser_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available parsers."""
        parser_info = {}
        for name, parser in self.parsers.items():
            parser_info[name] = {
                'name': parser.name,
                'supported_formats': parser.supported_formats,
                'description': self._get_parser_description(name)
            }
        return parser_info
    
    def _get_parser_description(self, parser_name: str) -> str:
        """Get description for a parser."""
        descriptions = {
            'PyPDF': 'Basic PDF text extraction using PyPDF library',
            'PyMuPDF': 'Advanced PDF parsing with table and image detection using PyMuPDF',
            'pdfplumber': 'Detailed PDF analysis with excellent table extraction capabilities',
            'PDFMiner': 'Low-level PDF parsing with detailed layout analysis',
            'tabula': 'Specialized table extraction from PDF documents',
            'PDFQuery': 'jQuery-like PDF querying for structured data extraction',
            'LlamaParse': 'AI-powered document parsing supporting multiple formats (requires API key)'
        }
        return descriptions.get(parser_name, 'Document parser')