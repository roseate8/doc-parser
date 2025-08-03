"""
Streamlit app for the Document Parser Tool.
"""
import streamlit as st
import os
from pathlib import Path
import tempfile
from datetime import datetime

from parsers.parser_manager import ParserManager
from converters.output_converter import OutputConverter
from file_manager import FileManager
try:
    from hierarchy_analyzer import HierarchyAnalyzer
    HIERARCHY_ANALYSIS_AVAILABLE = True
except ImportError:
    HIERARCHY_ANALYSIS_AVAILABLE = False
    print("⚠️ Hierarchy analysis not available. Install requirements: pip install -r requirements_hierarchy.txt")

try:
    from ocr_analyzer import OCRAnalyzer
    OCR_ANALYSIS_AVAILABLE = True
except ImportError:
    OCR_ANALYSIS_AVAILABLE = False
    print("⚠️ OCR analysis not available. Install requirements: pip install -r requirements_ocr.txt")


# Set default LlamaParse API key if not already set
DEFAULT_LLAMAPARSE_API_KEY = "llx-OU9aMioU6m6aTz3xOU110tLeSMyDLutu21rR9gh4NJ2bTLka"
if not os.getenv('LLAMA_CLOUD_API_KEY'):
    os.environ['LLAMA_CLOUD_API_KEY'] = DEFAULT_LLAMAPARSE_API_KEY


# Configure Streamlit page
st.set_page_config(
    page_title="Document Parser Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def get_parser_manager():
    """Get cached parser manager instance."""
    llamaparse_api_key = os.getenv('LLAMA_CLOUD_API_KEY')
    return ParserManager(llamaparse_api_key)


@st.cache_resource
def get_file_manager():
    """Get cached file manager instance."""
    return FileManager()


@st.cache_data
def parse_document_cached(file_path_str, parser_name):
    """Cached document parsing to avoid re-parsing the same file."""
    parser_manager = get_parser_manager()
    return parser_manager.parse_document(Path(file_path_str), parser_name)


def main():
    """Main Streamlit application."""
    
    # Initialize managers
    parser_manager = get_parser_manager()
    file_manager = get_file_manager()
    
    # App header
    st.title("📄 Multi-Format Document Parser Tool")
    st.markdown("Upload documents and parse them using various libraries with multiple output formats.")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # LlamaParse API key input
        st.subheader("LlamaParse Setup")
        current_api_key = os.getenv('LLAMA_CLOUD_API_KEY', '')
        
        # Show status
        if current_api_key == DEFAULT_LLAMAPARSE_API_KEY:
            st.success("🔑 Using default LlamaParse API key")
        elif current_api_key:
            st.success("🔑 Using custom LlamaParse API key")
        else:
            st.warning("⚠️ No LlamaParse API key configured")
        
        # Optional API key override
        with st.expander("🔧 Advanced: Override API Key"):
            api_key = st.text_input(
                "Custom LlamaParse API Key",
                value="",
                type="password",
                help="Leave blank to use default API key. Enter a different key to override."
            )
            if api_key and api_key != current_api_key:
                os.environ['LLAMA_CLOUD_API_KEY'] = api_key
                st.success("✅ API key updated!")
                # Clear parser manager cache to use new API key
                st.cache_resource.clear()
            
            if st.button("🔄 Reset to Default API Key"):
                os.environ['LLAMA_CLOUD_API_KEY'] = DEFAULT_LLAMAPARSE_API_KEY
                st.success("✅ Reset to default API key!")
                # Clear parser manager cache to use default API key
                st.cache_resource.clear()
        
        # Storage info
        st.subheader("📊 Storage Info")
        storage_info = file_manager.get_storage_info()
        st.metric("Total Files", storage_info['total_files'])
        st.metric("Total Size", f"{storage_info['total_size_mb']} MB")
        
        # Cleanup option
        if st.button("🗑️ Cleanup Old Files (30+ days)"):
            try:
                deleted = file_manager.cleanup_old_files()
                st.success(f"Deleted {deleted} old files")
                # Clear session state to refresh file list
                for key in list(st.session_state.keys()):
                    if key.startswith("uploaded_"):
                        del st.session_state[key]
            except Exception as e:
                st.error(f"❌ Cleanup failed: {str(e)}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📁 File Management")
        
        # File upload section
        st.subheader("Upload New File")
        # Convert file extensions for Streamlit (remove dots)
        supported_types = [ext[1:] for ext in file_manager.get_supported_formats()]
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=supported_types,
            help="Supported formats: " + ", ".join(file_manager.get_supported_formats())
        )
        
        if uploaded_file is not None:
            # Check if file was already processed
            if f"uploaded_{uploaded_file.name}" not in st.session_state:
                # Save uploaded file
                try:
                    file_content = uploaded_file.read()
                    saved_path = file_manager.save_uploaded_file(file_content, uploaded_file.name)
                    
                    if saved_path:
                        st.success(f"✅ File uploaded successfully: {saved_path.name}")
                        st.session_state[f"uploaded_{uploaded_file.name}"] = True
                        # Mark for refresh without immediate rerun
                        st.session_state['files_changed'] = True
                    else:
                        st.error("❌ Failed to upload file")
                except Exception as e:
                    st.error(f"❌ Upload failed: {str(e)}")
        
        # Existing files section
        st.subheader("Existing Files")
        uploaded_files = file_manager.get_uploaded_files()
        
        if not uploaded_files:
            st.info("No files uploaded yet. Upload a file to get started!")
        else:
            # Display files in a table format
            for i, file_info in enumerate(uploaded_files):
                with st.expander(f"📄 {file_info['filename']} ({file_info['size_mb']} MB)"):
                    col_info, col_actions = st.columns([2, 1])
                    
                    with col_info:
                        st.text(f"Size: {file_info['size_mb']} MB")
                        st.text(f"Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                        st.text(f"Type: {file_info['extension']}")
                    
                    with col_actions:
                        if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                            try:
                                if file_manager.delete_file(file_info['filename']):
                                    st.success("File deleted!")
                                    # Clear related session state
                                    if f"uploaded_{file_info['filename']}" in st.session_state:
                                        del st.session_state[f"uploaded_{file_info['filename']}"]
                                    # Mark for refresh without immediate rerun
                                    st.session_state['files_changed'] = True
                                else:
                                    st.error("Failed to delete file")
                            except Exception as e:
                                st.error(f"❌ Delete failed: {str(e)}")
    
    with col2:
        st.header("🔧 Parsing Configuration")
        
        # File selection (refresh if files changed)
        if st.session_state.get('files_changed', False):
            st.session_state['files_changed'] = False
            # Files list will be refreshed naturally on next run
        
        uploaded_files = file_manager.get_uploaded_files()
        if uploaded_files:
            selected_file = st.selectbox(
                "Select file to parse",
                options=[f['filename'] for f in uploaded_files],
                format_func=lambda x: f"{x} ({next(f['size_mb'] for f in uploaded_files if f['filename'] == x)} MB)"
            )
            
            if selected_file:
                file_path = file_manager.get_file_path(selected_file)
                
                # Parser selection
                supported_parsers = parser_manager.get_supported_parsers(file_path)
                if supported_parsers:
                    selected_parser = st.selectbox(
                        "Select parsing library",
                        options=supported_parsers,
                        help="Choose the parser that best fits your needs"
                    )
                    
                    # Show parser info
                    parser_info = parser_manager.get_parser_info()
                    if selected_parser in parser_info:
                        st.info(f"ℹ️ {parser_info[selected_parser]['description']}")
                    
                    # Parse button
                    if st.button("🚀 Parse Document", type="primary"):
                        with st.spinner(f"Parsing with {selected_parser}..."):
                            try:
                                # Parse document
                                parsed_data = parse_document_cached(str(file_path), selected_parser)
                                
                                # Validate parsed data
                                if parsed_data and 'metadata' in parsed_data:
                                    # Check for parsing errors in metadata
                                    if 'error' in parsed_data.get('metadata', {}):
                                        st.error(f"❌ Parser error: {parsed_data['metadata']['error']}")
                                    else:
                                        # Store in session state
                                        st.session_state.parsed_data = parsed_data
                                        st.session_state.selected_file = selected_file
                                        st.session_state.selected_parser = selected_parser
                                        
                                        st.success(f"✅ Document parsed successfully with {selected_parser}!")
                                else:
                                    st.error("❌ Parsing returned invalid data")
                                
                            except Exception as e:
                                st.error(f"❌ Parsing failed: {str(e)}")
                                # Clear any partial results
                                if 'parsed_data' in st.session_state:
                                    del st.session_state.parsed_data
                else:
                    st.warning("⚠️ No supported parsers for this file format")
        else:
            st.info("📁 Upload a file first to start parsing")
    
    # Results section
    if 'parsed_data' in st.session_state:
        st.header("📊 Parsing Results")
        
                # Tabs for different views
        available_tabs = ["📄 HTML", "📝 Markdown", "📋 JSON", "🗂️ XML", "ℹ️ Metadata"]
        if HIERARCHY_ANALYSIS_AVAILABLE:
            available_tabs.append("🏗️ Hierarchy")
        if OCR_ANALYSIS_AVAILABLE:
            available_tabs.append("👁️ OCR Analysis")
        
        tabs = st.tabs(available_tabs)
        tab1, tab2, tab3, tab4, tab5 = tabs[:5]
        
        # Handle optional tabs
        tab_hierarchy = tabs[5] if len(tabs) > 5 and HIERARCHY_ANALYSIS_AVAILABLE else None
        if HIERARCHY_ANALYSIS_AVAILABLE and OCR_ANALYSIS_AVAILABLE:
            tab_ocr = tabs[6] if len(tabs) > 6 else None
        elif OCR_ANALYSIS_AVAILABLE and not HIERARCHY_ANALYSIS_AVAILABLE:
            tab_ocr = tabs[5] if len(tabs) > 5 else None
        else:
            tab_ocr = None
        
        parsed_data = st.session_state.parsed_data
        
        with tab1:
            st.subheader("HTML Output")
            try:
                html_output = OutputConverter.to_html(parsed_data)
                st.download_button(
                    "💾 Download HTML",
                    data=html_output,
                    file_name=f"{st.session_state.selected_file}_{st.session_state.selected_parser}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
                # Display HTML safely with size limit
                if len(html_output) > 50000:  # If HTML is too large, show preview
                    st.warning("⚠️ HTML output is large. Showing first 50,000 characters...")
                    st.components.v1.html(html_output[:50000] + "...", height=600, scrolling=True)
                else:
                    st.components.v1.html(html_output, height=600, scrolling=True)
            except Exception as e:
                st.error(f"❌ Failed to generate HTML: {str(e)}")
        
        with tab2:
            st.subheader("Markdown Output")
            try:
                markdown_output = OutputConverter.to_markdown(parsed_data)
                st.download_button(
                    "💾 Download Markdown",
                    data=markdown_output,
                    file_name=f"{st.session_state.selected_file}_{st.session_state.selected_parser}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
                # Display with size limit
                if len(markdown_output) > 10000:
                    st.warning("⚠️ Markdown output is large. Showing first 10,000 characters...")
                    st.markdown(markdown_output[:10000] + "\n\n...(truncated)...")
                else:
                    st.markdown(markdown_output)
            except Exception as e:
                st.error(f"❌ Failed to generate Markdown: {str(e)}")
        
        with tab3:
            st.subheader("JSON Output")
            try:
                json_output = OutputConverter.to_json(parsed_data)
                st.download_button(
                    "💾 Download JSON",
                    data=json_output,
                    file_name=f"{st.session_state.selected_file}_{st.session_state.selected_parser}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                st.json(parsed_data)
            except Exception as e:
                st.error(f"❌ Failed to generate JSON: {str(e)}")
        
        with tab4:
            st.subheader("XML Output")
            try:
                xml_output = OutputConverter.to_xml(parsed_data)
                st.download_button(
                    "💾 Download XML",
                    data=xml_output,
                    file_name=f"{st.session_state.selected_file}_{st.session_state.selected_parser}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml",
                    mime="application/xml"
                )
                # Display with size limit
                if len(xml_output) > 10000:
                    st.warning("⚠️ XML output is large. Showing first 10,000 characters...")
                    st.code(xml_output[:10000] + "\n...(truncated)...", language="xml")
                else:
                    st.code(xml_output, language="xml")
            except Exception as e:
                st.error(f"❌ Failed to generate XML: {str(e)}")
        
        with tab5:
            st.subheader("Parsing Metadata")
            metadata = parsed_data.get('metadata', {})
            
            # Metadata-only download button
            try:
                metadata_json = OutputConverter.to_metadata_json(parsed_data)
                st.download_button(
                    "💾 Download Metadata Only (JSON)",
                    data=metadata_json,
                    file_name=f"{st.session_state.selected_file}_{st.session_state.selected_parser}_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"❌ Failed to generate metadata JSON: {str(e)}")
            
            col_meta1, col_meta2 = st.columns(2)
            
            with col_meta1:
                st.metric("Parser Used", parsed_data.get('parser_name', 'Unknown'))
                st.metric("Text Length", len(parsed_data.get('text', '')))
                
            with col_meta2:
                st.metric("Tables Found", len(parsed_data.get('tables', [])))
                st.metric("Images Found", len(parsed_data.get('images', [])))
            
            # Show detailed metadata
            st.subheader("Detailed Metadata")
            st.json(metadata)
            
            # Show extracted text preview
            text_content = parsed_data.get('text', '')
            if text_content:
                st.subheader("Text Content Preview")
                st.text_area(
                    "Extracted Text (first 1000 characters)",
                    value=text_content[:1000] + ("..." if len(text_content) > 1000 else ""),
                    height=200,
                    disabled=True
                )
        
        # Hierarchy Analysis Tab (if available)
        if HIERARCHY_ANALYSIS_AVAILABLE and tab_hierarchy is not None:
            with tab_hierarchy:
                st.subheader("🏗️ Document Hierarchy Analysis")
                st.write("Analyze if extracted hierarchy (headings, lists) matches visual document structure using LayoutParser.")
                
                if st.button("🔍 Analyze Document Hierarchy", type="primary"):
                    with st.spinner("Analyzing document hierarchy..."):
                        try:
                            # Initialize hierarchy analyzer
                            analyzer = HierarchyAnalyzer()
                            
                            # Get file path and extracted text
                            file_manager = get_file_manager()
                            selected_file = st.session_state.get('selected_file', '')
                            
                            if selected_file:
                                file_path = file_manager.get_file_path(selected_file)
                                
                                # Extract text from parsed data (check multiple possible structures)
                                extracted_text = ""
                                if 'content' in parsed_data:
                                    if isinstance(parsed_data['content'], dict):
                                        extracted_text = parsed_data['content'].get('text', '') or parsed_data['content'].get('html', '') or str(parsed_data['content'])
                                    else:
                                        extracted_text = str(parsed_data['content'])
                                elif 'text' in parsed_data:
                                    extracted_text = parsed_data['text']
                                elif 'html' in parsed_data:
                                    # Strip HTML tags for hierarchy analysis
                                    import re
                                    extracted_text = re.sub('<[^<]+?>', '', parsed_data['html'])
                                else:
                                    # Fallback - convert entire parsed data to string
                                    extracted_text = str(parsed_data)
                                
                                # Ensure we have meaningful text
                                if len(extracted_text.strip()) < 10:
                                    extracted_text = ""
                            
                            # Debug information
                            st.write("**Debug Info:**")
                            st.write(f"• Selected file: {selected_file}")
                            st.write(f"• File path exists: {file_path.exists() if selected_file else 'No file selected'}")
                            st.write(f"• Extracted text length: {len(extracted_text)} characters")
                            st.write(f"• Parsed data keys: {list(parsed_data.keys())}")
                            
                            if selected_file and file_path.exists() and extracted_text:
                                # Perform hierarchy analysis
                                analysis_result = analyzer.analyze_document_hierarchy(
                                    file_path, 
                                    extracted_text
                                )
                                
                                # Display results
                                st.success("✅ Hierarchy analysis completed!")
                                
                                # Overall Assessment
                                overall = analysis_result.get('overall_assessment', {})
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    quality = overall.get('hierarchy_quality', 'unknown').replace('_', ' ').title()
                                    st.metric("Hierarchy Quality", quality)
                                
                                with col2:
                                    preservation = overall.get('structure_preservation', 0)
                                    st.metric("Structure Preservation", f"{preservation:.1%}")
                                
                                with col3:
                                    suitability = overall.get('parser_suitability', 'unknown').replace('_', ' ').title()
                                    st.metric("Parser Suitability", suitability)
                                
                                # Text Hierarchy Analysis
                                st.subheader("📝 Extracted Text Hierarchy")
                                text_hierarchy = analysis_result.get('text_hierarchy', {})
                                patterns = text_hierarchy.get('patterns', {})
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Headings", patterns.get('heading_count', 0))
                                with col2:
                                    st.metric("Lists", patterns.get('list_count', 0))
                                with col3:
                                    st.metric("Paragraphs", patterns.get('paragraph_count', 0))
                                with col4:
                                    ratio = patterns.get('text_structure_ratio', 0)
                                    st.metric("Structure Ratio", f"{ratio:.2f}")
                                
                                # Visual Hierarchy (if available)
                                visual_hierarchy = analysis_result.get('visual_hierarchy', {})
                                if 'error' not in visual_hierarchy and 'info' not in visual_hierarchy:
                                    st.subheader("🖼️ Visual Layout Analysis")
                                    
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Visual Titles", len(visual_hierarchy.get('titles', [])))
                                    with col2:
                                        st.metric("Visual Lists", len(visual_hierarchy.get('lists', [])))
                                    with col3:
                                        st.metric("Tables", len(visual_hierarchy.get('tables', [])))
                                    with col4:
                                        st.metric("Figures", len(visual_hierarchy.get('figures', [])))
                                
                                # Comparison Results
                                comparison = analysis_result.get('comparison', {})
                                if 'match_score' in comparison:
                                    st.subheader("⚖️ Hierarchy Comparison")
                                    
                                    match_score = comparison.get('match_score', 0)
                                    st.progress(match_score, text=f"Overall Match Score: {match_score:.1%}")
                                    
                                    # Insights
                                    insights = comparison.get('insights', [])
                                    if insights:
                                        st.write("**Insights:**")
                                        for insight in insights:
                                            st.write(f"• {insight}")
                                    
                                    # Discrepancies
                                    discrepancies = comparison.get('discrepancies', [])
                                    if discrepancies:
                                        st.write("**Discrepancies Found:**")
                                        for discrepancy in discrepancies:
                                            st.warning(discrepancy)
                                    
                                    # Recommendations
                                    recommendations = comparison.get('recommendations', [])
                                    if recommendations:
                                        st.write("**Recommendations:**")
                                        for rec in recommendations:
                                            st.info(f"💡 {rec}")
                                
                                # Summary
                                summary = overall.get('summary', [])
                                if summary:
                                    with st.expander("📋 Analysis Summary", expanded=True):
                                        for item in summary:
                                            st.write(f"• {item}")
                                
                                # Download analysis results
                                try:
                                    import json
                                    analysis_json = json.dumps(analysis_result, indent=2, default=str)
                                    st.download_button(
                                        "💾 Download Hierarchy Analysis (JSON)",
                                        data=analysis_json,
                                        file_name=f"{st.session_state.selected_file}_hierarchy_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                                except Exception as e:
                                    st.error(f"❌ Failed to generate analysis report: {str(e)}")
                            
                            else:
                                if not selected_file:
                                    st.error("❌ No file selected. Please parse a document first.")
                                elif not file_path.exists():
                                    st.error(f"❌ File not found: {file_path}")
                                elif not extracted_text:
                                    st.error("❌ No text content extracted. The document might be empty or parsing failed.")
                                    st.write("**Available data structure:**")
                                    st.json(parsed_data)
                        
                        except Exception as e:
                            st.error(f"❌ Hierarchy analysis failed: {str(e)}")
                            st.write("This might be due to missing dependencies. Try installing:")
                            st.code("pip install -r requirements_hierarchy.txt")
                
                # Information about hierarchy analysis
                with st.expander("ℹ️ About Hierarchy Analysis"):
                    st.write("""
                    **Hierarchy Analysis** uses LayoutParser to compare extracted text structure with visual document layout:
                    
                    **What it analyzes:**
                    - **Headings/Titles**: Compares detected text headings with visual title elements
                    - **Lists**: Compares extracted lists with visual list structures  
                    - **Structure Preservation**: How well the parsing maintained document organization
                    - **Layout Elements**: Detects tables, figures, and other visual components
                    
                    **Match Score Interpretation:**
                    - **80-100%**: Excellent hierarchy preservation
                    - **60-79%**: Good preservation with minor issues
                    - **40-59%**: Moderate preservation, some structure lost
                    - **Below 40%**: Poor preservation, significant structure loss
                    
                    **Requirements:**
                    - Only works with PDF files for visual analysis
                    - Requires LayoutParser and associated dependencies
                    - Uses deep learning models for layout detection
                    """)
        
        # OCR Analysis Tab (if available)
        if OCR_ANALYSIS_AVAILABLE and tab_ocr is not None:
            with tab_ocr:
                st.subheader("👁️ OCR Performance Analysis")
                st.write("Analyze OCR (Optical Character Recognition) performance and detect image-based content.")
                
                if st.button("🔍 Analyze OCR Performance", type="primary"):
                    with st.spinner("Analyzing OCR performance..."):
                        try:
                            # Initialize OCR analyzer
                            analyzer = OCRAnalyzer()
                            
                            # Get file path and extracted text
                            file_manager = get_file_manager()
                            selected_file = st.session_state.get('selected_file', '')
                            
                            if selected_file:
                                file_path = file_manager.get_file_path(selected_file)
                                
                                # Extract text from parsed data
                                extracted_text = ""
                                if 'content' in parsed_data:
                                    if isinstance(parsed_data['content'], dict):
                                        extracted_text = parsed_data['content'].get('text', '') or str(parsed_data['content'])
                                    else:
                                        extracted_text = str(parsed_data['content'])
                                elif 'text' in parsed_data:
                                    extracted_text = parsed_data['text']
                                else:
                                    extracted_text = str(parsed_data)
                                
                                # Debug information
                                st.write("**Debug Info:**")
                                st.write(f"• Selected file: {selected_file}")
                                st.write(f"• File extension: {file_path.suffix}")
                                st.write(f"• Available OCR engines: {analyzer.available_engines}")
                                
                                if file_path.suffix.lower() == '.pdf' and file_path.exists():
                                    # Perform OCR analysis
                                    analysis_result = analyzer.analyze_document_ocr_performance(file_path, extracted_text)
                                    
                                    # Display results
                                    st.success("✅ OCR analysis completed!")
                                    
                                    # Overall Assessment
                                    overall = analysis_result.get('overall_assessment', {})
                                    col1, col2, col3, col4 = st.columns(4)
                                    
                                    with col1:
                                        doc_type = overall.get('document_type', 'unknown').title()
                                        st.metric("Document Type", doc_type)
                                    
                                    with col2:
                                        extraction_quality = overall.get('extraction_quality', 'unknown').title()
                                        st.metric("Extraction Quality", extraction_quality)
                                    
                                    with col3:
                                        ocr_needed = "Yes" if overall.get('ocr_needed', False) else "No"
                                        st.metric("OCR Needed", ocr_needed)
                                    
                                    with col4:
                                        confidence = overall.get('confidence', 0)
                                        st.metric("Confidence", f"{confidence:.1f}%")
                                    
                                    # Scanned Document Detection
                                    st.subheader("🔍 Scanned Document Detection")
                                    scanned_detection = analysis_result.get('scanned_detection', {})
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        likely_scanned = scanned_detection.get('likely_scanned', False)
                                        st.metric("Likely Scanned", "Yes" if likely_scanned else "No")
                                    
                                    with col2:
                                        scan_confidence = scanned_detection.get('confidence', 0)
                                        st.progress(scan_confidence / 100, text=f"Confidence: {scan_confidence:.1f}%")
                                    
                                    # Evidence
                                    evidence = scanned_detection.get('evidence', [])
                                    if evidence:
                                        st.write("**Evidence:**")
                                        for item in evidence:
                                            st.write(f"• {item}")
                                    
                                    # Native Text Analysis
                                    st.subheader("📝 Native Text Extraction Analysis")
                                    native_analysis = analysis_result.get('native_text_analysis', {})
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.write("**PyMuPDF Extraction:**")
                                        pymupdf_data = native_analysis.get('pymupdf', {})
                                        if 'error' not in pymupdf_data:
                                            st.metric("Quality Score", f"{pymupdf_data.get('quality_score', 0):.1f}/100")
                                            st.metric("Characters", f"{pymupdf_data.get('character_count', 0):,}")
                                            st.metric("Words", f"{pymupdf_data.get('word_count', 0):,}")
                                        else:
                                            st.error(f"Error: {pymupdf_data['error']}")
                                    
                                    with col2:
                                        st.write("**pdfplumber Extraction:**")
                                        pdfplumber_data = native_analysis.get('pdfplumber', {})
                                        if 'error' not in pdfplumber_data:
                                            st.metric("Quality Score", f"{pdfplumber_data.get('quality_score', 0):.1f}/100")
                                            st.metric("Characters", f"{pdfplumber_data.get('character_count', 0):,}")
                                            st.metric("Words", f"{pdfplumber_data.get('word_count', 0):,}")
                                        else:
                                            st.error(f"Error: {pdfplumber_data['error']}")
                                    
                                    # Image Analysis
                                    st.subheader("🖼️ Image Content Analysis")
                                    image_analysis = analysis_result.get('image_analysis', {})
                                    
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Total Images", image_analysis.get('total_images', 0))
                                    with col2:
                                        st.metric("Large Images", image_analysis.get('large_images', 0))
                                    with col3:
                                        total_area = image_analysis.get('total_image_area', 0)
                                        st.metric("Total Image Area", f"{total_area:,} px²")
                                    with col4:
                                        images_by_page = image_analysis.get('images_by_page', {})
                                        avg_per_page = len(images_by_page) / max(len(images_by_page), 1) if images_by_page else 0
                                        st.metric("Avg per Page", f"{avg_per_page:.1f}")
                                    
                                    # Images by Page
                                    if images_by_page:
                                        st.write("**Images by Page:**")
                                        for page, count in sorted(images_by_page.items()):
                                            st.write(f"• Page {page}: {count} images")
                                    
                                    # OCR Engine Comparison
                                    ocr_comparison = analysis_result.get('ocr_comparison', {})
                                    if ocr_comparison.get('sample_results'):
                                        st.subheader("⚖️ OCR Engine Comparison")
                                        
                                        engines_tested = ocr_comparison.get('engines_tested', [])
                                        st.write(f"**Engines tested:** {', '.join(engines_tested)}")
                                        
                                        sample_results = ocr_comparison['sample_results']
                                        
                                        for i, sample in enumerate(sample_results):
                                            with st.expander(f"📷 Sample Image {i+1} (Page {sample['page']}, Size: {sample['image_size']})", expanded=i==0):
                                                results = sample.get('results', {})
                                                
                                                # Show results for each engine
                                                for engine, result in results.items():
                                                    if engine == 'comparison':
                                                        continue
                                                    
                                                    if 'error' not in result:
                                                        col1, col2, col3, col4 = st.columns(4)
                                                        with col1:
                                                            st.write(f"**{engine.title()}:**")
                                                        with col2:
                                                            st.write(f"Confidence: {result.get('avg_confidence', 0):.1f}%")
                                                        with col3:
                                                            st.write(f"Characters: {result.get('character_count', 0)}")
                                                        with col4:
                                                            st.write(f"Time: {result.get('processing_time', 0):.2f}s")
                                                        
                                                        # Show extracted text preview
                                                        text = result.get('text', '')
                                                        if text:
                                                            st.text_area(f"{engine} extracted text", text[:200] + "..." if len(text) > 200 else text, height=100, key=f"{engine}_{i}")
                                                    else:
                                                        st.error(f"**{engine.title()}:** {result['error']}")
                                                
                                                # Show comparison
                                                comparison = results.get('comparison', {})
                                                if comparison:
                                                    st.write("**Comparison Results:**")
                                                    if comparison.get('highest_confidence'):
                                                        st.write(f"• Highest confidence: {comparison['highest_confidence']}")
                                                    if comparison.get('fastest'):
                                                        st.write(f"• Fastest: {comparison['fastest']}")
                                                    if comparison.get('most_text'):
                                                        st.write(f"• Most text extracted: {comparison['most_text']}")
                                    
                                    # Recommendations
                                    recommendations = analysis_result.get('recommendations', [])
                                    if recommendations:
                                        st.subheader("💡 OCR Recommendations")
                                        with st.expander("📋 View Detailed OCR Recommendations", expanded=True):
                                            for i, rec in enumerate(recommendations, 1):
                                                st.write(f"**{i}.** {rec}")
                                            
                                            # Add OCR improvement tips
                                            st.write("---")
                                            st.write("**OCR Improvement Tips:**")
                                            st.write("- **For scanned documents**: Use image preprocessing (contrast, brightness adjustment)")
                                            st.write("- **For low quality images**: Try multiple OCR engines and compare results")
                                            st.write("- **For tables in images**: Consider table-specific OCR tools")
                                            st.write("- **For non-English text**: Configure OCR language settings")
                                            st.write("- **For handwritten text**: Use specialized handwriting recognition models")
                                    
                                    # Download analysis results
                                    try:
                                        import json
                                        # Remove image data for JSON export (too large)
                                        export_result = analysis_result.copy()
                                        if 'image_analysis' in export_result:
                                            export_result.pop('image_analysis', None)
                                        
                                        analysis_json = json.dumps(export_result, indent=2, default=str)
                                        st.download_button(
                                            "💾 Download OCR Analysis (JSON)",
                                            data=analysis_json,
                                            file_name=f"{st.session_state.selected_file}_ocr_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                            mime="application/json"
                                        )
                                    except Exception as e:
                                        st.error(f"❌ Failed to generate analysis report: {str(e)}")
                                
                                elif file_path.suffix.lower() != '.pdf':
                                    st.warning("⚠️ OCR analysis is currently only supported for PDF files")
                                else:
                                    st.error("❌ File not found or not accessible")
                            
                            else:
                                st.error("❌ No file selected. Please parse a document first.")
                        
                        except Exception as e:
                            st.error(f"❌ OCR analysis failed: {str(e)}")
                            st.write("This might be due to missing dependencies. Try installing:")
                            st.code("pip install -r requirements_ocr.txt")
                
                # Information about OCR analysis
                with st.expander("ℹ️ About OCR Analysis"):
                    st.write("""
                    **OCR Analysis** evaluates text extraction quality and recommends optimal OCR strategies:
                    
                    **What it analyzes:**
                    - **Scanned Document Detection**: Identifies if document contains scanned images
                    - **Native Text Quality**: Evaluates built-in text extraction quality
                    - **Image Content**: Finds and analyzes embedded images
                    - **OCR Engine Comparison**: Tests multiple OCR engines (Tesseract, EasyOCR, PaddleOCR)
                    - **Performance Metrics**: Speed, accuracy, and confidence scores
                    
                    **Document Types:**
                    - **Digital**: Created digitally, good native text extraction
                    - **Mixed**: Combination of digital text and scanned images
                    - **Scanned**: Entirely scanned, requires OCR for text extraction
                    
                    **OCR Engines Tested:**
                    - **Tesseract**: Open-source, fast, good for clean text
                    - **EasyOCR**: Deep learning-based, good for various fonts
                    - **PaddleOCR**: Advanced neural network, excellent accuracy
                    
                    **When to Use OCR:**
                    - Poor native text extraction quality
                    - Document appears to be scanned
                    - Images contain readable text
                    - Handwritten content needs extraction
                    
                    **Requirements:**
                    - Only works with PDF files
                    - Requires OCR engines (install with requirements_ocr.txt)
                    - May need system-level Tesseract installation
                    """)

    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit • Multi-Format Document Parser Tool")


if __name__ == "__main__":
    main()