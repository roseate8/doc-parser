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
        """Convert parsed data to HTML format."""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parsed Document: {html.escape(data.get('metadata', {}).get('file_name', 'Unknown'))}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
        .header {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .metadata {{ background-color: #e9e9e9; padding: 10px; border-radius: 3px; margin-bottom: 15px; }}
        .content {{ margin-bottom: 20px; }}
        .table-container {{ overflow-x: auto; margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .images {{ margin: 20px 0; }}
        .image-info {{ background-color: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Document Parsing Results</h1>
        <p><strong>Parser Used:</strong> {html.escape(data.get('parser_name', 'Unknown'))}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="metadata">
        <h2>Metadata</h2>
        <ul>"""
        
        metadata = data.get('metadata', {})
        for key, value in metadata.items():
            html_content += f"<li><strong>{html.escape(str(key))}:</strong> {html.escape(str(value))}</li>"
        
        html_content += """</ul>
    </div>
    
    <div class="content">
        <h2>Document Content</h2>
        <div style="white-space: pre-wrap; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; margin-bottom: 20px;">{}</div>
    </div>""".format(html.escape(data.get('text', 'No text extracted')))
        
        # Add tables if any
        tables = data.get('tables', [])
        if tables:
            html_content += "<div class='tables'><h2>Extracted Tables</h2>"
            for i, table in enumerate(tables):
                html_content += f"<h3>Table {i + 1}</h3>"
                html_content += "<div class='table-container'><table>"
                
                table_data = table.get('data', [])
                if table_data:
                    # Add header row if available
                    if len(table_data) > 0:
                        html_content += "<thead><tr>"
                        for cell in table_data[0]:
                            html_content += f"<th>{html.escape(str(cell or ''))}</th>"
                        html_content += "</tr></thead>"
                    
                    # Add data rows
                    if len(table_data) > 1:
                        html_content += "<tbody>"
                        for row in table_data[1:]:
                            html_content += "<tr>"
                            for cell in row:
                                html_content += f"<td>{html.escape(str(cell or ''))}</td>"
                            html_content += "</tr>"
                        html_content += "</tbody>"
                
                html_content += "</table></div>"
            html_content += "</div>"
        
        # Add images if any
        images = data.get('images', [])
        if images:
            html_content += "<div class='images'><h2>Image Information</h2>"
            for i, img in enumerate(images):
                html_content += f"<div class='image-info'><h4>Image {i + 1}</h4><ul>"
                for key, value in img.items():
                    html_content += f"<li><strong>{html.escape(str(key))}:</strong> {html.escape(str(value))}</li>"
                html_content += "</ul></div>"
            html_content += "</div>"
        
        html_content += """
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
        """Convert parsed data to JSON format."""
        # Reorganize data with content first, metadata separate
        output_data = {
            'content': {
                'text': data.get('text', ''),
                'tables': data.get('tables', []),
                'images': data.get('images', [])
            },
            'metadata': data.get('metadata', {}),
            'parser_info': {
                'parser_name': data.get('parser_name', 'Unknown'),
                'generated_at': datetime.now().isoformat()
            },
            'raw_data': data.get('raw_data')
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
        """Convert parsed data to XML format."""
        root = ET.Element("document_parsing_result")
        
        # Add parser info
        parser_elem = ET.SubElement(root, "parser_info")
        parser_elem.set("name", str(data.get('parser_name', 'Unknown')))
        parser_elem.set("generated_at", datetime.now().isoformat())
        
        # Add metadata
        metadata_elem = ET.SubElement(root, "metadata")
        metadata = data.get('metadata', {})
        for key, value in metadata.items():
            meta_item = ET.SubElement(metadata_elem, "item")
            meta_item.set("key", str(key))
            meta_item.text = str(value)
        
        # Add text content
        text_elem = ET.SubElement(root, "text_content")
        text_elem.text = data.get('text', 'No text extracted')
        
        # Add tables
        tables = data.get('tables', [])
        if tables:
            tables_elem = ET.SubElement(root, "tables")
            for i, table in enumerate(tables):
                table_elem = ET.SubElement(tables_elem, "table")
                table_elem.set("index", str(i))
                
                # Add table metadata
                for key, value in table.items():
                    if key != 'data':
                        table_elem.set(key, str(value))
                
                # Add table data
                table_data = table.get('data', [])
                if table_data:
                    for row_idx, row in enumerate(table_data):
                        row_elem = ET.SubElement(table_elem, "row")
                        row_elem.set("index", str(row_idx))
                        for col_idx, cell in enumerate(row):
                            cell_elem = ET.SubElement(row_elem, "cell")
                            cell_elem.set("index", str(col_idx))
                            cell_elem.text = str(cell or '')
        
        # Add images
        images = data.get('images', [])
        if images:
            images_elem = ET.SubElement(root, "images")
            for i, img in enumerate(images):
                img_elem = ET.SubElement(images_elem, "image")
                img_elem.set("index", str(i))
                for key, value in img.items():
                    img_elem.set(str(key), str(value))
        
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