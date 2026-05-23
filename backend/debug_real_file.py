
#!/usr/bin/env python3
"""
调试为什么复杂文件中提取不到方法
"""
import os
import sys
import tempfile
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import arkts_analyzer


def create_test_file(dir_path):
    filename = os.path.join(dir_path, "DebugTest.ets")
    
    with open(filename, "w") as f:
        f.write("""
class DebugTest {
    method1() {
        this.method2();
    }
    
    method2() {
        console.log('test');
    }
    
    build() {
        Column() {
            Text('Test');
        }
    }
}
""")
    
    return filename


def main():
    temp_dir = tempfile.mkdtemp(prefix="debug_real_")
    db_path = os.path.join(temp_dir, "debug.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        # 创建并分析测试文件
        test_file = create_test_file(temp_dir)
        
        print("=" * 80)
        print("测试文件内容:")
        print("=" * 80)
        with open(test_file) as f:
            content = f.read()
            print(content)
        
        print("\n" + "=" * 80)
        print("parse_file 结果:")
        print("=" * 80)
        result = arkts_analyzer.parse_file(test_file)
        for cls in result.get('classes', []):
            print(f"类名: {cls.get('name')}")
            print(f"方法数: {len(cls.get('methods', []))}")
            print(f"方法: {cls.get('methods')}")
        
        # 现在测试一个更复杂的文件
        print("\n" + "=" * 80)
        print("测试更复杂的文件:")
        print("=" * 80)
        
        complex_file = os.path.join(temp_dir, "ComplexFile.ets")
        with open(complex_file, "w") as f:
            f.write("""
class ComplexFile {
    complexMethod(param: string) {
        this.helperMethod();
    }
    
    helperMethod() {
        console.log('helper');
    }
    
    anotherMethod(x: number, y: number) {
        this.complexMethod('test');
    }
    
    build() {
        Row() {
            Button('Test');
        }
    }
}
""")
        
        complex_result = arkts_analyzer.parse_file(complex_file)
        for cls in complex_result.get('classes', []):
            print(f"类名: {cls.get('name')}")
            print(f"方法数: {len(cls.get('methods', []))}")
            print(f"方法: {cls.get('methods')}")
        
        print("\n--- 检查括号匹配 ---")
        
        test_content = """
class TestBraceMatch {
    method() {
        {
            nested()
        }
    }
}
"""
        open_idx = test_content.find('{')
        print(f"第一个 { 在位置: {open_idx}")
        
        # 测试我们的括号匹配函数
        analyzer = arkts_analyzer.ArkTSAnalyzer()
        matching_idx = analyzer._find_matching_brace(test_content, open_idx)
        print(f"匹配的 } 在位置: {matching_idx}")
        if matching_idx != -1:
            print(f"匹配的内容: {test_content[open_idx:matching_idx+1]}")
        
        return 0
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        database.set_custom_db_path(None)


if __name__ == "__main__":
    sys.exit(main())
