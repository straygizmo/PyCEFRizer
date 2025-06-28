"""Tests for main PyCEFRizer class."""

import json
import pytest
from unittest.mock import Mock, patch

from pycefrizer import PyCEFRizer
from pycefrizer.exceptions import TextLengthError, SpacyModelError


class TestPyCEFRizer:
    """Test suite for PyCEFRizer class."""
    
    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing."""
        return {
            'short': "This is too short.",  # Less than 10 words
            'valid': " ".join(["word"] * 50),  # 50 words
            'long': " ".join(["word"] * 11000),  # More than 10000 words
            'empty': "",
            'whitespace': "   \n\t  ",
            'simple': """
                The cat sat on the mat. The dog ran in the park.
                Birds fly in the sky. Fish swim in water.
                Trees grow in the forest. Flowers bloom in spring.
                Children play with toys. Adults work at jobs.
                The sun shines bright. The moon glows at night.
            """,  # Simple A1-level text
            'complex': """
                The paradigmatic shift in contemporary epistemological discourse
                necessitates a comprehensive reconsideration of ontological premises.
                Quantum mechanics elucidates the probabilistic nature of subatomic
                phenomena, challenging deterministic frameworks. The emergence of
                artificial intelligence precipitates philosophical inquiries regarding
                consciousness and cognition. Interdisciplinary synthesis facilitates
                nuanced understanding of complex systems. Phenomenological analysis
                reveals intricate relationships between subjective experience and
                objective reality.
            """  # Complex C1-C2 level text
        }
    
    @patch('pycefrizer.pycefrizer.spacy.load')
    def test_initialization(self, mock_spacy_load):
        """Test PyCEFRizer initialization."""
        mock_nlp = Mock()
        mock_spacy_load.return_value = mock_nlp
        
        analyzer = PyCEFRizer()
        
        assert analyzer.nlp == mock_nlp
        mock_spacy_load.assert_called_once_with('en_core_web_sm')
    
    @patch('pycefrizer.pycefrizer.spacy.load')
    def test_initialization_with_custom_model(self, mock_spacy_load):
        """Test initialization with custom spaCy model."""
        mock_nlp = Mock()
        mock_spacy_load.return_value = mock_nlp
        
        analyzer = PyCEFRizer(spacy_model='en_core_web_lg')
        
        mock_spacy_load.assert_called_once_with('en_core_web_lg')
    
    @patch('pycefrizer.pycefrizer.spacy.load')
    def test_initialization_model_not_found(self, mock_spacy_load):
        """Test initialization when spaCy model is not found."""
        mock_spacy_load.side_effect = OSError("Model not found")
        
        with pytest.raises(SpacyModelError) as exc_info:
            PyCEFRizer()
        
        assert "not found" in str(exc_info.value)
        assert "python -m spacy download" in str(exc_info.value)
    
    @patch('pycefrizer.pycefrizer.spacy.load')
    def test_validate_input(self, mock_spacy_load, sample_texts):
        """Test input validation."""
        mock_spacy_load.return_value = Mock()
        analyzer = PyCEFRizer()
        
        # Test valid input
        word_count = analyzer.validate_input(sample_texts['valid'])
        assert word_count == 50
        
        # Test empty input
        with pytest.raises(TextLengthError) as exc_info:
            analyzer.validate_input(sample_texts['empty'])
        assert "cannot be empty" in str(exc_info.value)
        
        # Test whitespace only
        with pytest.raises(TextLengthError) as exc_info:
            analyzer.validate_input(sample_texts['whitespace'])
        assert "cannot be empty" in str(exc_info.value)
        
        # Test too short
        with pytest.raises(TextLengthError) as exc_info:
            analyzer.validate_input(sample_texts['short'])
        assert "too short" in str(exc_info.value)
        assert "10 words required" in str(exc_info.value)
        
        # Test too long
        with pytest.raises(TextLengthError) as exc_info:
            analyzer.validate_input(sample_texts['long'])
        assert "too long" in str(exc_info.value)
        assert "10000 words allowed" in str(exc_info.value)
    
    @patch('pycefrizer.pycefrizer.spacy.load')
    def test_analyze_output_structure(self, mock_spacy_load, sample_texts):
        """Test analyze method output structure."""
        # Mock spaCy components
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=50)
        mock_doc.sents = [Mock() for _ in range(5)]
        
        mock_nlp = Mock(return_value=mock_doc)
        mock_spacy_load.return_value = mock_nlp
        
        with patch('pycefrizer.metrics.MetricsCalculator.calculate_all_metrics') as mock_metrics:
            mock_metrics.return_value = {
                'AvrDiff': 2.0,
                'BperA': 0.3,
                'CVV1': 3.0,
                'AvrFreqRank': 1000,
                'ARI': 8.0,
                'VperSent': 2.0,
                'POStypes': 8.0,
                'LenNP': 3.0
            }
            
            analyzer = PyCEFRizer()
            result = analyzer.analyze(sample_texts['simple'])
            
            # Check result structure
            assert isinstance(result, dict)
            assert 'CEFR-J_Level' in result
            assert isinstance(result['CEFR-J_Level'], str)
            
            # Check metric scores
            expected_metrics = [
                'AvrDiff_CEFR', 'BperA_CEFR', 'CVV1_CEFR', 
                'AvrFreqRank_CEFR', 'ARI_CEFR', 'VperSent_CEFR',
                'POStypes_CEFR', 'LenNP_CEFR'
            ]
            for metric in expected_metrics:
                assert metric in result
                assert isinstance(result[metric], str)
    
    @patch('pycefrizer.pycefrizer.spacy.load')
    def test_analyze_json(self, mock_spacy_load, sample_texts):
        """Test JSON output method."""
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=50)
        mock_doc.sents = [Mock() for _ in range(5)]
        
        mock_nlp = Mock(return_value=mock_doc)
        mock_spacy_load.return_value = mock_nlp
        
        with patch('pycefrizer.metrics.MetricsCalculator.calculate_all_metrics') as mock_metrics:
            mock_metrics.return_value = {
                'AvrDiff': 2.0,
                'BperA': 0.3,
                'CVV1': 3.0,
                'AvrFreqRank': 1000,
                'ARI': 8.0,
                'VperSent': 2.0,
                'POStypes': 8.0,
                'LenNP': 3.0
            }
            
            analyzer = PyCEFRizer()
            json_result = analyzer.analyze_json(sample_texts['simple'])
            
            # Check it's valid JSON
            parsed = json.loads(json_result)
            assert isinstance(parsed, dict)
            assert 'CEFR-J_Level' in parsed
    
    @patch('pycefrizer.pycefrizer.spacy.load')
    def test_get_detailed_analysis(self, mock_spacy_load, sample_texts):
        """Test detailed analysis method."""
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=50)
        mock_doc.sents = [Mock() for _ in range(5)]
        
        mock_nlp = Mock(return_value=mock_doc)
        mock_spacy_load.return_value = mock_nlp
        
        with patch('pycefrizer.metrics.MetricsCalculator.calculate_all_metrics') as mock_metrics:
            mock_metrics.return_value = {
                'AvrDiff': 2.12345,
                'BperA': 0.36789,
                'CVV1': 3.14159,
                'AvrFreqRank': 1234.5678,
                'ARI': 8.91011,
                'VperSent': 2.22222,
                'POStypes': 8.33333,
                'LenNP': 3.44444
            }
            
            analyzer = PyCEFRizer()
            result = analyzer.get_detailed_analysis(sample_texts['simple'])
            
            # Check result structure
            assert isinstance(result, dict)
            assert 'CEFR-J_Level' in result
            assert 'CEFR_Scores' in result
            assert 'Raw_Metrics' in result
            assert 'Text_Statistics' in result
            
            # Check raw metrics are rounded to 4 decimal places
            for value in result['Raw_Metrics'].values():
                assert len(str(value).split('.')[-1]) <= 4
            
            # Check text statistics
            stats = result['Text_Statistics']
            assert 'word_count' in stats
            assert 'sentence_count' in stats
            assert 'token_count' in stats