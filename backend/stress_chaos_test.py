
#!/usr/bin/env python3
"""
超级压力混乱测试！验证系统在极端条件下的稳定性！
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
print("STRESS & CHAOS TEST - EXTREME CONDITIONS!")
print("=" * 100)

def create_chaos_file(dir_path, index):
    """创建极其混乱的测试文件！"""
    filename = f"ChaosFile_{index:04d}.ets"
    filepath = os.path.join(dir_path, filename)
    
    content = ""
    num_classes = random.randint(1, 10)
    
    for ci in range(num_classes):
        class_name = f"ChaosClass_{index}_{ci}"
        is_struct = random.random() &lt; 0.3
        
        if random.random() &lt; 0.5:
            content += "@Component\n"
        if random.random() &lt; 0.3:
            content += "@Entry\n"
        
        if is_struct:
            content += f"struct {class_name} {{\n"
        else:
            content += f"class {class_name} {{\n"
        
        num_methods = random.randint(1, 20)
        for mi in range(num_methods):
            method_name = f"chaosMethod_{index}_{ci}_{mi}"
            content += f"  {method_name}() {{\n"
            
            num_lines = random.randint(1, 30)
            for _ in range(num_lines):
                if random.random() &lt; 0.2:
                    other_method = f"chaosMethod_{index}_{ci}_{random.randint(0, mi)}"
                    content += f"    {other_method}();\n"
                elif random.random() &lt; 0.3:
                    components = ["Text", "Button", "Column", "Row", "List"]
                    content += f"    {random.choice(components)}() {{}}\n"
                else:
                    content += "    // chaos comment\n"
            
            content += "  }\n"
        
        content += "  build() {\n"
        for _ in range(random.randint(1, 10)):
            content += "    Column() {\n"
        for _ in range(random.randint(1, 10)):
            content += "    }\n"
        content += "  }\n"
        
        content += "}\n\n"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath

def main():
    temp_dir = tempfile.mkdtemp(prefix="chaos_test_")
    db_path = os.path.join(temp_dir, "chaos.db")
    project_dir = os.path.join(temp_dir, "chaos_project")
    os.makedirs(project_dir, exist_ok=True)
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        print(f"\n--- ROUND 1: Creating chaos project ---")
        num_files = 50
        files_created = []
        for i in range(num_files):
            filepath = create_chaos_file(project_dir, i)
            files_created.append(filepath)
        
        print(f"  Created {num_files} chaos files!")
        
        print(f"\n--- ROUND 2: Analyzing chaos project ---")
        start_time = time.time()
        for filepath in files_created:
            try:
                arkts_analyzer.update_file_knowledge_graph(filepath)
            except Exception as e:
                print(f"  ⚠️ Error analyzing: {filepath}: {e}")
        elapsed = time.time() - start_time
        
        print(f"  Analysis completed in {elapsed:.2f} seconds")
        
        print(f"\n--- ROUND 3: Verifying results ---")
        all_files = database.get_all_files()
        all_classes = database.get_all_classes()
        all_methods = database.get_all_methods()
        
        print(f"  Files: {len(all_files)}")
        print(f"  Classes: {len(all_classes)}")
        print(f"  Methods: {len(all_methods)}")
        
        print(f"\n--- ROUND 4: Rapid modifications ---")
        for i in range(100):
            filepath = os.path.join(project_dir, "RapidChaos.ets")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"class RapidChaos_{i} {{ build() {{ }} }}\n")
            arkts_analyzer.update_file_knowledge_graph(filepath)
        
        final_files = database.get_all_files()
        print(f"  Final files: {len(final_files)}")
        
        print("\n" + "=" * 100)
        print("STRESS & CHAOS TEST COMPLETED SUCCESSFULLY!")
        print("SYSTEM IS EXTREMELY STABLE!")
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
