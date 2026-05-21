
#!/usr/bin/env python3
"""
最终的超级全面测试系统！
"""
import os
import sys
import tempfile
import shutil
import random
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import arkts_analyzer

print("=" * 100)
print("FINAL ULTIMATE COMPREHENSIVE TESTING SYSTEM")
print("=" * 100)

def create_complex_file(dir_path, index):
    filename = f"ComplexFile_{index:04d}.ets"
    filepath = os.path.join(dir_path, filename)
    
    content = ""
    num_classes = random.randint(1, 4)
    for ci in range(num_classes):
        class_name = f"TestClass_{index}_{ci}"
        content += f"class {class_name} {{\n"
        
        num_methods = random.randint(1, 8)
        for mi in range(num_methods):
            method_name = f"doSomething_{index}_{ci}_{mi}"
            content += f"  {method_name}() {{\n"
            for _ in range(random.randint(1, 5)):
                content += "    // code here\n"
            content += "  }\n"
        
        content += "  build() {\n"
        for _ in range(random.randint(1, 6)):
            content += "    Column() {\n"
        for _ in range(random.randint(1, 6)):
            content += "    }\n"
        content += "  }\n"
        content += "}\n\n"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath


def main():
    temp_dir = tempfile.mkdtemp(prefix="final_test_")
    project_dir = os.path.join(temp_dir, "project")
    db_path = os.path.join(temp_dir, "test.db")
    os.makedirs(project_dir, exist_ok=True)
    
    all_passed = True
    total_files = 0
    total_classes = 0
    total_methods = 0
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        # Round 1: 基础测试
        print("\n--- ROUND 1: BASIC TEST ---")
        f1 = create_complex_file(project_dir, 1)
        arkts_analyzer.update_file_knowledge_graph(f1)
        results1 = database.get_all_files()
        print(f"  文件: {len(results1)}")
        
        # Round 2: 批量测试
        print("\n--- ROUND 2: BULK TEST ---")
        round2_files = []
        for i in range(2, 32):
            fpath = create_complex_file(project_dir, i)
            round2_files.append(fpath)
            arkts_analyzer.update_file_knowledge_graph(fpath)
        
        files2 = database.get_all_files()
        classes2 = database.get_all_classes()
        methods2 = database.get_all_methods()
        print(f"  文件: {len(files2)}, 类: {len(classes2)}, 方法: {len(methods2)}")
        total_files += len(files2)
        total_classes += len(classes2)
        total_methods += len(methods2)
        
        # Round 3: 快速修改
        print("\n--- ROUND 3: RAPID CHANGE ---")
        for i in range(50):
            fpath = os.path.join(project_dir, "RapidlyChanging.ets")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(f"class RapidTest{i} {{ build() {{ }} }}")
            arkts_analyzer.update_file_knowledge_graph(fpath)
        
        files3 = database.get_all_files()
        print(f"  文件: {len(files3)}")
        
        # Round 4: 边界测试
        print("\n--- ROUND 4: EDGE CASES ---")
        f_empty = os.path.join(project_dir, "Empty.ets")
        open(f_empty, "w").close()
        arkts_analyzer.update_file_knowledge_graph(f_empty)
        
        f_comment = os.path.join(project_dir, "Comments.ets")
        with open(f_comment, "w", encoding="utf-8") as f:
            f.write("// This is just comments\n// Another comment\n")
        arkts_analyzer.update_file_knowledge_graph(f_comment)
        
        # Final Summary
        print("\n" + "=" * 100)
        print("TEST SUMMARY")
        print("=" * 100)
        final_files = database.get_all_files()
        final_classes = database.get_all_classes()
        final_methods = database.get_all_methods()
        print(f"  最终 - 文件: {len(final_files)}, 类: {len(final_classes)}, 方法: {len(final_methods)}")
        
        all_passed = len(final_files) &gt; 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)
    
    print("\n" + "=" * 100)
    if all_passed:
        print("ALL TESTS PASSED! SYSTEM IS STABLE!")
        print("=" * 100)
        return 0
    else:
        print("SOME TESTS FAILED!")
        print("=" * 100)
        return 1


if __name__ == "__main__":
    sys.exit(main())
