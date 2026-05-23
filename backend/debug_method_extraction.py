
#!/usr/bin/env python3
"""
调试方法提取失败问题
"""
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import arkts_analyzer


def main():
    temp_dir = tempfile.mkdtemp(prefix="debug_")
    db_path = os.path.join(temp_dir, "debug.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        # 创建一个简单的测试文件
        test_file = os.path.join(temp_dir, "TestDebug.ets")
        
        with open(test_file, "w") as f:
            f.write("""
class TestClass {
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
        
        print("=" * 80)
        print("调试方法提取")
        print("=" * 80)
        print(f"\n测试文件内容:")
        print(open(test_file).read())
        
        # 测试parse_file
        print("\n--- parse_file 结果 ---")
        result = arkts_analyzer.parse_file(test_file)
        print(f"解析结果: {result}")
        for cls in result.get('classes', []):
            print(f"类: {cls.get('name')}")
            print(f"方法: {cls.get('methods')}")
            print(f"调用: {cls.get('calls')}")
        
        # 测试update_file_knowledge_graph
        print("\n--- update_file_knowledge_graph 结果 ---")
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        all_classes = database.get_all_classes()
        all_methods = database.get_all_methods()
        print(f"数据库中的类: {len(all_classes)}")
        for cls in all_classes:
            print(f"  {cls}")
        print(f"数据库中的方法: {len(all_methods)}")
        for meth in all_methods:
            print(f"  {meth}")
        
        return 0
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    sys.exit(main())
