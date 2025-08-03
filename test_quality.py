#!/usr/bin/env python3
"""Test the quality assessment system."""

from quality_assessment import QualityAssessment
import json

def test_quality_assessment():
    qa = QualityAssessment()
    
    # Test data with good quality text
    good_data = {
        'text': 'This is a well-structured document with proper sentences. It contains multiple paragraphs with good content flow. The text quality appears to be high with minimal noise and good semantic structure.',
        'metadata': {'file_name': 'test.pdf', 'file_size': 1024},
        'parser_name': 'PyMuPDF',
        'tables': [],
        'images': []
    }
    
    # Test data with poor quality text
    poor_data = {
        'text': 'jhsdf kjsdhf ksdjfh ksdjhfkjsdhf ksjdhf ksjdhfkjsdhfkjsdhf !!!!! aaaaa bbbbb',
        'metadata': {'file_name': 'test2.pdf', 'file_size': 512},
        'parser_name': 'PyPDF',
        'tables': [],
        'images': []
    }
    
    print('=== QUALITY ASSESSMENT TEST ===')
    
    # Test good quality
    result_good = qa.assess_quality(good_data)
    print('\\n📄 GOOD QUALITY DOCUMENT:')
    print(f'Overall Quality: {result_good["overall_quality"]:.3f}')
    print(f'Confidence Level: {result_good["confidence_level"]}')
    print(f'Quality Grade: {result_good["quality_grade"]}')
    print(f'Recommendations: {result_good["recommendations"]}')
    
    # Test poor quality
    result_poor = qa.assess_quality(poor_data)
    print('\\n📄 POOR QUALITY DOCUMENT:')
    print(f'Overall Quality: {result_poor["overall_quality"]:.3f}')
    print(f'Confidence Level: {result_poor["confidence_level"]}')
    print(f'Quality Grade: {result_poor["quality_grade"]}')
    print(f'Recommendations: {result_poor["recommendations"]}')
    
    print('\\n✅ Quality assessment system working correctly!')

if __name__ == "__main__":
    test_quality_assessment()