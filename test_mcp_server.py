#!/usr/bin/env python3
"""
Test script for PyCEFRizer MCP Server
"""
import asyncio
import json
from pycefrizer.mcp_server import (
    analyze_text,
    get_word_cefr_level,
    get_unused_words,
    get_detailed_analysis,
    get_cefr_statistics,
    get_cefr_words
)


async def test_mcp_server():
    """Test the MCP server functions"""
    print("Testing PyCEFRizer MCP Server...\n")
    
    # Test text
    test_text = """
    The cat sat on the mat. This is a simple sentence. 
    However, we can also include more sophisticated vocabulary 
    to demonstrate the analyzer's capability to distinguish 
    between different difficulty levels. The implementation 
    requires careful consideration of linguistic features.
    """
    
    # Test 1: Basic text analysis
    print("1. Testing analyze_text...")
    result = await analyze_text(test_text)
    print(f"Result: {result}\n")
    
    # Test 2: Word CEFR level
    print("2. Testing get_word_cefr_level...")
    words = ["cat", "sophisticated", "implementation", "linguistic"]
    for word in words:
        level = await get_word_cefr_level(word)
        print(f"  {word}: {level}")
    print()
    
    # Test 3: Unused words
    print("3. Testing get_unused_words...")
    unused = await get_unused_words("A1", test_text)
    print(f"Unused A1 words (first 5): {json.loads(unused) if unused.startswith('{') else unused}\n")
    
    # Test 4: Detailed analysis
    print("4. Testing get_detailed_analysis...")
    detailed = await get_detailed_analysis(test_text)
    print(f"Detailed analysis: {detailed}\n")
    
    # Test 5: CEFR statistics
    print("5. Testing get_cefr_statistics...")
    stats = await get_cefr_statistics(test_text)
    print(f"CEFR statistics: {stats}\n")
    
    # Test 6: Get CEFR words
    print("6. Testing get_cefr_words...")
    levels = ["A1", "A2", "B1"]
    for level in levels:
        words_result = await get_cefr_words(level)
        if words_result.startswith('{'):
            words_data = json.loads(words_result)
            print(f"  {level}: {words_data['total_unique_words']} unique words (showing first 5)")
            print(f"    Sample: {words_data['words'][:5]}")
        else:
            print(f"  {level}: {words_result}")
    print()
    
    print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())