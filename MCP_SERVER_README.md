# PyCEFRizer MCP Server

PyCEFRizer now supports the Model Context Protocol (MCP), allowing AI assistants like Claude to directly analyze English text difficulty levels.

## Installation

1. Install PyCEFRizer with MCP support using uv:
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install PyCEFRizer with MCP support
uv pip install -e ".[mcp]"
```

2. Download the spaCy model if not already installed:
```bash
uv run python -m spacy download en_core_web_sm
```

## Configuration

### For Claude Desktop

Add the following to your Claude Desktop configuration file:

**On macOS/Linux:** `~/.config/Claude/claude_desktop_config.json`
**On Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pycefrizer": {
      "command": "uv",
      "args": ["run", "python", "-m", "pycefrizer.mcp_server"],
      "cwd": "/path/to/PyCEFRizer"
    }
  }
}
```

Replace `/path/to/PyCEFRizer` with the actual path to your PyCEFRizer installation.

### Alternative: Using the provided mcp.json

You can also copy the provided `mcp.json` configuration file to your Claude Desktop config directory.

## Running the MCP Server

### Standalone Mode (for testing)
```bash
uv run python -m pycefrizer.mcp_server
```

### Via Script Entry Point
```bash
uv run pycefrizer-mcp
```

## Available MCP Tools

The PyCEFRizer MCP server provides the following tools:

### 1. `analyze_text`
Analyze English text and return CEFR-J level assessment with metric scores.

**Parameters:**
- `text` (string): English text to analyze (10-10,000 words)

**Returns:** JSON with CEFR-J level and 8 metric scores

### 2. `get_word_cefr_level`
Get the CEFR level of a single English word.

**Parameters:**
- `word` (string): English word to look up

**Returns:** CEFR level (A1, A2, B1, B2, C1, C2) or "Not found"

### 3. `get_unused_words`
Find unused vocabulary from a specific CEFR level in the given text.

**Parameters:**
- `level` (string): CEFR level to search (A1, A2, B1, B2, C1, C2)
- `text` (string): English text to analyze

**Returns:** JSON mapping unused words to their parts of speech

### 4. `get_detailed_analysis`
Get detailed analysis including raw metric values and processed scores.

**Parameters:**
- `text` (string): English text to analyze (10-10,000 words)

**Returns:** JSON with detailed analysis including raw metrics and CEFR scores

### 5. `analyze_file`
Analyze text from a file and return CEFR-J level assessment.

**Parameters:**
- `file_path` (string): Path to text file to analyze

**Returns:** JSON with CEFR-J level and 8 metric scores

### 6. `batch_analyze`
Analyze multiple texts and return CEFR-J levels for each.

**Parameters:**
- `texts` (array of strings): List of English texts to analyze

**Returns:** JSON with results for each text

### 7. `get_cefr_statistics`
Get statistics about CEFR level distribution in the text.

**Parameters:**
- `text` (string): English text to analyze

**Returns:** JSON with word count by CEFR level and percentage distribution

### 8. `get_cefr_words`
Get all unique words (base forms) from a specific CEFR level with their parts of speech.

**Parameters:**
- `level` (string): CEFR level (A1, A2, B1, B2, C1, C2)

**Returns:** JSON with list of unique base_form and pos pairs for the specified level

## Example Usage in Claude

Once configured, you can use PyCEFRizer in Claude like this:

```
Claude: I'll analyze this text using the PyCEFRizer tool.

[Uses analyze_text tool]

The text has a CEFR-J level of B2.1, indicating upper-intermediate difficulty.
```

## Testing the MCP Server

Run the included test script:
```bash
uv run python test_mcp_server.py
```

This will test all available MCP tools and verify the server is working correctly.

## Troubleshooting

1. **Server not starting**: Ensure all dependencies are installed, especially the MCP package
2. **spaCy model not found**: Run `python -m spacy download en_core_web_sm`
3. **Permission errors**: Make sure the MCP server has read access to necessary data files

## Security Note

The MCP server only provides text analysis functionality and does not modify any files or execute arbitrary code. It's safe to use with AI assistants.