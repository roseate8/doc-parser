"""
Document Parser Quality Assessment System

Evaluates the quality of parsed document output using multiple metrics
to provide a comprehensive confidence score for parser performance.
"""

import re
import string
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import statistics
from collections import Counter
import hashlib


class QualityAssessment:
    """Comprehensive quality assessment for document parser outputs."""
    
    def __init__(self):
        # Weights for the quality formula - these can be tuned based on requirements
        self.weights = {
            'completeness': 0.25,      # w1 - How complete is the extraction
            'semantic_quality': 0.20,  # w2 - Semantic coherence and structure
            'noise_reduction': 0.20,   # w3 - (1 - noise_level) 
            'format_preservation': 0.15, # w4 - How well formatting is preserved
            'content_structure': 0.20    # w5 - Logical structure and organization
        }
    
    def assess_quality(self, parsed_data: Dict[str, Any], file_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Comprehensive quality assessment of parsed document output.
        
        Args:
            parsed_data: The parsed document data from any parser
            file_path: Optional path to original file for additional analysis
            
        Returns:
            Dictionary containing quality metrics and overall score
        """
        text_content = parsed_data.get('text', '')
        metadata = parsed_data.get('metadata', {})
        parser_name = parsed_data.get('parser_name', 'Unknown')
        
        # Calculate individual quality metrics
        completeness_score = self._calculate_completeness(text_content, metadata)
        semantic_quality = self._calculate_semantic_quality(text_content)
        noise_level = self._calculate_noise_level(text_content)
        format_preservation = self._calculate_format_preservation(text_content, parsed_data)
        content_structure = self._calculate_content_structure(text_content)
        
        # Apply formula: Quality = w1*completeness + w2*semantic + w3*(1-noise) + w4*format + w5*structure
        overall_quality = (
            self.weights['completeness'] * completeness_score +
            self.weights['semantic_quality'] * semantic_quality +
            self.weights['noise_reduction'] * (1 - noise_level) +
            self.weights['format_preservation'] * format_preservation +
            self.weights['content_structure'] * content_structure
        )
        
        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(overall_quality, text_content)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            completeness_score, semantic_quality, noise_level, 
            format_preservation, content_structure, parser_name
        )
        
        return {
            'overall_quality': round(overall_quality, 3),
            'confidence_level': confidence_level,
            'metrics': {
                'completeness_score': round(completeness_score, 3),
                'semantic_quality': round(semantic_quality, 3),
                'noise_level': round(noise_level, 3),
                'format_preservation': round(format_preservation, 3),
                'content_structure': round(content_structure, 3)
            },
            'parser_name': parser_name,
            'text_stats': {
                'character_count': len(text_content),
                'word_count': len(text_content.split()),
                'line_count': len(text_content.splitlines()),
                'paragraph_count': len([p for p in text_content.split('\n\n') if p.strip()])
            },
            'recommendations': recommendations,
            'quality_grade': self._get_quality_grade(overall_quality)
        }
    
    def _calculate_completeness(self, text: str, metadata: Dict) -> float:
        """Calculate how complete the text extraction appears to be."""
        if not text.strip():
            return 0.0
        
        score = 0.5  # Base score
        
        # Length-based indicators
        if len(text) > 100:
            score += 0.2
        if len(text) > 1000:
            score += 0.1
        
        # Content indicators
        sentences = re.split(r'[.!?]+', text)
        complete_sentences = [s for s in sentences if len(s.strip()) > 10]
        if complete_sentences:
            score += 0.2 * min(len(complete_sentences) / 5, 1.0)
        
        # Check for truncation indicators
        truncation_indicators = ['...', '[truncated]', '[continued]', 'Page 1 of']
        if any(indicator in text for indicator in truncation_indicators):
            score -= 0.1
        
        return min(score, 1.0)
    
    def _calculate_semantic_quality(self, text: str) -> float:
        """Calculate semantic quality and coherence of the text."""
        if not text.strip():
            return 0.0
        
        score = 0.0
        words = text.split()
        
        if not words:
            return 0.0
        
        # Vocabulary diversity
        unique_words = set(word.lower().strip(string.punctuation) for word in words)
        if len(words) > 0:
            diversity_ratio = len(unique_words) / len(words)
            score += min(diversity_ratio * 2, 0.3)  # Cap at 0.3
        
        # Sentence structure quality
        sentences = re.split(r'[.!?]+', text)
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if valid_sentences:
            avg_sentence_length = statistics.mean(len(s.split()) for s in valid_sentences)
            if 5 <= avg_sentence_length <= 30:  # Reasonable sentence length
                score += 0.2
            
            # Check for proper capitalization
            properly_capitalized = sum(1 for s in valid_sentences if s and s[0].isupper())
            if properly_capitalized > len(valid_sentences) * 0.7:
                score += 0.1
        
        # Coherence indicators (basic)
        coherence_words = ['however', 'therefore', 'moreover', 'furthermore', 'additionally', 
                          'consequently', 'meanwhile', 'subsequently', 'nevertheless']
        coherence_count = sum(1 for word in coherence_words if word in text.lower())
        score += min(coherence_count * 0.05, 0.2)
        
        # Paragraph structure
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) > 1:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_noise_level(self, text: str) -> float:
        """Calculate the level of noise/garbage in the extracted text."""
        if not text.strip():
            return 1.0  # Maximum noise for empty text
        
        noise_score = 0.0
        total_chars = len(text)
        
        if total_chars == 0:
            return 1.0
        
        # Excessive special characters
        special_chars = sum(1 for c in text if not c.isalnum() and c not in ' \n\t.,;:!?()-"\'')
        noise_score += min(special_chars / total_chars, 0.3)
        
        # Repeated characters (OCR errors)
        repeated_patterns = re.findall(r'(.)\1{3,}', text)  # 4+ repeated chars
        noise_score += min(len(repeated_patterns) * 0.05, 0.2)
        
        # Gibberish detection (sequences of consonants or random chars)
        gibberish_patterns = re.findall(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{6,}', text)
        noise_score += min(len(gibberish_patterns) * 0.1, 0.2)
        
        # Fragmented words (too many single characters)
        words = text.split()
        single_chars = sum(1 for word in words if len(word.strip(string.punctuation)) == 1)
        if words:
            noise_score += min(single_chars / len(words), 0.3)
        
        return min(noise_score, 1.0)
    
    def _calculate_format_preservation(self, text: str, parsed_data: Dict) -> float:
        """Calculate how well the original formatting is preserved."""
        score = 0.0
        
        # Line breaks preservation
        line_count = len(text.splitlines())
        if line_count > 1:
            score += 0.3
        
        # Paragraph preservation
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            score += 0.2
        
        # Table detection bonus
        tables = parsed_data.get('tables', [])
        if tables:
            score += 0.3
        
        # List detection (bullet points, numbers)
        list_patterns = re.findall(r'^\s*[•\-\*\d+]\s+', text, re.MULTILINE)
        if list_patterns:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_content_structure(self, text: str) -> float:
        """Calculate the logical structure and organization of content."""
        score = 0.0
        
        # Heading detection
        potential_headings = re.findall(r'^[A-Z][A-Za-z\s]{2,50}$', text, re.MULTILINE)
        if potential_headings:
            score += 0.3
        
        # Balanced content distribution
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        if paragraphs:
            lengths = [len(p) for p in paragraphs]
            if len(lengths) > 1:
                # Check if paragraphs have reasonable length distribution
                avg_length = statistics.mean(lengths)
                if 50 <= avg_length <= 1000:
                    score += 0.2
        
        # Content flow indicators
        flow_indicators = re.findall(r'\b(first|second|third|finally|conclusion|introduction)\b', 
                                   text.lower())
        if flow_indicators:
            score += 0.2
        
        # Proper punctuation usage
        sentences = re.split(r'[.!?]+', text)
        proper_sentences = [s for s in sentences if s.strip() and len(s.strip()) > 5]
        if proper_sentences:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_confidence_level(self, overall_quality: float, text: str) -> str:
        """Determine confidence level based on quality score and text characteristics."""
        if overall_quality >= 0.8:
            return "Very High"
        elif overall_quality >= 0.65:
            return "High" 
        elif overall_quality >= 0.5:
            return "Medium"
        elif overall_quality >= 0.3:
            return "Low"
        else:
            return "Very Low"
    
    def _generate_recommendations(self, completeness: float, semantic: float, noise: float, 
                                format_pres: float, structure: float, parser_name: str) -> List[str]:
        """Generate actionable recommendations based on quality metrics."""
        recommendations = []
        
        if completeness < 0.6:
            recommendations.append("Consider using a different parser for better text extraction")
            
        if semantic < 0.5:
            recommendations.append("Text quality is low - manual review recommended")
            
        if noise > 0.4:
            recommendations.append("High noise detected - consider post-processing cleanup")
            
        if format_pres < 0.4:
            recommendations.append("Formatting not well preserved - try PyMuPDF or pdfplumber for PDFs")
            
        if structure < 0.4:
            recommendations.append("Document structure not well maintained - consider LlamaParse for complex layouts")
        
        # Parser-specific recommendations
        if parser_name == "PyPDF" and (format_pres < 0.5 or structure < 0.5):
            recommendations.append("PyPDF is basic - try PyMuPDF or pdfplumber for better results")
            
        if parser_name == "LlamaParse" and completeness < 0.7:
            recommendations.append("LlamaParse may need better prompting or document preprocessing")
        
        if not recommendations:
            recommendations.append("Quality is good - output should be suitable for most use cases")
            
        return recommendations
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade."""
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B+"
        elif score >= 0.6:
            return "B"
        elif score >= 0.5:
            return "C+"
        elif score >= 0.4:
            return "C"
        elif score >= 0.3:
            return "D"
        else:
            return "F"


def assess_multiple_parsers(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare quality across multiple parser results for the same document.
    
    Args:
        results: List of parsing results from different parsers
        
    Returns:
        Comparison analysis with best parser recommendation
    """
    if not results:
        return {"error": "No results to compare"}
    
    assessor = QualityAssessment()
    assessments = []
    
    for result in results:
        assessment = assessor.assess_quality(result)
        assessments.append(assessment)
    
    # Find best performer
    best_assessment = max(assessments, key=lambda x: x['overall_quality'])
    
    # Calculate agreement metrics
    qualities = [a['overall_quality'] for a in assessments]
    quality_std = statistics.stdev(qualities) if len(qualities) > 1 else 0
    
    return {
        'assessments': assessments,
        'best_parser': best_assessment['parser_name'],
        'best_quality': best_assessment['overall_quality'],
        'quality_variance': round(quality_std, 3),
        'consensus_level': "High" if quality_std < 0.1 else "Medium" if quality_std < 0.2 else "Low",
        'recommendation': f"Use {best_assessment['parser_name']} for best results" if len(assessments) > 1 else "Single parser assessment completed"
    }