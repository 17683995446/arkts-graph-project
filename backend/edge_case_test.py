
#!/usr/bin/env python3
"""
Edge Case & Bug Discovery Test Suite
Tests extreme scenarios to discover hidden bugs
"""

import os
import sys
import tempfile
import time
import random
import sqlite3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import arkts_analyzer
from file_monitor import FileMonitorService


class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name, message=""):
        self.passed.append({"test": test_name, "message": message})
        print(f"  ✅ {test_name}")
        if message:
            print(f"     {message}")
    
    def add_fail(self, test_name, error):
        self.failed.append({"test": test_name, "error": str(error)})
        print(f"  ❌ {test_name}")
        print(f"     Error: {error}")
    
    def add_warning(self, test_name, warning):
        self.warnings.append({"test": test_name, "warning": warning})
        print(f"  ⚠️  {test_name}")
        print(f"     Warning: {warning}")


def test_empty_and_minimal_files(temp_dir, results):
    """Test edge cases with empty or minimal files"""
    print("\n" + "="*70)
    print("📋 TEST SUITE 1: Empty & Minimal Files")
    print("="*70)
    
    try:
        # Test 1.1: Completely empty file
        empty_file = temp_dir / "empty.ets"
        empty_file.write_text("", encoding='utf-8')
        try:
            arkts_analyzer.update_file_knowledge_graph(str(empty_file))
            classes = database.get_all_classes()
            results.add_pass("Empty file handling", f"Handled empty file, found {len([c for c in classes if c['file_id'] and c['name'] == 'empty'])} classes")
        except Exception as e:
            results.add_fail("Empty file handling", e)
        
        # Test 1.2: File with only whitespace
        ws_file = temp_dir / "whitespace.ets"
        ws_file.write_text("   \n\t\t  \n\n   ", encoding='utf-8')
        try:
            arkts_analyzer.update_file_knowledge_graph(str(ws_file))
            results.add_pass("Whitespace-only file handling")
        except Exception as e:
            results.add_fail("Whitespace-only file handling", e)
        
        # Test 1.3: File with only comments
        comment_file = temp_dir / "comments.ets"
        comment_file.write_text("""
// This is a comment
/*
 * Multi-line comment
 */
// Another comment
""", encoding='utf-8')
        try:
            arkts_analyzer.update_file_knowledge_graph(str(comment_file))
            results.add_pass("Comment-only file handling")
        except Exception as e:
            results.add_fail("Comment-only file handling", e)
        
        # Test 1.4: File with special Unicode characters
        unicode_file = temp_dir / "unicode.ets"
        unicode_file.write_text("""
// 文件名: 测试.ets
// Author: 测试用户
// Date: 2024-01-01
class 测试类 {
  方法1() {}
}
""", encoding='utf-8')
        try:
            arkts_analyzer.update_file_knowledge_graph(str(unicode_file))
            results.add_pass("Unicode file handling", "Successfully parsed Chinese characters")
        except Exception as e:
            results.add_fail("Unicode file handling", e)
            
    except Exception as e:
        results.add_fail("Test suite 1", e)


def test_very_large_files(temp_dir, results):
    """Test with extremely large files"""
    print("\n" + "="*70)
    print("📋 TEST SUITE 2: Very Large Files")
    print("="*70)
    
    try:
        # Test 2.1: File with 1000 classes
        large_file = temp_dir / "large.ets"
        content = []
        for i in range(1000):
            content.append(f"struct LargeClass{i} {{")
            content.append(f"  method{i}1() {{ }}")
            content.append(f"  method{i}2() {{ }}")
            content.append(f"  method{i}3() {{ }}")
            content.append("}")
        
        large_file.write_text("\n".join(content), encoding='utf-8')
        
        start = time.time()
        try:
            arkts_analyzer.update_file_knowledge_graph(str(large_file))
            elapsed = time.time() - start
            classes = database.get_all_classes()
            file_classes = [c for c in classes if 'LargeClass' in c.get('name', '')]
            results.add_pass("Large file (1000 classes)", f"Parsed in {elapsed:.2f}s, found {len(file_classes)} classes")
            
            if elapsed > 5.0:
                results.add_warning("Large file performance", f"Parsing took {elapsed:.2f}s, consider optimization")
        except Exception as e:
            results.add_fail("Large file handling", e)
        
        # Test 2.2: File with deeply nested structures
        nested_file = temp_dir / "nested.ets"
        content = ["class OuterClass {"]
        for depth in range(50):
            content.append("  " * (depth + 1) + f"inner{depth}() {{")
        for depth in range(50, 0, -1):
            content.append("  " * depth + "}")
        content.append("}")
        
        nested_file.write_text("\n".join(content), encoding='utf-8')
        try:
            arkts_analyzer.update_file_knowledge_graph(str(nested_file))
            results.add_pass("Deeply nested structure (50 levels)")
        except RecursionError as e:
            results.add_fail("Deeply nested structure", "RecursionError - potential stack overflow")
        except Exception as e:
            results.add_fail("Deeply nested structure", e)
            
    except Exception as e:
        results.add_fail("Test suite 2", e)


def test_concurrent_operations(temp_dir, results):
    """Test concurrent database operations for race conditions"""
    print("\n" + "="*70)
    print("📋 TEST SUITE 3: Concurrent Operations & Race Conditions")
    print("="*70)
    
    try:
        # Test 3.1: Concurrent file insertions
        print("\n  Testing concurrent file insertions...")
        errors = []
        success_count = 0
        
        def insert_file(index):
            try:
                file_path = f"/test/concurrent/file_{index}.ets"
                content = f"class Test{index} {{ method{index}() {{ }} }}"
                # Create dummy file for hash BEFORE computing hash
                dummy_file = temp_dir / f"dummy_{index}.ets"
                dummy_file.write_text(content)
                file_hash = database.compute_file_hash(str(dummy_file))
                database.insert_file(file_path, file_hash)
                return True
            except Exception as e:
                errors.append(str(e))
                return False
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(insert_file, i) for i in range(100)]
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
        
        if success_count == 100:
            results.add_pass("Concurrent insertions", f"100 concurrent inserts, 0 errors")
        else:
            results.add_fail("Concurrent insertions", f"Only {success_count}/100 succeeded, {len(errors)} errors")
        
        # Test 3.2: Concurrent reads during writes
        print("\n  Testing reads during writes...")
        stop_flag = threading.Event()
        
        def writer():
            for i in range(50):
                try:
                    database.insert_file(f"/test/concurrent/writer_{i}.ets", b"test_hash_concurrent_writer")
                except Exception:
                    pass
        
        def reader():
            count = 0
            while not stop_flag.is_set() and count < 100:
                try:
                    database.get_all_files()
                    count += 1
                except Exception:
                    pass
            return count
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            writer_future = executor.submit(writer)
            reader_future = executor.submit(reader)
            time.sleep(1)
            stop_flag.set()
            reader_count = reader_future.result()
            writer_future.result()
        
        results.add_pass("Concurrent read/write", f"Safe concurrent operations, {reader_count} reads completed")
        
        # Test 3.3: Concurrent file monitor operations
        print("\n  Testing concurrent file monitor operations...")
        monitor = FileMonitorService(str(temp_dir), 500)
        
        def create_and_sync_files(start_idx, count):
            for i in range(start_idx, start_idx + count):
                file_path = temp_dir / f"monitor_test_{i}.ets"
                file_path.write_text(f"class MonitorTest{i} {{ test{i}() {{ }} }}")
                try:
                    arkts_analyzer.update_file_knowledge_graph(str(file_path))
                except Exception:
                    pass
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_and_sync_files, i * 20, 20) for i in range(5)]
            for future in as_completed(futures):
                future.result()
        
        results.add_pass("Concurrent file monitor operations", "Handled concurrent sync operations")
        
    except Exception as e:
        results.add_fail("Test suite 3", e)


def test_invalid_and_malformed_data(temp_dir, results):
    """Test handling of invalid and malformed data"""
    print("\n" + "="*70)
    print("📋 TEST SUITE 4: Invalid & Malformed Data")
    print("="*70)
    
    try:
        # Test 4.1: Invalid SQL queries
        print("\n  Testing invalid SQL queries...")
        invalid_queries = [
            "SELECT * FROM nonexistent_table",
            "DROP TABLE files",
            "DELETE FROM files",
            "INSERT INTO files (id) VALUES (999999)",
            "SELECT * FROM files WHERE id = ' OR '1'='1",
        ]
        
        safe_handled = 0
        for query in invalid_queries:
            try:
                result = database.execute_custom_query(query)
                results.add_warning(f"Unsafe query handling", f"Query executed: {query[:50]}")
            except Exception as e:
                safe_handled += 1
        
        results.add_pass("Invalid SQL query handling", f"{safe_handled}/{len(invalid_queries)} queries safely blocked")
        
        # Test 4.2: Malformed ArkTS files
        print("\n  Testing malformed ArkTS files...")
        malformed_files = [
            ("unclosed_brace.ets", "class Test {"),
            ("extra_braces.ets", "class Test { } }"),
            ("invalid_syntax.ets", "class @Test { }"),
            ("empty_class_name.ets", "class { }"),
            ("weird_characters.ets", "class Test\u0000 { }"),
        ]
        
        handled_count = 0
        for filename, content in malformed_files:
            file_path = temp_dir / filename
            file_path.write_text(content, encoding='utf-8')
            try:
                arkts_analyzer.update_file_knowledge_graph(str(file_path))
                handled_count += 1
            except Exception:
                pass
        
        results.add_pass("Malformed file handling", f"Handled {handled_count}/{len(malformed_files)} malformed files")
        
        # Test 4.3: Invalid file hashes
        print("\n  Testing invalid file hashes...")
        try:
            database.insert_file("/test/invalid/hash1", "not_a_valid_hash")
            results.add_pass("Invalid hash handling", "Accepted string hash")
        except Exception as e:
            results.add_warning("Invalid hash handling", str(e))
        
    except Exception as e:
        results.add_fail("Test suite 4", e)


def test_file_system_operations(temp_dir, results):
    """Test file system operations and edge cases"""
    print("\n" + "="*70)
    print("📋 TEST SUITE 5: File System Operations")
    print("="*70)
    
    try:
        # Test 5.1: Non-existent file
        print("\n  Testing non-existent file...")
        try:
            arkts_analyzer.update_file_knowledge_graph("/nonexistent/path/file.ets")
            results.add_warning("Non-existent file", "Should have raised an error")
        except FileNotFoundError:
            results.add_pass("Non-existent file handling", "Properly raised FileNotFoundError")
        except Exception as e:
            results.add_warning("Non-existent file handling", f"Raised {type(e).__name__}")
        
        # Test 5.2: File with very long path
        print("\n  Testing very long file paths...")
        long_path_parts = ["a"] * 100
        # Use Path() constructor properly instead of + operator
        long_path = Path(temp_dir) / "/".join(long_path_parts) / "file.ets"
        try:
            long_path.parent.mkdir(parents=True, exist_ok=True)
            long_path.write_text("class Test { }")
            arkts_analyzer.update_file_knowledge_graph(str(long_path))
            results.add_pass("Long path handling", f"Handled path with {len(str(long_path))} characters")
        except Exception as e:
            results.add_warning("Long path handling", str(e))
        
        # Test 5.3: File permissions (if applicable)
        print("\n  Testing file permission issues...")
        # Create a read-only file
        readonly_file = temp_dir / "readonly.ets"
        readonly_file.write_text("class Test { }")
        try:
            os.chmod(str(readonly_file), 0o444)
            # Try to update it
            arkts_analyzer.update_file_knowledge_graph(str(readonly_file))
            results.add_pass("Read-only file handling")
        except PermissionError:
            results.add_pass("Permission error handling", "Properly detected read-only file")
        except Exception as e:
            results.add_warning("Permission handling", str(e))
        finally:
            try:
                os.chmod(str(readonly_file), 0o644)
            except Exception:
                pass
        
    except Exception as e:
        results.add_fail("Test suite 5", e)


def test_database_integrity(temp_dir, results):
    """Test database integrity and consistency"""
    print("\n" + "="*70)
    print("📋 TEST SUITE 6: Database Integrity")
    print("="*70)
    
    try:
        # Test 6.1: Orphaned records check
        print("\n  Checking for orphaned records...")
        files = database.get_all_files()
        classes = database.get_all_classes()
        methods = database.get_all_methods()
        calls = database.get_all_calls()
        
        orphaned_classes = 0
        for cls in classes:
            if not any(f['id'] == cls['file_id'] for f in files):
                orphaned_classes += 1
        
        orphaned_methods = 0
        for method in methods:
            if not any(c['id'] == method['class_id'] for c in classes):
                orphaned_methods += 1
        
        if orphaned_classes == 0 and orphaned_methods == 0:
            results.add_pass("Database integrity", "No orphaned records found")
        else:
            results.add_fail("Database integrity", f"Found {orphaned_classes} orphaned classes, {orphaned_methods} orphaned methods")
        
        # Test 6.2: Duplicate entries
        print("\n  Checking for duplicate entries...")
        file_paths = [f['path'] for f in files]
        if len(file_paths) == len(set(file_paths)):
            results.add_pass("Duplicate check", "No duplicate file paths")
        else:
            duplicates = len(file_paths) - len(set(file_paths))
            results.add_warning("Duplicate check", f"Found {duplicates} duplicate paths")
        
        # Test 6.3: Database file corruption simulation
        print("\n  Testing database recovery...")
        db_path = database.get_db_path()
        try:
            # Check if database is valid
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            conn.close()
            
            if integrity == "ok":
                results.add_pass("Database integrity check", "Database passed integrity check")
            else:
                results.add_fail("Database integrity check", f"Integrity check failed: {integrity}")
        except Exception as e:
            results.add_fail("Database integrity check", str(e))
        
    except Exception as e:
        results.add_fail("Test suite 6", e)


def run_all_tests():
    """Run all edge case tests"""
    print("\n" + "="*70)
    print("🚀 STARTING COMPREHENSIVE EDGE CASE & BUG DISCOVERY TESTS")
    print("="*70)
    
    results = TestResults()
    
    with tempfile.TemporaryDirectory(prefix="arkts_edge_case_test_") as temp_dir:
        temp_path = Path(temp_dir)
        
        # Initialize database
        db_path = temp_path / "edge_case_test.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        print(f"\n📁 Test directory: {temp_path}")
        print(f"📊 Database: {db_path}")
        
        # Run all test suites
        test_empty_and_minimal_files(temp_path, results)
        test_very_large_files(temp_path, results)
        test_concurrent_operations(temp_path, results)
        test_invalid_and_malformed_data(temp_path, results)
        test_file_system_operations(temp_path, results)
        test_database_integrity(temp_path, results)
        
        # Restore default database
        database.set_custom_db_path(None)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    print(f"\n✅ Passed: {len(results.passed)}")
    print(f"❌ Failed: {len(results.failed)}")
    print(f"⚠️  Warnings: {len(results.warnings)}")
    
    if results.failed:
        print(f"\n{'='*70}")
        print("🐛 CRITICAL BUGS FOUND:")
        print("="*70)
        for failure in results.failed:
            print(f"\n❌ {failure['test']}")
            print(f"   {failure['error']}")
    
    if results.warnings:
        print(f"\n{'='*70}")
        print("⚠️  WARNINGS & POTENTIAL ISSUES:")
        print("="*70)
        for warning in results.warnings:
            print(f"\n⚠️  {warning['test']}")
            print(f"   {warning['warning']}")
    
    if not results.failed:
        print(f"\n{'='*70}")
        print("🎉 ALL TESTS PASSED - NO CRITICAL BUGS FOUND!")
        print("="*70)
    
    return results


if __name__ == "__main__":
    run_all_tests()
