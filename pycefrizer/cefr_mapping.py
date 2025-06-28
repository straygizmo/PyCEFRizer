"""CEFR level mapping functions for PyCEFRizer."""

from typing import Dict, List, Tuple

from .config import config
from .logger import logger


class CEFRMapper:
    """Maps metric scores to CEFR-J levels using regression equations."""
    
    def __init__(self):
        """Initialize the CEFR mapper with regression equations and level mappings."""
        logger.debug("CEFRMapper initialized")
    
    def apply_regression(self, metric_value: float, metric_name: str) -> float:
        """Apply regression equation to a metric value.
        
        Args:
            metric_value: Raw metric value
            metric_name: Name of the metric
            
        Returns:
            CEFR score (0-7)
            
        Raises:
            ValueError: If metric name is unknown
        """
        if metric_name not in config.REGRESSION_COEFFICIENTS:
            raise ValueError(f"Unknown metric: {metric_name}")
        
        slope, intercept = config.REGRESSION_COEFFICIENTS[metric_name]
        cefr_score = metric_value * slope + intercept
        
        # Cap at maximum score
        cefr_score = min(cefr_score, config.MAX_CEFR_SCORE)
        
        logger.debug(f"{metric_name}: {metric_value:.4f} -> CEFR {cefr_score:.4f}")
        return cefr_score
    
    def calculate_cefr_scores(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """Calculate CEFR scores for all metrics.
        
        Args:
            metrics: Dictionary of metric names to raw values
            
        Returns:
            Dictionary of metric names to CEFR scores
        """
        cefr_scores = {}
        
        for metric_name, metric_value in metrics.items():
            try:
                cefr_score = self.apply_regression(metric_value, metric_name)
                cefr_scores[f"{metric_name}_CEFR"] = round(cefr_score, 2)
            except ValueError as e:
                logger.error(f"Error processing metric {metric_name}: {e}")
                raise
                
        return cefr_scores
    
    def calculate_final_level(self, cefr_scores: Dict[str, float]) -> float:
        """Calculate final CEFR level by averaging middle 6 values.
        
        Excludes minimum and maximum values for stability.
        
        Args:
            cefr_scores: Dictionary of metric names to CEFR scores
            
        Returns:
            Final averaged CEFR score
        """
        # Extract just the scores
        scores = list(cefr_scores.values())
        
        if len(scores) <= 2:
            # If we have 2 or fewer scores, just average them all
            final_score = sum(scores) / len(scores) if scores else 0.0
            logger.warning(f"Only {len(scores)} scores available, averaging all")
            return final_score
        
        # Sort scores
        scores.sort()
        
        # Log min and max that will be excluded
        logger.debug(f"Excluding min ({scores[0]:.2f}) and max ({scores[-1]:.2f})")
        
        # Remove minimum and maximum
        middle_scores = scores[1:-1]
        
        if not middle_scores:
            return 0.0
            
        # Calculate average of middle values
        final_score = sum(middle_scores) / len(middle_scores)
        logger.info(f"Final CEFR score: {final_score:.4f}")
        
        return final_score
    
    def map_to_cefr_j(self, score: float) -> str:
        """Map numeric score to CEFR-J level.
        
        Args:
            score: Numeric CEFR score
            
        Returns:
            CEFR-J level string
        """
        for boundary, level in config.CEFR_J_BOUNDARIES:
            if score < boundary:
                logger.info(f"Score {score:.4f} maps to CEFR-J level: {level}")
                return level
                
        # This should not happen due to the inf boundary, but just in case
        logger.warning(f"Score {score:.4f} exceeds all boundaries, defaulting to C2")
        return 'C2'
    
    def process_metrics(self, metrics: Dict[str, float]) -> Tuple[str, Dict[str, str]]:
        """Process metrics to get final CEFR-J level and individual scores.
        
        Args:
            metrics: Dictionary of raw metric values
            
        Returns:
            Tuple of (CEFR-J level, dict of formatted CEFR scores)
        """
        logger.info("Processing metrics for CEFR-J level estimation")
        
        # Calculate CEFR scores for each metric
        cefr_scores = self.calculate_cefr_scores(metrics)
        
        # Log individual CEFR scores
        for metric, score in cefr_scores.items():
            logger.debug(f"{metric}: {score}")
        
        # Calculate final level
        final_score = self.calculate_final_level(cefr_scores)
        cefr_j_level = self.map_to_cefr_j(final_score)
        
        # Format scores as strings for output
        formatted_scores = {
            metric: str(score) for metric, score in cefr_scores.items()
        }
        
        return cefr_j_level, formatted_scores