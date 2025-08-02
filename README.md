# Multi-Format Document Parser Tool

A comprehensive Python-based tool for parsing various document formats using multiple parsing libraries with a user-friendly Streamlit interface.

## Features

- **Multi-Format Support**: Parse PDF, DOCX, XLSX, HTML, Markdown, images, CSV, and more
- **Multiple Parsing Libraries**: Choose from 7 different parsing libraries:
  - PyPDF - Basic PDF text extraction
  - PyMuPDF - Advanced PDF parsing with tables and images
  - pdfplumber - Detailed PDF analysis with excellent table extraction
  - PDFMiner - Low-level PDF parsing with layout analysis
  - tabula - Specialized table extraction from PDFs
  - PDFQuery - jQuery-like PDF querying
  - LlamaParse - AI-powered document parsing (requires API key)

- **Multiple Output Formats**: View and download results in HTML, Markdown, JSON, or XML
- **File Management**: Upload, store, and manage documents with automatic cleanup
- **Interactive Web Interface**: Built with Streamlit for ease of use

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Streamlit)

Run the Streamlit application:

```bash
streamlit run app.py
```

The app will open in your browser where you can:
1. Upload documents using drag-and-drop or file picker
2. Select from previously uploaded files
3. Choose a parsing library
4. View results in multiple formats
5. Download parsed output

### LlamaParse Setup (Optional)

To use LlamaParse, you need an API key:

1. Sign up at [LlamaIndex Cloud](https://cloud.llamaindex.ai/)
2. Get your API key
3. Set it as an environment variable:
   ```bash
   export LLAMA_CLOUD_API_KEY="your_api_key_here"
   ```
   Or enter it in the Streamlit sidebar

## Project Structure

```
doc-parser/
├── app.py                      # Main Streamlit application
├── file_manager.py             # File upload and storage management
├── requirements.txt            # Python dependencies
├── uploads/                    # Directory for uploaded files
├── parsers/                    # Parser implementations
│   ├── __init__.py
│   ├── base_parser.py         # Base parser interface
│   ├── parser_manager.py      # Parser management
│   ├── pypdf_parser.py        # PyPDF implementation
│   ├── pymupdf_parser.py      # PyMuPDF implementation
│   ├── pdfplumber_parser.py   # pdfplumber implementation
│   ├── pdfminer_parser.py     # PDFMiner implementation
│   ├── tabula_parser.py       # tabula implementation
│   ├── pdfquery_parser.py     # PDFQuery implementation
│   └── llamaparse_parser.py   # LlamaParse implementation
└── converters/                 # Output format converters
    ├── __init__.py
    └── output_converter.py     # HTML, Markdown, JSON, XML converters
```

## Supported File Formats

- **PDF**: .pdf
- **Word Documents**: .docx, .doc
- **Excel Spreadsheets**: .xlsx, .xls
- **PowerPoint**: .pptx
- **Web Documents**: .html, .xml
- **Text Documents**: .md, .txt, .csv
- **Images**: .jpg, .jpeg, .png (with OCR capabilities)

## Parser Comparison

| Parser | Best For | Table Extraction | Image Detection | Performance |
|--------|----------|------------------|-----------------|-------------|
| PyPDF | Basic text extraction | ❌ | ❌ | Fast |
| PyMuPDF | General-purpose PDF parsing | ✅ | ✅ | Fast |
| pdfplumber | Detailed table extraction | ✅✅ | ✅ | Medium |
| PDFMiner | Layout analysis | ❌ | ✅ | Slow |
| tabula | Table-focused extraction | ✅✅ | ❌ | Medium |
| PDFQuery | Structured data queries | Custom | Custom | Medium |
| LlamaParse | AI-powered, multi-format | ✅ | ✅ | Slow |

## Output Formats

### HTML
- Rich formatting with CSS styles
- Interactive tables
- Embedded metadata
- Perfect for web viewing

### Markdown
- Clean, readable text format
- Compatible with documentation systems
- Preserves table structure
- Great for GitHub/GitLab

### JSON
- Structured data format
- Easy integration with APIs
- Programmatic access to all data
- Machine-readable

### XML
- Hierarchical data structure
- Industry-standard format
- Schema-friendly
- Good for data exchange

## Environment Variables

- `LLAMA_CLOUD_API_KEY`: Required for LlamaParse functionality

## Requirements

See `requirements.txt` for full list. Main dependencies:
- streamlit
- pypdf
- PyMuPDF
- pdfplumber
- pdfminer.six
- tabula-py
- pdfquery
- llamaparse (optional)

## Troubleshooting

### Common Issues

1. **Java not found (tabula)**:
   - Install Java JDK 8 or higher
   - Ensure Java is in your PATH

2. **LlamaParse not working**:
   - Check your API key
   - Verify internet connection
   - Ensure you have credits in your LlamaIndex account

3. **Large file processing**:
   - Some parsers may be slow with large files
   - Try different parsers for better performance
   - Consider splitting large documents

### Performance Tips

- Use PyMuPDF or PyPDF for simple text extraction (fastest)
- Use pdfplumber for detailed table extraction
- Use LlamaParse for complex layouts or non-PDF formats
- Enable caching in Streamlit for repeated parsing

## Contributing

Feel free to contribute by:
- Adding new parser implementations
- Improving output formats
- Enhancing the user interface
- Adding new file format support

## License

This project is open source. Feel free to use and modify as needed.