"""
Test script for hierarchy analysis functionality.
"""

from hierarchy_analyzer import HierarchyAnalyzer
import json
from pathlib import Path


def test_text_hierarchy():
    """Test text hierarchy extraction."""
    print("🧪 Testing Text Hierarchy Extraction")
    print("=" * 50)
    
    analyzer = HierarchyAnalyzer()
    
    sample_text = """
# Main Document Title

This is the introduction paragraph that explains what this document is about.

## Section 1: Overview

This section provides an overview of the main concepts:

• First key concept to understand
• Second important principle  
• Third fundamental idea

Some additional explanation follows here.

## Section 2: Detailed Analysis

Here we dive deeper into specific topics.

1. First detailed step in the process
2. Second step with more complexity
3. Third step involving multiple considerations

### Subsection 2.1: Technical Details

More technical information is provided in this subsection.

- Technical point A
- Technical point B
- Technical point C

## Section 3: Conclusion

Final thoughts and summary of key points.
"""
    
    # Analyze text hierarchy
    result = analyzer.extract_text_hierarchy(sample_text)
    
    print("📝 Text Hierarchy Results:")
    print(f"Headings found: {len(result['headings'])}")
    print(f"Lists found: {len(result['lists'])}")
    print(f"Paragraphs found: {len(result['paragraphs'])}")
    
    print("\n🔍 Detailed Results:")
    print(json.dumps(result, indent=2))
    
    return result


def test_full_analysis():
    """Test full document analysis if PDF is available."""
    print("\n🧪 Testing Full Document Analysis")
    print("=" * 50)
    
    # You can replace this with an actual PDF path for testing
    test_pdf = Path("test_document.pdf")
    
    if test_pdf.exists():
        analyzer = HierarchyAnalyzer()
        
        # Sample extracted text (replace with actual extracted text)
        sample_extracted_text = """
        Document Title
        
        Introduction section with overview content.
        
        Chapter 1: Getting Started
        
        • Step one in the process
        • Step two with details
        • Step three for completion
        
        Chapter 2: Advanced Topics
        
        1. First advanced concept
        2. Second advanced concept
        3. Third advanced concept
        
        Conclusion and final thoughts.
        """
        
        # Perform full analysis
        result = analyzer.analyze_document_hierarchy(test_pdf, sample_extracted_text)
        
        print("📊 Full Analysis Results:")
        print(json.dumps(result, indent=2, default=str))
        
        return result
    else:
        print("⚠️ No test PDF found. Skipping visual analysis test.")
        print("To test with a real PDF, place a file named 'test_document.pdf' in this directory.")
        return None


def test_comparison():
    """Test hierarchy comparison functionality."""
    print("\n🧪 Testing Hierarchy Comparison")
    print("=" * 50)
    
    analyzer = HierarchyAnalyzer()
    
    # Mock text hierarchy
    text_hierarchy = {
        'patterns': {
            'heading_count': 3,
            'list_count': 2,
            'paragraph_count': 5
        }
    }
    
    # Mock visual hierarchy
    visual_hierarchy = {
        'titles': [{'type': 'Title'}, {'type': 'Title'}, {'type': 'Title'}],
        'lists': [{'type': 'List'}, {'type': 'List'}],
        'tables': [],
        'figures': []
    }
    
    # Compare
    comparison = analyzer.compare_hierarchies(text_hierarchy, visual_hierarchy)
    
    print("⚖️ Comparison Results:")
    print(json.dumps(comparison, indent=2))
    
    return comparison


if __name__ == "__main__":
    print("🔍 Hierarchy Analyzer Test Suite")
    print("=" * 60)
    
    # Test text hierarchy extraction
    text_result = test_text_hierarchy()
    
    # Test comparison
    comparison_result = test_comparison()
    
    # Test full analysis (if PDF available)
    full_result = test_full_analysis()
    
    print("\n✅ Testing completed!")
    print("\n📋 Summary:")
    print(f"• Text hierarchy extraction: {'✅ Success' if text_result else '❌ Failed'}")
    print(f"• Hierarchy comparison: {'✅ Success' if comparison_result else '❌ Failed'}")
    print(f"• Full document analysis: {'✅ Success' if full_result else '⚠️ Skipped (no PDF)'}")