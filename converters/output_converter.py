"""
Output format converters for parsed document data.
"""
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from datetime import datetime
import html


class OutputConverter:
    """Converts parsed document data to various output formats."""
    
    @staticmethod
    def to_html(data: Dict[str, Any]) -> str:
        """Convert parsed data to HTML format - PURE CONTENT ONLY."""
        text_content = data.get('text', '')
        
        # Simple, clean HTML with just the content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; white-space: pre-wrap; }}
    </style>
</head>
<body>
{html.escape(text_content)}
</body>
</html>"""
        
        return html_content
    
    @staticmethod
    def to_markdown(data: Dict[str, Any]) -> str:
        """Convert parsed data to Markdown format - PURE CONTENT ONLY."""
        # Return only the raw text content, no metadata, headers, or extra formatting
        return data.get('text', '')
    
    @staticmethod
    def to_json(data: Dict[str, Any]) -> str:
        """Convert parsed data to JSON format - PURE CONTENT ONLY."""
        # Return only the text content as a simple JSON structure
        output_data = {
            'text': data.get('text', '')
        }
        
        return json.dumps(output_data, indent=2, ensure_ascii=False, default=str)
    
    @staticmethod
    def to_metadata_json(data: Dict[str, Any]) -> str:
        """Export only metadata as JSON."""
        metadata_only = {
            'file_info': data.get('metadata', {}),
            'parser_info': {
                'parser_name': data.get('parser_name', 'Unknown'),
                'generated_at': datetime.now().isoformat()
            },
            'content_stats': {
                'text_length': len(data.get('text', '')),
                'tables_count': len(data.get('tables', [])),
                'images_count': len(data.get('images', []))
            }
        }
        
        return json.dumps(metadata_only, indent=2, ensure_ascii=False, default=str)
    
    @staticmethod
    def to_xml(data: Dict[str, Any]) -> str:
        """Convert parsed data to XML format - PURE CONTENT ONLY."""
        root = ET.Element("document")
        root.text = data.get('text', '')
        
        # Convert to string with proper formatting
        return '<?xml version="1.0" encoding="UTF-8"?>\\n' + ET.tostring(root, encoding='unicode')
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported output formats."""
        return ['html', 'markdown', 'json', 'xml', 'metadata']
    
    @staticmethod
    def convert(data: Dict[str, Any], format_type: str) -> str:
        """Convert data to the specified format."""
        format_type = format_type.lower()
        
        if format_type == 'html':
            return OutputConverter.to_html(data)
        elif format_type == 'markdown':
            return OutputConverter.to_markdown(data)
        elif format_type == 'json':
            return OutputConverter.to_json(data)
        elif format_type == 'xml':
            return OutputConverter.to_xml(data)
        elif format_type == 'metadata':
            return OutputConverter.to_metadata_json(data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    @staticmethod
    def get_file_extension(format_type: str) -> str:
        """Get appropriate file extension for format."""
        extensions = {
            'html': '.html',
            'markdown': '.md',
            'json': '.json',
            'xml': '.xml',
            'metadata': '_metadata.json'
        }
        return extensions.get(format_type.lower(), '.txt')