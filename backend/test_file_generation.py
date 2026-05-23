
#!/usr/bin/env python3
"""
查看极端复杂测试文件生成的问题
"""
import os
import sys
import tempfile
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import arkts_analyzer


def create_extremely_complex_file(dir_path, index):
    """创建极端复杂的ArkTS文件"""
    filename = os.path.join(dir_path, "CheckTest.ets")
    
    content = "// 极端复杂的测试文件 - 包含混乱代码、深层嵌套、特殊字符\n\n"
    
    class_names = []
    
    # 创建1个简单的类来测试
    class_name = "SimpleTest"
    class_names.append(class_name)
    
    content += f"class {class_name} {{\n"
    
    # 方法
    num_methods = 3
    method_names = []
    for m_idx in range(num_methods):
        method_name = f"method{m_idx}"
        method_names.append(method_name)
        content += f"    {method_name}() {{\n"
        content += f"        console.log('test');\n"
        content += "    }\n\n"
    
    content += "    build() {\n"
    content += "        Column() {\n"
    content += "            Text('Test');\n"
    content += "        }\n"
    content += "    }\n"
    content += "}\n\n"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filename


def main():
    temp_dir = tempfile.mkdtemp(prefix="check_test_")
    
    try:
        print("=" * 100)
        print("测试文件生成检查")
        print("=" * 100)
        
        # 创建测试文件
        test_file = create_extremely_complex_file(temp_dir, 0)
        
        print(f"\n测试文件路径: {test_file}")
        
        print("\n--- 测试文件内容 ---")
        with open(test_file) as f:
            content = f.read()
            print(content)
        
        print("\n--- 使用 parse_file 分析 ---")
        result = arkts_analyzer.parse_file(test_file)
        for cls in result.get('classes', []):
            print(f"  类名: {cls.get('name')}")
            print(f"  方法数: {len(cls.get('methods', []))}")
            print(f"  方法: {cls.get('methods')}")
        
        print("\n--- 现在看极端复杂的文件问题 ---")
        # 创建一个真正极端的文件（类似我们的测试函数）
        extreme_file = os.path.join(temp_dir, "ExtremeFile.ets")
        with open(extreme_file, 'w') as f:
            f.write("""
class ExtremeTest {
    method0() {
        {
            this.method1();
        }
    }
    
    method1() {
        this.method2();
    }
    
    method2() {
        this.method3();
    }
    
    method3() {
        console.log('test');
    }
    
    build() {
        Column() {
            Text('Test');
        }
    }
}
""")
        
        print(f"\n极端文件内容:")
        print(open(extreme_file).read())
        
        extreme_result = arkts_analyzer.parse_file(extreme_file)
        print(f"\n极端文件分析结果:")
        for cls in extreme_result.get('classes', []):
            print(f"  类名: {cls.get('name')}")
            print(f"  方法数: {len(cls.get('methods', []))}")
            print(f"  方法: {cls.get('methods')}")
        
        return 0
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
