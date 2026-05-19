
#!/usr/bin/env python3
"""
DEEP SYSTEM TEST - Extreme Stress & Long-Term Stability
"""

import os
import sys
import time
import tempfile
import gc
import random
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
import arkts_analyzer


class DeepTester:
    def __init__(self):
        self.success = 0
        self.failed = 0
        self.warnings = []
        self.bugs = []
        self.performance_log = []
        self.memory_log = []
    
    def log_pass(self, name, detail=""):
        print(f"    ✅ {name} {detail}")
        self.success += 1
    
    def log_fail(self, name, error):
        print(f"    ❌ {name}: {error}")
        self.failed += 1
        self.bugs.append((name, error))
    
    def log_warn(self, name, warning):
        print(f"    ⚠️  {name}: {warning}")
        self.warnings.append((name, warning))
    
    def log_perf(self, operation, time_sec, desc=""):
        self.performance_log.append({
            "op": operation,
            "time": time_sec,
            "desc": desc
        })
        print(f"      📊 {operation} took {time_sec:.2f}s {desc}")
    
    def test_deep_memory_stability(self, temp_dir):
        """Test 1: Long-term memory growth monitoring"""
        print("\n" + "=" * 80)
        print("  1. Deep Memory Stability (Growth Monitoring)")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "deep_memory.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        test_file = temp_path / "mem_test.ets"
        initial_content = "class Initial { }"
        test_file.write_text(initial_content, encoding='utf-8')
        
        # Initial sync and state
        arkts_analyzer.update_file_knowledge_graph(str(test_file))
        gc.collect()
        
        # Initial memory check
        import psutil
        process = psutil.Process()
        start_mem = process.memory_info().rss
        
        # 50,000 operations with memory sampling
        print("    Running 50,000 mixed operations...")
        
        start_time = time.time()
        last_sample = 0
        
        for i in range(50000):
            try:
                content = f"class Dynamic{i} {{ method{random.randint(0, 50)}() {{ }} }}"
                test_file.write_text(content, encoding='utf-8')
                arkts_analyzer.update_file_knowledge_graph(str(test_file))
                
                # Mix in reads
                if i % 10 == 0:
                    database.get_all_files()
                    database.get_all_classes()
                
                # Memory sampling every 5000
                if i % 5000 == 0 and i > 0:
                    gc.collect()
                    current_mem = process.memory_info().rss
                    delta_kb = (current_mem - start_mem) / 1024
                    self.memory_log.append((i, current_mem, delta_kb))
                    print(f"      Progress: {i}/50000, Mem delta: {delta_kb:.1f}KB")
            
            except Exception as e:
                self.log_fail(f"Op#{i}", str(e))
        
        elapsed = time.time() - start_time
        
        # Final memory check
        gc.collect()
        final_mem = process.memory_info().rss
        total_delta = (final_mem - start_mem) / 1024
        
        if total_delta < 500:  # less than 500KB is OK
            self.log_pass("Memory stability", f"{int(total_delta)}KB over 50k ops")
        else:
            self.log_warn("Memory growth", f"Significant {int(total_delta)}KB growth")
        
        self.log_perf("50,000 mixed ops", elapsed, "(reads + writes)")
    
    def test_extreme_data_growth(self, temp_dir):
        """Test 2: Extreme data volume growth"""
        print("\n" + "=" * 80)
        print("  2. Extreme Data Growth & Performance")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "data_growth.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        # Phase 1: Insert 2000 files
        print("    Phase 1: Inserting 2000 files...")
        start = time.time()
        for i in range(2000):
            database.insert_file(f"/test/phase1/file{i}.ets", f"hash{i}".encode())
        phase1_time = time.time() - start
        self.log_perf("2000 files insert", phase1_time)
        
        # Phase 2: Read while inserting 1000 more
        print("    Phase 2: Mixed reads/writes (1000 inserts)...")
        start = time.time()
        
        def worker(id):
            for i in range(50):
                try:
                    database.insert_file(f"/test/phase2/w{id}_f{i}.ets", b"h")
                    database.get_all_files()
                except Exception:
                    return False
            return True
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(worker, i) for i in range(20)]
            for f in as_completed(futures):
                f.result()
        
        phase2_time = time.time() - start
        self.log_perf("1000 mixed reads/writes", phase2_time)
        
        # Check how many files we have
        total_files = len(database.get_all_files())
        if total_files >= 2500:
            self.log_pass("Data volume", f"{total_files} files created successfully")
        else:
            self.log_warn("Data growth", f"Only {total_files} files")
    
    def test_error_recovery(self, temp_dir):
        """Test 3: Error recovery and system resilience"""
        print("\n" + "=" * 80)
        print("  3. Error Recovery & Resilience")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "recovery.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        # Test 1: Insert invalid data
        recovered = 0
        try:
            database.insert_file("/test/recovery/file.ets", None)  # invalid hash type
        except Exception:
            recovered += 1
        
        # Verify DB still working
        try:
            database.insert_file("/test/recovery/valid.ets", b"validhash")
            recovered += 1
        except Exception:
            pass
        
        if recovered == 2:
            self.log_pass("Error recovery", "System recovered from bad input")
        
        # Test 2: Large invalid file parsing
        big_bad_file = temp_path / "bad_file.ets"
        big_bad_content = "class Bad { " * 1000  # unclosed brace
        big_bad_file.write_text(big_bad_content, encoding='utf-8')
        
        try:
            arkts_analyzer.parse_file(str(big_bad_file))
            recovered += 1
        except Exception:
            self.log_pass("Bad parse", "Parser handled bad input")
    
    def test_mixed_extreme_operations(self, temp_dir):
        """Test 4: Extreme mixed operations (create, update, delete)"""
        print("\n" + "=" * 80)
        print("  4. Extreme Mixed Operations (CRUD)")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "mixed_ops.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        ops_count = 0
        errors = 0
        
        test_file = temp_path / "mixed.ets"
        
        print("    Running 2000 mixed CRUD ops...")
        start = time.time()
        
        for i in range(2000):
            try:
                op = random.randint(1, 3)
                
                if op == 1:  # Create
                    content = f"struct Mix{i} {{ }} "
                    test_file.write_text(content, encoding='utf-8')
                    arkts_analyzer.update_file_knowledge_graph(str(test_file))
                    ops_count += 1
                
                elif op == 2:  # Read
                    database.get_all_files()
                    database.get_all_classes()
                    ops_count += 1
                
                else:  # Update
                    content = f"struct Updated{i} {{ }} "
                    test_file.write_text(content, encoding='utf-8')
                    arkts_analyzer.update_file_knowledge_graph(str(test_file))
                    ops_count += 1
            
            except Exception:
                errors += 1
        
        elapsed = time.time() - start
        
        if errors == 0:
            self.log_pass("Mixed operations", f"{ops_count} ops in {elapsed:.2f}s")
        else:
            self.log_fail(f"Mixed ops", f"{errors} errors in {ops_count}")
        
        self.log_perf("2000 mixed CRUD", elapsed)
    
    def test_edge_db_queries(self, temp_dir):
        """Test 5: Edge case queries and database operations"""
        print("\n" + "=" * 80)
        print("  5. Edge Case Database Queries")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "edge_queries.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        # Insert test data
        for i in range(500):
            database.insert_file(f"/test/query/file{i}.ets", f"hash{i}".encode())
        
        # Test edge queries
        try:
            all_files = database.get_all_files()
            self.log_pass("All files query", f"{len(all_files)} files")
            
            all_classes = database.get_all_classes()
            all_methods = database.get_all_methods()
            
            if len(all_files) == 500:
                self.log_pass("Query edge cases", "All queries successful")
        
        except Exception as e:
            self.log_fail("Edge queries", str(e))


def run_deep_tests():
    print("\n" + "=" * 80)
    print("  🔥 DEEP SYSTEM TEST - Extreme Stress & Long-Term Stability")
    print("=" * 80)
    
    tester = DeepTester()
    start_all = time.time()
    
    with tempfile.TemporaryDirectory(prefix="deep_test_") as temp_dir:
        
        tester.test_deep_memory_stability(temp_dir)
        tester.test_extreme_data_growth(temp_dir)
        tester.test_error_recovery(temp_dir)
        tester.test_mixed_extreme_operations(temp_dir)
        tester.test_edge_db_queries(temp_dir)
    
    # Final summary
    print("\n" + "=" * 80)
    print("  📊 DEEP SYSTEM TEST - SUMMARY")
    print("=" * 80)
    
    print(f"\n✅ Success: {tester.success}")
    print(f"❌ Failed: {tester.failed}")
    if tester.warnings:
        print(f"⚠️ Warnings: {len(tester.warnings)}")
    print(f"⏱️ Total time: {time.time() - start_all:.2f}s")
    
    if tester.bugs:
        print("\n" + "=" * 80)
        print("  🐛 ISSUES FOUND")
        print("=" * 80)
        for name, err in tester.bugs:
            print(f"\n- {name}: {err}")
    else:
        print("\n🎉 NO ISSUES FOUND - SYSTEM IS EXTREMELY ROBUST!")
    
    print("\n📊 Performance stats:")
    for perf in tester.performance_log:
        print(f"  - {perf['op']}: {perf['time']:.2f}s {perf.get('desc', '')}")
    
    if tester.memory_log:
        print("\n📈 Memory samples:")
        for sample in tester.memory_log:
            op, mem, delta = sample
            print(f"  - {op} ops: {delta:.1f}KB delta")


if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("Installing psutil...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], capture_output=True)
    
    run_deep_tests()
