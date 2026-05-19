
#!/usr/bin/env python3
"""
调试组件关系问题！
"""
import tempfile
from pathlib import Path
import arkts_analyzer

def debug_parse():
    # 简单测试文件！
    test_content = """
@Component
@Entry
struct Index {
  @State count: number = 0
  build() {
    Column() {
      Counter()
      ProductList()
    }
  }
}

struct Counter {
  build() {
    Button('test')
  }
  
  increment() {}
}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ets', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        temp_path = Path(f.name)
    
    print(f"调试测试文件: {temp_path}")
    print("\n分析结果：")
    result = arkts_analyzer.parse_file(str(temp_path))
    
    for cls in result['classes']:
        print(f"  📦 类: {cls['name']}, 组件: {cls['is_component']}")
        print(f"    - 方法: {cls['methods']}")
        print(f"    - 调用: {cls['calls']}")
        print(f"    - 子组件: {cls['child_components']}")
    
    print("\n" + "="*80)
    print("✅ 调试结束！")

if __name__ == "__main__":
    debug_parse()
