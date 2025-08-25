# Code Navigation MCP Server

A Model Context Protocol (MCP) server that provides intelligent code navigation, dependency analysis, and usage tracking for Python codebases.

## Features

### 🔍 **Code Dependency Analysis**
- Tracks imports, function calls, class inheritance
- Shows both forward dependencies (what X depends on) and reverse dependencies (what depends on X)
- Analyzes dependency types: imports, calls, inheritance, instantiation

### 📍 **Usage Finding**
- Locates all definitions of functions, classes, and variables
- Finds all places where an entity is used
- Tracks usage context (calls, inheritance, imports)

### 📊 **File Structure Analysis**
- Provides complete structural overview of Python files
- Organizes code by imports, classes, functions, and variables
- Includes docstrings and method listings for classes

## Installation

### Option 1: Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/code-navigation-mcp.git
cd code-navigation-mcp

# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

### Option 2: Docker

```bash
# Build the image
docker build -t code-navigation-mcp .

# Run the container
docker run -p 8080:8080 -v /path/to/your/code:/workspace:ro code-navigation-mcp
```

## Configuration

### For Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "code-navigation": {
      "command": "python",
      "args": ["/path/to/code-navigation-mcp/server.py"]
    }
  }
}
```

### For Other MCP Clients

The server exposes three main tools via the MCP protocol:

1. **get_code_dependencies** - Analyze dependencies
2. **find_code_usages** - Find usage locations
3. **analyze_file_structure** - Get file structure

## Usage Examples

### Finding Dependencies

```python
# Request:
{
  "tool": "get_code_dependencies",
  "arguments": {
    "entity_name": "DataProcessor",
    "index_path": "/path/to/project",
    "recursive": true
  }
}

# Response shows:
# - What DataProcessor depends on (imports, calls, inherits from)
# - What depends on DataProcessor (classes that inherit, functions that call it)
```

### Finding Usages

```python
# Request:
{
  "tool": "find_code_usages",
  "arguments": {
    "entity_name": "calculate_score",
    "index_path": "/path/to/project"
  }
}

# Response shows:
# - Where calculate_score is defined
# - All places where it's called
# - File and line number for each usage
```

### Analyzing File Structure

```python
# Request:
{
  "tool": "analyze_file_structure",
  "arguments": {
    "file_path": "/path/to/module.py"
  }
}

# Response provides:
# - List of imports
# - Classes with their methods
# - Standalone functions
# - Module-level variables
# - Docstrings for documented entities
```

## How It Works

### Code Analysis Pipeline

1. **AST Parsing**: Uses Python's Abstract Syntax Tree (AST) to parse code
2. **Entity Extraction**: Identifies all code entities (classes, functions, variables)
3. **Dependency Tracking**: Records relationships between entities
4. **Index Building**: Creates searchable index for fast lookups
5. **Caching**: Caches analyzed files to improve performance

### Supported Python Constructs

- ✅ Function and class definitions
- ✅ Method definitions
- ✅ Import statements (import and from...import)
- ✅ Function calls
- ✅ Class inheritance
- ✅ Variable assignments
- ✅ Docstrings
- ✅ Nested classes and functions

### Performance Considerations

- **Lazy Loading**: Files are indexed on-demand
- **Caching**: Analyzed files are cached to avoid re-parsing
- **Incremental Updates**: Can index individual files or directories
- **Recursive Options**: Control directory traversal depth

## Advanced Features

### Custom Entity Types

The server can be extended to track additional entity types:

```python
# Add to CodeAnalyzer class:
def visit_AsyncFunctionDef(self, node):
    # Track async functions
    pass

def visit_Decorator(self, node):
    # Track decorator usage
    pass
```

### Cross-Language Support

While currently Python-focused, the architecture supports adding analyzers for other languages:

```python
class JavaScriptAnalyzer:
    # Parse JS/TS files using appropriate parser
    pass

class GoAnalyzer:
    # Parse Go files
    pass
```

## Limitations

- Currently supports Python files only
- Requires valid Python syntax (won't work with syntax errors)
- Dynamic imports and runtime-generated code aren't tracked
- Cross-file type inference is limited

## Contributing

Contributions are welcome! Areas for improvement:

- [ ] Support for more languages (JavaScript, TypeScript, Go, Rust)
- [ ] Type inference and type checking integration
- [ ] Git integration for tracking changes
- [ ] Performance optimizations for large codebases
- [ ] Real-time file watching and incremental updates
- [ ] Symbol renaming and refactoring support

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please open an issue on GitHub.