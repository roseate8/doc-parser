"""
Base parser interface for all document parsers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path


class BaseParser(ABC):
    """Abstract base class for all document parsers."""
    
    def __init__(self, name: str, supported_formats: List[str]):
        self.name = name
        self.supported_formats = supported_formats
    
    @abstractmethod
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a document and return structured data.
        
        Args:
            file_path: Path to the document to parse
            
        Returns:
            Dictionary containing parsed data with standard structure:
            {
                'text': str,           # Extracted text content
                'metadata': dict,      # File metadata
                'tables': list,        # Extracted tables (if any)
                'images': list,        # Image information (if any)
                'raw_data': any        # Raw parser-specific data
            }
        """
        pass
    
    @abstractmethod
    def is_supported(self, file_path: Path) -> bool:
        """Check if the file format is supported by this parser."""
        pass
    
    def get_file_extension(self, file_path: Path) -> str:
        """Get the file extension in lowercase."""
        return file_path.suffix.lower()


class ParseResult:
    """Standardized result object for parsed documents."""
    
    def __init__(self, text: str = "", metadata: Optional[Dict] = None, 
                 tables: Optional[List] = None, images: Optional[List] = None,
                 raw_data: Any = None, parser_name: str = ""):
        self.text = text
        self.metadata = metadata or {}
        self.tables = tables or []
        self.images = images or []
        self.raw_data = raw_data
        self.parser_name = parser_name
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'text': self.text,
            'metadata': self.metadata,
            'tables': self.tables,
            'images': self.images,
            'parser_name': self.parser_name,
            'raw_data': self.raw_data
        }