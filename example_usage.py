#!/usr/bin/env python3
"""Example usage of PyCEFRizer analyzer with texts at different CEFR levels."""

import json
import logging
from pycefrizer import PyCEFRizer, setup_logger, get_word_level


def main():
    """Demonstrate PyCEFRizer usage with various text samples."""
    # Set up logging for more detailed output
    setup_logger(level=logging.WARNING)  # Change to DEBUG for detailed logs
    
    # Create analyzer instance
    analyzer = PyCEFRizer()
    
    # Example texts at different CEFR levels
    texts = {
        "A1-A2 Level": """
        My name is John. I am a student. I go to school every day. 
        I like to read books and play games. My favorite subject is science. 
        I have many friends at school. We eat lunch together. 
        After school, I go home and do my homework. 
        Then I watch TV with my family. I go to bed at nine o'clock.
        """,
        
        "B1-B2 Level": """
        The development of renewable energy sources has become a critical priority 
        for many countries around the world. Solar panels and wind turbines are 
        increasingly being installed to reduce dependence on fossil fuels. 
        These technologies offer significant environmental benefits, including 
        reduced greenhouse gas emissions and improved air quality. However, 
        challenges remain in terms of energy storage and grid integration. 
        Governments are implementing various policies to encourage investment 
        in clean energy infrastructure. As technology continues to advance, 
        the cost of renewable energy is expected to decrease further, making 
        it more accessible to developing nations.
        """,
        
        "C1-C2 Level": """
        The paradigmatic shift in contemporary epistemological discourse has 
        engendered a fundamental reconsideration of the ontological premises 
        that underpin our understanding of consciousness and cognition. 
        Neuroscientific advances have elucidated the intricate mechanisms 
        of synaptic plasticity, revealing the brain's remarkable capacity 
        for adaptation and reorganization. The emergence of quantum theories 
        of consciousness has precipitated contentious debates regarding the 
        nature of subjective experience and its relationship to physical 
        substrates. These interdisciplinary investigations necessitate a 
        nuanced synthesis of empirical findings and philosophical inquiry, 
        challenging reductionist frameworks while acknowledging the 
        irreducible complexity of mental phenomena.
        """
    }
    
    # Analyze each text
    for level_desc, text in texts.items():
        print(f"\n{'='*60}")
        print(f"Analyzing {level_desc} text")
        print(f"{'='*60}")
        
        try:
            # Get basic analysis
            result = analyzer.analyze(text)
            
            print(f"\nCEFR-J Level: {result['CEFR-J_Level']}")
            print("\nMetric CEFR Scores:")
            for metric, score in sorted(result.items()):
                if metric != 'CEFR-J_Level':
                    print(f"  {metric}: {score}")
            
            # Get detailed analysis for more information
            detailed = analyzer.get_detailed_analysis(text)
            
            print("\nRaw Metric Values:")
            for metric, value in sorted(detailed['Raw_Metrics'].items()):
                print(f"  {metric}: {value}")
            
            print("\nText Statistics:")
            for stat, value in sorted(detailed['Text_Statistics'].items()):
                print(f"  {stat}: {value}")
                
        except Exception as e:
            print(f"Error analyzing text: {e}")
    
    # Demonstrate custom text analysis
    print(f"\n{'='*60}")
    print("Custom Text Analysis")
    print(f"{'='*60}")
    
    custom_text = """
    Technology has transformed how we communicate and access information. 
    Smartphones enable instant messaging and video calls across continents. 
    Social media platforms connect billions of users worldwide, facilitating 
    the rapid spread of news and ideas. However, these advancements also 
    raise concerns about privacy, misinformation, and digital addiction. 
    Educational institutions are adapting their curricula to prepare students 
    for careers in an increasingly digital economy. Remote work has become 
    more prevalent, offering flexibility but also blurring work-life boundaries. 
    As artificial intelligence continues to evolve, society must carefully 
    consider the ethical implications of automated decision-making systems.
    """
    
    print("\nAnalyzing custom text...")
    
    try:
        # Get JSON output
        result_json = analyzer.analyze_json(custom_text)
        print("\nJSON Output:")
        print(result_json)
        
        # Parse and display specific information
        result = json.loads(result_json)
        print(f"\nSummary: The text is at CEFR-J level {result['CEFR-J_Level']}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Demonstrate word lookup feature
    print(f"\n{'='*60}")
    print("Word CEFR Level Lookup")
    print(f"{'='*60}")
    
    test_words = [
        "cat", "dog", "house", "beautiful", "paradigm", 
        "epistemological", "run", "quickly", "the", "and",
        "democracy", "photosynthesis", "hello", "goodbye",
        "computer", "algorithm", "xyz123"  # Non-existent word
    ]
    
    print("\nWord CEFR Levels:")
    for word in test_words:
        level = get_word_level(word)
        if level:
            print(f"  {word:<20} -> {level}")
        else:
            print(f"  {word:<20} -> (not found)")
    
    # Demonstrate single word analysis through main analyze method
    print("\nSingle word analysis through analyze():")
    for word in ["beautiful", "paradigm", "xyz123"]:
        result = analyzer.analyze(word)
        level = result.get("CEFR_Level", "")
        print(f"  {word}: {level if level else '(not found)'}")
    
    print("\n" + "="*60)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()