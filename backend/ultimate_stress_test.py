
#!/usr/bin/env python3
"""
超级压力全面测试系统 - 多次迭代
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
print("🚀 ULTIMATE STRESS & CHAOS TESTING SYSTEM")
print("=" * 100)

def create_test_file(dir_path, index, complexity):
    """创建复杂的测试文件"""
    filename = f"TestFile_{index:04d}.ets"
    filepath = os.path.join(dir_path, filename)
    
    classes = []
    num_classes = random.randint(1, 5)
    
    for ci in range(num_classes):
        class_name = f"Class_{index}_{ci}"
        is_component = random.random() &lt; 0.4
        
        lines = []
        if is_component:
            lines.append("@Component")
        lines.append(f"class {class_name} {{")
        
        num_fields = random.randint(0, 15)
        for fi in range(num_fields):
            lines.append(f"  private field_{fi}: string = 'test';")
        
        num_methods = random.randint(1, 10)
        for mi in range(num_methods):
            method_name = f"method_{index}_{ci}_{mi}"
            lines.append(f"  {method_name}() {{")
            for _ in range(random.randint(1, 10)):
                lines.append("    // some code")
            lines.append("  }")
        
        if random.random() &lt; 0.8:
            lines.append("  build() {")
            for _ in range(random.randint(1, 8)):
                lines.append("    Column() {")
            for _ in range(random.randint(1, 8)):
                lines.append("    }")
            lines.append("  }")
        
        lines.append("}")
        classes.append("\n".join(lines))
    
    content = "\n\n".join(classes)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath


def run_iteration(iteration_num, db_path, project_dir):
    """运行一次完整迭代"""
    print(f"\n--- 迭代 {iteration_num} ---")
    start_time = time.time()
    
    # 设置数据库
    database.set_custom_db_path(db_path)
    database.init_database(db_path)
    
    # 创建测试文件
    num_files = 20 + iteration_num * 10
    files = []
    for i in range(num_files):
        filepath = create_test_file(project_dir, i, complexity=2 + iteration_num)
        files.append(filepath)
    
    # 逐个分析
    for filepath in files:
        try:
            arkts_analyzer.update_file_knowledge_graph(filepath)
        except Exception as e:
            print(f"  ⚠️  警告: 分析 {filepath} 失败: {e}")
    
    # 验证
    all_files = database.get_all_files()
    all_classes = database.get_all_classes()
    all_methods = database.get_all_methods()
    
    elapsed = time.time() - start_time
    
    print(f"  📄 文件: {len(all_files)}, 🏗️ 类: {len(all_classes)}, 🔧 方法: {len(all_methods)}")
    print(f"  ⏱️  耗时: {elapsed:.2f}秒")
    
    return len(all_files) &gt;= 5, all_files, all_classes, all_methods


def main():
    temp_dir = tempfile.mkdtemp(prefix="ultimate_test_")
    db_path = os.path.join(temp_dir, "test.db")
    project_dir = os.path.join(temp_dir, "project")
    os.makedirs(project_dir, exist_ok=True)
    
    try:
        all_results = []
        total_files = 0
        total_classes = 0
        total_methods = 0
        
        # 5次迭代
        for i in range(1, 6):
            success, files, classes, methods = run_iteration(i, db_path, project_dir)
            all_results.append(success)
            total_files += len(files)
            total_classes += len(classes)
            total_methods += len(methods)
            
            # 重置数据库以便下一次迭代
            database.set_custom_db_path(None)
            os.remove(db_path)
        
        # 统计
        print("\n" + "=" * 100)
        print("📊  ULTIMATE TEST SUMMARY")
        print("=" * 100)
        
        passed = sum(1 for r in all_results if r)
        failed = len(all_results) - passed
        
        print(f"  总迭代: {len(all_results)}")
        print(f"  通过: {passed}")
        print(f"  失败: {failed}")
        
        print(f"\n  总计处理文件数: {total_files}")
        print(f"  总计处理类数: {total_classes}")
        print(f"  总计处理方法数: {total_methods}")
        
        if failed == 0:
            print("\n🎉 所有迭代完美通过！系统非常稳定！")
            return 0
        else:
            print(f"\n⚠️  {failed} 次迭代失败")
            return 1
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    sys.exit(main())

