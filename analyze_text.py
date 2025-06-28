#!/usr/bin/env python3
"""Simple CLI for analyzing text with PyCEFRizer."""

import sys
import json
from pycefrizer import PyCEFRizer


def main():
    if len(sys.argv) > 1:
        # Text provided as command line argument
        text = ' '.join(sys.argv[1:])
    else:
        # Read from stdin
        print("Enter text to analyze (press Ctrl+D when done):")
        text = sys.stdin.read()
    
    # Create analyzer
    analyzer = PyCEFRizer()
    
    try:
        # Analyze text
        result = analyzer.analyze(text)
        
        # Print results
        print("\nPyCEFRizer Analysis Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()