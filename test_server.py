#!/usr/bin/env python3
"""Test script for the Code Navigation MCP Server"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from server import CodeNavigationServer, CodeAnalyzer, FileCache


async def test_code_analyzer():
    """Test the CodeAnalyzer directly"""
    print("Testing CodeAnalyzer...")
    
    sample_dir = Path("examples/sample_project")
    models_file = sample_dir / "models.py"
    
    if not models_file.exists():
        print(f"Error: Sample file {models_file} not found")
        return False
        
    cache = FileCache()
    analyzer = cache.get_analyzer(models_file)
    
    if not analyzer:
        print("Error: Failed to analyze file")
        return False
        
    print(f"Found {len(analyzer.entities)} entities:")
    for entity in analyzer.entities[:5]:
        print(f"  - {entity.type}: {entity.name} at line {entity.line}")
        
    print(f"Found {len(analyzer.dependencies)} dependencies")
    
    return True


async def test_server_methods():
    """Test the server methods directly"""
    print("\nTesting Server Methods...")
    
    server = CodeNavigationServer()
    sample_dir = "examples/sample_project"
    
    # Test 1: Analyze file structure
    print("\n1. Testing analyze_file_structure...")
    result = await server.analyze_file_structure(f"{sample_dir}/models.py")
    
    if 'error' not in result:
        print(f"   File structure analysis:")
        print(f"   - Classes: {len(result.get('classes', []))}")
        print(f"   - Functions: {len(result.get('functions', []))}")
        print(f"   - Imports: {len(result.get('imports', []))}")
    else:
        print(f"   Error: {result['error']}")
        return False
        
    # Test 2: Find code usages
    print("\n2. Testing find_code_usages...")
    result = await server.find_code_usages(
        entity_name="User",
        search_directory=sample_dir,
        recursive=True
    )
    print(f"   Found {len(result)} usages of 'User' class")
    for usage in result[:3]:
        if usage['type'] == 'definition':
            print(f"   - Definition in {usage['entity']['file']}")
        else:
            print(f"   - {usage['context']} in {usage['file']}:{usage['line']}")
            
    # Test 3: Get code dependencies
    print("\n3. Testing get_code_dependencies...")
    result = await server.get_code_dependencies(
        entity_name="UserService",
        file_or_directory=sample_dir,
        recursive=True,
        include_reverse=True
    )
    if result['entity']:
        print(f"   Entity: {result['entity']['name']} ({result['entity']['type']})")
        print(f"   - Forward dependencies: {len(result['forward_dependencies'])}")
        print(f"   - Reverse dependencies: {len(result['reverse_dependencies'])}")
    else:
        print("   Entity 'UserService' not found")
        
    return True


async def test_complex_dependencies():
    """Test complex dependency scenarios"""
    print("\n4. Testing complex dependency analysis...")
    
    server = CodeNavigationServer()
    sample_dir = "examples/sample_project"
    
    # Find dependencies for PostService
    result = await server.get_code_dependencies(
        entity_name="PostService",
        file_or_directory=sample_dir,
        recursive=True,
        include_reverse=True
    )
    
    print("   PostService dependencies:")
    if result['entity']:
        if result['forward_dependencies']:
            print("   Forward dependencies:")
            for dep in result['forward_dependencies'][:5]:
                print(f"     - {dep['type']}: {dep['target']}")
                
        if result['reverse_dependencies']:
            print("   Reverse dependencies (who uses PostService):")
            for dep in result['reverse_dependencies'][:5]:
                print(f"     - {dep['source']['name']} ({dep['type']})")
    else:
        print("   Entity 'PostService' not found")
                
    return True


async def test_inheritance_tracking():
    """Test inheritance relationship tracking"""
    print("\n5. Testing inheritance tracking...")
    
    server = CodeNavigationServer()
    sample_dir = "examples/sample_project"
    
    # Check User class inheritance from BaseModel
    result = await server.get_code_dependencies(
        entity_name="User",
        file_or_directory=sample_dir,
        recursive=True,
        include_reverse=False
    )
    
    if result['entity']:
        print(f"   User class found at line {result['entity']['line']}")
        inheritance_deps = [d for d in result['forward_dependencies'] if d['type'] == 'inheritance']
        if inheritance_deps:
            print(f"   Inherits from: {', '.join(d['target'] for d in inheritance_deps)}")
        
        instantiation_deps = [d for d in result['forward_dependencies'] if d['type'] == 'instantiation']
        if instantiation_deps:
            print(f"   Creates instances of: {', '.join(set(d['target'] for d in instantiation_deps))}")
    
    return True


async def test_import_tracking():
    """Test import statement tracking"""
    print("\n6. Testing import tracking...")
    
    server = CodeNavigationServer()
    sample_dir = "examples/sample_project"
    
    # Analyze services.py imports
    result = await server.analyze_file_structure(f"{sample_dir}/services.py")
    
    if 'error' not in result:
        imports = result.get('imports', [])
        print(f"   Found {len(imports)} imports in services.py:")
        for imp in imports:
            print(f"     - {imp['name']} at line {imp['line']}")
    
    return True


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Code Navigation MCP Server Test Suite")
    print("=" * 60)
    
    tests = [
        ("Code Analyzer", test_code_analyzer),
        ("Server Methods", test_server_methods),
        ("Complex Dependencies", test_complex_dependencies),
        ("Inheritance Tracking", test_inheritance_tracking),
        ("Import Tracking", test_import_tracking)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\nError in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
            
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
        
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed")
        
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)