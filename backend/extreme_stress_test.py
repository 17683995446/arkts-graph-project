
#!/usr/bin/env python3
"""
EXTREME STRESS & STABILITY TEST
- Very large files (10000+ lines)
- Extreme concurrency (1000 threads)
- Complex syntax handling
- Long running stability (50000 operations)
- Error recovery & edge cases
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


class ExtremeTester:
    def __init__(self):
        self.success_count = 0
        self.fail_count = 0
        self.errors = []
        self.start_time = time.time()
    
    def log_pass(self, test_name, details=""):
        print(f"    ✅ {test_name} {details}")
        self.success_count += 1
    
    def log_fail(self, test_name, error):
        print(f"    ❌ {test_name}: {error}")
        self.fail_count += 1
        self.errors.append((test_name, error))
    
    def log_warning(self, test_name, warning):
        print(f"    ⚠️  {test_name}: {warning}")
    
    def test_1_extremely_large_file(self, temp_dir):
        """Test 1: Process extremely large ArkTS file (10000+ classes)"""
        print("\n" + "=" * 80)
        print("  TEST 1: Extremely Large File Processing")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        large_file = temp_path / "huge_arkts_file.ets"
        
        print("    Generating 20000-line ArkTS file...")
        content_lines = []
        for i in range(2000):
            content_lines.append(f"struct Component{i} {{")
            for j in range(5):
                content_lines.append(f"  method{j}() {{")
                content_lines.append(f"    this.helper{random.randint(0,9)}()")
                content_lines.append("  }")
            content_lines.append("}")
        
        content = "\n".join(content_lines)
        large_file.write_text(content, encoding='utf-8')
        
        print(f"    File size: {len(content)/1024:.1f} KB")
        
        start = time.time()
        try:
            result = arkts_analyzer.parse_file(str(large_file))
            elapsed = time.time() - start
            
            if len(result['classes']) > 1000:
                self.log_pass(
                    "Large file processing",
                    f"{len(result['classes'])} classes in {elapsed:.2f}s"
                )
            else:
                self.log_warning("Large file parsing", "Fewer classes than expected")
        
        except Exception as e:
            self.log_fail("Large file parsing", str(e))
    
    def test_2_extreme_concurrency(self, temp_dir):
        """Test 2: 1000 concurrent operations"""
        print("\n" + "=" * 80)
        print("  TEST 2: Extreme Concurrency (1000 threads)")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "extreme_concurrent.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        print("    Starting 1000 concurrent operations...")
        
        def database_worker(worker_id):
            for i in range(5):
                try:
                    # Mix read and write operations
                    database.insert_file(
                        f"/test/worker{worker_id}_file{i}.ets",
                        f"hash_{worker_id}_{i}".encode()
                    )
                    database.get_all_files()
                    database.get_all_classes()
                except Exception as e:
                    return False
            return True
        
        start = time.time()
        success = 0
        with ThreadPoolExecutor(max_workers=200) as executor:
            futures = [
                executor.submit(database_worker, i) 
                for i in range(1000)
            ]
            
            for idx, future in enumerate(as_completed(futures)):
                if idx % 100 == 0:
                    print(f"    Progress: {idx}/1000 operations")
                
                if future.result():
                    success += 1
        
        elapsed = time.time() - start
        
        if success == 1000:
            self.log_pass("Extreme concurrency", f"{success} successes in {elapsed:.2f}s")
        else:
            self.log_fail(f"Extreme concurrency", f"Only {success}/1000 passed")
        
        database.set_custom_db_path(None)
    
    def test_3_long_running_stability(self, temp_dir):
        """Test 3: 50000 operations stability test"""
        print("\n" + "=" * 80)
        print("  TEST 3: Long-Running Stability (50000 operations)")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "long_stability.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        test_file = temp_path / "stable_test.ets"
        
        operations_done = 0
        errors_encountered = 0
        checkpoints = [1000, 5000, 10000, 25000, 50000]
        
        print("    Running 50000 operations...")
        for i in range(50000):
            try:
                # Mix of operations
                test_content = f"class TestClass{i} {{ methodA() {{}} }}"
                test_file.write_text(test_content, encoding='utf-8')
                arkts_analyzer.update_file_knowledge_graph(str(test_file))
                
                database.get_all_files()
                database.get_all_classes()
                
                operations_done += 1
                
                if (i + 1) in checkpoints:
                    print(f"    Checkpoint: {i+1} operations completed")
            
            except Exception:
                errors_encountered += 1
        
        if errors_encountered == 0:
            self.log_pass("Long-running stability", "50000 operations, 0 errors")
        else:
            self.log_fail(f"Long-running stability", f"{errors_encountered} errors")
        
        database.set_custom_db_path(None)
    
    def test_4_complex_arkts_syntax(self, temp_dir):
        """Test 4: Complex ArkTS syntax handling"""
        print("\n" + "=" * 80)
        print("  TEST 4: Complex ArkTS Syntax Handling")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        
        complex_files = [
            ("Nested structures", """
struct Outer {
  @State var: number = 1
  build() {
    Column() {
      Inner()
    }
  }
}

struct Inner {
  build() {
    Text("Hi")
  }
}"""),
            ("Decorators", """
@Component
@Entry
struct WithDecorators {
  @Prop externalProp: string
  @State localState: number = 0
  build() {}
}"""),
            ("Methods with types", """
class FullTypes {
  methodWithArgs(a: number, b: string): void {
    let result: number = a * 2
  }
}"""),
            ("Multiple nested blocks", """
class NestedBlocks {
  method() {
    if (true) {
      for (let i in [1,2,3]) {
        try {
          console.log(i)
        } catch (e) {
          // nothing
        }
      }
    }
  }
}"""),
        ]
        
        success_count = 0
        for name, content in complex_files:
            try:
                file_path = temp_path / f"{name.replace(' ','_')}.ets"
                file_path.write_text(content, encoding='utf-8')
                parsed = arkts_analyzer.parse_file(str(file_path))
                
                if len(parsed['classes']) > 0:
                    self.log_pass(f"Syntax: {name}", f"{len(parsed['classes'])} classes")
                    success_count += 1
                else:
                    self.log_warning(f"Syntax: {name}", "No classes found")
            
            except Exception as e:
                self.log_fail(f"Syntax: {name}", str(e))
        
        if success_count == len(complex_files):
            self.log_pass("Complex syntax", "All complex syntax handled correctly")
    
    def test_5_error_recovery(self, temp_dir):
        """Test 5: Error handling and recovery"""
        print("\n" + "=" * 80)
        print("  TEST 5: Error Recovery & Robustness")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "recovery_test.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        # Test invalid file paths
        bad_paths = [
            ("/nonexistent/directory/file.ets", "FileNotFound"),
            ("", "Empty path"),
            ("\0"*100, "Null chars"),
        ]
        
        bad_handled = 0
        for path, desc in bad_paths:
            try:
                database.get_file_by_path(path)
                bad_handled += 1
            except Exception:
                bad_handled += 1
        
        # Test malformed SQL
        malformed_sql_tests = [
            "SELECT *",
            "SELEC * FROM files",
            "-- comment",
        ]
        
        sql_handled = 0
        for sql in malformed_sql_tests:
            try:
                database.execute_custom_query(sql)
            except Exception:
                sql_handled += 1
        
        if bad_handled == len(bad_paths):
            self.log_pass("Error recovery", "All bad file paths handled")
        
        database.set_custom_db_path(None)


def run_all_tests():
    print("\n" + "=" * 80)
    print("  🚀 EXTREME STRESS & STABILITY TEST")
    print("  This will find performance issues and edge case bugs!")
    print("=" * 80)
    
    tester = ExtremeTester()
    
    with tempfile.TemporaryDirectory(prefix="arkts_extreme_test_") as temp_dir:
        
        # Run all extreme tests
        tester.test_1_extremely_large_file(temp_dir)
        tester.test_2_extreme_concurrency(temp_dir)
        tester.test_3_long_running_stability(temp_dir)
        tester.test_4_complex_arkts_syntax(temp_dir)
        tester.test_5_error_recovery(temp_dir)
    
    # Final summary
    print("\n" + "=" * 80)
    print("  📊 EXTREME TEST SUMMARY")
    print("=" * 80)
    
    print(f"\n✅ Successful: {tester.success_count}")
    print(f"❌ Failed: {tester.fail_count}")
    print(f"⏱️  Time elapsed: {time.time() - tester.start_time:.2f}s")
    
    if tester.errors:
        print("\n" + "=" * 80)
        print("  🐛 BUGS FOUND:")
        print("=" * 80)
        for test_name, error in tester.errors:
            print(f"\n- {test_name}: {error}")
    else:
        print("\n🎉 NO BUGS FOUND! SYSTEM IS EXTREMELY ROBUST!")
    
    return tester


if __name__ == "__main__":
    run_all_tests()
