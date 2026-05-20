
#!/usr/bin/env python3
"""
简单的调试测试！
"""
import tempfile
from pathlib import Path
import database
import arkts_analyzer


def test_simple():
    """简单测试！"""
    # 创建一个极其简单的测试文件
    test_content = """
@Component
struct Main {
  build() {
    MyComponent()
  }
}

struct MyComponent {
  build() {
    Column()
  }
}
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ets", delete=False, encoding="utf-8") as f:
        f.write(test_content)
        temp_file = Path(f.name)
    
    print("=== 测试文件内容 ===\n")
    print(test_content)
    print("\n=== 开始解析 ===\n")
    
    # 初始化数据库
    db_path = temp_file.parent / "debug_test.db"
    database.set_custom_db_path(str(db_path))
    database.init_database()
    
    # 解析
    result = arkts_analyzer.parse_file(str(temp_file))
    print("解析结果:")
    for cls in result["classes"]:
        print(f"  类: {cls['name']}, 组件: {cls['is_component']}")
        print(f"    方法: {cls['methods']}")
        print(f"    调用: {cls['calls']}")
        print(f"    子组件: {cls['child_components']}")
    
    # 更新知识图谱
    print("\n=== 更新知识图谱 ===\n")
    arkts_analyzer.update_file_knowledge_graph(str(temp_file))
    
    print("\n=== 最终数据库状态 ===\n")
    all_files = database.get_all_files()
    all_classes = database.get_all_classes()
    all_components = database.get_all_components()
    all_calls = database.get_all_calls()
    
    print(f"文件数: {len(all_files)}")
    print(f"类数: {len(all_classes)}")
    print(f"组件关系: {len(all_components)}")
    print(f"调用关系: {len(all_calls)}")
    for comp in all_components:
        print(f"  组件关系: {comp}")
    
    print("\n=== 完成 ===")


if __name__ == "__main__":
    test_simple()
