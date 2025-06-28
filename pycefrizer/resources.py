"""Resource loading and management for PyCEFRizer."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from functools import lru_cache

import spacy
from spacy.tokens import Doc, Token

from .config import config
from .exceptions import ResourceLoadError
from .logger import logger


class ResourceManager:
    """Manages loading and accessing linguistic resources for PyCEFRizer."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the ResourceManager.
        
        Args:
            data_dir: Optional custom data directory path
        """
        if data_dir is None:
            self.data_dir = Path(__file__).parent / 'data'
        else:
            self.data_dir = Path(data_dir)
            
        self._word_lookup: Optional[Dict[str, Dict[str, str]]] = None
        self._coca_frequencies: Optional[Dict[str, int]] = None
        
        logger.debug(f"ResourceManager initialized with data_dir: {self.data_dir}")
        
    @property
    def word_lookup(self) -> Dict[str, Dict[str, str]]:
        """Lazy load word lookup dictionary.
        
        Returns:
            Dictionary mapping words to their linguistic information
            
        Raises:
            ResourceLoadError: If the resource file cannot be loaded
        """
        if self._word_lookup is None:
            self._word_lookup = self._load_word_lookup()
        return self._word_lookup
    
    @property
    def coca_frequencies(self) -> Dict[str, int]:
        """Lazy load COCA frequencies.
        
        Returns:
            Dictionary mapping words to their frequency ranks
            
        Raises:
            ResourceLoadError: If the resource file cannot be loaded
        """
        if self._coca_frequencies is None:
            self._coca_frequencies = self._load_coca_frequencies()
        return self._coca_frequencies
        
    def _load_word_lookup(self) -> Dict[str, Dict[str, str]]:
        """Load the word lookup dictionary with CEFR levels.
        
        Returns:
            Dict mapping words to their information (base_form, pos, CEFR)
            
        Raises:
            ResourceLoadError: If the file cannot be loaded
        """
        filepath = self.data_dir / 'word_lookup.json'
        
        try:
            logger.info(f"Loading word lookup from {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                word_lookup = json.load(f)
            
            logger.info(f"Loaded {len(word_lookup)} words from word lookup")
            return word_lookup
            
        except FileNotFoundError:
            raise ResourceLoadError(f"Word lookup file not found: {filepath}")
        except json.JSONDecodeError as e:
            raise ResourceLoadError(f"Invalid JSON in word lookup file: {e}")
        except Exception as e:
            raise ResourceLoadError(f"Error loading word lookup: {e}")
    
    def _load_coca_frequencies(self) -> Dict[str, int]:
        """Load COCA frequency rankings.
        
        Returns:
            Dict mapping words to their frequency ranks
            
        Raises:
            ResourceLoadError: If the file cannot be loaded
        """
        filepath = self.data_dir / 'coca_frequencies.json'
        
        try:
            logger.info(f"Loading COCA frequencies from {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                frequencies = json.load(f)
            
            # Convert all words to lowercase for consistent lookup
            frequencies_lower = {
                word.lower(): rank 
                for word, rank in frequencies.items()
            }
            
            logger.info(f"Loaded {len(frequencies_lower)} frequency rankings")
            return frequencies_lower
            
        except FileNotFoundError:
            raise ResourceLoadError(f"COCA frequencies file not found: {filepath}")
        except json.JSONDecodeError as e:
            raise ResourceLoadError(f"Invalid JSON in COCA frequencies file: {e}")
        except Exception as e:
            raise ResourceLoadError(f"Error loading COCA frequencies: {e}")
    
    @lru_cache(maxsize=10000)
    def get_word_level(self, word: str) -> Optional[str]:
        """Get the CEFR level of a word.
        
        Args:
            word: The word to look up
            
        Returns:
            CEFR level (A1, A2, B1, B2, C1, C2) or None if not found
        """
        word_lower = word.lower()
        
        # Check if word exists in lookup
        if word_lower in self.word_lookup:
            return self.word_lookup[word_lower].get('CEFR')
            
        return None
    
    @lru_cache(maxsize=10000)
    def get_word_difficulty(self, word: str) -> float:
        """Get numeric difficulty score for a word.
        
        Args:
            word: The word to look up
            
        Returns:
            Difficulty score (1=A1, 2=A2, 3=B1, 4=B2, 5=C1, 6=C2) or 0 if not found
        """
        level = self.get_word_level(word)
        
        if level is None:
            return 0.0
            
        return float(config.CEFR_LEVELS.get(level, 0))
    
    @lru_cache(maxsize=10000)
    def get_word_frequency_rank(self, word: str) -> int:
        """Get COCA frequency rank for a word.
        
        Args:
            word: The word to look up
            
        Returns:
            Frequency rank (1-10000) or 10000 if not found
        """
        word_lower = word.lower()
        return self.coca_frequencies.get(word_lower, config.DEFAULT_FREQUENCY_RANK)
    
    def get_content_words(self, doc: Doc) -> List[Token]:
        """Extract content words from a spaCy doc.
        
        Content words are nouns, verbs, adjectives, and adverbs.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            List of content word tokens
        """
        content_words = []
        
        for token in doc:
            # Skip punctuation and stop words
            if token.is_punct or token.is_stop:
                continue
                
            # Check if it's a content word based on POS tag
            if token.pos_ in config.CONTENT_POS_TAGS:
                content_words.append(token)
                
        return content_words
    
    def get_content_words_by_level(self, doc: Doc) -> Dict[str, List[str]]:
        """Group content words by their CEFR level.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            Dict mapping CEFR levels to lists of words at that level
        """
        content_words = self.get_content_words(doc)
        words_by_level: Dict[str, List[str]] = {
            'A1': [], 'A2': [], 'B1': [], 'B2': [], 'C1': [], 'C2': [], 'unknown': []
        }
        
        for token in content_words:
            # Try the token text first, then lemma
            word_text = token.text.lower()
            word_lemma = token.lemma_.lower()
            
            # First try exact match with token text
            level = self.get_word_level(word_text)
            
            # If not found, try with lemma
            if not level:
                level = self.get_word_level(word_lemma)
            
            if level:
                words_by_level[level].append(word_lemma)
            else:
                words_by_level['unknown'].append(word_lemma)
                
        return words_by_level
    
    def clear_cache(self) -> None:
        """Clear the LRU cache for word lookups."""
        self.get_word_level.cache_clear()
        self.get_word_difficulty.cache_clear()
        self.get_word_frequency_rank.cache_clear()
        logger.debug("Cleared resource cache")