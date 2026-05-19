
#!/usr/bin/env python3
"""
QUICKER EXTREME STRESS TEST - Still challenging but faster!
"""

import os
import sys
import time
import tempfile
import gc
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
import arkts_analyzer


class QuickExtremeTester:
    def __init__(self):
        self.success = 0
        self.failed = 0
        self.warnings = []
        self.bugs = []
    
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
    
    def test_large_file_quick(self, temp_dir):
        print("\n" + "=" * 80)
        print("  1. Large File Test (1000 classes)")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        big_file = temp_path / "large_1000.ets"
        
        content = []
        for i in range(1000):
            content.append(f"struct Component{i} {{ build() {{ }} }}")
        
        big_file.write_text("\n".join(content), encoding='utf-8')
        
        print(f"    File: {big_file.stat().st_size / 1024:.2f} KB")
        
        start = time.time()
        parsed = arkts_analyzer.parse_file(str(big_file))
        elapsed = time.time() - start
        
        if len(parsed['classes']) >= 900:
            self.log_pass("Large file", f"{len(parsed['classes'])} classes in {elapsed:.2f}s")
        else:
            self.log_fail("Large file parsing", f"Only got {len(parsed['classes'])}")
    
    def test_concurrency_quick(self, temp_dir):
        print("\n" + "=" * 80)
        print("  2. Extreme Concurrency (200 threads)")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "quick_concurrent.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        def do_work(id):
            for _ in range(5):
                try:
                    database.insert_file(f"/test/quick{id}.ets", b"hash")
                    database.get_all_files()
                except Exception:
                    return False
            return True
        
        print("    Starting 200 threads...")
        start = time.time()
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(do_work, i) for i in range(200)]
            done = sum(f.result() for f in as_completed(futures))
        
        elapsed = time.time() - start
        if done == 200:
            self.log_pass("Concurrency", f"{done} threads in {elapsed:.2f}s")
        else:
            self.log_fail("Concurrency", f"Only {done}/200 passed")
        
        database.set_custom_db_path(None)
    
    def test_stability_quick(self, temp_dir):
        print("\n" + "=" * 80)
        print("  3. Stability (10000 operations)")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        db_path = temp_path / "quick_stability.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        test_file = temp_path / "stability.ets"
        
        errors = 0
        print("    Running 10000 operations...")
        for i in range(10000):
            try:
                content = f"class QuickTest{i} {{ }} "
                test_file.write_text(content, encoding='utf-8')
                arkts_analyzer.update_file_knowledge_graph(str(test_file))
                database.get_all_files()
            
            except Exception:
                errors += 1
        
        if errors == 0:
            self.log_pass("Stability test", "10000 operations, 0 errors")
        else:
            self.log_fail(f"Stability test", f"{errors} errors")
        
        database.set_custom_db_path(None)
    
    def test_complex_syntax(self, temp_dir):
        print("\n" + "=" * 80)
        print("  4. Complex Syntax Handling")
        print("=" * 80)
        
        temp_path = Path(temp_dir)
        
        test_cases = [
            """@Component @Entry struct Main { @State a=1 build() { } }""",
            """class Complex { method1(a:number) { for(let i=0;i<10;i++){ if(i>5) {console.log(i) } } } }"""
        ]
        
        for i, content in enumerate(test_cases):
            f = temp_path / f"test{i}.ets"
            f.write_text(content, encoding='utf-8')
            try:
                arkts_analyzer.parse_file(str(f))
                self.log_pass(f"Syntax test #{i+1}", "Complex syntax")
            except Exception as e:
                self.log_fail(f"Syntax case #{i+1}", str(e))


def run_tests():
    print("\n" + "=" * 80)
    print("  🚀 QUICK EXTREME STRESS TEST")
    print("=" * 80)
    
    tester = QuickExtremeTester()
    start_all = time.time()
    
    with tempfile.TemporaryDirectory(prefix="quick_test_") as temp_dir:
        
        tester.test_large_file_quick(temp_dir)
        tester.test_concurrency_quick(temp_dir)
        tester.test_stability_quick(temp_dir)
        tester.test_complex_syntax(temp_dir)
    
    # Summary
    print("\n" + "=" * 80)
    print("  📊 QUICK TEST SUMMARY")
    print("=" * 80)
    
    print(f"\n✅  ✅ Success: {tester.success}")
    print(f"    ❌ Failed: {tester.failed}")
    print(f"    ⏱️  Total time: {time.time() - start_all:.2f}s")
    
    if tester.bugs:
        print("\n" + "=" * 80)
        print("  🐛 ISSUES FOUND")
        print("=" * 80)
        for name, err in tester.bugs:
            print(f"\n- {name}: {err}")
    else:
        print("\n🎉 NO ISSUES FOUND!")


if __name__ == "__main__":
    run_tests()
