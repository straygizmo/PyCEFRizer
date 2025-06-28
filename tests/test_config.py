"""Tests for configuration module."""

import pytest
from pycefrizer.config import config


def test_config_values():
    """Test that configuration values are correctly set."""
    assert config.MIN_WORDS == 10
    assert config.MAX_WORDS == 10000
    assert config.SPACY_MODEL == 'en_core_web_sm'
    assert len(config.CONTENT_POS_TAGS) == 4
    assert 'NOUN' in config.CONTENT_POS_TAGS
    

def test_cefr_levels():
    """Test CEFR level mappings."""
    assert config.CEFR_LEVELS['A1'] == 1
    assert config.CEFR_LEVELS['C2'] == 6
    assert len(config.CEFR_LEVELS) == 6


def test_regression_coefficients():
    """Test regression coefficient structure."""
    assert len(config.REGRESSION_COEFFICIENTS) == 8
    
    for metric, (slope, intercept) in config.REGRESSION_COEFFICIENTS.items():
        assert isinstance(slope, float)
        assert isinstance(intercept, float)
        
    assert config.REGRESSION_COEFFICIENTS['CVV1'] == (1.1059, -1.208)


def test_cefr_j_boundaries():
    """Test CEFR-J boundary values."""
    assert len(config.CEFR_J_BOUNDARIES) == 12
    
    # Check first and last boundaries
    assert config.CEFR_J_BOUNDARIES[0] == (0.5, 'preA1')
    assert config.CEFR_J_BOUNDARIES[-1] == (float('inf'), 'C2')
    
    # Check that boundaries are in ascending order
    prev_boundary = -float('inf')
    for boundary, level in config.CEFR_J_BOUNDARIES:
        assert boundary > prev_boundary
        prev_boundary = boundary