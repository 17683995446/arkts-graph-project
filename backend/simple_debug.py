
#!/usr/bin/env python3
"""
简单调试 - 定位方法提取问题
"""
import os
import sys
import tempfile
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import arkts_analyzer


def main():
    temp_dir = tempfile.mkdtemp(prefix="simple_debug_")
    
    try:
        test_file = os.path.join(temp_dir, "SimpleTest.ets")
        
        with open(test_file, "w") as f:
            f.write("""
class SimpleTest {
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
        
        print("=" * 100)
        print("调试分析过程")
        print("=" * 100)
        
        # 手动测试解析过程
        with open(test_file, 'r') as f:
            content = f.read()
            print(f"\n完整内容:\n{repr(content)}")
        
        # 测试类匹配
        class_pattern = r'(?:@Component\s+)?(?:@Entry\s+)?struct\s+(\w+)|class\s+(\w+)'
        matches = list(re.finditer(class_pattern, content))
        print(f"\n匹配到的类模式: {len(matches)}")
        for i, m in enumerate(matches):
            print(f"  [{i}] match={m}, groups={m.groups()}")
        
        # 测试我们的 analyzer
        analyzer = arkts_analyzer.ArkTSAnalyzer()
        classes = analyzer.analyze_file(test_file)
        print(f"\nanalyze_file 找到 {len(classes)} 个类")
        for cls in classes:
            print(f"  类名: {cls.name}")
            print(f"  方法数: {len(cls.methods)}, 方法: {cls.methods}")
        
        return 0
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
