#!/usr/bin/env python3
"""
Code Navigation MCP Server
Provides intelligent code navigation, dependency analysis, and usage tracking for Python codebases.
"""

import ast
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import hashlib

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EntityInfo:
    """Information about a code entity (class, function, variable)"""
    name: str
    type: str  # 'class', 'function', 'method', 'variable'
    file: str
    line: int
    column: int
    docstring: Optional[str] = None
    parent: Optional[str] = None  # For methods, the parent class
    
    def to_dict(self):
        return asdict(self)


@dataclass
class DependencyInfo:
    """Information about a dependency relationship"""
    source: EntityInfo
    target: str  # Target entity name
    type: str  # 'import', 'call', 'instantiation', 'inheritance'
    line: int
    column: int
    
    def to_dict(self):
        return {
            'source': self.source.to_dict(),
            'target': self.target,
            'type': self.type,
            'line': self.line,
            'column': self.column
        }


@dataclass
class FileStructure:
    """Structure of a Python file"""
    file_path: str
    imports: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Dict[str, Any]] = field(default_factory=list)
    variables: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


class CodeAnalyzer(ast.NodeVisitor):
    """AST-based code analyzer for Python files"""
    
    def __init__(self, file_path: str):
        self.file_path = str(file_path)
        self.entities: List[EntityInfo] = []
        self.dependencies: List[DependencyInfo] = []
        self.current_class: Optional[str] = None
        self.imports: Dict[str, str] = {}  # alias -> full_name
        self.imported_names: Set[str] = set()
        
    def visit_Import(self, node: ast.Import):
        """Process import statements"""
        for alias in node.names:
            name = alias.asname or alias.name
            self.imports[name] = alias.name
            self.imported_names.add(alias.name)
            self._add_import_dependency(alias.name, node)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Process from...import statements"""
        module = node.module or ''
        for alias in node.names:
            name = alias.asname or alias.name
            full_name = f"{module}.{alias.name}" if module else alias.name
            self.imports[name] = full_name
            self.imported_names.add(full_name)
            self._add_import_dependency(full_name, node)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node: ast.ClassDef):
        """Process class definitions"""
        docstring = ast.get_docstring(node)
        entity = EntityInfo(
            name=node.name,
            type='class',
            file=self.file_path,
            line=node.lineno,
            column=node.col_offset,
            docstring=docstring
        )
        self.entities.append(entity)
        
        # Track inheritance
        for base in node.bases:
            if isinstance(base, ast.Name):
                self._add_dependency(entity, base.id, 'inheritance', base)
            elif isinstance(base, ast.Attribute):
                self._add_dependency(entity, self._get_full_name(base), 'inheritance', base)
                
        # Visit class body
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Process function definitions"""
        self._visit_function_like(node)
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Process async function definitions"""
        self._visit_function_like(node)
        
    def _visit_function_like(self, node):
        """Process function or method definitions"""
        docstring = ast.get_docstring(node)
        entity_type = 'method' if self.current_class else 'function'
        entity = EntityInfo(
            name=node.name,
            type=entity_type,
            file=self.file_path,
            line=node.lineno,
            column=node.col_offset,
            docstring=docstring,
            parent=self.current_class
        )
        self.entities.append(entity)
        
        # Visit function body to find calls
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call):
                self._process_call(stmt, entity)
                
    def visit_Assign(self, node: ast.Assign):
        """Process variable assignments"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                entity = EntityInfo(
                    name=target.id,
                    type='variable',
                    file=self.file_path,
                    line=target.lineno,
                    column=target.col_offset,
                    parent=self.current_class
                )
                self.entities.append(entity)
                
                # Check if it's a class instantiation
                if isinstance(node.value, ast.Call):
                    self._process_call(node.value, entity)
                    
        self.generic_visit(node)
        
    def _process_call(self, node: ast.Call, source: EntityInfo):
        """Process a function/method call or class instantiation"""
        if isinstance(node.func, ast.Name):
            target = node.func.id
            # Check if it's a class instantiation
            dep_type = 'instantiation' if target[0].isupper() else 'call'
            self._add_dependency(source, target, dep_type, node.func)
        elif isinstance(node.func, ast.Attribute):
            target = self._get_full_name(node.func)
            self._add_dependency(source, target, 'call', node.func)
            
    def _get_full_name(self, node: ast.Attribute) -> str:
        """Get the full name from an attribute node"""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return '.'.join(reversed(parts))
        
    def _add_dependency(self, source: EntityInfo, target: str, dep_type: str, node: ast.AST):
        """Add a dependency relationship"""
        dep = DependencyInfo(
            source=source,
            target=target,
            type=dep_type,
            line=node.lineno,
            column=node.col_offset
        )
        self.dependencies.append(dep)
        
    def _add_import_dependency(self, target: str, node: ast.AST):
        """Add an import dependency"""
        # Create a file-level entity for imports
        source = EntityInfo(
            name='<module>',
            type='module',
            file=self.file_path,
            line=1,
            column=0
        )
        dep = DependencyInfo(
            source=source,
            target=target,
            type='import',
            line=node.lineno,
            column=node.col_offset
        )
        self.dependencies.append(dep)


class FileCache:
    """Cache for parsed file information"""
    
    def __init__(self):
        self._cache: Dict[str, Tuple[str, CodeAnalyzer]] = {}
        
    def get_analyzer(self, file_path: Path) -> Optional[CodeAnalyzer]:
        """Get cached analyzer or parse file if needed"""
        str_path = str(file_path)
        
        # Check if file exists
        if not file_path.exists():
            return None
            
        # Get file hash
        file_hash = self._get_file_hash(file_path)
        
        # Check cache
        if str_path in self._cache:
            cached_hash, analyzer = self._cache[str_path]
            if cached_hash == file_hash:
                return analyzer
                
        # Parse file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content, str_path)
            analyzer = CodeAnalyzer(str_path)
            analyzer.visit(tree)
            self._cache[str_path] = (file_hash, analyzer)
            return analyzer
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return None
            
    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of file contents"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()


class CodeNavigationServer:
    """MCP server for code navigation"""
    
    def __init__(self):
        self.server = Server("code-navigation-mcp")
        self.cache = FileCache()
        
    def _get_python_files(self, path: Path, recursive: bool) -> List[Path]:
        """Get all Python files in a path"""
        if path.is_file():
            return [path] if path.suffix == '.py' else []
            
        if recursive:
            return list(path.rglob('*.py'))
        else:
            return list(path.glob('*.py'))
            
    async def get_code_dependencies(
        self,
        entity_name: str,
        file_or_directory: str,
        recursive: bool = True,
        include_reverse: bool = True
    ) -> Dict[str, Any]:
        """Analyze forward and reverse dependencies for an entity"""
        path = Path(file_or_directory)
        files = self._get_python_files(path, recursive)
        
        forward_deps = []
        reverse_deps = []
        entity_info = None
        
        for file_path in files:
            analyzer = self.cache.get_analyzer(file_path)
            if not analyzer:
                continue
                
            # Find entity definition
            for entity in analyzer.entities:
                if entity.name == entity_name:
                    entity_info = entity
                    # Get forward dependencies
                    for dep in analyzer.dependencies:
                        if dep.source.name == entity_name:
                            forward_deps.append(dep.to_dict())
                            
            # Find reverse dependencies if requested
            if include_reverse:
                for dep in analyzer.dependencies:
                    if dep.target == entity_name or dep.target.endswith(f'.{entity_name}'):
                        reverse_deps.append(dep.to_dict())
                        
        return {
            'entity': entity_info.to_dict() if entity_info else None,
            'forward_dependencies': forward_deps,
            'reverse_dependencies': reverse_deps if include_reverse else []
        }
        
    async def find_code_usages(
        self,
        entity_name: str,
        search_directory: str,
        recursive: bool = True
    ) -> List[Dict[str, Any]]:
        """Find all usages of a specific entity across the codebase"""
        path = Path(search_directory)
        files = self._get_python_files(path, recursive)
        
        usages = []
        definitions = []
        
        for file_path in files:
            analyzer = self.cache.get_analyzer(file_path)
            if not analyzer:
                continue
                
            # Find definitions
            for entity in analyzer.entities:
                if entity.name == entity_name:
                    definitions.append({
                        'type': 'definition',
                        'entity': entity.to_dict()
                    })
                    
            # Find usages
            for dep in analyzer.dependencies:
                if dep.target == entity_name or dep.target.endswith(f'.{entity_name}'):
                    usages.append({
                        'type': 'usage',
                        'context': dep.type,
                        'file': dep.source.file,
                        'line': dep.line,
                        'column': dep.column,
                        'source': dep.source.to_dict()
                    })
                    
        return definitions + usages
        
    async def analyze_file_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyze and return the structure of a Python file"""
        path = Path(file_path)
        analyzer = self.cache.get_analyzer(path)
        
        if not analyzer:
            return {'error': f'Could not parse file: {file_path}'}
            
        structure = FileStructure(file_path=file_path)
        
        # Organize entities by type
        for entity in analyzer.entities:
            entity_dict = entity.to_dict()
            
            if entity.type == 'class':
                # Add methods to the class
                methods = [e.to_dict() for e in analyzer.entities 
                          if e.type == 'method' and e.parent == entity.name]
                entity_dict['methods'] = methods
                structure.classes.append(entity_dict)
            elif entity.type == 'function':
                structure.functions.append(entity_dict)
            elif entity.type == 'variable' and not entity.parent:
                structure.variables.append(entity_dict)
                
        # Add imports
        for dep in analyzer.dependencies:
            if dep.type == 'import':
                structure.imports.append({
                    'name': dep.target,
                    'line': dep.line
                })
                
        return structure.to_dict()
            
    async def run(self):
        """Run the MCP server"""
        # Register tool handlers
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="get_code_dependencies",
                    description="Analyze forward and reverse dependencies for a code entity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_name": {
                                "type": "string",
                                "description": "Name of the class, function, or variable to analyze"
                            },
                            "file_or_directory": {
                                "type": "string",
                                "description": "Path to file or directory to analyze"
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Whether to search directories recursively",
                                "default": True
                            },
                            "include_reverse": {
                                "type": "boolean",
                                "description": "Include reverse dependencies (who uses this entity)",
                                "default": True
                            }
                        },
                        "required": ["entity_name", "file_or_directory"]
                    }
                ),
                Tool(
                    name="find_code_usages",
                    description="Find all usages of a specific entity across the codebase",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_name": {
                                "type": "string",
                                "description": "Name of the entity to find usages for"
                            },
                            "search_directory": {
                                "type": "string",
                                "description": "Directory to search in"
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Whether to search recursively",
                                "default": True
                            }
                        },
                        "required": ["entity_name", "search_directory"]
                    }
                ),
                Tool(
                    name="analyze_file_structure",
                    description="Analyze and return the structure of a Python file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the Python file to analyze"
                            }
                        },
                        "required": ["file_path"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list:
            """Handle tool calls"""
            if name == "get_code_dependencies":
                result = await self.get_code_dependencies(**arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            elif name == "find_code_usages":
                result = await self.find_code_usages(**arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            elif name == "analyze_file_structure":
                result = await self.analyze_file_structure(**arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                raise ValueError(f"Unknown tool: {name}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point"""
    import asyncio
    
    server = CodeNavigationServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()