"""
Test script for OCR analysis functionality.
"""

from ocr_analyzer import OCRAnalyzer
import json
from pathlib import Path
from PIL import Image
import io


def test_ocr_analyzer_basic():
    """Test basic OCR analyzer functionality."""
    print("🧪 Testing OCR Analyzer Basic Functionality")
    print("=" * 50)
    
    analyzer = OCRAnalyzer()
    
    print(f"Available OCR engines: {analyzer.available_engines}")
    
    if not analyzer.available_engines:
        print("⚠️ No OCR engines available. Install dependencies:")
        print("pip install -r requirements_ocr.txt")
        return False
    
    print("✅ OCR analyzer initialized successfully")
    return True


def test_image_detection():
    """Test image detection functionality."""
    print("\n🧪 Testing Image Detection")
    print("=" * 50)
    
    # You can replace this with an actual PDF path for testing
    test_pdf = Path("test_document.pdf")
    
    if test_pdf.exists():
        analyzer = OCRAnalyzer()
        
        print("📷 Testing PyMuPDF image detection...")
        images_pymupdf = analyzer.detect_images_pymupdf(test_pdf)
        print(f"PyMuPDF found: {len(images_pymupdf)} images")
        
        print("📷 Testing pdfplumber image detection...")
        images_pdfplumber = analyzer.detect_images_pdfplumber(test_pdf)
        print(f"pdfplumber found: {len(images_pdfplumber)} images")
        
        if images_pymupdf:
            print("\n🔍 Sample image info (PyMuPDF):")
            sample_img = images_pymupdf[0]
            print(f"• Page: {sample_img['page']}")
            print(f"• Size: {sample_img['width']}x{sample_img['height']}")
            print(f"• Format: {sample_img['format']}")
            print(f"• File size: {sample_img['size_bytes']} bytes")
        
        return len(images_pymupdf) > 0 or len(images_pdfplumber) > 0
    else:
        print("⚠️ No test PDF found. Skipping image detection test.")
        print("To test with a real PDF, place a file named 'test_document.pdf' in this directory.")
        return None


def test_native_text_analysis():
    """Test native text extraction analysis."""
    print("\n🧪 Testing Native Text Analysis")
    print("=" * 50)
    
    test_pdf = Path("test_document.pdf")
    
    if test_pdf.exists():
        analyzer = OCRAnalyzer()
        
        print("📝 Analyzing native text extraction...")
        native_analysis = analyzer.analyze_native_text_extraction(test_pdf)
        
        print("📊 Results:")
        for extractor, data in native_analysis.items():
            if 'error' not in data:
                print(f"\n{extractor.upper()}:")
                print(f"• Quality Score: {data.get('quality_score', 0):.1f}/100")
                print(f"• Characters: {data.get('character_count', 0):,}")
                print(f"• Words: {data.get('word_count', 0):,}")
                print(f"• Extractable: {'Yes' if data.get('extractable', False) else 'No'}")
            else:
                print(f"\n{extractor.upper()}: Error - {data['error']}")
        
        return True
    else:
        print("⚠️ No test PDF found. Skipping native text analysis.")
        return None


def test_scanned_detection():
    """Test scanned document detection."""
    print("\n🧪 Testing Scanned Document Detection")
    print("=" * 50)
    
    test_pdf = Path("test_document.pdf")
    
    if test_pdf.exists():
        analyzer = OCRAnalyzer()
        
        print("🔍 Detecting if document is scanned...")
        scanned_detection = analyzer.detect_scanned_document(test_pdf)
        
        print("📊 Results:")
        print(f"• Likely scanned: {'Yes' if scanned_detection.get('likely_scanned', False) else 'No'}")
        print(f"• Confidence: {scanned_detection.get('confidence', 0):.1f}%")
        
        evidence = scanned_detection.get('evidence', [])
        if evidence:
            print("• Evidence:")
            for item in evidence:
                print(f"  - {item}")
        
        return True
    else:
        print("⚠️ No test PDF found. Skipping scanned detection test.")
        return None


def test_ocr_engines():
    """Test OCR engines with a sample image."""
    print("\n🧪 Testing OCR Engines")
    print("=" * 50)
    
    analyzer = OCRAnalyzer()
    
    if not analyzer.available_engines:
        print("⚠️ No OCR engines available for testing.")
        return False
    
    # Create a simple test image with text
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a white image with black text
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to built-in if not available
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text = "This is a test OCR image"
        draw.text((10, 35), text, fill='black', font=font)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        print(f"🔍 Testing OCR engines with sample image...")
        print(f"Expected text: '{text}'")
        
        # Test OCR engines
        ocr_results = analyzer.compare_ocr_engines(img_bytes)
        
        print("\n📊 OCR Results:")
        for engine, result in ocr_results.items():
            if engine == 'comparison':
                continue
            
            if 'error' not in result:
                extracted_text = result.get('text', '').strip()
                confidence = result.get('avg_confidence', 0)
                processing_time = result.get('processing_time', 0)
                
                print(f"\n{engine.upper()}:")
                print(f"• Extracted: '{extracted_text}'")
                print(f"• Confidence: {confidence:.1f}%")
                print(f"• Time: {processing_time:.3f}s")
                print(f"• Match: {'✅' if text.lower() in extracted_text.lower() else '❌'}")
            else:
                print(f"\n{engine.upper()}: ❌ {result['error']}")
        
        # Show comparison if available
        comparison = ocr_results.get('comparison', {})
        if comparison:
            print(f"\n🏆 Comparison Results:")
            if comparison.get('highest_confidence'):
                print(f"• Best accuracy: {comparison['highest_confidence']}")
            if comparison.get('fastest'):
                print(f"• Fastest: {comparison['fastest']}")
            if comparison.get('most_text'):
                print(f"• Most text: {comparison['most_text']}")
        
        return True
        
    except ImportError:
        print("⚠️ PIL not available for creating test image.")
        return False
    except Exception as e:
        print(f"❌ Error testing OCR engines: {e}")
        return False


def test_full_analysis():
    """Test full OCR analysis if PDF is available."""
    print("\n🧪 Testing Full OCR Analysis")
    print("=" * 50)
    
    test_pdf = Path("test_document.pdf")
    
    if test_pdf.exists():
        analyzer = OCRAnalyzer()
        
        print("🔍 Running complete OCR analysis...")
        
        # Mock extracted text
        sample_extracted_text = "Sample extracted text from the document parser."
        
        # Perform full analysis
        result = analyzer.analyze_document_ocr_performance(test_pdf, sample_extracted_text)
        
        print("📊 Full Analysis Results:")
        
        # Overall assessment
        overall = result.get('overall_assessment', {})
        print(f"\nOverall Assessment:")
        print(f"• Document Type: {overall.get('document_type', 'unknown')}")
        print(f"• Extraction Quality: {overall.get('extraction_quality', 'unknown')}")
        print(f"• OCR Needed: {'Yes' if overall.get('ocr_needed', False) else 'No'}")
        print(f"• Confidence: {overall.get('confidence', 0):.1f}%")
        
        # Show recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        
        return True
    else:
        print("⚠️ No test PDF found. Skipping full analysis test.")
        print("To test with a real PDF, place a file named 'test_document.pdf' in this directory.")
        return None


if __name__ == "__main__":
    print("👁️ OCR Analyzer Test Suite")
    print("=" * 60)
    
    # Test basic functionality
    basic_success = test_ocr_analyzer_basic()
    
    # Test image detection
    image_detection_result = test_image_detection()
    
    # Test native text analysis
    native_analysis_result = test_native_text_analysis()
    
    # Test scanned detection
    scanned_detection_result = test_scanned_detection()
    
    # Test OCR engines
    ocr_engines_success = test_ocr_engines()
    
    # Test full analysis
    full_analysis_result = test_full_analysis()
    
    print("\n✅ Testing completed!")
    print("\n📋 Summary:")
    print(f"• Basic functionality: {'✅ Success' if basic_success else '❌ Failed'}")
    print(f"• Image detection: {'✅ Success' if image_detection_result else '⚠️ Skipped (no PDF)' if image_detection_result is None else '❌ Failed'}")
    print(f"• Native text analysis: {'✅ Success' if native_analysis_result else '⚠️ Skipped (no PDF)' if native_analysis_result is None else '❌ Failed'}")
    print(f"• Scanned detection: {'✅ Success' if scanned_detection_result else '⚠️ Skipped (no PDF)' if scanned_detection_result is None else '❌ Failed'}")
    print(f"• OCR engines: {'✅ Success' if ocr_engines_success else '❌ Failed'}")
    print(f"• Full analysis: {'✅ Success' if full_analysis_result else '⚠️ Skipped (no PDF)' if full_analysis_result is None else '❌ Failed'}")
    
    if not basic_success:
        print("\n📦 Install OCR dependencies:")
        print("pip install -r requirements_ocr.txt")
        print("\nSystem requirements:")
        print("• Windows: Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki")
        print("• Linux: sudo apt-get install tesseract-ocr")
        print("• macOS: brew install tesseract")