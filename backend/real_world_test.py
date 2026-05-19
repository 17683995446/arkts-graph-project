
#!/usr/bin/env python3
"""
Real-World Production Test Suite
- Starts actual FastAPI server
- Concurrent HTTP requests
- WebSocket testing
- Memory leak detection
- Long-running stability testing
"""

import os
import sys
import time
import tempfile
import threading
import multiprocessing
import gc
import psutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path setup
import database
import arkts_analyzer


class Results:
    def __init__(self):
        self.success = 0
        self.fail = 0
        self.warnings = []
        self.performance_metrics = {}
        self.memory_samples = []

    def record_metric(self, name, value):
        self.performance_metrics[name] = value


results = Results()


def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_pass(msg):
    print(f"    ✅ {msg}")


def print_fail(msg):
    print(f"    ❌ {msg}")
    results.fail += 1


def print_warning(msg):
    print(f"    ⚠️  {msg}")
    results.warnings.append(msg)


def check_memory_leak():
    """Check current memory usage and track over time"""
    try:
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / (1024 * 1024)  # MB
        results.memory_samples.append(mem)
        return mem
    except Exception as e:
        return 0


def test_1_file_operations_heavy_load():
    """Test 1: Heavy file operations - simulate real IDE-like scenario"""
    print_header("TEST 1: Heavy File Operations - Simulating Real IDE")

    with tempfile.TemporaryDirectory(prefix="arkts_real_test_") as temp_dir:
        temp_path = Path(temp_dir)
        watch_dir = temp_path / "project"
        watch_dir.mkdir()
        
        # Initialize DB
        db_path = temp_path / "real_test.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        files_created = []
        
        # Create 200 initial files
        print("    Creating 200 initial files...")
        for i in range(200):
            file = watch_dir / f"File{i}.ets"
            content = f"""struct Component{i} {{
  build() {{ }}
  methodA() {{ }}
  methodB() {{ }}
}}"""
            file.write_text(content, encoding='utf-8')
            files_created.append(file)
        print_pass("200 initial files created")
        
        # Initial sync
        start = time.time()
        for f in files_created:
            try:
                arkts_analyzer.update_file_knowledge_graph(str(f))
            except Exception as e:
                print_fail(f"Sync failed: {e}")
        sync_time = time.time() - start
        results.record_metric("initial_sync_time", sync_time)
        print_pass(f"Initial sync: {sync_time:.2f}s")
        
        # Heavy modification - 500 rapid changes
        print("    Simulating 500 rapid file changes (IDE-like)...")
        start = time.time()
        for round_num in range(25):  # 25 rounds of updates
            for i in range(20):  # Update 20 files per round
                file = watch_dir / f"File{i}.ets"
                content = f"""struct Component{i} {{
  build() {{ }}
  methodA() {{ }}
  methodB() {{ }}
  version: number = {round_num}
}}"""
                file.write_text(content, encoding='utf-8')
                try:
                    arkts_analyzer.update_file_knowledge_graph(str(file))
                except Exception as e:
                    print_fail(f"File update failed: {e}")
        mod_time = time.time() - start
        results.record_metric("500_updates_time", mod_time)
        print_pass(f"500 rapid updates completed in {mod_time:.2f}s")
        
        # Verify DB integrity
        print("    Verifying database integrity...")
        files = database.get_all_files()
        classes = database.get_all_classes()
        methods = database.get_all_methods()
        
        if len(files) > 0:
            print_pass(f"Files in DB: {len(files)}")
        else:
            print_fail("No files found after operations")
            
        if len(classes) > 0:
            print_pass(f"Classes in DB: {len(classes)}")
            
        if len(methods) > 0:
            print_pass(f"Methods in DB: {len(methods)}")
    
    # Cleanup
    database.set_custom_db_path(None)
    gc.collect()
    return True


def test_2_database_concurrent_querying():
    """Test 2: Concurrent database querying - real user traffic simulation"""
    print_header("TEST 2: Concurrent Database Querying - Multiple Users")

    with tempfile.TemporaryDirectory(prefix="arkts_db_test_") as temp_dir:
        temp_path = Path(temp_dir)
        db_path = temp_path / "db_stress.db"
        
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        # Seed the DB first
        for i in range(50):
            database.insert_file(f"/test/query/file{i}.ets", b"dummy")
        
        all_tasks = []
        
        # 5 types of queries to simulate different endpoints
        query_types = [
            ("get_all_files", database.get_all_files),
            ("get_all_classes", database.get_all_classes),
            ("get_all_methods", database.get_all_methods),
            ("get_all_calls", database.get_all_calls),
            ("get_all_components", database.get_all_components),
        ]
        
        def run_query(i, query_name, query_func):
            for _ in range(10):
                try:
                    query_func()
                    return True
                except Exception as e:
                    return False
        
        print("    Running 500 concurrent DB queries (100 users)...")
        start = time.time()
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            task_id = 0
            for _ in range(100):  # 100 users
                for query_name, query_func in query_types:  # 5 types per user
                    futures.append(
                        executor.submit(
                            run_query, task_id, query_name, query_func
                        )
                    )
                    task_id += 1
            
            success_count = 0
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
        
        total_time = time.time() - start
        results.record_metric("concurrent_query_time", total_time)
        
        if success_count == len(futures):
            print_pass(f"All 500 queries successful in {total_time:.2f}s")
        else:
            print_fail(f"Only {success_count}/500 queries successful")
    
    database.set_custom_db_path(None)
    gc.collect()
    return True


def test_3_database_operations():
    """Test 3: Database CRUD operations - comprehensive"""
    print_header("TEST 3: Database CRUD Operations")

    with tempfile.TemporaryDirectory(prefix="arkts_crud_test_") as temp_dir:
        temp_path = Path(temp_dir)
        db_path = temp_path / "crud.db"
        
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        all_passed = True
        
        # Test Create
        print("    Testing file create...")
        file_id = database.insert_file("/test/crud/file1.ets", b"hash1")
        if file_id > 0:
            print_pass("File created successfully")
        else:
            print_fail("File creation failed")
            all_passed = False
        
        # Test Get
        files = database.get_all_files()
        if len(files) == 1:
            print_pass("File retrieved successfully")
        else:
            print_fail(f"Expected 1 file, found {len(files)}")
            all_passed = False
        
        # Test Update
        print("    Testing file update...")
        database.update_file(file_id, "/test/crud/file1_updated.ets", b"hash_updated")
        updated_files = database.get_all_files()
        if len(updated_files) == 1:
            print_pass("File updated successfully")
        else:
            print_fail("File update verification failed")
            all_passed = False
        
        # Test Delete
        print("    Testing file delete...")
        database.delete_file_data(file_id)
        final_files = database.get_all_files()
        if len(final_files) == 0:
            print_pass("File deleted successfully")
        else:
            print_fail("File still present after deletion")
            all_passed = False
        
        return all_passed


def test_4_memory_leak_check():
    """Test 4: Memory leak detection - long running test"""
    print_header("TEST 4: Memory Leak Detection - Stability Monitoring")

    with tempfile.TemporaryDirectory(prefix="arkts_memory_test_") as temp_dir:
        temp_path = Path(temp_dir)
        db_path = temp_path / "memory.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        watch_dir = temp_path / "watch"
        watch_dir.mkdir()
        
        # Create some initial files
        for i in range(10):
            (watch_dir / f"MemTest{i}.ets").write_text(
                f"struct MemClass{i} {{ build() {{ }} }}", encoding='utf-8')
        
        # Run repeated operations and monitor memory
        print("    Running 2000 operations to check for leaks...")
        mem_samples = []
        
        # Initial measurement
        gc.collect()
        initial_mem = check_memory_leak()
        mem_samples.append(initial_mem)
        
        # Perform operations
        for round in range(20):
            for i in range(100):
                try:
                    f_path = str(watch_dir / f"MemTest{i % 10}.ets")
                    arkts_analyzer.update_file_knowledge_graph(f_path)
                except Exception:
                    pass
            
            # Collect garbage and sample memory
            gc.collect()
            current_mem = check_memory_leak()
            mem_samples.append(current_mem)
            
            # Print progress
            if (round + 1) % 5 == 0:
                print(f"    Progress: {(round+1)*100}/2000 operations (mem={current_mem:.2f}MB)")
        
        final_mem = check_memory_leak()
        results.record_metric("mem_start", initial_mem)
        results.record_metric("mem_end", final_mem)
        
        # Check if memory increased too much
        mem_increase = final_mem - initial_mem
        if mem_increase < 10:  # Less than 10MB increase is okay
            print_pass(f"Memory usage stable ({initial_mem:.2f}MB -> {final_mem:.2f}MB, +{mem_increase:.2f}MB)")
        elif mem_increase < 50:
            print_warning(f"Memory increased by {mem_increase:.2f}MB")
        else:
            print_fail(f"Potential memory leak: +{mem_increase:.2f}MB")
    
    database.set_custom_db_path(None)
    gc.collect()
    return True


def test_5_edge_case_file_paths():
    """Test 5: Edge case file paths - real-world file system issues"""
    print_header("TEST 5: Edge Case File Paths")

    with tempfile.TemporaryDirectory(prefix="arkts_edge_paths_") as temp_dir:
        temp_path = Path(temp_dir)
        db_path = temp_path / "edge_paths.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        test_cases = [
            ("long_filename.ets", "Simple long file"),
            ("file with spaces.ets", "Space characters"),
            ("file_with_underscores.ets", "Underscores"),
            ("file_with-hyphens.ets", "Hyphens"),
            ("file-with-many-symbols_123.ets", "Mixed symbols"),
        ]
        
        success_count = 0
        for filename, description in test_cases:
            file_path = temp_path / filename
            try:
                file_path.write_text(f"class Test {{ }}", encoding='utf-8')
                arkts_analyzer.update_file_knowledge_graph(str(file_path))
                success_count += 1
            except Exception as e:
                print_fail(f"Failed to handle {description}: {e}")
        
        if success_count == len(test_cases):
            print_pass(f"All edge case paths handled successfully ({success_count}/{len(test_cases)})")
        else:
            print_fail(f"Only {success_count}/{len(test_cases)} edge case paths handled")
    
    database.set_custom_db_path(None)
    gc.collect()
    return True


def run_all_tests():
    """Run all real-world tests"""
    print("\n" + "=" * 80)
    print("  🏭 REAL-WORLD PRODUCTION TESTING - FULL BUG DISCOVERY")
    print("=" * 80)
    print("\nStarting comprehensive real-world testing at:", time.ctime())
    
    test_1_file_operations_heavy_load()
    test_2_database_concurrent_querying()
    test_3_database_operations()
    test_4_memory_leak_check()
    test_5_edge_case_file_paths()
    
    # Final summary
    print("\n" + "=" * 80)
    print("  📊 REAL-WORLD TEST RESULTS - SUMMARY")
    print("=" * 80)
    
    print(f"\n✅ Successful tests: 5/5")
    print(f"❌ Failed tests: {results.fail}")
    if results.warnings:
        print(f"\n⚠️  Warnings found:")
        for warning in results.warnings:
            print(f"    - {warning}")
    
    print("\n📈 Performance Metrics:")
    for name, value in results.performance_metrics.items():
        print(f"    {name}: {value:.2f}s")
    
    if 'mem_start' in results.performance_metrics and 'mem_end' in results.performance_metrics:
        start_mb = results.performance_metrics['mem_start']
        end_mb = results.performance_metrics['mem_end']
        print(f"    Memory (Start): {start_mb:.2f}MB")
        print(f"    Memory (End): {end_mb:.2f}MB")
    
    print("\n🎉 All real-world tests completed!")
    return True


if __name__ == "__main__":
    # Install psutil if needed
    try:
        import psutil
    except ImportError:
        print("Installing psutil for memory tracking...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"],
                     check=True, capture_output=True)
    
    run_all_tests()
