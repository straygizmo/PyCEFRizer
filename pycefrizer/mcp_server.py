#!/usr/bin/env python3
"""
MCP Server for PyCEFRizer - CEFR-J Level Estimator
Provides MCP tools for analyzing English text difficulty levels
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from mcp import Server, Tool
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, ToolResult

from pycefrizer import PyCEFRizer
from pycefrizer.exceptions import PyCEFRizerError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("pycefrizer")

# Initialize PyCEFRizer instance
analyzer = PyCEFRizer()


@server.tool()
async def analyze_text(text: str) -> str:
    """
    Analyze English text and return CEFR-J level assessment with metric scores.
    
    Args:
        text: English text to analyze (10-10,000 words)
        
    Returns:
        JSON string with CEFR-J level and 8 metric scores
    """
    try:
        result = analyzer.analyze(text)
        return result
    except PyCEFRizerError as e:
        return f"Error analyzing text: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in analyze_text: {str(e)}")
        return f"Unexpected error: {str(e)}"


@server.tool()
async def get_word_cefr_level(word: str) -> str:
    """
    Get the CEFR level of a single English word.
    
    Args:
        word: English word to look up
        
    Returns:
        CEFR level of the word (A1, A2, B1, B2, C1, C2) or "Not found"
    """
    try:
        result = analyzer.get_word_cefr_level(word)
        return result if result else "Not found"
    except Exception as e:
        logger.error(f"Error in get_word_cefr_level: {str(e)}")
        return f"Error: {str(e)}"


@server.tool()
async def get_unused_words(level: str, text: str) -> str:
    """
    Find unused vocabulary from a specific CEFR level in the given text.
    
    Args:
        level: CEFR level to search (A1, A2, B1, B2, C1, C2)
        text: English text to analyze
        
    Returns:
        JSON string mapping unused words to their parts of speech
    """
    try:
        import json
        result = analyzer.get_unused_words(level, text)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except PyCEFRizerError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error in get_unused_words: {str(e)}")
        return f"Error: {str(e)}"


@server.tool()
async def get_detailed_analysis(text: str) -> str:
    """
    Get detailed analysis including raw metric values and processed scores.
    
    Args:
        text: English text to analyze (10-10,000 words)
        
    Returns:
        JSON string with detailed analysis including raw metrics and CEFR scores
    """
    try:
        result = analyzer.get_detailed_analysis(text)
        return result
    except PyCEFRizerError as e:
        return f"Error analyzing text: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in get_detailed_analysis: {str(e)}")
        return f"Unexpected error: {str(e)}"


@server.tool()
async def analyze_file(file_path: str) -> str:
    """
    Analyze text from a file and return CEFR-J level assessment.
    
    Args:
        file_path: Path to text file to analyze
        
    Returns:
        JSON string with CEFR-J level and 8 metric scores
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File not found: {file_path}"
        
        if not path.is_file():
            return f"Error: Path is not a file: {file_path}"
        
        # Read file content
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
        
        # Analyze text
        result = analyzer.analyze(text)
        return result
    except Exception as e:
        logger.error(f"Unexpected error in analyze_file: {str(e)}")
        return f"Unexpected error: {str(e)}"


@server.tool()
async def batch_analyze(texts: list[str]) -> str:
    """
    Analyze multiple texts and return CEFR-J levels for each.
    
    Args:
        texts: List of English texts to analyze
        
    Returns:
        JSON string with results for each text
    """
    try:
        import json
        results = []
        
        for i, text in enumerate(texts):
            try:
                result_json = analyzer.analyze(text)
                result_dict = json.loads(result_json)
                results.append({
                    "index": i,
                    "success": True,
                    "result": result_dict
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })
        
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Unexpected error in batch_analyze: {str(e)}")
        return f"Unexpected error: {str(e)}"


@server.tool()
async def get_cefr_statistics(text: str) -> str:
    """
    Get statistics about CEFR level distribution in the text.
    
    Args:
        text: English text to analyze
        
    Returns:
        JSON string with word count by CEFR level and percentage distribution
    """
    try:
        import json
        from collections import Counter
        
        # Process text with spaCy
        doc = analyzer.nlp(text)
        
        # Count words by CEFR level
        level_counter = Counter()
        total_content_words = 0
        unknown_words = []
        
        for token in doc:
            if token.is_alpha and not token.is_stop:
                word = token.text.lower()
                level = analyzer.get_word_cefr_level(word)
                
                if level and level != "Not found":
                    level_counter[level] += 1
                    total_content_words += 1
                else:
                    unknown_words.append(word)
                    total_content_words += 1
        
        # Calculate percentages
        percentages = {}
        for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            count = level_counter.get(level, 0)
            percentages[level] = {
                "count": count,
                "percentage": round(count / total_content_words * 100, 2) if total_content_words > 0 else 0
            }
        
        result = {
            "total_content_words": total_content_words,
            "level_distribution": percentages,
            "unknown_words_count": len(unknown_words),
            "unknown_words_sample": unknown_words[:10]  # First 10 unknown words
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error in get_cefr_statistics: {str(e)}")
        return f"Error: {str(e)}"


@server.tool()
async def get_cefr_words(level: str) -> str:
    """
    Get all unique words (base forms) from a specific CEFR level with their parts of speech.
    
    Args:
        level: CEFR level (A1, A2, B1, B2, C1, C2)
        
    Returns:
        JSON string with list of unique base_form and pos pairs for the specified level
    """
    try:
        import json
        
        # Validate level
        valid_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        if level not in valid_levels:
            return f"Error: Invalid CEFR level '{level}'. Must be one of: {', '.join(valid_levels)}"
        
        # Load word lookup data
        word_lookup = analyzer.resources.word_lookup
        
        # Create a set to store unique (base_form, pos) pairs
        unique_words = set()
        
        # Iterate through all words and collect unique base forms for the specified level
        for word_data in word_lookup.values():
            if word_data.get('CEFR') == level:
                base_form = word_data.get('base_form', '')
                pos = word_data.get('pos', '')
                if base_form and pos:
                    unique_words.add((base_form, pos))
        
        # Convert to list of dictionaries for JSON serialization
        result = [
            {"base_form": base_form, "pos": pos} 
            for base_form, pos in sorted(unique_words)
        ]
        
        return json.dumps({
            "level": level,
            "total_unique_words": len(result),
            "words": result
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error in get_cefr_words: {str(e)}")
        return f"Error: {str(e)}"


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting PyCEFRizer MCP Server...")
    
    try:
        # Run the server using stdio transport
        async with stdio_server() as streams:
            await server.run(
                streams.read_stream,
                streams.write_stream,
                server.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())