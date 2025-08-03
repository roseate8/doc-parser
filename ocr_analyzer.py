"""
OCR Performance Analyzer.

This module analyzes OCR (Optical Character Recognition) performance by:
1. Detecting images in documents
2. Testing multiple OCR engines
3. Comparing native text extraction vs OCR
4. Providing performance metrics and recommendations
"""

import time
import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import json
import re
import io
import tempfile

# Optional OCR dependencies
try:
    import pytesseract
    import cv2
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False


class OCRAnalyzer:
    """Analyzes OCR performance and document image content."""
    
    def __init__(self):
        """Initialize OCR analyzer with available engines."""
        self.available_engines = []
        self.ocr_engines = {}
        
        # Initialize Tesseract
        if TESSERACT_AVAILABLE:
            try:
                # Test if Tesseract is properly installed
                pytesseract.get_tesseract_version()
                self.available_engines.append('tesseract')
                print("✅ Tesseract OCR available")
            except Exception as e:
                print(f"⚠️ Tesseract found but not working: {e}")
        
        # Initialize EasyOCR
        if EASYOCR_AVAILABLE:
            try:
                self.ocr_engines['easyocr'] = easyocr.Reader(['en'])
                self.available_engines.append('easyocr')
                print("✅ EasyOCR available")
            except Exception as e:
                print(f"⚠️ EasyOCR initialization failed: {e}")
        
        # Initialize PaddleOCR
        if PADDLEOCR_AVAILABLE:
            try:
                self.ocr_engines['paddleocr'] = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
                self.available_engines.append('paddleocr')
                print("✅ PaddleOCR available")
            except Exception as e:
                print(f"⚠️ PaddleOCR initialization failed: {e}")
        
        if not self.available_engines:
            print("⚠️ No OCR engines available. Install dependencies for full functionality.")
    
    def detect_images_pymupdf(self, pdf_path: Path) -> List[Dict]:
        """Detect and extract images using PyMuPDF."""
        images = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get image list
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    
                    # Extract image
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Get image properties
                    pil_image = Image.open(io.BytesIO(image_bytes))
                    
                    image_info = {
                        'page': page_num + 1,
                        'index': img_index,
                        'width': pil_image.width,
                        'height': pil_image.height,
                        'format': image_ext,
                        'size_bytes': len(image_bytes),
                        'area_pixels': pil_image.width * pil_image.height,
                        'image_data': image_bytes,
                        'bbox': img[1:5] if len(img) > 4 else None  # Bounding box if available
                    }
                    
                    images.append(image_info)
            
            doc.close()
            return images
            
        except Exception as e:
            print(f"❌ Error detecting images with PyMuPDF: {e}")
            return []
    
    def detect_images_pdfplumber(self, pdf_path: Path) -> List[Dict]:
        """Detect images using pdfplumber."""
        images = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Get images from page
                    page_images = page.images
                    
                    for img_index, img in enumerate(page_images):
                        image_info = {
                            'page': page_num + 1,
                            'index': img_index,
                            'bbox': [img['x0'], img['top'], img['x1'], img['bottom']],
                            'width': img['width'],
                            'height': img['height'],
                            'object_type': img.get('object_type', 'unknown'),
                            'area_pixels': img['width'] * img['height']
                        }
                        images.append(image_info)
            
            return images
            
        except Exception as e:
            print(f"❌ Error detecting images with pdfplumber: {e}")
            return []
    
    def preprocess_image(self, image: Image.Image, method: str = 'basic') -> Image.Image:
        """Preprocess image for better OCR results."""
        if method == 'basic':
            # Basic preprocessing
            image = image.convert('L')  # Convert to grayscale
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)  # Increase contrast
            
        elif method == 'advanced':
            # Advanced preprocessing with OpenCV
            if not TESSERACT_AVAILABLE:
                return self.preprocess_image(image, 'basic')
            
            # Convert PIL to OpenCV
            img_array = np.array(image.convert('L'))
            
            # Apply Gaussian blur to reduce noise
            img_array = cv2.GaussianBlur(img_array, (5, 5), 0)
            
            # Apply threshold
            _, img_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Convert back to PIL
            image = Image.fromarray(img_array)
        
        return image
    
    def extract_text_tesseract(self, image: Image.Image, preprocess: bool = True) -> Dict:
        """Extract text using Tesseract OCR."""
        if not TESSERACT_AVAILABLE:
            return {'error': 'Tesseract not available'}
        
        try:
            start_time = time.time()
            
            if preprocess:
                image = self.preprocess_image(image, 'advanced')
            
            # Extract text with confidence data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Extract plain text
            text = pytesseract.image_to_string(image).strip()
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = np.mean(confidences) if confidences else 0
            
            processing_time = time.time() - start_time
            
            return {
                'text': text,
                'word_count': len(text.split()) if text else 0,
                'character_count': len(text),
                'avg_confidence': avg_confidence,
                'processing_time': processing_time,
                'word_confidences': confidences,
                'detected_words': len([w for w in data['text'] if w.strip()])
            }
            
        except Exception as e:
            return {'error': f'Tesseract extraction failed: {str(e)}'}
    
    def extract_text_easyocr(self, image: Image.Image) -> Dict:
        """Extract text using EasyOCR."""
        if not EASYOCR_AVAILABLE or 'easyocr' not in self.ocr_engines:
            return {'error': 'EasyOCR not available'}
        
        try:
            start_time = time.time()
            
            # Convert PIL to numpy array
            img_array = np.array(image)
            
            # Extract text
            results = self.ocr_engines['easyocr'].readtext(img_array)
            
            # Combine all text
            text = ' '.join([result[1] for result in results])
            
            # Calculate average confidence
            confidences = [result[2] for result in results]
            avg_confidence = np.mean(confidences) * 100 if confidences else 0
            
            processing_time = time.time() - start_time
            
            return {
                'text': text,
                'word_count': len(text.split()) if text else 0,
                'character_count': len(text),
                'avg_confidence': avg_confidence,
                'processing_time': processing_time,
                'detected_regions': len(results),
                'region_confidences': [r[2] * 100 for r in results]
            }
            
        except Exception as e:
            return {'error': f'EasyOCR extraction failed: {str(e)}'}
    
    def extract_text_paddleocr(self, image: Image.Image) -> Dict:
        """Extract text using PaddleOCR."""
        if not PADDLEOCR_AVAILABLE or 'paddleocr' not in self.ocr_engines:
            return {'error': 'PaddleOCR not available'}
        
        try:
            start_time = time.time()
            
            # Convert PIL to numpy array
            img_array = np.array(image)
            
            # Extract text
            results = self.ocr_engines['paddleocr'].ocr(img_array, cls=True)
            
            if not results or not results[0]:
                return {
                    'text': '',
                    'word_count': 0,
                    'character_count': 0,
                    'avg_confidence': 0,
                    'processing_time': time.time() - start_time,
                    'detected_regions': 0
                }
            
            # Extract text and confidence
            text_lines = []
            confidences = []
            
            for line in results[0]:
                if line and len(line) > 1:
                    text_lines.append(line[1][0])
                    confidences.append(line[1][1])
            
            text = ' '.join(text_lines)
            avg_confidence = np.mean(confidences) * 100 if confidences else 0
            
            processing_time = time.time() - start_time
            
            return {
                'text': text,
                'word_count': len(text.split()) if text else 0,
                'character_count': len(text),
                'avg_confidence': avg_confidence,
                'processing_time': processing_time,
                'detected_regions': len(text_lines),
                'region_confidences': [c * 100 for c in confidences]
            }
            
        except Exception as e:
            return {'error': f'PaddleOCR extraction failed: {str(e)}'}
    
    def analyze_native_text_extraction(self, pdf_path: Path) -> Dict:
        """Analyze native text extraction quality."""
        text_analysis = {
            'pymupdf': {'text': '', 'extractable': False, 'quality_score': 0},
            'pdfplumber': {'text': '', 'extractable': False, 'quality_score': 0}
        }
        
        # PyMuPDF extraction
        try:
            doc = fitz.open(pdf_path)
            pymupdf_text = ""
            for page in doc:
                pymupdf_text += page.get_text()
            doc.close()
            
            text_analysis['pymupdf'] = {
                'text': pymupdf_text,
                'extractable': len(pymupdf_text.strip()) > 0,
                'quality_score': self.calculate_text_quality_score(pymupdf_text),
                'character_count': len(pymupdf_text),
                'word_count': len(pymupdf_text.split())
            }
        except Exception as e:
            text_analysis['pymupdf']['error'] = str(e)
        
        # pdfplumber extraction
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pdfplumber_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    pdfplumber_text += page_text
                
                text_analysis['pdfplumber'] = {
                    'text': pdfplumber_text,
                    'extractable': len(pdfplumber_text.strip()) > 0,
                    'quality_score': self.calculate_text_quality_score(pdfplumber_text),
                    'character_count': len(pdfplumber_text),
                    'word_count': len(pdfplumber_text.split())
                }
        except Exception as e:
            text_analysis['pdfplumber']['error'] = str(e)
        
        return text_analysis
    
    def calculate_text_quality_score(self, text: str) -> float:
        """Calculate a quality score for extracted text."""
        if not text or len(text.strip()) == 0:
            return 0.0
        
        score = 0.0
        
        # Check for reasonable character distribution
        alpha_chars = sum(1 for c in text if c.isalpha())
        total_chars = len(text)
        alpha_ratio = alpha_chars / total_chars if total_chars > 0 else 0
        score += min(alpha_ratio * 100, 40)  # Max 40 points
        
        # Check for proper word formation
        words = text.split()
        valid_words = sum(1 for word in words if len(word) > 1 and any(c.isalpha() for c in word))
        word_quality = valid_words / len(words) if words else 0
        score += word_quality * 30  # Max 30 points
        
        # Check for sentence structure
        sentences = re.split(r'[.!?]+', text)
        sentence_quality = min(len(sentences) / max(len(words) / 10, 1), 1) if words else 0
        score += sentence_quality * 20  # Max 20 points
        
        # Check for reasonable line breaks and spacing
        lines = text.split('\n')
        avg_line_length = np.mean([len(line.strip()) for line in lines if line.strip()])
        if avg_line_length > 10:  # Reasonable line length
            score += 10
        
        return min(score, 100.0)
    
    def detect_scanned_document(self, pdf_path: Path) -> Dict:
        """Detect if document is likely scanned based on various indicators."""
        indicators = {
            'likely_scanned': False,
            'confidence': 0.0,
            'evidence': []
        }
        
        try:
            # Check native text extraction
            native_analysis = self.analyze_native_text_extraction(pdf_path)
            
            # Check image presence
            images = self.detect_images_pymupdf(pdf_path)
            
            total_score = 0
            max_score = 0
            
            # Indicator 1: Low native text extraction
            max_score += 30
            pymupdf_quality = native_analysis['pymupdf']['quality_score']
            pdfplumber_quality = native_analysis['pdfplumber']['quality_score']
            avg_quality = (pymupdf_quality + pdfplumber_quality) / 2
            
            if avg_quality < 20:
                total_score += 30
                indicators['evidence'].append("Very poor native text extraction quality")
            elif avg_quality < 50:
                total_score += 15
                indicators['evidence'].append("Poor native text extraction quality")
            
            # Indicator 2: High number of images relative to pages
            max_score += 25
            if images:
                doc = fitz.open(pdf_path)
                page_count = len(doc)
                doc.close()
                
                image_per_page_ratio = len(images) / page_count
                if image_per_page_ratio >= 1.0:
                    total_score += 25
                    indicators['evidence'].append(f"High image density: {image_per_page_ratio:.1f} images per page")
                elif image_per_page_ratio >= 0.5:
                    total_score += 15
                    indicators['evidence'].append(f"Moderate image density: {image_per_page_ratio:.1f} images per page")
            
            # Indicator 3: Large images (potential full-page scans)
            max_score += 25
            large_images = [img for img in images if img['area_pixels'] > 500000]  # ~700x700 pixels
            if large_images:
                large_image_ratio = len(large_images) / len(images) if images else 0
                if large_image_ratio > 0.7:
                    total_score += 25
                    indicators['evidence'].append("Many large images detected (likely full-page scans)")
                elif large_image_ratio > 0.3:
                    total_score += 15
                    indicators['evidence'].append("Some large images detected")
            
            # Indicator 4: Minimal extractable text
            max_score += 20
            total_chars = (native_analysis['pymupdf']['character_count'] + 
                          native_analysis['pdfplumber']['character_count']) / 2
            
            if total_chars < 100:
                total_score += 20
                indicators['evidence'].append("Very little extractable text")
            elif total_chars < 500:
                total_score += 10
                indicators['evidence'].append("Limited extractable text")
            
            # Calculate final confidence
            confidence = (total_score / max_score) * 100 if max_score > 0 else 0
            indicators['confidence'] = confidence
            indicators['likely_scanned'] = confidence > 60
            
            if not indicators['evidence']:
                indicators['evidence'].append("Document appears to have good native text extraction")
            
        except Exception as e:
            indicators['error'] = str(e)
        
        return indicators
    
    def compare_ocr_engines(self, image_data: bytes) -> Dict:
        """Compare performance of different OCR engines on the same image."""
        results = {}
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Test each available engine
            if 'tesseract' in self.available_engines:
                results['tesseract'] = self.extract_text_tesseract(image)
            
            if 'easyocr' in self.available_engines:
                results['easyocr'] = self.extract_text_easyocr(image)
            
            if 'paddleocr' in self.available_engines:
                results['paddleocr'] = self.extract_text_paddleocr(image)
            
            # Calculate comparison metrics
            if len(results) > 1:
                comparison = self.calculate_ocr_comparison_metrics(results)
                results['comparison'] = comparison
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def calculate_ocr_comparison_metrics(self, ocr_results: Dict) -> Dict:
        """Calculate comparison metrics between OCR engines."""
        comparison = {
            'best_accuracy': '',
            'fastest': '',
            'most_text': '',
            'highest_confidence': '',
            'recommendations': []
        }
        
        valid_results = {k: v for k, v in ocr_results.items() if 'error' not in v}
        
        if not valid_results:
            return comparison
        
        # Find best in each category
        best_confidence = max(valid_results.items(), key=lambda x: x[1].get('avg_confidence', 0))
        fastest = min(valid_results.items(), key=lambda x: x[1].get('processing_time', float('inf')))
        most_text = max(valid_results.items(), key=lambda x: x[1].get('character_count', 0))
        
        comparison['highest_confidence'] = f"{best_confidence[0]} ({best_confidence[1].get('avg_confidence', 0):.1f}%)"
        comparison['fastest'] = f"{fastest[0]} ({fastest[1].get('processing_time', 0):.2f}s)"
        comparison['most_text'] = f"{most_text[0]} ({most_text[1].get('character_count', 0)} chars)"
        
        # Generate recommendations
        if best_confidence[1].get('avg_confidence', 0) > 80:
            comparison['recommendations'].append(f"Use {best_confidence[0]} for highest accuracy")
        
        if fastest[1].get('processing_time', 0) < 1.0:
            comparison['recommendations'].append(f"Use {fastest[0]} for fastest processing")
        
        if not comparison['recommendations']:
            comparison['recommendations'].append("Consider image preprocessing for better results")
        
        return comparison
    
    def analyze_document_ocr_performance(self, pdf_path: Path, extracted_text: str = "") -> Dict:
        """Complete OCR performance analysis for a document."""
        print(f"🔍 Analyzing OCR performance for: {pdf_path.name}")
        
        result = {
            'file_path': str(pdf_path),
            'analysis_status': 'success',
            'scanned_detection': {},
            'native_text_analysis': {},
            'image_analysis': {},
            'ocr_comparison': {},
            'recommendations': [],
            'overall_assessment': {}
        }
        
        try:
            # Detect if document is scanned
            print("🔍 Detecting if document is scanned...")
            result['scanned_detection'] = self.detect_scanned_document(pdf_path)
            
            # Analyze native text extraction
            print("📝 Analyzing native text extraction...")
            result['native_text_analysis'] = self.analyze_native_text_extraction(pdf_path)
            
            # Detect and analyze images
            print("🖼️ Detecting images...")
            images = self.detect_images_pymupdf(pdf_path)
            
            result['image_analysis'] = {
                'total_images': len(images),
                'images_by_page': {},
                'large_images': 0,
                'total_image_area': 0
            }
            
            # Group images by page and calculate stats
            for img in images:
                page = img['page']
                if page not in result['image_analysis']['images_by_page']:
                    result['image_analysis']['images_by_page'][page] = 0
                result['image_analysis']['images_by_page'][page] += 1
                
                result['image_analysis']['total_image_area'] += img['area_pixels']
                if img['area_pixels'] > 500000:
                    result['image_analysis']['large_images'] += 1
            
            # Test OCR on sample images if available and engines are available
            if images and self.available_engines:
                print("🔍 Testing OCR engines on sample images...")
                sample_images = images[:3]  # Test first 3 images
                ocr_tests = []
                
                for img in sample_images:
                    ocr_result = self.compare_ocr_engines(img['image_data'])
                    ocr_tests.append({
                        'page': img['page'],
                        'image_size': f"{img['width']}x{img['height']}",
                        'results': ocr_result
                    })
                
                result['ocr_comparison'] = {
                    'engines_tested': self.available_engines,
                    'sample_results': ocr_tests
                }
            else:
                result['ocr_comparison'] = {
                    'engines_tested': self.available_engines,
                    'note': 'No images found or no OCR engines available'
                }
            
            # Generate recommendations
            result['recommendations'] = self.generate_ocr_recommendations(result)
            
            # Overall assessment
            result['overall_assessment'] = self.generate_ocr_assessment(result)
            
        except Exception as e:
            result['analysis_status'] = 'error'
            result['error'] = str(e)
            print(f"❌ Error during OCR analysis: {e}")
        
        return result
    
    def generate_ocr_recommendations(self, analysis_result: Dict) -> List[str]:
        """Generate OCR recommendations based on analysis."""
        recommendations = []
        
        scanned_detection = analysis_result.get('scanned_detection', {})
        native_analysis = analysis_result.get('native_text_analysis', {})
        image_analysis = analysis_result.get('image_analysis', {})
        ocr_comparison = analysis_result.get('ocr_comparison', {})
        
        # Scanned document recommendations
        if scanned_detection.get('likely_scanned', False):
            recommendations.append("Document appears to be scanned - OCR processing recommended")
            recommendations.append("Consider using image preprocessing to improve OCR accuracy")
        
        # Poor native text quality
        pymupdf_quality = native_analysis.get('pymupdf', {}).get('quality_score', 0)
        pdfplumber_quality = native_analysis.get('pdfplumber', {}).get('quality_score', 0)
        avg_quality = (pymupdf_quality + pdfplumber_quality) / 2
        
        if avg_quality < 50:
            recommendations.append("Poor native text extraction - try OCR-based parsers")
        
        # Image-heavy document
        if image_analysis.get('total_images', 0) > 5:
            recommendations.append("Document contains many images - check for embedded text")
        
        # OCR engine recommendations
        if ocr_comparison.get('sample_results'):
            sample_results = ocr_comparison['sample_results']
            if sample_results:
                comparison = sample_results[0].get('results', {}).get('comparison', {})
                recommendations.extend(comparison.get('recommendations', []))
        
        # Engine availability recommendations
        if not self.available_engines:
            recommendations.append("Install OCR engines (Tesseract, EasyOCR, PaddleOCR) for better text extraction")
        elif len(self.available_engines) == 1:
            recommendations.append("Install additional OCR engines for comparison and better results")
        
        if not recommendations:
            recommendations.append("Document has good native text extraction - OCR not needed")
        
        return recommendations
    
    def generate_ocr_assessment(self, analysis_result: Dict) -> Dict:
        """Generate overall OCR assessment."""
        assessment = {
            'ocr_needed': False,
            'document_type': 'unknown',
            'extraction_quality': 'unknown',
            'recommended_approach': 'native_extraction',
            'confidence': 0.0
        }
        
        scanned_detection = analysis_result.get('scanned_detection', {})
        native_analysis = analysis_result.get('native_text_analysis', {})
        
        # Determine if OCR is needed
        scanned_confidence = scanned_detection.get('confidence', 0)
        assessment['ocr_needed'] = scanned_confidence > 60
        
        # Determine document type
        if scanned_confidence > 80:
            assessment['document_type'] = 'scanned'
        elif scanned_confidence > 40:
            assessment['document_type'] = 'mixed'
        else:
            assessment['document_type'] = 'digital'
        
        # Assess extraction quality
        pymupdf_quality = native_analysis.get('pymupdf', {}).get('quality_score', 0)
        pdfplumber_quality = native_analysis.get('pdfplumber', {}).get('quality_score', 0)
        avg_quality = (pymupdf_quality + pdfplumber_quality) / 2
        
        if avg_quality > 70:
            assessment['extraction_quality'] = 'excellent'
            assessment['recommended_approach'] = 'native_extraction'
        elif avg_quality > 50:
            assessment['extraction_quality'] = 'good'
            assessment['recommended_approach'] = 'native_extraction'
        elif avg_quality > 30:
            assessment['extraction_quality'] = 'fair'
            assessment['recommended_approach'] = 'hybrid_ocr'
        else:
            assessment['extraction_quality'] = 'poor'
            assessment['recommended_approach'] = 'ocr_only'
        
        # Overall confidence
        assessment['confidence'] = min((avg_quality + (100 - scanned_confidence)) / 2, 100)
        
        return assessment


def install_ocr_dependencies():
    """Install OCR dependencies."""
    required_packages = [
        'pytesseract',
        'easyocr',
        'paddleocr',
        'opencv-python',
        'Pillow'
    ]
    
    print("📦 Installing OCR analysis packages...")
    import subprocess
    import sys
    
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")


if __name__ == "__main__":
    # Example usage
    analyzer = OCRAnalyzer()
    
    print(f"Available OCR engines: {analyzer.available_engines}")
    
    # Test with a sample image if available
    if analyzer.available_engines:
        print("OCR analyzer ready for use!")
    else:
        print("Install OCR dependencies for full functionality.")