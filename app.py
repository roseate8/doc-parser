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
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📄 HTML", "📝 Markdown", "📋 JSON", "🗂️ XML", "ℹ️ Metadata", "📊 Quality"])
        
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
        
        with tab6:
            st.subheader("📊 Quality Assessment")
            quality_data = parsed_data.get('quality_assessment', {})
            
            if 'error' in quality_data:
                st.error(f"❌ Quality assessment failed: {quality_data['error']}")
            else:
                # Overall Quality Score
                col_q1, col_q2, col_q3 = st.columns(3)
                
                with col_q1:
                    overall_quality = quality_data.get('overall_quality', 0)
                    st.metric(
                        "Overall Quality", 
                        f"{overall_quality:.1%}",
                        help="Composite quality score based on multiple factors"
                    )
                
                with col_q2:
                    confidence = quality_data.get('confidence_level', 'Unknown')
                    st.metric(
                        "Confidence Level", 
                        confidence,
                        help="How confident we are in the parsing results"
                    )
                
                with col_q3:
                    grade = quality_data.get('quality_grade', 'N/A')
                    st.metric(
                        "Quality Grade", 
                        grade,
                        help="Letter grade representation of quality"
                    )
                
                # Quality Metrics Breakdown
                st.subheader("🔍 Detailed Metrics")
                metrics = quality_data.get('metrics', {})
                
                col_m1, col_m2 = st.columns(2)
                
                with col_m1:
                    st.write("**Content Quality:**")
                    completeness = metrics.get('completeness_score', 0)
                    semantic = metrics.get('semantic_quality', 0)
                    noise = metrics.get('noise_level', 0)
                    
                    st.progress(completeness, text=f"Completeness: {completeness:.1%}")
                    st.progress(semantic, text=f"Semantic Quality: {semantic:.1%}")
                    st.progress(1-noise, text=f"Noise Reduction: {(1-noise):.1%}")
                
                with col_m2:
                    st.write("**Structure Quality:**")
                    format_pres = metrics.get('format_preservation', 0)
                    structure = metrics.get('content_structure', 0)
                    
                    st.progress(format_pres, text=f"Format Preservation: {format_pres:.1%}")
                    st.progress(structure, text=f"Content Structure: {structure:.1%}")
                
                # Text Statistics
                st.subheader("📈 Content Statistics")
                text_stats = quality_data.get('text_stats', {})
                
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                
                with col_s1:
                    st.metric("Characters", f"{text_stats.get('character_count', 0):,}")
                with col_s2:
                    st.metric("Words", f"{text_stats.get('word_count', 0):,}")
                with col_s3:
                    st.metric("Lines", f"{text_stats.get('line_count', 0):,}")
                with col_s4:
                    st.metric("Paragraphs", f"{text_stats.get('paragraph_count', 0):,}")
                
                # Recommendations
                recommendations = quality_data.get('recommendations', [])
                if recommendations:
                    st.subheader("💡 Recommendations")
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"{i}. {rec}")
                
                # Quality Assessment Download
                try:
                    import json
                    quality_json = json.dumps(quality_data, indent=2, default=str)
                    st.download_button(
                        "💾 Download Quality Report (JSON)",
                        data=quality_json,
                        file_name=f"{st.session_state.selected_file}_{st.session_state.selected_parser}_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to generate quality report: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit • Multi-Format Document Parser Tool")


if __name__ == "__main__":
    main()