#!/usr/bin/env python3
"""Check word_lookup.json contents."""

import json

# Load the word lookup
with open('data/word_lookup.json', 'r') as f:
    data = json.load(f)

print(f"Total words in word_lookup.json: {len(data)}")
print("\nFirst 10 entries:")
for i, (word, info) in enumerate(data.items()):
    print(f"  {word}: {info}")
    if i >= 9:
        break

# Check for common words
common_words = ['the', 'be', 'have', 'do', 'education', 'student', 'learn', 'teacher', 'school']
print("\nChecking common words:")
for word in common_words:
    if word in data:
        print(f"  {word}: {data[word]}")
    else:
        print(f"  {word}: NOT FOUND")

# Check CEFR level distribution
level_counts = {}
for word, info in data.items():
    level = info.get('CEFR', 'Unknown')
    level_counts[level] = level_counts.get(level, 0) + 1

print("\nCEFR level distribution:")
for level in sorted(level_counts.keys()):
    print(f"  {level}: {level_counts[level]} words")