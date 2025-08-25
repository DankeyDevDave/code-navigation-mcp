# Code Navigation MCP Server

An intelligent Model Context Protocol (MCP) server for code navigation, dependency analysis, and usage tracking in Python codebases.

## Features

- **AST-based Code Analysis**: Deep understanding of Python code structure using Abstract Syntax Trees
- **Dependency Tracking**: Analyze forward and reverse dependencies between code entities
- **Usage Discovery**: Find all places where a class, function, or variable is used
- **File Structure Analysis**: Get organized overview of Python file contents
- **Performance Optimized**: Built-in caching layer for fast repeated queries
- **Docker Support**: Run in isolated container environments

## Installation

### Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/code-navigation-mcp.git
cd code-navigation-mcp

# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

### Docker Installation

```bash
# Build the Docker image
docker build -t code-navigation-mcp .

# Run with volume mount for code analysis
docker run -p 8080:8080 -v /path/to/your/code:/workspace:ro code-navigation-mcp

# Or using docker-compose
docker-compose up
```

## Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-navigation": {
      "command": "python",
      "args": ["/path/to/code-navigation-mcp/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/code-navigation-mcp"
      }
    }
  }
}
```

## Available Tools

### 1. get_code_dependencies

Analyzes forward and reverse dependencies for a code entity.

**Parameters:**
- `entity_name` (str): Name of the class, function, or variable to analyze
- `file_or_directory` (str): Path to file or directory to analyze
- `recursive` (bool): Whether to search directories recursively (default: true)
- `include_reverse` (bool): Include reverse dependencies (default: true)

**Example Usage:**
```python
# Find all dependencies of a class
result = await get_code_dependencies(
    entity_name="UserManager",
    file_or_directory="/workspace/src",
    recursive=True,
    include_reverse=True
)
```

**Returns:**
```json
{
  "entity": {
    "name": "UserManager",
    "type": "class",
    "file": "/workspace/src/users.py",
    "line": 10,
    "docstring": "Manages user operations"
  },
  "forward_dependencies": [
    {
      "target": "DatabaseConnection",
      "type": "instantiation",
      "line": 15
    }
  ],
  "reverse_dependencies": [
    {
      "source": {
        "name": "create_user",
        "type": "function",
        "file": "/workspace/src/api.py"
      },
      "type": "call",
      "line": 45
    }
  ]
}
```

### 2. find_code_usages

Finds all usages of a specific entity across the codebase.

**Parameters:**
- `entity_name` (str): Name of the entity to find usages for
- `search_directory` (str): Directory to search in
- `recursive` (bool): Whether to search recursively (default: true)

**Example Usage:**
```python
# Find all places where a function is used
usages = await find_code_usages(
    entity_name="validate_email",
    search_directory="/workspace",
    recursive=True
)
```

**Returns:**
```json
[
  {
    "type": "definition",
    "entity": {
      "name": "validate_email",
      "type": "function",
      "file": "/workspace/utils/validators.py",
      "line": 25
    }
  },
  {
    "type": "usage",
    "context": "call",
    "file": "/workspace/api/users.py",
    "line": 78,
    "source": {
      "name": "register_user",
      "type": "function"
    }
  }
]
```

### 3. analyze_file_structure

Provides a structured overview of a Python file's contents.

**Parameters:**
- `file_path` (str): Path to the Python file to analyze

**Example Usage:**
```python
# Analyze the structure of a Python file
structure = await analyze_file_structure(
    file_path="/workspace/src/main.py"
)
```

**Returns:**
```json
{
  "file_path": "/workspace/src/main.py",
  "imports": [
    {"name": "os", "line": 1},
    {"name": "json", "line": 2}
  ],
  "classes": [
    {
      "name": "Application",
      "type": "class",
      "line": 10,
      "docstring": "Main application class",
      "methods": [
        {
          "name": "__init__",
          "type": "method",
          "line": 12
        },
        {
          "name": "run",
          "type": "method",
          "line": 20
        }
      ]
    }
  ],
  "functions": [
    {
      "name": "main",
      "type": "function",
      "line": 50,
      "docstring": "Entry point"
    }
  ],
  "variables": [
    {
      "name": "CONFIG",
      "type": "variable",
      "line": 5
    }
  ]
}
```

## Usage Examples

### Example 1: Analyzing a Django Project

```python
# Find all usages of a Django model
usages = await find_code_usages(
    entity_name="User",
    search_directory="/workspace/myproject",
    recursive=True
)

# Analyze dependencies of a view function
deps = await get_code_dependencies(
    entity_name="user_profile_view",
    file_or_directory="/workspace/myproject/views",
    recursive=True
)
```

### Example 2: Refactoring Assistant

```python
# Before renaming a function, find all its usages
usages = await find_code_usages(
    entity_name="old_function_name",
    search_directory="/workspace",
    recursive=True
)

# Check what a class depends on before moving it
deps = await get_code_dependencies(
    entity_name="MyClass",
    file_or_directory="/workspace/src",
    include_reverse=False  # Only forward dependencies
)
```

### Example 3: Code Review Helper

```python
# Analyze the structure of a file being reviewed
structure = await analyze_file_structure(
    file_path="/workspace/src/new_feature.py"
)

# Check if a new class integrates well with existing code
deps = await get_code_dependencies(
    entity_name="NewFeatureClass",
    file_or_directory="/workspace",
    include_reverse=True
)
```

## Architecture

### Core Components

1. **AST Parser**: Uses Python's `ast` module to parse and understand code structure
2. **Code Analyzer**: Visitor pattern implementation for traversing AST nodes
3. **Dependency Tracker**: Records relationships between code entities
4. **File Cache**: Caches parsed results with MD5 hash validation
5. **MCP Server**: Exposes tools via Model Context Protocol

### Supported Python Constructs

- ✅ Classes and inheritance
- ✅ Functions and methods
- ✅ Async functions
- ✅ Variable assignments
- ✅ Import statements (import and from...import)
- ✅ Function calls
- ✅ Class instantiation
- ✅ Docstring extraction
- ✅ Nested classes and functions

### Performance Features

- **Lazy Loading**: Files are only parsed when needed
- **Smart Caching**: File content hashing prevents unnecessary re-parsing
- **Incremental Analysis**: Only changed files are re-analyzed
- **Efficient Traversal**: Single-pass AST visiting for multiple analyses

## Limitations

- **Python Only**: Currently supports only Python code (no JS, TS, Go, etc.)
- **Static Analysis**: No runtime or dynamic import tracking
- **Valid Syntax Required**: Files must be syntactically valid Python
- **No Type Inference**: Limited cross-file type tracking

## Development

### Running Tests

```bash
# Run with sample Python files
python test_server.py

# Run with real project
python server.py --test-dir /path/to/project
```

### Extending the Analyzer

To add support for additional Python constructs:

1. Add a new `visit_*` method to `CodeAnalyzer` class
2. Process the AST node and extract relevant information
3. Add to appropriate entity or dependency lists

Example:
```python
def visit_Decorator(self, node: ast.Decorator):
    """Process decorator usage"""
    # Custom decorator processing logic
    self.generic_visit(node)
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

MIT License - see LICENSE file for details