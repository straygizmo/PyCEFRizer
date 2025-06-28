"""Convenience functions for word CEFR level lookup."""

from typing import Optional
from .pycefrizer import PyCEFRizer

# Global analyzer instance for convenience functions
_analyzer: Optional[PyCEFRizer] = None


def get_word_level(word: str) -> str:
    """Get CEFR level for a single word.
    
    This is a convenience function that creates a global PyCEFRizer
    instance on first use.
    
    Args:
        word: Single English word to look up
        
    Returns:
        CEFR level (A1, A2, B1, B2, C1, C2) or empty string if not found
        
    Example:
        >>> from pycefrizer import get_word_level
        >>> get_word_level("cat")
        'A1'
        >>> get_word_level("paradigm")
        'C1'
        >>> get_word_level("xyzabc")
        ''
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = PyCEFRizer()
    
    return _analyzer.get_word_cefr_level(word)


def check_word_level(word: str, target_level: str) -> bool:
    """Check if a word is at or below a target CEFR level.
    
    Args:
        word: Single English word to check
        target_level: Target CEFR level (A1, A2, B1, B2, C1, C2)
        
    Returns:
        True if word is at or below target level, False otherwise
        
    Example:
        >>> from pycefrizer import check_word_level
        >>> check_word_level("cat", "A2")  # cat is A1
        True
        >>> check_word_level("paradigm", "B1")  # paradigm is C1
        False
    """
    level = get_word_level(word)
    if not level:
        return False
    
    level_order = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    
    try:
        word_index = level_order.index(level)
        target_index = level_order.index(target_level.upper())
        return word_index <= target_index
    except ValueError:
        return False