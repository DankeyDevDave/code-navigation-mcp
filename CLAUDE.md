# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that provides intelligent code navigation, dependency analysis, and usage tracking for Python codebases. The server enables AI assistants to analyze code structure, track dependencies, and find usage patterns across Python projects.

## Development Commands

### Running the Server
```bash
# Start the MCP server
python server.py

# Or using npm scripts
npm start
```

### Docker Operations
```bash
# Build Docker image
docker build -t code-navigation-mcp .

# Run with volume mount for code analysis
docker run -p 8080:8080 -v /path/to/analyze:/workspace:ro code-navigation-mcp

# Using docker-compose
docker-compose up
```

### Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Requirements: mcp>=0.1.0, typing-extensions>=4.0.0
```

## Architecture

### Core Components

The server implements three main MCP tools:

1. **get_code_dependencies** - Analyzes forward and reverse dependencies for entities
   - Tracks imports, function calls, class inheritance, instantiation
   - Supports recursive directory traversal
   
2. **find_code_usages** - Locates all uses of a specific entity
   - Finds definitions and all usage locations
   - Includes context (calls, inheritance, imports)
   
3. **analyze_file_structure** - Provides structural overview of Python files
   - Organizes by imports, classes, functions, variables
   - Includes docstrings and method listings

### Code Analysis Pipeline

1. **AST Parsing** - Uses Python's Abstract Syntax Tree for code parsing
2. **Entity Extraction** - Identifies classes, functions, variables
3. **Dependency Tracking** - Records relationships between entities
4. **Index Building** - Creates searchable index with caching
5. **Lazy Loading** - Files indexed on-demand for performance

### MCP Protocol Integration

The server exposes tools via the Model Context Protocol, allowing integration with:
- Claude Desktop (via claude_desktop_config.json)
- Other MCP-compatible clients
- Docker containers with volume mounts for isolated analysis

## Configuration

### Claude Desktop Integration
Add to `claude_desktop_config.json`:
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

### Environment Variables
- `MCP_MODE=server` - Run in server mode
- `LOG_LEVEL=INFO` - Control logging verbosity
- `PYTHONPATH` - Include server directory for imports

## Implementation Notes

### Server Implementation (server.py)
The main server file should implement:
- MCP server initialization
- Tool registration for the three analysis functions
- AST-based code analyzer class
- Caching layer for performance
- Request/response handling per MCP protocol

### Supported Python Constructs
- Function and class definitions
- Method definitions within classes
- Import statements (import and from...import)
- Function calls and class instantiation
- Class inheritance chains
- Variable assignments
- Docstrings extraction
- Nested classes and functions

### Performance Optimizations
- File caching to avoid re-parsing
- Lazy loading of files on first access
- Incremental updates for changed files
- Optional recursive directory traversal

## Current Limitations

- Python-only support (no JavaScript, TypeScript, Go, etc.)
- Requires syntactically valid Python files
- No tracking of dynamic imports or runtime-generated code
- Limited cross-file type inference
- No real-time file watching (requires manual re-indexing)

## Extension Points

### Adding Language Support
The architecture supports adding analyzers for other languages by implementing language-specific AST parsers in new analyzer classes.

### Custom Entity Types
The CodeAnalyzer class can be extended with additional visitor methods for tracking decorators, async functions, or other Python constructs.