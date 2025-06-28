"""Tests for CEFR mapping module."""

import pytest
from pycefrizer.cefr_mapping import CEFRMapper


class TestCEFRMapper:
    """Test suite for CEFRMapper class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mapper = CEFRMapper()
        
    def test_apply_regression(self):
        """Test regression equation application."""
        # Test known values
        assert self.mapper.apply_regression(2.0, 'CVV1') == pytest.approx(1.0038, 0.001)
        assert self.mapper.apply_regression(0.5, 'BperA') == pytest.approx(7.001, 0.001)
        
        # Test capping at 7
        assert self.mapper.apply_regression(100.0, 'CVV1') == 7.0
        
        # Test unknown metric
        with pytest.raises(ValueError):
            self.mapper.apply_regression(1.0, 'UnknownMetric')
    
    def test_calculate_cefr_scores(self):
        """Test CEFR score calculation for all metrics."""
        metrics = {
            'AvrDiff': 2.0,
            'BperA': 0.3,
            'CVV1': 3.0,
            'AvrFreqRank': 1000,
            'ARI': 8.0,
            'VperSent': 2.0,
            'POStypes': 8.0,
            'LenNP': 3.0
        }
        
        scores = self.mapper.calculate_cefr_scores(metrics)
        
        # Check all metrics are present
        assert len(scores) == 8
        assert all(key.endswith('_CEFR') for key in scores)
        
        # Check specific calculations
        assert scores['CVV1_CEFR'] == pytest.approx(2.11, 0.01)
        assert scores['ARI_CEFR'] == pytest.approx(3.22, 0.01)
    
    def test_calculate_final_level(self):
        """Test final level calculation."""
        # Test with 8 scores (normal case)
        scores = {
            'CVV1_CEFR': 1.0,
            'BperA_CEFR': 2.0,
            'POStypes_CEFR': 3.0,
            'ARI_CEFR': 4.0,
            'AvrDiff_CEFR': 5.0,
            'AvrFreqRank_CEFR': 6.0,
            'VperSent_CEFR': 7.0,
            'LenNP_CEFR': 8.0
        }
        
        # Should exclude min (1.0) and max (8.0), average remaining 6
        final_score = self.mapper.calculate_final_level(scores)
        assert final_score == pytest.approx(4.5, 0.01)
        
        # Test with 2 scores
        scores_small = {'Metric1_CEFR': 2.0, 'Metric2_CEFR': 4.0}
        assert self.mapper.calculate_final_level(scores_small) == 3.0
        
        # Test with empty scores
        assert self.mapper.calculate_final_level({}) == 0.0
    
    def test_map_to_cefr_j(self):
        """Test mapping scores to CEFR-J levels."""
        test_cases = [
            (0.3, 'preA1'),
            (0.5, 'A1.1'),
            (1.0, 'A1.2'),
            (1.5, 'A2.1'),
            (2.5, 'B1.1'),
            (3.5, 'B2.1'),
            (4.5, 'C1'),
            (6.0, 'C2'),
            (10.0, 'C2'),  # Very high score
        ]
        
        for score, expected_level in test_cases:
            assert self.mapper.map_to_cefr_j(score) == expected_level
    
    def test_process_metrics(self):
        """Test complete metric processing pipeline."""
        metrics = {
            'AvrDiff': 2.0,
            'BperA': 0.3,
            'CVV1': 3.0,
            'AvrFreqRank': 1000,
            'ARI': 8.0,
            'VperSent': 2.0,
            'POStypes': 8.0,
            'LenNP': 3.0
        }
        
        cefr_j_level, cefr_scores = self.mapper.process_metrics(metrics)
        
        # Check output structure
        assert isinstance(cefr_j_level, str)
        assert isinstance(cefr_scores, dict)
        assert len(cefr_scores) == 8
        
        # Check all scores are strings
        assert all(isinstance(score, str) for score in cefr_scores.values())