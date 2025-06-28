#!/usr/bin/env python3
"""Command-line interface for PyCEFRizer."""

import sys
import json
import argparse
from pathlib import Path
from .pycefrizer import PyCEFRizer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PyCEFRizer - CEFR-J Level Estimator for English text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pycefrizer "Your English text here..."
  pycefrizer -f input.txt
  pycefrizer -f input.txt -o output.json
  cat text.txt | pycefrizer
        """
    )
    
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to analyze (if not provided, reads from stdin)"
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Input file path"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (if not provided, prints to stdout)"
    )
    
    parser.add_argument(
        "-d", "--detailed",
        action="store_true",
        help="Show detailed analysis with raw metric values"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 3.0.0"
    )
    
    parser.add_argument(
        "-w", "--word",
        action="store_true",
        help="Word mode: look up CEFR level for a single word"
    )
    
    args = parser.parse_args()
    
    # Determine input text
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        # Read from stdin
        text = sys.stdin.read()
    
    if not text.strip():
        print("Error: No text provided", file=sys.stderr)
        sys.exit(1)
    
    # Create analyzer
    analyzer = PyCEFRizer()
    
    try:
        # Analyze text
        if args.word:
            # Word mode - just return the CEFR level
            level = analyzer.get_word_cefr_level(text.strip())
            if level:
                output = level
            else:
                output = ""
        else:
            # Full text analysis
            if args.detailed:
                result = analyzer.get_detailed_analysis(text)
            else:
                result = analyzer.analyze(text)
            
            # Format output
            output = json.dumps(result, indent=2)
        
        # Write output
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"Analysis saved to: {args.output}")
            except Exception as e:
                print(f"Error writing output file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()