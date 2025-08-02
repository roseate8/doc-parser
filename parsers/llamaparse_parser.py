"""
LlamaParse parser implementation.
"""
from pathlib import Path
from typing import Dict, Any
import os
from .base_parser import BaseParser, ParseResult


class LlamaParseParser(BaseParser):
    """Parser using LlamaParse library."""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            name="LlamaParse",
            supported_formats=['.pdf', '.docx', '.pptx', '.html', '.xml']
        )
        self.api_key = api_key or os.getenv('LLAMA_CLOUD_API_KEY')
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse document using LlamaParse."""
        try:
            if not self.api_key:
                raise ValueError("LlamaParse requires an API key. Set LLAMA_CLOUD_API_KEY environment variable.")
            
            # Import here to avoid issues if llamaparse is not available
            from llama_parse import LlamaParse
            
            # Initialize LlamaParse
            parser = LlamaParse(
                api_key=self.api_key,
                result_type="markdown",  # Get markdown output
                verbose=True
            )
            
            # Parse the document
            documents = parser.load_data(str(file_path))
            
            # Extract text from documents
            text_content = ""
            raw_documents = []
            
            for doc in documents:
                text_content += doc.text + "\\n\\n"
                raw_documents.append({
                    'text': doc.text,
                    'metadata': getattr(doc, 'metadata', {})
                })
            
            # Extract metadata
            metadata = {
                'file_size': file_path.stat().st_size,
                'file_name': file_path.name,
                'num_documents': len(documents),
                'text_length': len(text_content),
                'extraction_method': 'llamaparse'
            }
            
            # Add document-specific metadata if available
            if documents and hasattr(documents[0], 'metadata'):
                doc_metadata = documents[0].metadata
                if doc_metadata:
                    metadata.update(doc_metadata)
            
            result = ParseResult(
                text=text_content.strip(),
                metadata=metadata,
                tables=[],  # LlamaParse doesn't explicitly extract tables separately
                images=[],  # LlamaParse doesn't explicitly extract images separately
                raw_data={'documents': raw_documents},
                parser_name=self.name
            )
            
            return result.to_dict()
            
        except ImportError:
            return {
                'text': '',
                'metadata': {'error': 'LlamaParse library not available', 'file_name': file_path.name},
                'tables': [],
                'images': [],
                'parser_name': self.name,
                'raw_data': None
            }
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
        """Check if file is supported by LlamaParse."""
        return self.get_file_extension(file_path) in self.supported_formats