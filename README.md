# PyCEFRizer - CEFR-J Level Estimator

A Python implementation of PyCEFRizer (CEFR-J Level Estimator) for estimating the CEFR-J level of English reading passages.

## Overview

PyCEFRizer analyzes English text (10-10,000 words) and estimates its difficulty level according to the CEFR-J framework. It uses 8 linguistic metrics:

- **CVV1**: Corrected Verb Variation (verb diversity)
- **BperA**: B-level to A-level content word ratio
- **POStypes**: Average distinct POS tags per sentence
- **ARI**: Automated Readability Index
- **AvrDiff**: Average difficulty of content words
- **AvrFreqRank**: Average frequency rank of words
- **VperSent**: Average verbs per sentence
- **LenNP**: Average noun phrase length

## Installation

### Install from GitHub (Recommended)

```bash
pip install git+https://github.com/straygizmo/PyCEFRizer.git
```

Or install with development dependencies:
```bash
pip install "git+https://github.com/straygizmo/PyCEFRizer.git#egg=pycefrizer[dev]"
```

After installation, download the required spaCy model:
```bash
python -m spacy download en_core_web_sm
```

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/straygizmo/PyCEFRizer.git
cd PyCEFRizer
```

2. Install in development mode:
```bash
pip install -e .
```

3. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

### Installation with uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that provides better performance and reliability.

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Clone and setup**:
```bash
git clone https://github.com/straygizmo/PyCEFRizer.git
cd PyCEFRizer
uv sync
```

3. **Install spaCy model**:
```bash
uv pip install --python .venv/bin/python en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

## Usage

### Basic Usage

```python
from pycefrizer import PyCEFRizer

# Create analyzer
analyzer = PyCEFRizer()

# Analyze text
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

### JSON Output

```python
# Get JSON formatted output
json_result = analyzer.analyze_json(text)
print(json_result)
```

### Detailed Analysis

```python
# Get detailed analysis with raw metric values
detailed = analyzer.get_detailed_analysis(text)
print(detailed)
# Includes raw metric values in addition to CEFR scores
```

### Command Line Usage

After installation, you can use the `pycefrizer` command:

```bash
# Analyze text directly
pycefrizer "Your English text here..."

# Analyze text from file
pycefrizer -f input.txt

# Save output to file
pycefrizer -f input.txt -o output.json

# Get detailed analysis with raw metrics
pycefrizer -d "Your text here..."

# Pipe text from another command
cat article.txt | pycefrizer
```

### Python API Usage

```python
import pycefrizer

# Quick analysis
result = pycefrizer.analyze("Your English text here...")
print(result)

# Using the class directly
from pycefrizer import PyCEFRizer

analyzer = PyCEFRizer()
result = analyzer.analyze("Your text here...")
```

### Word CEFR Level Lookup

PyCEFRizer can also look up CEFR levels for individual words:

```python
from pycefrizer import get_word_level, check_word_level

# Get CEFR level for a single word
level = get_word_level("beautiful")
print(level)  # Output: B1

# Check if a word is at or below a target level
is_basic = check_word_level("cat", "A2")  # True (cat is A1)
is_basic = check_word_level("paradigm", "B1")  # False (paradigm is C1)

# Using the analyzer directly
analyzer = PyCEFRizer()
level = analyzer.get_word_cefr_level("computer")
print(level)  # Output: A2

# Single word through analyze() method
result = analyzer.analyze("beautiful")
print(result)  # Output: {"CEFR_Level": "B1"}
```

### Finding Unused Vocabulary

PyCEFRizer can identify words from the dictionary at a specific CEFR level that are NOT used in the provided text. This is useful for educational material development and vocabulary gap analysis:

```python
from pycefrizer import PyCEFRizer

analyzer = PyCEFRizer()

# Find unused C1 vocabulary in a simple text
unused_c1 = analyzer.get_unused_words("C1", "The cat sat on the mat.")
print(unused_c1)  # Output: {"cloak": "noun", "exterior": "noun", ...}

# Find unused B2 vocabulary
text = "This is a comprehensive analysis of modern technology."
unused_b2 = analyzer.get_unused_words("B2", text)
print(f"Number of unused B2 words: {len(unused_b2)}")
# Shows B2 words not used in the text
```

Command line usage:
```bash
# Look up a single word
pycefrizer -w "beautiful"
# Output: B1

# Word not in dictionary returns empty
pycefrizer -w "xyz123"
# Output: (empty line)
```

### Usage with uv

If you installed with uv, prefix commands with `uv run`:

```bash
# Run example analysis
uv run python example_usage.py

# Analyze custom text
uv run python analyze_text.py "Your English text here..."

# Test with the provided test data
uv run python test_with_file.py

# Interactive Python session
uv run python
>>> from pycefrizer import PyCEFRizer
>>> analyzer = PyCEFRizer()
>>> result = analyzer.analyze("Your text here...")
>>> print(result)
```

## CEFR-J Levels

The analyzer returns one of the following CEFR-J levels:

- **preA1**: Below A1 level
- **A1.1, A1.2, A1.3**: Elementary levels
- **A2.1, A2.2**: Pre-intermediate levels
- **B1.1, B1.2**: Intermediate levels
- **B2.1, B2.2**: Upper-intermediate levels
- **C1**: Advanced level
- **C2**: Proficient level

## Data Files

The analyzer uses two data files in the `data/` directory:

- `word_lookup.json`: Comprehensive word lookup dictionary with CEFR levels, base forms, and POS tags (21,891 words)
- `coca_frequencies.json`: Word frequency rankings from COCA

Note: The included data files contain sample data. For production use, you should obtain complete EVP and COCA datasets.

## Requirements

- Python 3.9+
- spaCy 3.7.2
- textstat 0.7.4
- nltk 3.8+

## Development

### Building the Package

To build the package for distribution:

```bash
# Install build tools
pip install build

# Build the package
python -m build

# This creates dist/ directory with:
# - pycefrizer-3.0.0.tar.gz (source distribution)
# - pycefrizer-3.0.0-py3-none-any.whl (wheel distribution)
```

### Publishing to PyPI

```bash
# Install twine for secure upload
pip install twine

# Upload to TestPyPI first (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

### Adding Dependencies

With standard pip:
```bash
pip install package-name
```

With uv:
```bash
uv add package-name
```

### Updating Dependencies

With uv:
```bash
uv sync --upgrade
```

## Credits

### Research Foundation

This implementation is based on the methodology described in:

**Uchida, S., & Negishi, M. (2025). "Estimating the CEFR-J Level of English Reading Passages: Development and Accuracy of CVLA3". To appear in English Corpus Studies, Vol. 32.**

The full research paper is included in this repository at `theses/Uchida_Negishi_2025.md`.

『CEFR-J Wordlist Version 1.6』 東京外国語大学投野由紀夫研究室. （URL: http://www.cefr-j.org/download.html より 2022 年 2 月ダウンロード）

### Implementation

This PyCEFRizer (CEFR-J Level Estimator) implementation was designed and developed using [Claude Code](https://claude.ai/code), Anthropic's AI coding assistant. The implementation faithfully follows the CVLA3 methodology described in the research paper, including:

- All 8 linguistic metrics (CVV1, BperA, POStypes, ARI, AvrDiff, AvrFreqRank, VperSent, LenNP)
- Regression equations for CEFR score calculation
- CEFR-J level mapping methodology
- Statistical approach of averaging middle 6 values for stability

### Key Features

- Uses spaCy for NLP processing (POS tagging, dependency parsing)
- Implements 8 linguistic metrics for comprehensive text analysis
- Applies regression equations to convert metrics to CEFR scores
- Averages middle 6 scores (excluding min/max) for stability
- Maps final score to CEFR-J level

## License

This implementation is for educational and research purposes. When using this software, please cite:

1. The original research paper by Uchida & Negishi (2025)
2. This implementation as: "PyCEFRizer - CEFR-J Level Estimator, implemented using Claude Code based on Uchida & Negishi (2025)"

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

- The authors of the original CVLA3 research for their innovative methodology
- The spaCy team for their excellent NLP library
- The English Vocabulary Profile and COCA for linguistic resources
