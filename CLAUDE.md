# PyCEFRizer Implementation Plan

## Overview
PyCEFRizer (CEFR-J Level Estimator) is a Python-based text analyzer that estimates the CEFR-J level of English reading passages. It takes 10-10000 words of English text as input and outputs a JSON with CEFR-J level assessment and metric scores.

## Key Requirements
- Input: English text (10-10000 words)
- Output: JSON format with CEFR-J level and 8 metric scores
- Backend: Python with spaCy 3.7.2 (en_core_web_sm) and textstat 0.7.4
- Metrics: CVV1, BperA, POStypes, ARI, AvrDiff, AvrFreqRank, VperSent, LenNP

## Python Package Management
**Use `uv` for all Python package management and virtual environment operations.**

### Installation with uv:
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install spacy==3.7.2 textstat==0.7.4 pytest

# Download spaCy model
uv run python -m spacy download en_core_web_sm
```

## Architecture Design

### 1. Core Modules

#### `pycefrizer.py` - Main analyzer class
- Class: `PyCEFRizer`
- Methods:
  - `__init__()`: Initialize spaCy model and resources
  - `analyze(text)`: Main method that returns JSON result
  - `calculate_cefr_level()`: Compute final CEFR-J level from metrics

#### `metrics.py` - Metric calculation functions
- `calculate_cvv1(doc)`: Verb diversity (verb tokens / sqrt(2 * verb types))
- `calculate_bpera(doc, word_levels)`: B-level to A-level content word ratio
- `calculate_postypes(doc)`: Average distinct POS tags per sentence
- `calculate_ari(text)`: Automated Readability Index
- `calculate_avrdiff(doc, word_levels)`: Average difficulty of content words
- `calculate_avrfreqrank(doc, freq_ranks)`: Average frequency rank
- `calculate_vpersent(doc)`: Average verbs per sentence
- `calculate_lennp(doc)`: Average noun phrase length

#### `resources.py` - Resource loading and management
- `load_word_lookup()`: Load word lookup dictionary with CEFR levels
- `load_coca_frequencies()`: Load COCA frequency rankings
- `get_content_words(doc)`: Extract content words from spaCy doc

#### `cefr_mapping.py` - CEFR level mapping
- Regression equations for each metric
- CEFR-J level conversion table
- `apply_regression(metric_value, metric_name)`: Apply regression equation
- `calculate_final_level(metric_scores)`: Average middle 6 values
- `map_to_cefr_j(score)`: Convert score to CEFR-J level

### 2. Data Resources Required

#### Word Lookup Dictionary
- Contains 21,891 words with:
  - Base forms
  - Parts of speech
  - CEFR levels (A1-C2)
- Distribution:
  - A1: 2,399 words
  - A2: 3,028 words
  - B1: 5,498 words
  - B2: 6,352 words
  - C1: 2,376 words
  - C2: 2,238 words

#### COCA Frequency Rankings
- Top 10,000 most frequent words from Corpus of Contemporary American English
- Words beyond rank 10,000 treated as 10,000

### 3. Implementation Steps

#### Phase 1: Setup and Resources
1. Set up project structure
2. Install dependencies: spacy, textstat, nltk (for additional processing)
3. Download spaCy model: `python -m spacy download en_core_web_sm`
4. Prepare word lookup dictionary data
5. Prepare COCA frequency data

#### Phase 2: Core Metrics Implementation
1. Implement text preprocessing with spaCy
2. Implement each of the 8 metrics:
   - **CVV1**: Count verb tokens and types (excluding be-verbs)
   - **BperA**: Identify content words, classify by CEFR level
   - **POStypes**: Count unique POS tags per sentence
   - **ARI**: Use textstat library
   - **AvrDiff**: Map content words to numeric levels (A1=1, A2=2, etc.)
   - **AvrFreqRank**: Look up words in COCA rankings
   - **VperSent**: Count all verbs per sentence
   - **LenNP**: Parse noun phrases, calculate average length

#### Phase 3: CEFR Level Calculation
1. Implement regression equations (with min(x, 7) cap):
   ```python
   CVV1_CEFR = min(CVV1 * 1.1059 - 1.208, 7)
   BperA_CEFR = min(BperA * 13.146 + 0.428, 7)
   POStypes_CEFR = min(POStypes * 1.768 - 12.006, 7)
   ARI_CEFR = min(ARI * 0.607 - 1.632, 7)
   AvrDiff_CEFR = min(AvrDiff * 6.417 - 7.184, 7)
   AvrFreqRank_CEFR = min(AvrFreqRank * 0.004 - 0.608, 7)
   VperSent_CEFR = min(VperSent * 2.203 - 2.486, 7)
   LenNP_CEFR = min(LenNP * 2.629 - 6.697, 7)
   ```

2. Implement averaging logic:
   - Sort 8 CEFR scores
   - Exclude minimum and maximum
   - Average remaining 6 values

3. Implement CEFR-J mapping:
   ```
   x < 0.5         → preA1
   0.5 ≤ x < 0.84  → A1.1
   0.84 ≤ x < 1.17 → A1.2
   1.17 ≤ x < 1.5  → A1.3
   1.5 ≤ x < 2     → A2.1
   2 ≤ x < 2.5     → A2.2
   2.5 ≤ x < 3     → B1.1
   3 ≤ x < 3.5     → B1.2
   3.5 ≤ x < 4     → B2.1
   4 ≤ x < 4.5     → B2.2
   4.5 ≤ x < 5.5   → C1
   x ≥ 5.5         → C2
   ```

#### Phase 4: Integration and Testing
1. Create main analyzer class that orchestrates all components
2. Implement JSON output formatting
3. Add input validation (10-10000 words)
4. Create test cases with known CEFR levels
5. Validate accuracy against sample texts

### 4. Key Implementation Details

#### Text Preprocessing
- Use spaCy for tokenization, POS tagging, dependency parsing
- Handle sentence segmentation properly
- Identify content words (nouns, verbs, adjectives, adverbs)

#### Special Handling
- CVV1: Exclude be-verbs from calculation
- AvrFreqRank: Exclude 3 most infrequent words to prevent outliers
- Zero values: Don't always exclude as minimum (e.g., BperA=0 → 0.428)

#### Error Handling
- Validate input length (10-10000 words)
- Handle missing words in EVP/COCA lists
- Graceful degradation if some metrics fail

### 5. Example Usage
```python
analyzer = PyCEFRizer()
text = "Your English text here..."
result = analyzer.analyze(text)
print(result)
# Output:
# {
#    "CEFR-J_Level": "B2.2",
#    "CVV1_CEFR": "4.23",
#    "BperA_CEFR": "3.87",
#    "POStypes_CEFR": "4.12",
#    "ARI_CEFR": "4.56",
#    "AvrDiff_CEFR": "4.01",
#    "AvrFreqRank_CEFR": "3.92",
#    "VperSent_CEFR": "4.34",
#    "LenNP_CEFR": "4.15"
# }
```

### 6. Testing Strategy
1. Unit tests for each metric calculation
2. Integration tests with sample texts from paper
3. Validation against reference results for comparison
4. Edge case testing (very short/long texts, unusual vocabulary)

### 7. Future Enhancements
- Batch processing mode for multiple files
- Local deployment option
- Performance optimization for large texts
- Additional output formats (CSV, detailed report)

### 8. Additional Methods

#### `get_unused_words(level, text)` - Find unused vocabulary from a specific CEFR level
This method identifies words from the dictionary at a specific CEFR level that are NOT used in the provided text. 
Useful for:
- Identifying vocabulary that could be introduced to learners
- Finding gaps in text coverage for specific levels
- Educational material development

```python
analyzer = PyCEFRizer()
unused_c1 = analyzer.get_unused_words("C1", "The cat sat on the mat.")
print(unused_c1)  # Output: {"cloak": "noun", "exterior": "noun", ...}
```

Parameters:
- `level`: CEFR level to search (A1, A2, B1, B2, C1, C2)
- `text`: English text to analyze (10-10000 words)

Returns:
- Dictionary mapping unused words to their parts of speech

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.