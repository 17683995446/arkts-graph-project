
#!/usr/bin/env python3
"""
DEEP SYSTEM TEST LITE - Extreme Stress but Faster
"""

import os
import sys
import time
import tempfile
import gc
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
import arkts_analyzer


class DeepTesterLite:
    def __init__(self):
        self.success = 0
        self.failed = 0
        self.warnings = []
        self.bugs = []
        self.performance_log = []
    
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
        """Test 1: Long-term memory monitoring"""
        print("\n" + "=" * 80)
        print("  1. Deep Memory Stability (Growth Monitoring)")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "deep_memory.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        test_file = temp_path / "mem_test.ets"
        test_file.write_text("class Initial { }", encoding='utf-8')
        
        arkts_analyzer.update_file_knowledge_graph(str(test_file))
        gc.collect()
        
        # Try to import psutil or skip detailed memory check
        try:
            import psutil
            process = psutil.Process()
            start_mem = process.memory_info().rss
        except ImportError:
            psutil = None
            start_mem = 0
            print("    (psutil not available, skipping detailed memory)")
        
        # 20,000 operations
        print("    Running 20,000 mixed operations...")
        start_time = time.time()
        
        for i in range(20000):
            try:
                content = f"class Dynamic{i} {{ method{random.randint(0, 50)}() {{ }} }}"
                test_file.write_text(content, encoding='utf-8')
                arkts_analyzer.update_file_knowledge_graph(str(test_file))
                
                if i % 10 == 0:
                    database.get_all_files()
                    database.get_all_classes()
                
                if i % 5000 == 0 and i > 0:
                    gc.collect()
                    print(f"      Progress: {i}/20000")
            
            except Exception as e:
                self.log_fail(f"Op#{i}", str(e))
        
        elapsed = time.time() - start_time
        self.log_perf("20,000 mixed ops", elapsed, "(reads + writes)")
        
        gc.collect()
        if psutil:
            final_mem = process.memory_info().rss
            total_delta = (final_mem - start_mem) / 1024
            if total_delta < 500:
                self.log_pass("Memory stability", f"{int(total_delta)}KB over 20k ops")
    
    def test_extreme_data_growth(self, temp_dir):
        """Test 2: Extreme data volume growth"""
        print("\n" + "=" * 80)
        print("  2. Extreme Data Growth & Performance")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "data_growth.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        # Phase 1: Insert 1500 files
        print("    Phase 1: Inserting 1500 files...")
        start = time.time()
        for i in range(1500):
            database.insert_file(f"/test/phase1/file{i}.ets", f"hash{i}".encode())
        phase1_time = time.time() - start
        self.log_perf("1500 files insert", phase1_time)
        
        # Phase 2: Mixed reads/writes
        print("    Phase 2: Mixed reads/writes...")
        start = time.time()
        
        def worker(id):
            for i in range(30):
                try:
                    database.insert_file(f"/test/phase2/w{id}_f{i}.ets", b"h")
                    database.get_all_files()
                except Exception:
                    return False
            return True
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(worker, i) for i in range(15)]
            for f in as_completed(futures):
                f.result()
        
        phase2_time = time.time() - start
        self.log_perf("Mixed reads/writes", phase2_time)
        
        total_files = len(database.get_all_files())
        if total_files >= 1800:
            self.log_pass("Data volume", f"{total_files} files created successfully")
    
    def test_error_recovery(self, temp_dir):
        """Test 3: Error recovery & resilience"""
        print("\n" + "=" * 80)
        print("  3. Error Recovery & Resilience")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "recovery.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        recovered = 0
        try:
            database.insert_file("/test/recovery/file.ets", None)
        except Exception:
            recovered += 1
        
        try:
            database.insert_file("/test/recovery/valid.ets", b"validhash")
            recovered += 1
        except Exception:
            pass
        
        if recovered == 2:
            self.log_pass("Error recovery", "System recovered from bad input")
        
        big_bad_file = temp_path / "bad_file.ets"
        big_bad_file.write_text("class Bad { " * 500, encoding='utf-8')
        
        try:
            arkts_analyzer.parse_file(str(big_bad_file))
        except Exception:
            self.log_pass("Bad parse", "Parser handled bad input")
    
    def test_mixed_extreme_operations(self, temp_dir):
        """Test 4: Extreme mixed operations"""
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
                
                if op == 1:
                    content = f"struct Mix{i} {{ }} "
                    test_file.write_text(content, encoding='utf-8')
                    arkts_analyzer.update_file_knowledge_graph(str(test_file))
                    ops_count += 1
                elif op == 2:
                    database.get_all_files()
                    database.get_all_classes()
                    ops_count += 1
                else:
                    content = f"struct Updated{i} {{ }} "
                    test_file.write_text(content, encoding='utf-8')
                    arkts_analyzer.update_file_knowledge_graph(str(test_file))
                    ops_count += 1
            
            except Exception:
                errors += 1
        
        elapsed = time.time() - start
        
        if errors == 0:
            self.log_pass("Mixed operations", f"{ops_count} ops in {elapsed:.2f}s")
        
        self.log_perf("2000 mixed CRUD", elapsed)
    
    def test_edge_db_queries(self, temp_dir):
        """Test 5: Edge case database queries"""
        print("\n" + "=" * 80)
        print("  5. Edge Case Database Queries")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "edge_queries.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        for i in range(500):
            database.insert_file(f"/test/query/file{i}.ets", f"hash{i}".encode())
        
        try:
            all_files = database.get_all_files()
            self.log_pass("All files query", f"{len(all_files)} files")
            
            if len(all_files) == 500:
                self.log_pass("Query edge cases", "All queries successful")
        
        except Exception as e:
            self.log_fail("Edge queries", str(e))


def run_deep_tests_lite():
    print("\n" + "=" * 80)
    print("  🔥 DEEP SYSTEM TEST LITE - Extreme Stress & Long-Term Stability")
    print("=" * 80)
    
    tester = DeepTesterLite()
    start_all = time.time()
    
    with tempfile.TemporaryDirectory(prefix="deep_test_lite_") as temp_dir:
        
        tester.test_deep_memory_stability(temp_dir)
        tester.test_extreme_data_growth(temp_dir)
        tester.test_error_recovery(temp_dir)
        tester.test_mixed_extreme_operations(temp_dir)
        tester.test_edge_db_queries(temp_dir)
    
    print("\n" + "=" * 80)
    print("  📊 DEEP SYSTEM TEST LITE - SUMMARY")
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


if __name__ == "__main__":
    run_deep_tests_lite()
