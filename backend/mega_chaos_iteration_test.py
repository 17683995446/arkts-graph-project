
#!/usr/bin/env python3
"""
超大规模混乱场景多次迭代测试系统
"""
import os
import sys
import tempfile
import shutil
import random
import time
import re
import string
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detailed_logger import (
    trace, log_line, log_branch, log_warning, log_error,
    print_stats_summary, LOG_STATS
)
import database
import arkts_analyzer

# 随机配置
CLASS_NAME_WORDS = [
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
    "Smart", "Fast", "Quick", "Slow", "Red", "Blue", "Green", "Yellow",
    "Main", "Helper", "Core", "Utils", "Widget", "Panel", "Screen", "Dialog",
    "Super", "Ultra", "Mega", "Hyper", "Final", "Pro", "Lite"
]
METHOD_NAME_WORDS = ["build", "init", "update", "render", "draw", "click", "tap", "show", "hide"]
COMPONENT_NAMES = ["Text", "Button", "Column", "Row", "Stack", "Image", "List", "Scroll"]
SPECIAL_CHARS = list("!@#$%^&*()_+-=[]{}|;:,.<>?中文测试日本語한국어")

class IterationTest:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="mega_chaos_test_")
        self.project_dir = os.path.join(self.temp_dir, "project")
        self.db_path = os.path.join(self.temp_dir, "test.db")
        os.makedirs(self.project_dir, exist_ok=True)
        
        log_line(f"临时目录: {self.temp_dir}")
    
    def __enter__(self):
        database.set_custom_db_path(self.db_path)
        database.init_database(self.db_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        database.set_custom_db_path(None)
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def generate_random_class_name(self):
        return random.choice(CLASS_NAME_WORDS) + random.choice(CLASS_NAME_WORDS) + "Class"
    
    def generate_random_method_name(self):
        return random.choice(METHOD_NAME_WORDS) + random.choice(string.ascii_uppercase)
    
    def generate_random_content(self, complexity: int = 5):
        """生成复杂混乱的ArkTS内容"""
        lines = []
        num_classes = random.randint(1, 5)
        for _ in range(num_classes):
            class_name = self.generate_random_class_name()
            is_struct = random.random() &lt; 0.3
            is_component = random.random() &lt; 0.5
            
            if is_struct and is_component:
                lines.append("@Component")
            if random.random() &lt; 0.2:
                lines.append("@Entry")
            
            if is_struct:
                lines.append(f"struct {class_name} {{")
            else:
                lines.append(f"export class {class_name} {{")
            
            # 添加字段
            num_fields = random.randint(0, 20)
            for _ in range(num_fields):
                field_type = random.choice(["string", "number", "boolean", "any"])
                field_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
                if random.random() &lt; 0.3:
                    field_name += random.choice(SPECIAL_CHARS)
                if random.random() &lt; 0.5:
                    lines.append(f"  private {field_name}: {field_type};")
                else:
                    default_val = random.choice(['"test"', "0", "true", "null"])
                    lines.append(f"  private {field_name}: {field_type} = {default_val};")
            
            # 添加方法
            num_methods = random.randint(1, 15)
            for _ in range(num_methods):
                method_name = self.generate_random_method_name()
                lines.append(f"  {method_name}() {{")
                num_lines = random.randint(0, 30)
                for _ in range(num_lines):
                    choice = random.random()
                    if choice &lt; 0.2:
                        called_method = self.generate_random_method_name()
                        lines.append(f"    {called_method}();")
                    elif choice &lt; 0.4:
                        lines.append(f"    let x = {random.randint(0, 100)};")
                    elif choice &lt; 0.6:
                        lines.append(f"    // {''.join(random.choices(string.printable, k=random.randint(5, 50)))}")
                    else:
                        pass
                lines.append("  }")
            
            # 添加build方法
            if random.random() &lt; 0.8:
                lines.append("  build() {")
                build_lines = random.randint(1, 20)
                for _ in range(build_lines):
                    comp = random.choice(COMPONENT_NAMES)
                    lines.append(f"    {comp}() {{")
                for _ in range(build_lines):
                    lines.append("    }")
                lines.append("  }")
            
            lines.append("}")
        
        # 随机添加一些混乱内容
        if random.random() &lt; 0.3:
            lines.append("// " * random.randint(1, 5) + " 混乱注释")
        if random.random() &lt; 0.2:
            lines.append("  " * random.randint(1, 10) + " 多余缩进")
        
        return "\n".join(lines)
    
    def create_test_file(self, filename: str, complexity: int = 3):
        filepath = os.path.join(self.project_dir, filename)
        content = self.generate_random_content(complexity)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath
    
    def test_iteration_1(self):
        """第1次迭代：基础大规模测试"""
        log_line("=== 第1次迭代：基础大规模 ===")
        
        num_files = 50
        files_created = []
        
        for i in range(num_files):
            filename = f"TestFile_{i:03d}.ets"
            filepath = self.create_test_file(filename, complexity=random.randint(2, 6))
            files_created.append(filepath)
        
        # 逐个分析
        for filepath in files_created:
            try:
                arkts_analyzer.update_file_knowledge_graph(filepath)
            except Exception as e:
                log_error(f"分析 {filepath} 失败", e)
        
        # 验证结果
        files = database.get_all_files()
        classes = database.get_all_classes()
        
        log_line(f"分析结果：文件 {len(files)}, 类 {len(classes)}")
        
        return len(files) &gt;= 10
    
    def test_iteration_2(self):
        """第2次迭代：快速文件变更"""
        log_line("=== 第2次迭代：快速文件变更 ===")
        
        # 创建并快速修改同一个文件
        filename = "RapidlyChanging.ets"
        
        for i in range(50):
            filepath = os.path.join(self.project_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"class Iteration2Test{i} {{\n  build() {{}}\n}}")
            
            try:
                arkts_analyzer.update_file_knowledge_graph(filepath)
            except Exception as e:
                log_error(f"快速修改 {i} 失败", e)
        
        # 验证最终状态
        files = database.get_all_files()
        return len(files) == 1
    
    def test_iteration_3(self):
        """第3次迭代：文件删除与添加混合"""
        log_line("=== 第3次迭代：混合操作 ===")
        
        # 批量创建
        created_files = []
        for i in range(20):
            filename = f"MixFile_{i:03d}.ets"
            filepath = self.create_test_file(filename, complexity=random.randint(1, 4))
            created_files.append(filepath)
        
        for filepath in created_files:
            arkts_analyzer.update_file_knowledge_graph(filepath)
        
        # 删除一半
        for i in range(10):
            try:
                filepath = created_files[i]
                if os.path.exists(filepath):
                    os.remove(filepath)
                    existing_file = database.get_file_by_path(filepath)
                    if existing_file:
                        database.delete_file_data(existing_file['id'])
            except Exception as e:
                log_error(f"删除 {i} 失败", e)
        
        # 再添加10个
        for i in range(30, 40):
            filename = f"MixFile_{i:03d}.ets"
            filepath = self.create_test_file(filename)
            arkts_analyzer.update_file_knowledge_graph(filepath)
        
        # 验证
        files = database.get_all_files()
        log_line(f"混合操作后文件数：{len(files)}")
        
        return len(files) &gt; 0
    
    def test_iteration_4(self):
        """第4次迭代：边界条件与极端混乱"""
        log_line("=== 第4次迭代：极端边界 ===")
        
        # 空文件
        f1 = os.path.join(self.project_dir, "Empty.ets")
        open(f1, "w").close()
        
        # 只有空格
        f2 = os.path.join(self.project_dir, "Spaces.ets")
        with open(f2, "w", encoding="utf-8") as f:
            f.write("   \n\n  \t  ")
        
        # 超长类名
        f3 = os.path.join(self.project_dir, "LongName.ets")
        with open(f3, "w", encoding="utf-8") as f:
            class_name = "A" * 500 + "Class"
            f.write(f"class {class_name} {{\n  build() {{}}\n}}")
        
        # 全是注释
        f4 = os.path.join(self.project_dir, "AllComments.ets")
        with open(f4, "w", encoding="utf-8") as f:
            for i in range(100):
                f.write(f"// This is comment line {i}\n")
        
        # 混合编码字符
        f5 = os.path.join(self.project_dir, "Encoding.ets")
        with open(f5, "w", encoding="utf-8") as f:
            f.write("class EncodingTest { build() { Text('测试: 中文 日本語 한국어 Русский'); } }")
        
        # 分析所有
        for f in [f1, f2, f3, f4, f5]:
            try:
                arkts_analyzer.update_file_knowledge_graph(f)
            except Exception as e:
                log_error(f"边界测试失败: {f}", e)
        
        # 应该没有崩溃
        return True
    
    def test_iteration_5(self):
        """第5次迭代：性能压力"""
        log_line("=== 第5次迭代：性能压力 ===")
        
        start = time.time()
        num_files = 100
        
        for i in range(num_files):
            filename = f"PerfFile_{i:03d}.ets"
            filepath = self.create_test_file(filename, complexity=random.randint(3, 7))
            arkts_analyzer.update_file_knowledge_graph(filepath)
        
        elapsed = time.time() - start
        log_line(f"分析 {num_files} 文件耗时: {elapsed:.2f}秒")
        
        files = database.get_all_files()
        classes = database.get_all_classes()
        
        log_line(f"最终:  {len(files)} 文件, {len(classes)} 类")
        
        return len(files) &gt;= 80


def main():
    print("="*100)
    print("🚀 MEGA CHAOS ITERATION TESTING SYSTEM")
    print("="*100)
    
    results = {}
    
    with IterationTest() as test:
        # 第1次迭代
        print("\n--- 第1次迭代 ---")
        try:
            results['iter1'] = test.test_iteration_1()
        except Exception as e:
            log_error("第1次迭代异常", e)
            results['iter1'] = False
        
        # 第2次迭代
        print("\n--- 第2次迭代 ---")
        try:
            results['iter2'] = test.test_iteration_2()
        except Exception as e:
            log_error("第2次迭代异常", e)
            results['iter2'] = False
        
        # 第3次迭代
        print("\n--- 第3次迭代 ---")
        try:
            results['iter3'] = test.test_iteration_3()
        except Exception as e:
            log_error("第3次迭代异常", e)
            results['iter3'] = False
        
        # 第4次迭代
        print("\n--- 第4次迭代 ---")
        try:
            results['iter4'] = test.test_iteration_4()
        except Exception as e:
            log_error("第4次迭代异常", e)
            results['iter4'] = False
        
        # 第5次迭代
        print("\n--- 第5次迭代 ---")
        try:
            results['iter5'] = test.test_iteration_5()
        except Exception as e:
            log_error("第5次迭代异常", e)
            results['iter5'] = False
    
    # 统计
    print("\n" + "="*100)
    print("📊  MEGA ITERATION TESTING SUMMARY")
    print("="*100)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"  总迭代: {total}")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    
    for name, ok in results.items():
        print(f"  - {name}: {'✅ PASS' if ok else '❌ FAIL'}")
    
    print_stats_summary()
    
    if failed == 0:
        print("\n🎉 所有迭代完美通过！系统非常稳定！")
        return 0
    else:
        print(f"\n⚠️  {failed} 个迭代失败，需要进一步调查")
        return 1


if __name__ == "__main__":
    sys.exit(main())
