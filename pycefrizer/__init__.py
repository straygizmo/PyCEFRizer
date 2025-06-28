"""PyCEFRizer - CEFR-J Level Estimator.

A Python implementation for estimating the CEFR-J level of English reading passages.
Based on the CVLA3 methodology from Uchida & Negishi (2025).
"""

from .pycefrizer import PyCEFRizer
from .metrics import MetricsCalculator
from .resources import ResourceManager
from .cefr_mapping import CEFRMapper
from .config import config
from .exceptions import (
    PyCEFRizerError,
    TextLengthError,
    ResourceLoadError,
    SpacyModelError,
    MetricCalculationError
)
from .logger import logger, setup_logger
from .word_lookup import get_word_level, check_word_level
from .metrics import MetricsCalculator
from .resources import ResourceManager
from .cefr_mapping import CEFRMapper

__version__ = "3.0.0"
__all__ = [
    # Main classes
    "PyCEFRizer",
    "MetricsCalculator",
    "ResourceManager",
    "CEFRMapper",
    # Configuration
    "config",
    # Exceptions
    "PyCEFRizerError",
    "TextLengthError",
    "ResourceLoadError",
    "SpacyModelError",
    "MetricCalculationError",
    # Utilities
    "analyze",
    "logger",
    "setup_logger",
    "get_word_level",
    "check_word_level",
]

# Convenience function
def analyze(text):
    """Convenience function to analyze text."""
    analyzer = PyCEFRizer()
    return analyzer.analyze(text)