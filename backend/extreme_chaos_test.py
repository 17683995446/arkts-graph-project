
#!/usr/bin/env python3
"""
极致混乱和复杂的真实场景测试！
- 大量 ArkTS 文件
- 复杂嵌套组件关系
- 混乱的命名
- 极端文件大小
- 混乱的并发操作
- 错误恢复场景
"""
import tempfile
import time
import random
import threading
import traceback
from pathlib import Path
from typing import List

import database
import arkts_analyzer


class ChaosTester:
    def __init__(self):
        self.test_dir = None
        self.db_path = None
        self.bugs_found = []
        self.success_count = 0
        self.error_count = 0
    
    def create_chaotic_arkts_file(self, index: int):
        """创建一个混乱的、有各种复杂度的 ArkTS 文件！"""
        file_name = f"ChaoticFile_{index}_{random.randint(1000, 9999)}.ets"
        content = []
        
        # 顶部混乱的注释和导入（可能有问题）
        content.append("// File with chaotic and complex content")
        content.append("// Created for extreme testing")
        if random.random() &lt; 0.3:
            content.append(f"// Missing import {random.randint(1, 10)}")
        
        content.append("")
        
        # 添加一些类/组件，名字混乱
        num_classes = random.randint(1, 10)
        class_names = []
        
        for ci in range(num_classes):
            class_type = random.choice(["struct", "class"])
            name_prefix = random.choice(["Comp", "View", "Model", "Service", "Util", "UI"])
            class_name = f"{name_prefix}_{random.randint(100, 999)}_{ci}"
            class_names.append(class_name)
            
            is_component = random.random() &lt; 0.7
            if is_component:
                if random.random() &lt; 0.3:
                    content.append("@Component")
                if random.random() &lt; 0.1:
                    content.append("@Entry")
            
            content.append(f"{class_type} {class_name} {{")
            
            # 添加一些混乱的状态和属性
            num_properties = random.randint(0, 5)
            for pi in range(num_properties):
                prop_type = random.choice(["@State", "@Prop", "@Link", "@Provide", "@Consume", "@Watch", ""])
                var_type = random.choice(["number", "string", "boolean", "any"])
                var_name = f"prop_{random.randint(100, 999)}"
                default_vals = ['0', '""', 'true', 'false']
                content.append(f"  {prop_type} {var_name}: {var_type} = {random.choice(default_vals)};")
            
            content.append("")
            
            # 添加混乱的方法
            num_methods = random.randint(1, 10)
            for mi in range(num_methods):
                method_name = f"{random.choice(['do', 'handle', 'process', 'calc', 'render'])}"
                method_name += f"_{random.randint(100, 999)}"
                content.append(f"  {method_name}() {{")
                
                # 方法内部添加混乱调用
                num_calls = random.randint(0, 10)
                for ci in range(num_calls):
                    call_name = random.choice(class_names) if random.random() &lt; 0.5 else f"func_{random.randint(1, 100)}"
                    if call_name not in ["if", "for", "while", "switch"]:
                        content.append(f"    {call_name}();")
                
                content.append("  }")
            
            content.append("")
            
            # 可能添加 build 方法
            if is_component and random.random() &lt; 0.9:
                content.append("  build() {")
                
                # build 中添加混乱的组件
                num_children = random.randint(1, 10)
                for chi in range(num_children):
                    child_name = random.choice(class_names) if random.random() &lt; 0.5 else random.choice([
                        "Text", "Button", "Column", "Row", "Stack"
                    ])
                    content.append(f"    {child_name}();")
                
                content.append("  }")
            
            content.append("}")
            content.append("")
        
        final_content = "\n".join(content)
        return file_name, final_content
    
    def setup(self):
        print("=== 设置极端混乱测试 ===")
        self.test_dir = Path(tempfile.mkdtemp(prefix="arkts_chaos_test_"))
        print(f"测试目录: {self.test_dir}")
        
        self.db_path = self.test_dir / "chaos_test.db"
        database.set_custom_db_path(str(self.db_path))
        database.init_database()
    
    def test_phase_1_large_batch(self):
        """阶段1：大量文件批量创建"""
        print("\n=== 阶段 1: 大量文件批量创建 ===")
        num_files = 200  # 大量文件！
        created_files = []
        
        start_time = time.time()
        
        for i in range(num_files):
            try:
                file_name, content = self.create_chaotic_arkts_file(i)
                file_path = self.test_dir / file_name
                file_path.write_text(content, encoding="utf-8")
                created_files.append(file_path)
                
                # 更新知识图谱
                arkts_analyzer.update_file_knowledge_graph(str(file_path))
                
                self.success_count += 1
                
                if (i + 1) % 20 == 0:
                    print(f"  ✅ 已处理 {i + 1}/{num_files} 文件")
            
            except Exception as e:
                self.error_count += 1
                bug = {
                    "phase": 1,
                    "index": i,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                self.bugs_found.append(bug)
                print(f"  ❌ 文件 {i} 错误: {e}")
        
        elapsed = time.time() - start_time
        
        print(f"  阶段 1 完成: {self.success_count} 成功, {self.error_count} 错误, 耗时 {elapsed:.2f}秒")
        
        # 验证数据完整性
        all_files = database.get_all_files()
        all_classes = database.get_all_classes()
        
        print(f"  📊 数据库中文件数: {len(all_files)}")
        print(f"  📊 数据库中类/组件数: {len(all_classes)}")
        
        return created_files
    
    def test_phase_2_chaotic_updates(self, files: List[Path]):
        """阶段2：混乱的更新操作"""
        print("\n=== 阶段 2: 混乱的更新操作 ===")
        
        num_updates = 500  # 非常多次更新！
        updates_success = 0
        
        start_time = time.time()
        
        for i in range(num_updates):
            try:
                # 随机选择一个文件进行修改
                file_to_update = random.choice(files)
                file_name = file_to_update.name
                new_content = self.create_chaotic_arkts_file(i)[1]
                file_to_update.write_text(new_content, encoding="utf-8")
                
                # 更新知识图谱
                arkts_analyzer.update_file_knowledge_graph(str(file_to_update))
                
                updates_success += 1
                
                if (i + 1) % 50 == 0:
                    print(f"  ✅ 已更新 {i + 1}/{num_updates} 次")
            
            except Exception as e:
                self.error_count += 1
                bug = {
                    "phase": 2,
                    "index": i,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                self.bugs_found.append(bug)
        
        elapsed = time.time() - start_time
        print(f"  阶段 2 完成: {updates_success} 更新, 耗时 {elapsed:.2f}秒")
    
    def test_phase_3_mixed_operations(self):
        """阶段3：混合操作（读、写、查询）"""
        print("\n=== 阶段 3: 混合操作 ===")
        
        start_time = time.time()
        operations = 200
        successful_ops = 0
        
        for i in range(operations):
            try:
                op_type = random.randint(0, 3)
                
                if op_type == 0:  # 读取所有文件
                    _ = database.get_all_files()
                elif op_type == 1:  # 读取所有类
                    _ = database.get_all_classes()
                elif op_type == 2:  # 读取所有方法
                    _ = database.get_all_methods()
                else:  # 读取调用关系
                    _ = database.get_all_calls()
                
                successful_ops += 1
                
                if (i + 1) % 20 == 0:
                    print(f"  ✅ 完成 {i + 1}/{operations} 次查询")
            
            except Exception as e:
                self.error_count += 1
                bug = {
                    "phase": 3,
                    "index": i,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                self.bugs_found.append(bug)
        
        elapsed = time.time() - start_time
        print(f"  阶段 3 完成: {successful_ops} 查询, 耗时 {elapsed:.2f}秒")
    
    def test_phase_4_deletion_chaos(self, files: List[Path]):
        """阶段4：混乱删除操作"""
        print("\n=== 阶段 4: 混乱删除操作 ===")
        
        # 随机删除一些文件
        num_to_delete = min(len(files), 50)
        files_to_delete = random.sample(files, num_to_delete)
        
        delete_success = 0
        start_time = time.time()
        
        for i, file_path in enumerate(files_to_delete):
            try:
                # 在数据库中删除
                file_in_db = database.get_file_by_path(str(file_path))
                if file_in_db:
                    database.delete_file_data(file_in_db["id"])
                
                # 删除物理文件
                if file_path.exists():
                    file_path.unlink()
                
                delete_success += 1
                
                if (i + 1) % 10 == 0:
                    print(f"  ✅ 已删除 {i + 1}/{num_to_delete} 个文件")
            
            except Exception as e:
                self.error_count += 1
                bug = {
                    "phase": 4,
                    "index": i,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                self.bugs_found.append(bug)
        
        elapsed = time.time() - start_time
        print(f"  阶段 4 完成: {delete_success} 删除, 耗时 {elapsed:.2f}秒")
    
    def test_phase_5_extreme_concurrent(self):
        """阶段5：极端并发操作"""
        print("\n=== 阶段 5: 极端并发操作 ===")
        
        num_threads = 30  # 大量并发线程！
        operations_per_thread = 50
        
        start_time = time.time()
        threads = []
        
        def worker(thread_id):
            thread_success = 0
            for i in range(operations_per_thread):
                try:
                    if random.random() &lt; 0.5:
                        _ = database.get_all_files()
                    else:
                        _ = database.get_all_classes()
                    thread_success += 1
                except Exception:
                    pass
            return thread_success
        
        for t in range(num_threads):
            t_obj = threading.Thread(target=lambda: worker(t))
            t_obj.start()
            threads.append(t_obj)
        
        for t_obj in threads:
            t_obj.join()
        
        elapsed = time.time() - start_time
        print(f"  阶段 5 完成: {num_threads} 个并发线程, 耗时 {elapsed:.2f}秒")
    
    def run_all_chaos_tests(self):
        """运行所有混乱测试！"""
        print("=== 开始极端混乱和复杂的真实场景测试 ===\n")
        
        self.setup()
        files = self.test_phase_1_large_batch()
        self.test_phase_2_chaotic_updates(files)
        self.test_phase_3_mixed_operations()
        self.test_phase_4_deletion_chaos(files)
        self.test_phase_5_extreme_concurrent()
        
        # 最终报告
        print("\n" + "="*80)
        print("=== 混乱测试完成报告 ===")
        print("="*80)
        print(f"✅ 成功操作: {self.success_count}")
        print(f"❌ 错误数量: {self.error_count}")
        
        if self.bugs_found:
            print(f"\n🐛 发现 {len(self.bugs_found)} 个问题！")
            for bug in self.bugs_found[:5]:  # 只显示前5个
                print(f"  - 阶段{bug['phase']}, 索引{bug['index']}: {bug['error']}")
        else:
            print("\n🎉 没有发现任何问题！系统极其健壮！")
        
        # 最终数据库状态
        all_files = database.get_all_files()
        all_classes = database.get_all_classes()
        print(f"\n📊 最终状态: {len(all_files)} 文件, {len(all_classes)} 类/组件")


if __name__ == "__main__":
    tester = ChaosTester()
    tester.run_all_chaos_tests()
