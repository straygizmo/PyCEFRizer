"""PyCEFRizer - CEFR-J Level Estimator."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Union

import spacy
from spacy.language import Language
from spacy.tokens import Doc

from .cefr_mapping import CEFRMapper
from .config import config
from .exceptions import SpacyModelError, TextLengthError
from .logger import logger
from .metrics import MetricsCalculator
from .resources import ResourceManager


class PyCEFRizer:
    """Main analyzer class for PyCEFRizer (CEFR-J Level Estimator).
    
    This class provides the main interface for analyzing English text and
    estimating its CEFR-J difficulty level based on 8 linguistic metrics.
    
    Attributes:
        nlp: spaCy language model for text processing
        resources: ResourceManager for accessing linguistic data
        metrics_calc: MetricsCalculator for computing linguistic metrics
        cefr_mapper: CEFRMapper for converting metrics to CEFR-J levels
    """
    
    def __init__(
        self, 
        spacy_model: Optional[Union[str, Language]] = None,
        data_dir: Optional[Path] = None,
        log_level: int = logging.INFO
    ):
        """Initialize the analyzer with required resources.
        
        Args:
            spacy_model: Optional spaCy model name or loaded model.
                        Defaults to 'en_core_web_sm'
            data_dir: Optional custom data directory for resources
            log_level: Logging level (default: INFO)
            
        Raises:
            SpacyModelError: If spaCy model cannot be loaded
        """
        # Set logging level
        logger.setLevel(log_level)
        
        # Load spaCy model
        self._load_spacy_model(spacy_model)
        
        # Initialize components
        logger.info("Initializing PyCEFRizer components")
        self.resources = ResourceManager(data_dir=data_dir)
        self.metrics_calc = MetricsCalculator(self.resources)
        self.cefr_mapper = CEFRMapper()
        
        logger.info("PyCEFRizer initialized successfully")
    
    def _load_spacy_model(self, model: Optional[Union[str, Language]] = None) -> None:
        """Load the spaCy model.
        
        Args:
            model: Model name or loaded model
            
        Raises:
            SpacyModelError: If model cannot be loaded
        """
        if isinstance(model, Language):
            self.nlp = model
            logger.info("Using provided spaCy model")
            return
            
        model_name = model or config.SPACY_MODEL
        
        try:
            logger.info(f"Loading spaCy model: {model_name}")
            self.nlp = spacy.load(model_name)
            logger.info(f"Successfully loaded spaCy model: {model_name}")
        except OSError as e:
            error_msg = (
                f"spaCy model '{model_name}' not found. "
                f"Please install it with: python -m spacy download {model_name}"
            )
            logger.error(error_msg)
            raise SpacyModelError(error_msg) from e
    
    def validate_input(self, text: str) -> int:
        """Validate input text meets requirements.
        
        Args:
            text: Input text to validate
            
        Returns:
            Word count of the text
            
        Raises:
            TextLengthError: If text doesn't meet length requirements
        """
        if not text or not text.strip():
            raise TextLengthError("Input text cannot be empty")
        
        # Count words (simple whitespace split)
        word_count = len(text.split())
        
        if word_count < config.MIN_WORDS:
            error_msg = (
                f"Text is too short. Minimum {config.MIN_WORDS} words required, "
                f"but got {word_count} words."
            )
            logger.error(error_msg)
            raise TextLengthError(error_msg)
        
        if word_count > config.MAX_WORDS:
            error_msg = (
                f"Text is too long. Maximum {config.MAX_WORDS} words allowed, "
                f"but got {word_count} words."
            )
            logger.error(error_msg)
            raise TextLengthError(error_msg)
            
        logger.info(f"Input validated: {word_count} words")
        return word_count
    
    def get_word_cefr_level(self, word: str) -> str:
        """Get CEFR level for a single word.
        
        Args:
            word: Single English word to look up
            
        Returns:
            CEFR level (A1, A2, B1, B2, C1, C2) or empty string if not found
        """
        # Clean the word (strip whitespace and convert to lowercase)
        word = word.strip().lower()
        
        # Check if it's a single word (no spaces)
        if ' ' in word or not word:
            return ""
            
        # Look up the word
        level = self.resources.get_word_level(word)
        
        if level:
            logger.info(f"Word '{word}' has CEFR level: {level}")
            return level
        else:
            logger.info(f"Word '{word}' not found in dictionary")
            return ""
    
    def analyze(self, text: str) -> Dict[str, str]:
        """Analyze English text and return CEFR-J level assessment.
        
        This is the main analysis method that processes the input text
        through all metrics and returns the CEFR-J level estimation.
        For single words, returns only the CEFR level.
        
        Args:
            text: English text to analyze (10-10000 words) or single word
            
        Returns:
            Dictionary with CEFR-J level and individual metric scores,
            or just CEFR_Level for single words
            
        Raises:
            TextLengthError: If input doesn't meet length requirements
            MetricCalculationError: If metric calculation fails
            ResourceLoadError: If resources cannot be loaded
        """
        # Check if input is a single word
        stripped_text = text.strip()
        if ' ' not in stripped_text and stripped_text:
            # Single word case - return only CEFR level
            level = self.get_word_cefr_level(stripped_text)
            return {"CEFR_Level": level}
        
        # Validate input for full text analysis
        word_count = self.validate_input(text)
        
        # Process text with spaCy
        logger.info("Processing text with spaCy")
        doc = self.nlp(text)
        logger.debug(f"Processed {len(doc)} tokens, {len(list(doc.sents))} sentences")
        
        # Calculate all metrics
        metrics = self.metrics_calc.calculate_all_metrics(doc, text)
        
        # Map to CEFR levels
        cefr_j_level, cefr_scores = self.cefr_mapper.process_metrics(metrics)
        
        # Prepare output
        result = {
            "CEFR-J_Level": cefr_j_level,
            **cefr_scores
        }
        
        logger.info(f"Analysis complete: {cefr_j_level}")
        return result
    
    def analyze_json(self, text: str, **json_kwargs) -> str:
        """Analyze text and return JSON string.
        
        Args:
            text: English text to analyze
            **json_kwargs: Additional arguments to pass to json.dumps
            
        Returns:
            JSON string with results
        """
        result = self.analyze(text)
        
        # Set default JSON formatting
        kwargs = {"indent": 2}
        kwargs.update(json_kwargs)
        
        return json.dumps(result, **kwargs)
    
    def get_detailed_analysis(self, text: str) -> Dict[str, Union[str, Dict]]:
        """Get detailed analysis including raw metric values.
        
        This method provides additional information beyond the basic
        analysis, including the raw metric values before CEFR conversion.
        
        Args:
            text: English text to analyze
            
        Returns:
            Dictionary with CEFR-J level, CEFR scores, and raw metrics
            
        Raises:
            TextLengthError: If input doesn't meet length requirements
            MetricCalculationError: If metric calculation fails
            ResourceLoadError: If resources cannot be loaded
        """
        # Check if input is a single word
        stripped_text = text.strip()
        if ' ' not in stripped_text and stripped_text:
            # Single word case - return only CEFR level
            level = self.get_word_cefr_level(stripped_text)
            return {"CEFR_Level": level}
        
        # Validate input for full text analysis
        word_count = self.validate_input(text)
        
        # Process text with spaCy
        logger.info("Processing text for detailed analysis")
        doc = self.nlp(text)
        
        # Calculate all metrics
        raw_metrics = self.metrics_calc.calculate_all_metrics(doc, text)
        
        # Map to CEFR levels
        cefr_j_level, cefr_scores = self.cefr_mapper.process_metrics(raw_metrics)
        
        # Prepare detailed output
        result = {
            "CEFR-J_Level": cefr_j_level,
            "CEFR_Scores": cefr_scores,
            "Raw_Metrics": {k: round(v, 4) for k, v in raw_metrics.items()},
            "Text_Statistics": {
                "word_count": word_count,
                "sentence_count": len(list(doc.sents)),
                "token_count": len(doc)
            }
        }
        
        return result


def main():
    """Example usage of PyCEFRizer."""
    # Example text
    sample_text = """
    The impact of climate change on global ecosystems has become increasingly evident 
    in recent decades. Rising temperatures, shifting precipitation patterns, and extreme 
    weather events are altering habitats and threatening biodiversity worldwide. 
    Scientists have observed significant changes in species distribution, with many 
    animals and plants migrating to higher elevations or latitudes in search of suitable 
    conditions. Coral reefs, which support approximately 25% of marine species, are 
    experiencing widespread bleaching due to ocean warming and acidification. 
    Furthermore, the melting of polar ice caps not only contributes to sea level rise 
    but also disrupts the delicate balance of Arctic and Antarctic ecosystems. These 
    environmental changes pose serious challenges for conservation efforts and require 
    immediate action to mitigate their effects. International cooperation and sustainable 
    practices are essential to preserve our planet's biodiversity for future generations.
    """
    
    # Create analyzer
    analyzer = PyCEFRizer()
    
    # Analyze text
    try:
        print("=" * 60)
        print("PyCEFRizer Analysis")
        print("=" * 60)
        
        result = analyzer.analyze(sample_text)
        print("\nBasic Analysis Result:")
        print(json.dumps(result, indent=2))
        
        # Get detailed analysis
        detailed = analyzer.get_detailed_analysis(sample_text)
        print("\nDetailed Analysis:")
        print(json.dumps(detailed, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        logger.exception("Error in main example")


if __name__ == "__main__":
    main()