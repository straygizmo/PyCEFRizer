"""Custom exceptions for PyCEFRizer."""


class PyCEFRizerError(Exception):
    """Base exception for PyCEFRizer."""
    pass


class TextLengthError(PyCEFRizerError):
    """Raised when text length is outside allowed range."""
    pass


class ResourceLoadError(PyCEFRizerError):
    """Raised when resources cannot be loaded."""
    pass


class SpacyModelError(PyCEFRizerError):
    """Raised when spaCy model is not available."""
    pass


class MetricCalculationError(PyCEFRizerError):
    """Raised when a metric calculation fails."""
    pass