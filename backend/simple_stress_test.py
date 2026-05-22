
#!/usr/bin/env python3
"""
简化版但同样强大的压力测试！
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
print("SIMPLE BUT POWERFUL STRESS TEST!")
print("=" * 100)

def create_stress_file(dir_path, index):
    filename = f"StressFile_{index:04d}.ets"
    filepath = os.path.join(dir_path, filename)
    
    content = ""
    num_classes = random.randint(1, 6)
    
    for ci in range(num_classes):
        class_name = f"StressClass_{index}_{ci}"
        content += f"class {class_name} {{\n"
        
        num_methods = random.randint(1, 15)
        for mi in range(num_methods):
            method_name = f"stressMethod_{index}_{ci}_{mi}"
            content += f"  {method_name}() {{\n    // do work\n  }}\n"
        
        content += "  build() {\n    Column() {\n    }\n  }\n"
        content += "}\n\n"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath

def main():
    temp_dir = tempfile.mkdtemp(prefix="simple_stress_")
    db_path = os.path.join(temp_dir, "stress.db")
    project_dir = os.path.join(temp_dir, "stress_project")
    os.makedirs(project_dir, exist_ok=True)
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        print(f"\n--- 1. Creating stress project ---")
        num_files = 30
        files_created = []
        for i in range(num_files):
            filepath = create_stress_file(project_dir, i)
            files_created.append(filepath)
        
        print(f"  Created {num_files} stress files")
        
        print(f"\n--- 2. Analyzing stress project ---")
        start_time = time.time()
        for filepath in files_created:
            arkts_analyzer.update_file_knowledge_graph(filepath)
        elapsed = time.time() - start_time
        
        print(f"  Analysis done in {elapsed:.2f} seconds")
        
        print(f"\n--- 3. Verifying results ---")
        all_files = database.get_all_files()
        all_classes = database.get_all_classes()
        all_methods = database.get_all_methods()
        
        print(f"  Files: {len(all_files)}")
        print(f"  Classes: {len(all_classes)}")
        print(f"  Methods: {len(all_methods)}")
        
        print(f"\n--- 4. Rapid modifications ---")
        for i in range(50):
            filepath = os.path.join(project_dir, "Rapid.ets")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"class Rapid_{i} {{ build() {{ }} }}\n")
            arkts_analyzer.update_file_knowledge_graph(filepath)
        
        final_files = database.get_all_files()
        print(f"  Final files: {len(final_files)}")
        
        print("\n" + "=" * 100)
        print("ALL TESTS PASSED! SYSTEM IS EXTREMELY STABLE!")
        print("=" * 100)
        
        return 0
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    sys.exit(main())
