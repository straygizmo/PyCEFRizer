#!/usr/bin/env python3
"""
MCP Server for PyCEFRizer - CEFR-J Level Estimator
Provides MCP tools for analyzing English text difficulty levels
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from pycefrizer import PyCEFRizer
from pycefrizer.exceptions import PyCEFRizerError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("pycefrizer")

# Initialize PyCEFRizer instance
analyzer = PyCEFRizer()


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="analyze_text",
            description="Analyze English text and return CEFR-J level assessment with metric scores",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "English text to analyze (10-10,000 words)"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="get_word_cefr_level",
            description="Get the CEFR level of a single English word",
            inputSchema={
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "English word to look up"
                    }
                },
                "required": ["word"]
            }
        ),
        Tool(
            name="get_unused_words",
            description="Find unused vocabulary from a specific CEFR level in the given text",
            inputSchema={
                "type": "object",
                "properties": {
                    "level": {
                        "type": "string",
                        "description": "CEFR level to search (A1, A2, B1, B2, C1, C2)",
                        "enum": ["A1", "A2", "B1", "B2", "C1", "C2"]
                    },
                    "text": {
                        "type": "string",
                        "description": "English text to analyze"
                    }
                },
                "required": ["level", "text"]
            }
        ),
        Tool(
            name="get_detailed_analysis",
            description="Get detailed analysis including raw metric values and processed scores",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "English text to analyze (10-10,000 words)"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="analyze_file",
            description="Analyze text from a file and return CEFR-J level assessment",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to text file to analyze"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_available_words",
            description="Get all available words in the dictionary for a specific CEFR level",
            inputSchema={
                "type": "object",
                "properties": {
                    "level": {
                        "type": "string",
                        "description": "CEFR level to retrieve words for",
                        "enum": ["A1", "A2", "B1", "B2", "C1", "C2"]
                    }
                },
                "required": ["level"]
            }
        ),
        Tool(
            name="get_cefr_words",
            description="Get all available words from the dictionary grouped by CEFR levels",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "analyze_text":
            result = await analyze_text(arguments.get("text", ""))
        elif name == "get_word_cefr_level":
            result = await get_word_cefr_level(arguments.get("word", ""))
        elif name == "get_unused_words":
            result = await get_unused_words(
                arguments.get("level", ""),
                arguments.get("text", "")
            )
        elif name == "get_detailed_analysis":
            result = await get_detailed_analysis(arguments.get("text", ""))
        elif name == "analyze_file":
            result = await analyze_file(arguments.get("file_path", ""))
        elif name == "get_available_words":
            result = await get_available_words(arguments.get("level", ""))
        elif name == "get_cefr_words":
            result = await get_cefr_words()
        else:
            result = f"Unknown tool: {name}"
        
        return [TextContent(type="text", text=result)]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


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
        result = analyzer.get_unused_words(level, text)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except PyCEFRizerError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error in get_unused_words: {str(e)}")
        return f"Error: {str(e)}"


async def get_detailed_analysis(text: str) -> str:
    """
    Get detailed analysis including raw metric values and processed scores.
    
    Args:
        text: English text to analyze (10-10,000 words)
        
    Returns:
        JSON string with detailed metrics and scores
    """
    try:
        result = analyzer.get_detailed_analysis(text)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except PyCEFRizerError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in get_detailed_analysis: {str(e)}")
        return f"Unexpected error: {str(e)}"


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
        
        # Analyze the text
        result = analyzer.analyze(text)
        return result
        
    except PyCEFRizerError as e:
        return f"Error analyzing file: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in analyze_file: {str(e)}")
        return f"Unexpected error: {str(e)}"


async def get_available_words(level: str) -> str:
    """
    Get all available words in the dictionary for a specific CEFR level.
    
    Args:
        level: CEFR level to retrieve words for (A1, A2, B1, B2, C1, C2)
        
    Returns:
        JSON string listing all words at the specified level
    """
    try:
        # Get all words at the specified level
        all_words = analyzer.word_lookup_manager.word_lookup
        level_words = []
        
        for word, entries in all_words.items():
            for entry in entries:
                if entry.get('cefr', '').upper() == level.upper():
                    level_words.append({
                        'word': word,
                        'pos': entry.get('pos', 'unknown')
                    })
        
        # Sort words alphabetically
        level_words.sort(key=lambda x: x['word'])
        
        result = {
            'level': level.upper(),
            'total_words': len(level_words),
            'words': level_words
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error in get_available_words: {str(e)}")
        return f"Error: {str(e)}"


async def get_cefr_words() -> str:
    """
    Get all available words from the dictionary grouped by CEFR levels.
    
    Returns:
        JSON string with words grouped by CEFR levels
    """
    try:
        # Initialize result structure
        cefr_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        result = {level: [] for level in cefr_levels}
        
        # Get all words from the lookup
        all_words = analyzer.word_lookup_manager.word_lookup
        
        # Group words by CEFR level
        for word, entries in all_words.items():
            for entry in entries:
                level = entry.get('cefr', '').upper()
                if level in cefr_levels:
                    result[level].append({
                        'word': word,
                        'pos': entry.get('pos', 'unknown')
                    })
        
        # Sort words in each level alphabetically
        for level in cefr_levels:
            result[level].sort(key=lambda x: x['word'])
        
        # Add summary statistics
        summary = {
            'total_words': sum(len(words) for words in result.values()),
            'words_by_level': {level: len(words) for level, words in result.items()},
            'words': result
        }
        
        return json.dumps(summary, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error in get_cefr_words: {str(e)}")
        return f"Error: {str(e)}"


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting PyCEFRizer MCP Server...")
    
    try:
        # Run the server using stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="pycefrizer",
                    server_version="0.1.0",
                    capabilities={
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    }
                )
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
