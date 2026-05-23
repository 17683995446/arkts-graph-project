
#!/usr/bin/env python3
"""
极端复杂代码分析测试 - 第一阶段
测试系统在极端复杂场景下的表现
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


def create_extremely_complex_file(dir_path, index, num_classes=5, max_methods=20, max_depth=3):
    """创建极端复杂的ArkTS文件"""
    filename = f"ExtremeComplex_{index:04d}.ets"
    filepath = os.path.join(dir_path, filename)
    
    content = "// 极端复杂的测试文件 - 包含混乱代码、深层嵌套、特殊字符\n\n"
    
    class_names = []
    
    for c_idx in range(num_classes):
        class_name = f"ExtremeClass_{index}_{c_idx}"
        class_names.append(class_name)
        
        is_struct = random.random() < 0.2
        is_component = random.random() < 0.6
        is_entry = is_component and random.random() < 0.3
        
        if is_entry:
            content += "@Entry\n"
        if is_component:
            content += "@Component\n"
        
        if is_struct:
            content += f"struct {class_name} {{\n"
        else:
            content += f"class {class_name} {{\n"
        
        # 方法
        num_methods = random.randint(5, max_methods)
        method_names = []
        for m_idx in range(num_methods):
            method_name = f"complexMethod_{index}_{c_idx}_{m_idx}"
            method_names.append(method_name)
            is_async = random.random() < 0.15
            
            if is_async:
                content += f"    async {method_name}"
            else:
                content += f"    {method_name}"
            
            # 参数
            params = []
            num_params = random.randint(0, 8)
            for p_idx in range(num_params):
                param_types = ['string', 'number', 'boolean', 'object', 'any', 'void']
                param_names = ['data', 'index', 'value', 'state', 'config', 'options', 'context']
                params.append(f"{random.choice(param_names)}_{p_idx}: {random.choice(param_types)}")
            
            if params:
                content += f"({', '.join(params)})"
            else:
                content += "()"
            
            # 返回值
            if random.random() < 0.4:
                return_types = ['void', 'string', 'number', 'boolean', 'any']
                content += f": {random.choice(return_types)}"
            
            content += " {\n"
            
            # 方法内容 - 极端混乱
            depth = random.randint(0, max_depth)
            indent = 4
            for _ in range(random.randint(5, 30)):
                indent = 4 + random.randint(0, depth * 2)
                
                if random.random() < 0.2 and method_names:
                    # 调用其他方法
                    if random.random() < 0.5 and len(method_names) > 1:
                        caller = random.choice(method_names[:-1])
                        callee = random.choice(method_names)
                        if caller != callee:
                            content += " " * indent + f"this.{caller}();\n"
                    else:
                        callee = random.choice(method_names)
                        content += " " * indent + f"this.{callee}();\n"
                elif random.random() < 0.15:
                    # UI组件
                    components = ['Text', 'Button', 'Column', 'Row', 'Stack', 'List', 'ForEach', 'If']
                    comp = random.choice(components)
                    content += " " * indent + f"{comp}"
                    if random.random() < 0.5:
                        content += "() {\n"
                    else:
                        content += " {\n"
                    if random.random() < 0.5:
                        content += " " * (indent + 2) + "}\n"
                elif random.random() < 0.1:
                    # 条件语句
                    conditions = ['if', 'while', 'for']
                    content += " " * indent + f"{random.choice(conditions)} (true) {{\n"
                    if random.random() < 0.5:
                        content += " " * (indent + 2) + "}\n"
                elif random.random() < 0.1:
                    # 注释
                    comments = [
                        "// TODO: 重构这段代码",
                        "// 临时方案",
                        "// 极端复杂逻辑",
                        "// 注意边界情况",
                        "/* 这是注释 */"
                    ]
                    content += " " * indent + f"{random.choice(comments)}\n"
                else:
                    # 随机内容
                    content += " " * indent + "// 混乱的代码行\n"
            
            content += "    }\n\n"
        
        # build方法（组件类）
        if is_component:
            content += "    build() {\n"
            build_depth = random.randint(0, 5)
            for d in range(build_depth):
                components = ['Text', 'Button', 'Column', 'Row', 'Stack']
                comp = random.choice(components)
                content += " " * (6 + d * 2) + f"{comp}() {{\n"
            for d in range(build_depth):
                content += " " * (6 + (build_depth - d - 1) * 2) + "}\n"
            content += "    }\n"
        
        content += "}\n\n"
    
    # 额外的混乱内容 - 让文件变得更复杂
    for _ in range(random.randint(0, 10)):
        if random.random() < 0.3:
            content += f"// 随机注释 {random.randint(1000, 9999)}\n"
        elif random.random() < 0.2:
            content += f"console.log('调试信息 {random.random()}');\n"
        else:
            content += "    \n"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath


def main():
    print("=" * 100)
    print("阶段1：极端复杂代码分析测试")
    print("=" * 100)
    
    temp_dir = tempfile.mkdtemp(prefix="extreme_complex_")
    db_path = os.path.join(temp_dir, "extreme.db")
    project_dir = os.path.join(temp_dir, "extreme_project")
    os.makedirs(project_dir, exist_ok=True)
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        total_start = time.time()
        
        # 测试规模：20个极端复杂文件
        num_files = 20
        total_classes = 0
        total_methods = 0
        
        print(f"\n正在创建并分析 {num_files} 个极端复杂的测试文件...")
        
        for i in range(num_files):
            start = time.time()
            filepath = create_extremely_complex_file(
                project_dir, 
                i, 
                num_classes=random.randint(3, 8), 
                max_methods=random.randint(10, 30),
                max_depth=random.randint(2, 6)
            )
            arkts_analyzer.update_file_knowledge_graph(filepath)
            elapsed = time.time() - start
            
            # 获取该文件的统计
            # 简化：直接读取所有文件并统计总数
            if (i + 1) % 5 == 0:
                all_files = database.get_all_files()
                all_classes = database.get_all_classes()
                all_methods = database.get_all_methods()
                
                print(f"  文件 {i+1}/{num_files}: {os.path.basename(filepath)}")
                print(f"    耗时: {elapsed:.2f}秒")
                print(f"    累计统计: 类 {len(all_classes)}, 方法 {len(all_methods)}")
        
        all_files = database.get_all_files()
        all_classes = database.get_all_classes()
        all_methods = database.get_all_methods()
        all_calls = database.get_all_calls()
        
        total_elapsed = time.time() - total_start
        
        print("\n" + "=" * 100)
        print("极端复杂代码分析测试 - 总结")
        print("=" * 100)
        print(f"文件数:         {len(all_files)}")
        print(f"类数:           {len(all_classes)}")
        print(f"方法数:         {len(all_methods)}")
        print(f"调用关系数:     {len(all_calls)}")
        print(f"总耗时:         {total_elapsed:.2f}秒")
        print(f"平均每文件耗时: {total_elapsed / num_files:.2f}秒")
        
        print("\n✅ 阶段1完成：无崩溃，系统稳定！")
        return 0
        
    except Exception as e:
        print(f"\n❌ 阶段1失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    sys.exit(main())
