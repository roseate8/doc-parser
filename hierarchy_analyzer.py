"""
Document Hierarchy Analyzer using LayoutParser.

This module analyzes the visual structure of documents and compares it
with extracted text hierarchy to validate parsing accuracy.
"""

from pathlib import Path
import re
from typing import Dict, List, Tuple, Any
import json
import numpy as np

# Optional dependencies for full functionality
VISUAL_ANALYSIS_AVAILABLE = False
try:
    import cv2
    import layoutparser as lp
    from PIL import Image
    import pdf2image
    VISUAL_ANALYSIS_AVAILABLE = True
except ImportError:
    # Stub imports to avoid IDE errors
    cv2 = lp = Image = pdf2image = None

if not VISUAL_ANALYSIS_AVAILABLE:
    print("⚠️ Visual analysis dependencies not installed. Text analysis only available.")


class HierarchyAnalyzer:
    """Analyzes document hierarchy using LayoutParser for visual structure detection."""
    
    def __init__(self):
        """Initialize the hierarchy analyzer with LayoutParser models."""
        self.model = None
        
        if VISUAL_ANALYSIS_AVAILABLE:
            try:
                # Load pre-trained LayoutParser model for document layout detection
                # Using PubLayNet model which detects: text, title, list, table, figure
                self.model = lp.Detectron2LayoutModel(
                    'lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
                    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                    label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
                )
                print("✅ LayoutParser model loaded successfully")
            except Exception as e:
                print(f"⚠️ Warning: Could not load LayoutParser model: {e}")
                self.model = None
        else:
            print("ℹ️ Text-only analysis mode. Install visual dependencies for full functionality.")
    
    def pdf_to_images(self, pdf_path: Path) -> List:
        """Convert PDF pages to images for layout analysis."""
        if not VISUAL_ANALYSIS_AVAILABLE:
            print("❌ Visual analysis dependencies not available")
            return []
            
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(
                pdf_path, 
                dpi=150,  # Good balance between quality and processing speed
                fmt='RGB'
            )
            
            # Convert PIL images to numpy arrays
            image_arrays = []
            for img in images:
                img_array = np.array(img)
                image_arrays.append(img_array)
            
            return image_arrays
        except Exception as e:
            print(f"❌ Error converting PDF to images: {e}")
            return []
    
    def detect_layout_elements(self, image) -> List[Dict]:
        """Detect layout elements using LayoutParser."""
        if not VISUAL_ANALYSIS_AVAILABLE or self.model is None:
            return []
        
        try:
            # Detect layout elements
            layout = self.model.detect(image)
            
            # Convert to dictionary format
            elements = []
            for block in layout:
                element = {
                    'type': block.type,
                    'bbox': [block.block.x_1, block.block.y_1, block.block.x_2, block.block.y_2],
                    'confidence': block.score,
                    'area': (block.block.x_2 - block.block.x_1) * (block.block.y_2 - block.block.y_1)
                }
                elements.append(element)
            
            # Sort by vertical position (top to bottom reading order)
            elements.sort(key=lambda x: x['bbox'][1])
            
            return elements
        except Exception as e:
            print(f"❌ Error detecting layout elements: {e}")
            return []
    
    def extract_text_hierarchy(self, text: str) -> Dict[str, List]:
        """Extract hierarchy patterns from text content."""
        hierarchy = {
            'headings': [],
            'lists': [],
            'paragraphs': [],
            'patterns': {}
        }
        
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detect headings (various patterns)
            heading_patterns = [
                r'^#+\s+(.+)$',  # Markdown headers
                r'^(\d+\.?\s*[A-Z][^.]*\.?)\s*$',  # Numbered sections
                r'^([A-Z][A-Z\s]{2,})\s*$',  # ALL CAPS
                r'^([A-Z][a-z\s]{3,})\s*$',  # Title case
            ]
            
            for pattern in heading_patterns:
                if re.match(pattern, line):
                    hierarchy['headings'].append({
                        'text': line,
                        'line_number': i,
                        'pattern': pattern,
                        'length': len(line)
                    })
                    break
            
            # Detect lists
            list_patterns = [
                r'^[•·▪▫◦‣⁃]\s+(.+)$',  # Bullet points
                r'^[-*]\s+(.+)$',  # Dash/asterisk bullets
                r'^\d+[.)]\s+(.+)$',  # Numbered lists
                r'^[a-zA-Z][.)]\s+(.+)$',  # Lettered lists
            ]
            
            for pattern in list_patterns:
                match = re.match(pattern, line)
                if match:
                    hierarchy['lists'].append({
                        'text': line,
                        'content': match.group(1),
                        'line_number': i,
                        'pattern': pattern
                    })
                    break
            
            # Regular paragraphs
            if len(line) > 20 and not any(re.match(p, line) for p in heading_patterns + list_patterns):
                hierarchy['paragraphs'].append({
                    'text': line[:100] + '...' if len(line) > 100 else line,
                    'line_number': i,
                    'length': len(line)
                })
        
        # Calculate patterns
        hierarchy['patterns'] = {
            'heading_count': len(hierarchy['headings']),
            'list_count': len(hierarchy['lists']),
            'paragraph_count': len(hierarchy['paragraphs']),
            'avg_heading_length': np.mean([h['length'] for h in hierarchy['headings']]) if hierarchy['headings'] else 0,
            'text_structure_ratio': len(hierarchy['headings']) / max(len(hierarchy['paragraphs']), 1)
        }
        
        return hierarchy
    
    def analyze_visual_hierarchy(self, elements: List[Dict]) -> Dict[str, Any]:
        """Analyze visual hierarchy from layout elements."""
        analysis = {
            'titles': [],
            'text_blocks': [],
            'lists': [],
            'tables': [],
            'figures': [],
            'layout_patterns': {}
        }
        
        # Group elements by type
        for element in elements:
            element_type = element['type'].lower()
            if element_type == 'title':
                analysis['titles'].append(element)
            elif element_type == 'text':
                analysis['text_blocks'].append(element)
            elif element_type == 'list':
                analysis['lists'].append(element)
            elif element_type == 'table':
                analysis['tables'].append(element)
            elif element_type == 'figure':
                analysis['figures'].append(element)
        
        # Calculate layout patterns
        total_elements = len(elements)
        if total_elements > 0:
            analysis['layout_patterns'] = {
                'title_ratio': len(analysis['titles']) / total_elements,
                'text_ratio': len(analysis['text_blocks']) / total_elements,
                'list_ratio': len(analysis['lists']) / total_elements,
                'table_ratio': len(analysis['tables']) / total_elements,
                'figure_ratio': len(analysis['figures']) / total_elements,
                'structure_complexity': len(set(e['type'] for e in elements)),
                'avg_confidence': np.mean([e['confidence'] for e in elements])
            }
        
        return analysis
    
    def compare_hierarchies(self, text_hierarchy: Dict, visual_hierarchy: Dict) -> Dict[str, Any]:
        """Compare extracted text hierarchy with visual layout hierarchy."""
        comparison = {
            'match_score': 0.0,
            'discrepancies': [],
            'insights': [],
            'recommendations': []
        }
        
        # Compare heading/title counts
        text_headings = text_hierarchy['patterns']['heading_count']
        visual_titles = len(visual_hierarchy['titles'])
        
        if visual_titles > 0:
            heading_match = min(text_headings / visual_titles, visual_titles / text_headings) if text_headings > 0 else 0
        else:
            heading_match = 1.0 if text_headings == 0 else 0.0
        
        # Compare list structures
        text_lists = text_hierarchy['patterns']['list_count']
        visual_lists = len(visual_hierarchy['lists'])
        
        if visual_lists > 0:
            list_match = min(text_lists / visual_lists, visual_lists / text_lists) if text_lists > 0 else 0
        else:
            list_match = 1.0 if text_lists == 0 else 0.0
        
        # Calculate overall match score
        comparison['match_score'] = (heading_match + list_match) / 2
        
        # Identify discrepancies
        if abs(text_headings - visual_titles) > 1:
            comparison['discrepancies'].append(
                f"Heading mismatch: Found {text_headings} text headings vs {visual_titles} visual titles"
            )
        
        if abs(text_lists - visual_lists) > 1:
            comparison['discrepancies'].append(
                f"List mismatch: Found {text_lists} text lists vs {visual_lists} visual lists"
            )
        
        # Generate insights
        if comparison['match_score'] > 0.8:
            comparison['insights'].append("✅ Excellent hierarchy extraction - structure well preserved")
        elif comparison['match_score'] > 0.6:
            comparison['insights'].append("⚠️ Good hierarchy extraction with minor discrepancies")
        elif comparison['match_score'] > 0.4:
            comparison['insights'].append("❌ Moderate hierarchy loss - some structure not captured")
        else:
            comparison['insights'].append("❌ Poor hierarchy extraction - significant structure loss")
        
        # Generate recommendations
        if visual_titles > text_headings:
            comparison['recommendations'].append("Consider using a parser better at detecting headers/titles")
        
        if visual_lists > text_lists:
            comparison['recommendations'].append("Consider using a parser with better list detection capabilities")
        
        if len(visual_hierarchy['tables']) > 0:
            comparison['recommendations'].append("Document contains tables - consider using table-specialized parsers")
        
        return comparison
    
    def analyze_document_hierarchy(self, file_path: Path, extracted_text: str) -> Dict[str, Any]:
        """Complete hierarchy analysis for a document."""
        print(f"🔍 Analyzing hierarchy for: {file_path.name}")
        
        result = {
            'file_path': str(file_path),
            'analysis_status': 'success',
            'text_hierarchy': {},
            'visual_hierarchy': {},
            'comparison': {},
            'overall_assessment': {}
        }
        
        try:
            # Extract text hierarchy
            print("📝 Extracting text hierarchy...")
            result['text_hierarchy'] = self.extract_text_hierarchy(extracted_text)
            
            # Only analyze PDF files for visual layout
            if file_path.suffix.lower() == '.pdf':
                print("🖼️ Converting PDF to images...")
                images = self.pdf_to_images(file_path)
                
                if images and self.model:
                    print("🔍 Detecting visual layout elements...")
                    all_elements = []
                    
                    for i, image in enumerate(images):
                        elements = self.detect_layout_elements(image)
                        # Add page information to elements
                        for element in elements:
                            element['page'] = i + 1
                        all_elements.extend(elements)
                    
                    result['visual_hierarchy'] = self.analyze_visual_hierarchy(all_elements)
                    
                    # Compare hierarchies
                    print("⚖️ Comparing text and visual hierarchies...")
                    result['comparison'] = self.compare_hierarchies(
                        result['text_hierarchy'], 
                        result['visual_hierarchy']
                    )
                else:
                    result['visual_hierarchy'] = {'error': 'Could not process PDF images or model not available'}
                    result['comparison'] = {'error': 'Visual analysis not available'}
            else:
                result['visual_hierarchy'] = {'info': 'Visual analysis only available for PDF files'}
                result['comparison'] = {'info': 'Comparison only available for PDF files'}
            
            # Overall assessment
            result['overall_assessment'] = self.generate_overall_assessment(result)
            
        except Exception as e:
            result['analysis_status'] = 'error'
            result['error'] = str(e)
            print(f"❌ Error during hierarchy analysis: {e}")
        
        return result
    
    def generate_overall_assessment(self, analysis_result: Dict) -> Dict[str, Any]:
        """Generate overall assessment of hierarchy extraction quality."""
        assessment = {
            'hierarchy_quality': 'unknown',
            'structure_preservation': 0.0,
            'parser_suitability': 'unknown',
            'summary': []
        }
        
        text_hierarchy = analysis_result.get('text_hierarchy', {})
        comparison = analysis_result.get('comparison', {})
        
        # Assess based on text patterns
        patterns = text_hierarchy.get('patterns', {})
        heading_count = patterns.get('heading_count', 0)
        list_count = patterns.get('list_count', 0)
        
        if 'match_score' in comparison:
            match_score = comparison['match_score']
            assessment['structure_preservation'] = match_score
            
            if match_score > 0.8:
                assessment['hierarchy_quality'] = 'excellent'
                assessment['parser_suitability'] = 'highly_suitable'
            elif match_score > 0.6:
                assessment['hierarchy_quality'] = 'good'
                assessment['parser_suitability'] = 'suitable'
            elif match_score > 0.4:
                assessment['hierarchy_quality'] = 'fair'
                assessment['parser_suitability'] = 'partially_suitable'
            else:
                assessment['hierarchy_quality'] = 'poor'
                assessment['parser_suitability'] = 'not_suitable'
        
        # Generate summary
        assessment['summary'] = [
            f"Detected {heading_count} headings and {list_count} lists in extracted text",
            f"Hierarchy quality: {assessment['hierarchy_quality']}",
            f"Parser suitability: {assessment['parser_suitability'].replace('_', ' ')}"
        ]
        
        if comparison.get('insights'):
            assessment['summary'].extend(comparison['insights'])
        
        return assessment


def install_dependencies():
    """Install required dependencies for hierarchy analysis."""
    required_packages = [
        'layoutparser[layoutmodels,tesseract,opencv]',
        'pdf2image',
        'opencv-python',
        'detectron2'
    ]
    
    print("📦 Installing required packages for hierarchy analysis...")
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
    analyzer = HierarchyAnalyzer()
    
    # Test with a sample text
    sample_text = """
    # Document Title
    
    This is an introduction paragraph explaining the purpose of this document.
    
    ## Section 1: Overview
    
    Here we discuss the main concepts:
    
    • First important point
    • Second important point  
    • Third important point
    
    ## Section 2: Details
    
    More detailed information follows.
    
    1. First detailed step
    2. Second detailed step
    3. Third detailed step
    
    ### Subsection 2.1
    
    Additional subsection content here.
    """
    
    # Analyze text hierarchy
    text_hierarchy = analyzer.extract_text_hierarchy(sample_text)
    print("\n📝 Text Hierarchy Analysis:")
    print(json.dumps(text_hierarchy, indent=2))