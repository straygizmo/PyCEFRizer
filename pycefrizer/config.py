"""Configuration settings for PyCEFRizer."""

from dataclasses import dataclass
from typing import Set, Dict, Tuple


@dataclass(frozen=True)
class Config:
    """Configuration settings for PyCEFRizer."""
    
    # Text length constraints
    MIN_WORDS: int = 10
    MAX_WORDS: int = 10000
    
    # spaCy model
    SPACY_MODEL: str = 'en_core_web_sm'
    
    # Content word POS tags
    CONTENT_POS_TAGS: Set[str] = frozenset({'NOUN', 'VERB', 'ADJ', 'ADV'})
    
    # Verb-related settings
    BE_VERBS: Set[str] = frozenset({'be', 'am', 'is', 'are', 'was', 'were', 'been', 'being'})
    
    # CEFR level mappings
    CEFR_LEVELS: Dict[str, int] = {
        'A1': 1,
        'A2': 2,
        'B1': 3,
        'B2': 4,
        'C1': 5,
        'C2': 6
    }
    
    # Regression equations coefficients (slope, intercept)
    REGRESSION_COEFFICIENTS: Dict[str, Tuple[float, float]] = {
        'CVV1': (1.1059, -1.208),
        'BperA': (13.146, 0.428),
        'POStypes': (1.768, -12.006),
        'ARI': (0.607, -1.632),
        'AvrDiff': (6.417, -7.184),
        'AvrFreqRank': (0.004, -0.608),
        'VperSent': (2.203, -2.486),
        'LenNP': (2.629, -6.697)
    }
    
    # CEFR-J level boundaries
    CEFR_J_BOUNDARIES: list = [
        (0.5, 'preA1'),
        (0.84, 'A1.1'),
        (1.17, 'A1.2'),
        (1.5, 'A1.3'),
        (2.0, 'A2.1'),
        (2.5, 'A2.2'),
        (3.0, 'B1.1'),
        (3.5, 'B1.2'),
        (4.0, 'B2.1'),
        (4.5, 'B2.2'),
        (5.5, 'C1'),
        (float('inf'), 'C2')
    ]
    
    # Metric calculation settings
    MAX_CEFR_SCORE: float = 7.0
    EXCLUDE_INFREQUENT_COUNT: int = 3  # For AvrFreqRank calculation
    DEFAULT_FREQUENCY_RANK: int = 10000  # For words not in COCA


# Global config instance
config = Config()