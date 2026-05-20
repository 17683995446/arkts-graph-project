
#!/usr/bin/env python3
"""
简化版但仍然非常复杂和混乱的测试！
"""
import tempfile
import time
import random
from pathlib import Path

import database
import arkts_analyzer


def create_simple_arkts_file(i):
    """创建一个简单但有挑战性的测试文件"""
    content = []
    
    # 添加 3 个类/组件
    names = []
    for j in range(3):
        name = f"Component_{i}_{j}"
        names.append(name)
        
        if random.random() &lt; 0.6:
            content.append("@Component")
        
        content.append(f"struct {name} {{")
        
        # 添加一些方法
        for k in range(2):
            method_name = f"method_{k}"
            content.append(f"  {method_name}() {{")
            if random.random() &lt; 0.5:
                content.append(f"    // do something")
            content.append("  }")
        
        content.append("  build() {")
        # 添加一些子组件
        for child in random.sample(names, min(2, len(names))):
            content.append(f"    {child}();")
        content.append("  }")
        
        content.append("}")
        content.append("")
    
    return "\n".join(content)


def run_chaos_tests():
    """运行混乱测试"""
    print("=== 开始极端混乱测试 ===\n")
    
    with tempfile.TemporaryDirectory(prefix="arkts_chaos_simple") as temp_dir:
        temp_path = Path(temp_dir)
        db_path = temp_path / "chaos_test.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        print(f"测试目录: {temp_dir}")
        
        # 阶段 1: 创建 100 个文件
        print("\n=== 阶段 1: 100 个文件批量创建 ===")
        files = []
        start1 = time.time()
        for i in range(100):
            try:
                file_content = create_simple_arkts_file(i)
                file_path = temp_path / f"file_{i}.ets"
                file_path.write_text(file_content, encoding="utf-8")
                files.append(file_path)
                
                arkts_analyzer.update_file_knowledge_graph(str(file_path))
                
                if (i + 1) % 20 == 0:
                    print(f"  已创建 {i + 1}/100 文件")
            except Exception as e:
                print(f"  错误 {i}: {e}")
        
        elapsed1 = time.time() - start1
        all_files = database.get_all_files()
        all_classes = database.get_all_classes()
        print(f"  完成 100 个文件，耗时 {elapsed1:.2f}秒")
        print(f"  数据库中: {len(all_files)} 文件, {len(all_classes)} 类")
        
        # 阶段 2: 更新 200 次
        print("\n=== 阶段 2: 200 次随机更新 ===")
        start2 = time.time()
        for i in range(200):
            try:
                file_to_update = random.choice(files)
                new_content = create_simple_arkts_file(i)
                file_to_update.write_text(new_content, encoding="utf-8")
                arkts_analyzer.update_file_knowledge_graph(str(file_to_update))
                
                if (i + 1) % 40 == 0:
                    print(f"  已更新 {i + 1}/200 次")
            except Exception as e:
                print(f"  更新错误 {i}: {e}")
        
        elapsed2 = time.time() - start2
        print(f"  完成 200 次更新，耗时 {elapsed2:.2f}秒")
        
        # 阶段 3: 混合查询 100 次
        print("\n=== 阶段 3: 100 次混合查询 ===")
        start3 = time.time()
        for i in range(100):
            try:
                database.get_all_files()
                database.get_all_classes()
                database.get_all_methods()
                if (i + 1) % 20 == 0:
                    print(f"  已查询 {i + 1}/100 次")
            except Exception as e:
                print(f"  查询错误 {i}: {e}")
        
        elapsed3 = time.time() - start3
        print(f"  完成 100 次查询，耗时 {elapsed3:.2f}秒")
        
        # 最终检查
        print("\n=== 最终数据状态 ===")
        final_files = database.get_all_files()
        final_classes = database.get_all_classes()
        final_methods = database.get_all_methods()
        final_calls = database.get_all_calls()
        
        print(f"📊 文件数: {len(final_files)}")
        print(f"📊 类/组件数: {len(final_classes)}")
        print(f"📊 方法数: {len(final_methods)}")
        print(f"📊 调用关系: {len(final_calls)}")
        
        print("\n=== 测试完成 ===")
        if len(final_calls) &gt; 0 or len(final_classes) &gt; 50:
            print("🎉 系统功能正常！")
        else:
            print("⚠️ 可能存在问题！")


if __name__ == "__main__":
    run_chaos_tests()
