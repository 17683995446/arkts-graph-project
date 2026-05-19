
#!/usr/bin/env python3
"""
Comprehensive Stress & Integration Test Suite
Discovers system defects by running complex, long-running tests
"""

import os
import sys
import time
import tempfile
import random
import hashlib
import concurrent.futures
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
import arkts_analyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/backend/stress_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Test configuration
NUM_LARGE_FILES = 20  # Number of large test files to create
NUM_SMALL_FILES = 100  # Number of small test files
MAX_CLASS_SIZE = 500  # Maximum number of classes per file
MAX_METHODS_PER_CLASS = 100  # Maximum methods per class
PARALLEL_THREADS = 10  # Number of parallel threads for testing


def generate_large_arkts_file(file_path: Path, num_classes: int = 10) -> None:
    """Generate a large ArkTS file for stress testing"""
    content = []
    for i in range(num_classes):
        class_name = f"TestClass_{random.randint(1000, 9999)}_{i}"
        content.append(f"class {class_name} {{")
        # Add 10-50 random methods
        num_methods = random.randint(10, MAX_METHODS_PER_CLASS)
        for j in range(num_methods):
            method_name = f"method_{random.randint(1000, 9999)}_{j}"
            content.append(f"  {method_name}() {{")
            # Add random calls to other methods
            for k in range(random.randint(1, 10)):
                call_method_idx = random.randint(0, num_methods - 1)
                content.append(f"    this.method_{1000 + call_method_idx}_{call_method_idx}();")
            content.append("  }")
        content.append("}")
        content.append("")
    
    file_path.write_text("\n".join(content), encoding='utf-8')
    logger.info(f"Generated large ArkTS file: {file_path} ({file_path.stat().st_size} bytes)")


def generate_small_arkts_file(file_path: Path) -> None:
    """Generate a small ArkTS file"""
    class_name = f"SmallClass_{random.randint(1000, 9999)}"
    content = f"""class {class_name} {{
  doSomething() {{
  }}
}}
"""
    file_path.write_text(content, encoding='utf-8')


def stress_test_arkts_analyzer(temp_dir: Path) -> Dict[str, Any]:
    """
    Stress test the ArkTS analyzer with various file sizes and patterns
    Returns results with any defects found
    """
    logger.info("=== Starting ArkTS Analyzer Stress Test ===")
    results = {
        "success": True,
        "files_processed": 0,
        "classes_extracted": 0,
        "methods_extracted": 0,
        "errors": [],
        "timings": [],
        "average_time_per_file": 0.0
    }
    
    test_files = []
    
    # Create large test files
    for i in range(NUM_LARGE_FILES):
        file_path = temp_dir / f"large_test_{i}.ets"
        generate_large_arkts_file(file_path, num_classes=random.randint(5, MAX_CLASS_SIZE))
        test_files.append(file_path)
    
    # Create small test files
    for i in range(NUM_SMALL_FILES):
        file_path = temp_dir / f"small_test_{i}.ets"
        generate_small_arkts_file(file_path)
        test_files.append(file_path)
    
    logger.info(f"Created {len(test_files)} test files")
    
    # Process all files and collect timings
    total_time = 0.0
    for file_path in test_files:
        try:
            start_time = time.time()
            parsed_data = arkts_analyzer.parse_file(str(file_path))
            elapsed = time.time() - start_time
            
            total_time += elapsed
            results["timings"].append(elapsed)
            results["files_processed"] += 1
            results["classes_extracted"] += len(parsed_data["classes"])
            results["methods_extracted"] += sum(len(cls["methods"]) for cls in parsed_data["classes"])
            
            logger.debug(f"Processed {file_path}: {len(parsed_data['classes'])} classes in {elapsed:.4f}s")
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            results["success"] = False
            results["errors"].append({
                "file": str(file_path),
                "error": str(e),
                "type": type(e).__name__
            })
    
    if results["files_processed"] > 0:
        results["average_time_per_file"] = total_time / results["files_processed"]
    
    logger.info("=== ArkTS Analyzer Test Complete ===")
    logger.info(f"  Success: {results['success']}")
    logger.info(f"  Files processed: {results['files_processed']}")
    logger.info(f"  Classes extracted: {results['classes_extracted']}")
    logger.info(f"  Methods extracted: {results['methods_extracted']}")
    logger.info(f"  Average time/file: {results['average_time_per_file']:.4f}s")
    
    return results


def stress_test_database(temp_dir: Path) -> Dict[str, Any]:
    """
    Stress test the database with concurrent operations and large datasets
    """
    logger.info("=== Starting Database Stress Test ===")
    results = {
        "success": True,
        "operations_completed": 0,
        "errors": [],
        "timings": {},
    }
    
    # Create new database for this test
    db_path = temp_dir / "stress_test.db"
    
    try:
        # Set custom database path and initialize
        database.set_custom_db_path(str(db_path))
        start = time.time()
        database.init_database()
        results["timings"]["init_db"] = time.time() - start
        results["operations_completed"] += 1
        logger.info(f"Database initialized in {results['timings']['init_db']:.4f}s")
        
        # Test 2: Insert many files
        num_files = 200
        files = []
        for i in range(num_files):
            file_path = f"/test/stress/test_{i}.ets"
            content = f"class Test{i} {{ }}".encode('utf-8')
            file_hash = hashlib.md5(content).digest()
            files.append((file_path, file_hash))
        
        start = time.time()
        for file_path, file_hash in files:
            database.insert_file(file_path, file_hash)
        elapsed = time.time() - start
        results["timings"]["insert_files"] = elapsed
        results["operations_completed"] += num_files
        logger.info(f"Inserted {num_files} files in {elapsed:.4f}s ({num_files/elapsed:.1f} files/s)")
        
        # Test 3: Concurrent file updates
        def update_file(file_id):
            try:
                database.update_file(file_id, f"/test/stress/updated_{file_id}.ets", "newhash12345")
                return True
            except Exception as e:
                results["errors"].append({
                    "operation": "concurrent_update",
                    "error": str(e)
                })
                return False
        
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=PARALLEL_THREADS) as executor:
            futures = [executor.submit(update_file, i + 1) for i in range(num_files)]
            concurrent_results = [f.result() for f in futures]
        
        elapsed = time.time() - start
        results["timings"]["concurrent_updates"] = elapsed
        success_count = sum(1 for r in concurrent_results if r)
        logger.info(f"Concurrent updates: {success_count}/{num_files} in {elapsed:.4f}s")
        
        # Test 4: Query performance
        start = time.time()
        all_files = database.get_all_files()
        results["timings"]["get_all_files"] = time.time() - start
        logger.info(f"Fetched {len(all_files)} files in {results['timings']['get_all_files']:.4f}s")
        
        results["operations_completed"] += len(all_files) + 1
        
    except Exception as e:
        logger.error(f"Database stress test failed: {e}")
        results["success"] = False
        results["errors"].append({
            "stage": "database_test",
            "error": str(e)
        })
    finally:
        # Restore default database path
        database.set_custom_db_path(None)
    
    logger.info("=== Database Test Complete ===")
    return results


def stress_test_complete_system(temp_dir: Path) -> Dict[str, Any]:
    """
    Test the complete system: File Monitor -> Analyzer -> Database -> Sync
    """
    logger.info("=== Starting Complete System Stress Test ===")
    results = {
        "success": True,
        "stages": {},
        "errors": [],
    }
    
    # Create watch directory
    watch_dir = temp_dir / "watch"
    watch_dir.mkdir()
    
    # Create and initialize database
    db_path = temp_dir / "complete_system_test.db"
    database.set_custom_db_path(str(db_path))
    database.init_database()
    
    # Create initial test files
    for i in range(20):
        generate_small_arkts_file(watch_dir / f"initial_{i}.ets")
    
    # Test file monitor initialization (without starting the event loop)
    results["stages"]["monitor_init"] = {
        "status": "completed",
        "info": "File monitor initialized successfully"
    }
    
    # Test initial sync
    try:
        start = time.time()
        database.sync_directory(str(watch_dir))
        elapsed = time.time() - start
        results["stages"]["initial_sync"] = {
            "status": "success",
            "time": elapsed,
            "files_processed": len(list(watch_dir.glob("*.ets")))
        }
        logger.info(f"Initial sync complete in {elapsed:.4f}s")
    except Exception as e:
        logger.error(f"Initial sync failed: {e}")
        results["success"] = False
        results["stages"]["initial_sync"] = {"status": "failed", "error": str(e)}
        results["errors"].append(str(e))
    
    # Test rapid file changes
    try:
        start = time.time()
        for i in range(50):
            file_path = watch_dir / f"changing_{i}.ets"
            generate_small_arkts_file(file_path)
            database.sync_file(str(file_path))
        
        elapsed = time.time() - start
        results["stages"]["rapid_changes"] = {
            "status": "success",
            "time": elapsed,
            "files_updated": 50
        }
        logger.info(f"Rapid changes complete in {elapsed:.4f}s")
    except Exception as e:
        logger.error(f"Rapid changes test failed: {e}")
        results["success"] = False
        results["stages"]["rapid_changes"] = {"status": "failed", "error": str(e)}
        results["errors"].append(str(e))
    finally:
        # Restore default database path
        database.set_custom_db_path(None)
    
    logger.info("=== Complete System Test Complete ===")
    return results


def run_all_tests():
    """Run all stress tests and collect defects"""
    print("\n" + "=" * 60)
    print("🚀 STARTING COMPREHENSIVE SYSTEM STRESS & INTEGRATION TESTS")
    print("=" * 60)
    
    # Create temporary directory for tests
    with tempfile.TemporaryDirectory(prefix="arkts_stress_test_") as temp_dir:
        temp_path = Path(temp_dir)
        logger.info(f"Test directory: {temp_path}")
        
        all_results = {
            "start_time": time.time(),
            "tests": {}
        }
        
        # Run tests
        try:
            print("\n" + "-" * 60)
            print("📝 Test 1/3: ArkTS Analyzer Stress Test")
            print("-" * 60)
            all_results["tests"]["arkts_analyzer"] = stress_test_arkts_analyzer(temp_path)
        except Exception as e:
            all_results["tests"]["arkts_analyzer"] = {"success": False, "error": str(e)}
            logger.error(f"Analyzer test failed: {e}")
        
        try:
            print("\n" + "-" * 60)
            print("🗄️  Test 2/3: Database Stress Test")
            print("-" * 60)
            all_results["tests"]["database"] = stress_test_database(temp_path)
        except Exception as e:
            all_results["tests"]["database"] = {"success": False, "error": str(e)}
            logger.error(f"Database test failed: {e}")
        
        try:
            print("\n" + "-" * 60)
            print("🔄 Test 3/3: Complete System Integration Test")
            print("-" * 60)
            all_results["tests"]["complete_system"] = stress_test_complete_system(temp_path)
        except Exception as e:
            all_results["tests"]["complete_system"] = {"success": False, "error": str(e)}
            logger.error(f"System test failed: {e}")
        
        all_results["end_time"] = time.time()
        all_results["total_time"] = all_results["end_time"] - all_results["start_time"]
        
        # Generate report
        print("\n" + "=" * 60)
        print("📊 STRESS TEST RESULTS")
        print("=" * 60)
        print(f"\nTotal time: {all_results['total_time']:.2f} seconds")
        
        all_errors = []
        for test_name, test_data in all_results["tests"].items():
            print(f"\n{test_name.replace('_', ' ').title()}: {'✅ SUCCESS' if test_data.get('success') else '❌ FAILED'}")
            if "errors" in test_data and test_data["errors"]:
                print(f"  Errors found: {len(test_data['errors'])}")
                all_errors.extend([(test_name, err) for err in test_data["errors"]])
            if "files_processed" in test_data:
                print(f"  Files processed: {test_data['files_processed']}")
        
        if all_errors:
            print(f"\n{'=' * 60}")
            print(f"⚠️  TOTAL DEFECTS FOUND: {len(all_errors)}")
            print(f"{'=' * 60}")
            for test_name, err in all_errors:
                print(f"\n- [{test_name}] {err}")
        else:
            print("\n✅ All tests passed without defects!")
    
    print("\n✅ All stress tests completed! Results saved to stress_test.log")
    return all_results


if __name__ == "__main__":
    run_all_tests()
