#!/usr/bin/env python3
"""Test PyCEFRizer analyzer with the testdata.txt file."""

import json
from pycefrizer import PyCEFRizer


def main():
    # Create analyzer
    analyzer = PyCEFRizer()
    
    # Read test data
    with open('testdata.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Count words
    word_count = len(text.split())
    print(f"Analyzing testdata.txt ({word_count} words)...")
    print("="*60)
    
    try:
        # Get basic analysis
        result = analyzer.analyze(text)
        
        print("\nPyCEFRizer Analysis Result:")
        print(f"CEFR-J Level: {result['CEFR-J_Level']}")
        
        print("\nIndividual Metric CEFR Scores:")
        for metric, score in result.items():
            if metric != 'CEFR-J_Level':
                print(f"  {metric}: {score}")
        
        # Get detailed analysis
        detailed = analyzer.get_detailed_analysis(text)
        
        print("\nRaw Metric Values:")
        for metric, value in detailed['Raw_Metrics'].items():
            print(f"  {metric}: {value}")
        
        # Calculate final score (for demonstration)
        scores = [float(v) for k, v in result.items() if k != 'CEFR-J_Level']
        scores.sort()
        middle_scores = scores[1:-1]  # Exclude min and max
        avg_score = sum(middle_scores) / len(middle_scores)
        print(f"\nFinal averaged score (excluding min/max): {avg_score:.2f}")
        print(f"Minimum score: {scores[0]} (excluded)")
        print(f"Maximum score: {scores[-1]} (excluded)")
        
        # Save full results to JSON
        output_file = 'testdata_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(detailed, f, indent=2)
        print(f"\nFull analysis saved to: {output_file}")
        
        # Test get_unused_words method
        print("\n" + "="*60)
        print("Testing get_unused_words method:")
        print("="*60)
        
        # Test for each CEFR level
        levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        for level in levels:
            unused_words = analyzer.get_unused_words(level, text)
            print(f"\nUnused {level} words: {len(unused_words)} total")
            
            # Show first 5 words as examples
            if unused_words:
                examples = list(unused_words.items())[:5]
                print(f"  Examples:")
                for word, pos in examples:
                    print(f"    - {word} ({pos})")
                if len(unused_words) > 5:
                    print(f"    ... and {len(unused_words) - 5} more")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()