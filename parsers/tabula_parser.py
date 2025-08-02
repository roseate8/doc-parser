"""
Tabula parser implementation for table extraction from PDFs.
"""
from pathlib import Path
from typing import Dict, Any, List
import tabula
import pandas as pd
from .base_parser import BaseParser, ParseResult


class TabulaParser(BaseParser):
    """Parser using tabula-py library for table extraction."""
    
    def __init__(self):
        super().__init__(
            name="tabula",
            supported_formats=['.pdf']
        )
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """Parse PDF tables using tabula."""
        try:
            # Extract all tables from the PDF
            tables_list = tabula.read_pdf(
                str(file_path), 
                pages='all', 
                multiple_tables=True,
                silent=True
            )
            
            # Convert tables to our format
            tables = []
            text_content = ""
            
            for i, df in enumerate(tables_list):
                if isinstance(df, pd.DataFrame) and not df.empty:
                    # Convert DataFrame to list of lists
                    table_data = [df.columns.tolist()] + df.values.tolist()
                    
                    tables.append({
                        'table_index': i,
                        'data': table_data,
                        'rows': len(table_data),
                        'columns': len(table_data[0]) if table_data else 0,
                        'shape': df.shape
                    })
                    
                    # Add table content as text
                    text_content += f"\\n\\nTable {i + 1}:\\n"
                    text_content += df.to_string(index=False) + "\\n"
            
            # Try to get basic text content using tabula
            try:
                # Extract text areas that are not tables
                text_areas = tabula.read_pdf(
                    str(file_path),
                    pages='all',
                    area=None,
                    guess=False,
                    stream=True,
                    silent=True
                )
                if text_areas and hasattr(text_areas[0], 'to_string'):
                    text_content = text_areas[0].to_string() + text_content
            except:
                pass
            
            # Extract metadata
            metadata = {
                'file_size': file_path.stat().st_size,
                'file_name': file_path.name,
                'num_tables': len(tables),
                'extraction_method': 'tabula-py'
            }
            
            result = ParseResult(
                text=text_content.strip(),
                metadata=metadata,
                tables=tables,
                images=[],  # tabula doesn't extract images
                raw_data={'dataframes': [df.to_dict() for df in tables_list if isinstance(df, pd.DataFrame)]},
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