"""
Simple test for hierarchy analysis (text-only functionality).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_text_only():
    """Test text-only functionality without visual dependencies."""
    print("🧪 Testing Text-Only Hierarchy Analysis")
    print("=" * 50)
    
    try:
        from hierarchy_analyzer import HierarchyAnalyzer
        print("✅ Successfully imported HierarchyAnalyzer")
        
        analyzer = HierarchyAnalyzer()
        print("✅ Successfully created analyzer instance")
        
        # Test sample text
        sample_text = """
# Main Document Title

This is the introduction paragraph explaining the document purpose.

## Section 1: Getting Started

Important concepts to understand:

• First key concept
• Second important principle  
• Third fundamental idea

## Section 2: Step-by-Step Process

Here's the detailed process:

1. First step in the workflow
2. Second step with more details
3. Third step for completion

### Subsection 2.1: Advanced Details

Additional technical information:

- Technical detail A
- Technical detail B  
- Technical detail C

## Conclusion

Final summary and key takeaways.
"""
        
        print("📝 Analyzing sample text...")
        result = analyzer.extract_text_hierarchy(sample_text)
        
        print("\n📊 Results:")
        print(f"✅ Headings found: {len(result['headings'])}")
        print(f"✅ Lists found: {len(result['lists'])}")
        print(f"✅ Paragraphs found: {len(result['paragraphs'])}")
        
        print("\n🔍 Detailed Breakdown:")
        
        # Show headings
        if result['headings']:
            print("\n📖 Headings:")
            for i, heading in enumerate(result['headings'], 1):
                print(f"  {i}. {heading['text']}")
        
        # Show lists
        if result['lists']:
            print("\n📋 Lists:")
            for i, list_item in enumerate(result['lists'], 1):
                print(f"  {i}. {list_item['text']}")
        
        # Show patterns
        patterns = result['patterns']
        print(f"\n📈 Patterns:")
        print(f"  • Heading count: {patterns['heading_count']}")
        print(f"  • List count: {patterns['list_count']}")
        print(f"  • Paragraph count: {patterns['paragraph_count']}")
        print(f"  • Structure ratio: {patterns['text_structure_ratio']:.2f}")
        
        # Test comparison functionality
        print("\n⚖️ Testing comparison functionality...")
        
        # Mock data for comparison test
        text_hierarchy = {'patterns': {'heading_count': 4, 'list_count': 2}}
        visual_hierarchy = {'titles': [1, 2, 3], 'lists': [1, 2], 'tables': [], 'figures': []}
        
        comparison = analyzer.compare_hierarchies(text_hierarchy, visual_hierarchy)
        print(f"✅ Comparison match score: {comparison.get('match_score', 0):.2f}")
        
        # Test overall assessment
        mock_analysis = {
            'text_hierarchy': result,
            'comparison': comparison
        }
        
        assessment = analyzer.generate_overall_assessment(mock_analysis)
        print(f"✅ Overall quality: {assessment.get('hierarchy_quality', 'unknown')}")
        
        print("\n🎉 All text-only tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def show_installation_guide():
    """Show installation guide for full functionality."""
    print("\n📦 Installation Guide for Full Functionality")
    print("=" * 50)
    
    print("""
To enable visual analysis with LayoutParser, install these dependencies:

🔧 Required Packages:
pip install layoutparser[layoutmodels,tesseract,opencv]
pip install pdf2image
pip install opencv-python
pip install 'git+https://github.com/facebookresearch/detectron2.git'
pip install Pillow

🔧 System Dependencies (Windows):
- Install Poppler: https://github.com/oschwartz10612/poppler-windows/releases/
- Add poppler/bin to your PATH

🔧 Alternative (all at once):
pip install -r requirements_hierarchy.txt

⚠️ Note: LayoutParser requires significant dependencies including PyTorch and Detectron2.
The installation might take 10-15 minutes and requires ~2GB of space.

✅ Current Status: Text-only analysis available
🎯 After installation: Full visual + text analysis available
""")


if __name__ == "__main__":
    print("🔍 Simple Hierarchy Analysis Test")
    print("=" * 60)
    
    # Test text functionality
    success = test_text_only()
    
    if success:
        print("\n✅ Core functionality working!")
        print("📝 Text hierarchy analysis is ready to use.")
    else:
        print("\n❌ Issues detected with core functionality.")
    
    # Show installation guide
    show_installation_guide()
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")