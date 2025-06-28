# Changelog

All notable changes to PyCEFRizer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2024-12-28

### Added
- Initial public release of PyCEFRizer
- Renamed from CLE to PyCEFRizer for better clarity
- Full pip package support with `pip install pycefrizer`
- Command-line interface with `pycefrizer` command
- Comprehensive documentation and examples
- Support for Python 3.9, 3.10, 3.11, and 3.12

### Features
- Analyzes English text (10-10,000 words) to estimate CEFR-J level
- Implements 8 linguistic metrics:
  - CVV1: Corrected Verb Variation
  - BperA: B-level to A-level content word ratio
  - POStypes: Average distinct POS tags per sentence
  - ARI: Automated Readability Index
  - AvrDiff: Average difficulty of content words
  - AvrFreqRank: Average frequency rank
  - VperSent: Average verbs per sentence
  - LenNP: Average noun phrase length
- Returns CEFR-J levels from preA1 to C2
- JSON output format
- Detailed analysis mode with raw metric values

### Technical Details
- Built with spaCy 3.7.2 for NLP processing
- Uses English Vocabulary Profile (EVP) word lookup data
- Implements COCA frequency rankings
- Based on CVLA3 methodology from Uchida & Negishi (2025)