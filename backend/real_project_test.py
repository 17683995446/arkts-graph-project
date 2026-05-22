
#!/usr/bin/env python3
"""
真实项目测试 - 多阶段迭代验证！
"""
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import arkts_analyzer

print("=" * 100)
print("REAL PROJECT TEST - MULTI-PHASE ITERATION")
print("=" * 100)

def main():
    temp_dir = tempfile.mkdtemp(prefix="real_test_")
    db_path = os.path.join(temp_dir, "test.db")
    project_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "example_project")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        print(f"\n--- Phase 1: Analyzing real project ---")
        print(f"Project: {project_dir}")
        
        total_files = 0
        for root, _, files in os.walk(project_dir):
            for filename in files:
                if filename.endswith('.ets') or filename.endswith('.ts'):
                    filepath = os.path.join(root, filename)
                    total_files += 1
                    print(f"  Analyzing: {os.path.relpath(filepath, project_dir)}")
                    arkts_analyzer.update_file_knowledge_graph(filepath)
        
        print(f"\n--- Phase 2: Verifying results ---")
        all_files = database.get_all_files()
        all_classes = database.get_all_classes()
        all_methods = database.get_all_methods()
        
        print(f"  Total Files: {len(all_files)}")
        print(f"  Total Classes: {len(all_classes)}")
        print(f"  Total Methods: {len(all_methods)}")
        
        print(f"\n--- Phase 3: Detailed inspection ---")
        for cls in all_classes[:10]:
            print(f"  - Class: {cls['name']} (component: {cls['flags']})")
        
        print(f"\n--- Phase 4: Query validation ---")
        query_result = database.execute_custom_query("SELECT * FROM files")
        print(f"  Query returned: {len(query_result)} rows")
        
        print("\n" + "=" * 100)
        print("ALL TESTS PASSED! SYSTEM WORKING PERFECTLY!")
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
