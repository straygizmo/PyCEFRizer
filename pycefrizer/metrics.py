"""Metric calculation functions for PyCEFRizer."""

import math
from typing import Dict, List, Set, Tuple

import textstat
from spacy.tokens import Doc, Token

from .config import config
from .exceptions import MetricCalculationError
from .logger import logger
from .resources import ResourceManager


class MetricsCalculator:
    """Calculates all metrics for PyCEFRizer analysis."""
    
    def __init__(self, resource_manager: ResourceManager):
        """Initialize the metrics calculator.
        
        Args:
            resource_manager: ResourceManager instance for accessing linguistic data
        """
        self.resources = resource_manager
        logger.debug("MetricsCalculator initialized")
        
    def calculate_cvv1(self, doc: Doc) -> float:
        """Calculate CVV1 (Corrected Verb Variation 1).
        
        CVV1 = number of verb tokens / sqrt(2 * number of verb types)
        Excludes be-verbs.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            CVV1 score
            
        Raises:
            MetricCalculationError: If calculation fails
        """
        try:
            verb_tokens: List[str] = []
            verb_types: Set[str] = set()
            
            for token in doc:
                # Check if it's a verb and not a be-verb
                if token.pos_ == 'VERB' and token.lemma_.lower() not in config.BE_VERBS:
                    verb_tokens.append(token.text.lower())
                    verb_types.add(token.lemma_.lower())
            
            # Calculate CVV1
            num_tokens = len(verb_tokens)
            num_types = len(verb_types)
            
            if num_types == 0:
                logger.debug("No verbs found for CVV1 calculation")
                return 0.0
                
            cvv1 = num_tokens / math.sqrt(2 * num_types)
            logger.debug(f"CVV1: {cvv1:.4f} (tokens: {num_tokens}, types: {num_types})")
            return cvv1
            
        except Exception as e:
            raise MetricCalculationError(f"Failed to calculate CVV1: {e}")
    
    def calculate_bpera(self, doc: Doc) -> float:
        """Calculate BperA (B-level to A-level content word ratio).
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            BperA ratio
            
        Raises:
            MetricCalculationError: If calculation fails
        """
        try:
            words_by_level = self.resources.get_content_words_by_level(doc)
            
            a_level_count = len(words_by_level['A1']) + len(words_by_level['A2'])
            b_level_count = len(words_by_level['B1']) + len(words_by_level['B2'])
            
            if a_level_count == 0:
                logger.debug("No A-level words found for BperA calculation")
                return 0.0
                
            bpera = b_level_count / a_level_count
            logger.debug(f"BperA: {bpera:.4f} (B-level: {b_level_count}, A-level: {a_level_count})")
            return bpera
            
        except Exception as e:
            raise MetricCalculationError(f"Failed to calculate BperA: {e}")
    
    def calculate_postypes(self, doc: Doc) -> float:
        """Calculate POStypes (average number of distinct POS tags per sentence).
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            Average POStypes per sentence
            
        Raises:
            MetricCalculationError: If calculation fails
        """
        try:
            total_pos_types = 0
            num_sentences = 0
            
            for sent in doc.sents:
                pos_tags: Set[str] = set()
                for token in sent:
                    if not token.is_punct:  # Exclude punctuation
                        pos_tags.add(token.pos_)
                
                total_pos_types += len(pos_tags)
                num_sentences += 1
            
            if num_sentences == 0:
                logger.debug("No sentences found for POStypes calculation")
                return 0.0
                
            avg_postypes = total_pos_types / num_sentences
            logger.debug(f"POStypes: {avg_postypes:.4f} (sentences: {num_sentences})")
            return avg_postypes
            
        except Exception as e:
            raise MetricCalculationError(f"Failed to calculate POStypes: {e}")
    
    def calculate_ari(self, text: str) -> float:
        """Calculate Automated Readability Index.
        
        Args:
            text: Raw text string
            
        Returns:
            ARI score
            
        Raises:
            MetricCalculationError: If calculation fails
        """
        try:
            ari = textstat.automated_readability_index(text)
            logger.debug(f"ARI: {ari:.4f}")
            return float(ari)
        except Exception as e:
            logger.warning(f"Failed to calculate ARI: {e}")
            return 0.0
    
    def calculate_avrdiff(self, doc: Doc) -> float:
        """Calculate AvrDiff (average difficulty of content words).
        
        Difficulty levels: A1=1, A2=2, B1=3, B2=4, C1=5, C2=6
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            Average difficulty score
            
        Raises:
            MetricCalculationError: If calculation fails
        """
        try:
            content_words = self.resources.get_content_words(doc)
            
            if not content_words:
                logger.debug("No content words found for AvrDiff calculation")
                return 0.0
                
            total_difficulty = 0.0
            counted_words = 0
            
            for token in content_words:
                # Try both token text and lemma
                word_text = token.text.lower()
                word_lemma = token.lemma_.lower()
                
                # First try exact match with token text
                difficulty = self.resources.get_word_difficulty(word_text)
                
                # If not found, try with lemma
                if difficulty == 0:
                    difficulty = self.resources.get_word_difficulty(word_lemma)
                    
                if difficulty > 0:  # Only count words found in word_lookup
                    total_difficulty += difficulty
                    counted_words += 1
            
            if counted_words == 0:
                logger.debug("No words with difficulty scores found")
                return 0.0
                
            avg_diff = total_difficulty / counted_words
            logger.debug(f"AvrDiff: {avg_diff:.4f} (words: {counted_words})")
            return avg_diff
            
        except Exception as e:
            raise MetricCalculationError(f"Failed to calculate AvrDiff: {e}")
    
    def calculate_avrfreqrank(self, doc: Doc) -> float:
        """Calculate AvrFreqRank (average frequency rank).
        
        Excludes 3 most infrequent words to prevent outliers.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            Average frequency rank
            
        Raises:
            MetricCalculationError: If calculation fails
        """
        try:
            ranks: List[int] = []
            
            for token in doc:
                # Skip punctuation and spaces
                if token.is_punct or token.is_space:
                    continue
                    
                rank = self.resources.get_word_frequency_rank(token.text.lower())
                ranks.append(rank)
            
            if len(ranks) <= config.EXCLUDE_INFREQUENT_COUNT:
                # If we have 3 or fewer words, just average them all
                avg_rank = sum(ranks) / len(ranks) if ranks else 0.0
            else:
                # Sort ranks to find the most infrequent (highest ranks)
                ranks.sort()
                
                # Remove the most infrequent words
                ranks = ranks[:-config.EXCLUDE_INFREQUENT_COUNT]
                
                avg_rank = sum(ranks) / len(ranks) if ranks else 0.0
            
            logger.debug(f"AvrFreqRank: {avg_rank:.4f} (words: {len(ranks)})")
            return avg_rank
            
        except Exception as e:
            raise MetricCalculationError(f"Failed to calculate AvrFreqRank: {e}")
    
    def calculate_vpersent(self, doc: Doc) -> float:
        """Calculate VperSent (average number of verbs per sentence).
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            Average verbs per sentence
            
        Raises:
            MetricCalculationError: If calculation fails
        """
        try:
            total_verbs = 0
            num_sentences = 0
            
            for sent in doc.sents:
                verb_count = sum(1 for token in sent if token.pos_ == 'VERB')
                total_verbs += verb_count
                num_sentences += 1
            
            if num_sentences == 0:
                logger.debug("No sentences found for VperSent calculation")
                return 0.0
                
            avg_verbs = total_verbs / num_sentences
            logger.debug(f"VperSent: {avg_verbs:.4f} (verbs: {total_verbs}, sentences: {num_sentences})")
            return avg_verbs
            
        except Exception as e:
            raise MetricCalculationError(f"Failed to calculate VperSent: {e}")
    
    def calculate_lennp(self, doc: Doc) -> float:
        """Calculate LenNP (average length of noun phrases).
        
        Measures noun phrases that serve as subjects or objects.
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            Average noun phrase length
            
        Raises:
            MetricCalculationError: If calculation fails
        """
        try:
            np_lengths: List[int] = []
            
            for chunk in doc.noun_chunks:
                # Count tokens in the noun phrase (excluding punctuation)
                np_length = sum(1 for token in chunk if not token.is_punct)
                
                if np_length > 0:
                    np_lengths.append(np_length)
            
            if not np_lengths:
                logger.debug("No noun phrases found for LenNP calculation")
                return 0.0
                
            avg_length = sum(np_lengths) / len(np_lengths)
            logger.debug(f"LenNP: {avg_length:.4f} (phrases: {len(np_lengths)})")
            return avg_length
            
        except Exception as e:
            raise MetricCalculationError(f"Failed to calculate LenNP: {e}")
    
    def calculate_all_metrics(self, doc: Doc, text: str) -> Dict[str, float]:
        """Calculate all metrics for the given text.
        
        Args:
            doc: spaCy Doc object
            text: Raw text string
            
        Returns:
            Dictionary of metric names to values
            
        Raises:
            MetricCalculationError: If any metric calculation fails
        """
        logger.info("Calculating all metrics")
        
        metrics = {}
        metric_functions = [
            ('AvrDiff', lambda: self.calculate_avrdiff(doc)),
            ('BperA', lambda: self.calculate_bpera(doc)),
            ('CVV1', lambda: self.calculate_cvv1(doc)),
            ('AvrFreqRank', lambda: self.calculate_avrfreqrank(doc)),
            ('ARI', lambda: self.calculate_ari(text)),
            ('VperSent', lambda: self.calculate_vpersent(doc)),
            ('POStypes', lambda: self.calculate_postypes(doc)),
            ('LenNP', lambda: self.calculate_lennp(doc))
        ]
        
        for metric_name, calc_func in metric_functions:
            try:
                metrics[metric_name] = calc_func()
            except MetricCalculationError:
                raise
            except Exception as e:
                logger.error(f"Unexpected error calculating {metric_name}: {e}")
                raise MetricCalculationError(f"Failed to calculate {metric_name}: {e}")
        
        logger.info("All metrics calculated successfully")
        return metrics