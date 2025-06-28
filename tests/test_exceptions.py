"""Tests for custom exceptions."""

import pytest
from pycefrizer.exceptions import (
    PyCEFRizerError,
    TextLengthError,
    ResourceLoadError,
    SpacyModelError,
    MetricCalculationError
)


def test_exception_hierarchy():
    """Test that all exceptions inherit from PyCEFRizerError."""
    assert issubclass(TextLengthError, PyCEFRizerError)
    assert issubclass(ResourceLoadError, PyCEFRizerError)
    assert issubclass(SpacyModelError, PyCEFRizerError)
    assert issubclass(MetricCalculationError, PyCEFRizerError)


def test_exception_messages():
    """Test exception message handling."""
    msg = "Test error message"
    
    with pytest.raises(TextLengthError) as exc_info:
        raise TextLengthError(msg)
    assert str(exc_info.value) == msg
    
    with pytest.raises(ResourceLoadError) as exc_info:
        raise ResourceLoadError(msg)
    assert str(exc_info.value) == msg