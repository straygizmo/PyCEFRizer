"""Tests for word CEFR level lookup functionality."""

import pytest
from unittest.mock import Mock, patch

from pycefrizer import PyCEFRizer, get_word_level, check_word_level
from pycefrizer.word_lookup import _analyzer


class TestWordLookup:
    """Test suite for word lookup functionality."""
    
    @patch('pycefrizer.pycefrizer.spacy.load')
    def test_get_word_cefr_level(self, mock_spacy_load):
        """Test getting CEFR level for single words."""
        mock_spacy_load.return_value = Mock()
        
        with patch('pycefrizer.resources.ResourceManager.get_word_level') as mock_get_level:
            # Set up mock responses
            mock_get_level.side_effect = lambda w: {
                'cat': 'A1',
                'beautiful': 'B1',
                'paradigm': 'C1',
                'xyz123': None
            }.get(w)
            
            analyzer = PyCEFRizer()
            
            # Test existing words
            assert analyzer.get_word_cefr_level('cat') == 'A1'
            assert analyzer.get_word_cefr_level('beautiful') == 'B1'
            assert analyzer.get_word_cefr_level('paradigm') == 'C1'
            
            # Test non-existent word
            assert analyzer.get_word_cefr_level('xyz123') == ''
            
            # Test empty input
            assert analyzer.get_word_cefr_level('') == ''
            
            # Test multi-word input (should return empty)
            assert analyzer.get_word_cefr_level('hello world') == ''
    
    @patch('pycefrizer.pycefrizer.spacy.load')
    def test_analyze_single_word(self, mock_spacy_load):
        """Test analyze method with single words."""
        mock_spacy_load.return_value = Mock()
        
        with patch('pycefrizer.resources.ResourceManager.get_word_level') as mock_get_level:
            mock_get_level.side_effect = lambda w: {
                'cat': 'A1',
                'beautiful': 'B1',
                'xyz123': None
            }.get(w)
            
            analyzer = PyCEFRizer()
            
            # Test single word returns only CEFR_Level
            result = analyzer.analyze('cat')
            assert result == {'CEFR_Level': 'A1'}
            
            result = analyzer.analyze('beautiful')
            assert result == {'CEFR_Level': 'B1'}
            
            # Test non-existent word
            result = analyzer.analyze('xyz123')
            assert result == {'CEFR_Level': ''}
    
    @patch('pycefrizer.pycefrizer.spacy.load')
    def test_convenience_functions(self, mock_spacy_load):
        """Test convenience functions for word lookup."""
        mock_spacy_load.return_value = Mock()
        
        # Reset global analyzer
        import pycefrizer.word_lookup
        pycefrizer.word_lookup._analyzer = None
        
        with patch('pycefrizer.resources.ResourceManager.get_word_level') as mock_get_level:
            mock_get_level.side_effect = lambda w: {
                'cat': 'A1',
                'beautiful': 'B1',
                'paradigm': 'C1',
                'xyz123': None
            }.get(w)
            
            # Test get_word_level
            assert get_word_level('cat') == 'A1'
            assert get_word_level('beautiful') == 'B1'
            assert get_word_level('xyz123') == ''
            
            # Check that analyzer was created
            assert pycefrizer.word_lookup._analyzer is not None
    
    def test_check_word_level(self):
        """Test check_word_level function."""
        with patch('pycefrizer.word_lookup.get_word_level') as mock_get_level:
            mock_get_level.side_effect = lambda w: {
                'cat': 'A1',
                'beautiful': 'B1',
                'paradigm': 'C1',
                'xyz123': ''
            }.get(w, '')
            
            # Test words at or below target level
            assert check_word_level('cat', 'A1') == True
            assert check_word_level('cat', 'A2') == True
            assert check_word_level('cat', 'C2') == True
            
            assert check_word_level('beautiful', 'B1') == True
            assert check_word_level('beautiful', 'B2') == True
            assert check_word_level('beautiful', 'A2') == False
            
            # Test word above target level
            assert check_word_level('paradigm', 'B1') == False
            assert check_word_level('paradigm', 'C1') == True
            assert check_word_level('paradigm', 'C2') == True
            
            # Test non-existent word
            assert check_word_level('xyz123', 'C2') == False
            
            # Test invalid target level
            assert check_word_level('cat', 'X1') == False