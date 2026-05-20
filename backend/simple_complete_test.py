
#!/usr/bin/env python3
"""
简化但完整的测试套件
"""
import os
import sys
import tempfile
import shutil
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
import arkts_analyzer
import llm_handler

def test_database_basic():
    """测试数据库基础功能"""
    temp_dir = tempfile.mkdtemp(prefix="test_db_")
    test_db = os.path.join(temp_dir, "test.db")
    try:
        database.set_custom_db_path(test_db)
        database.init_database(test_db)
        
        test_file = os.path.join(temp_dir, "Test.ets")
        with open(test_file, "w") as f:
            f.write("class Test {}")
        
        # 测试文件插入
        file_id = database.insert_file(test_file, "hash1234")
        print(f"  插入文件，ID: {file_id}")
        
        # 测试文件查询
        file = database.get_file_by_path(test_file)
        print(f"  查询文件: {file}")
        
        # 测试类插入
        class_id = database.insert_class("TestClass", file_id, 0)
        print(f"  插入类，ID: {class_id}")
        
        # 测试方法插入
        method_id = database.insert_method("build", class_id)
        print(f"  插入方法，ID: {method_id}")
        
        # 测试删除
        database.delete_file_data(file_id)
        print("  删除数据成功")
        
        files = database.get_all_files()
        assert len(files) == 0
        
        print("✅ 数据库基础测试通过")
        return True
    except Exception as e:
        print(f"❌ 数据库基础测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_arkts_analyzer():
    """测试ArkTS分析器"""
    temp_dir = tempfile.mkdtemp(prefix="test_analyzer_")
    test_db = os.path.join(temp_dir, "test.db")
    
    try:
        database.set_custom_db_path(test_db)
        database.init_database()
        
        # 创建测试文件
        test_file = os.path.join(temp_dir, "MyComponent.ets")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""
@Component
struct MyComponent {
    build() {
        Column() {
            Text('Hello')
        }
    }
}

class Helper {
    doSomething() {}
}
""")
        
        # 解析
        result = arkts_analyzer.parse_file(test_file)
        print(f"  解析结果: {result}")
        assert len(result['classes']) == 2
        
        # 更新知识图谱
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        # 验证
        files = database.get_all_files()
        classes = database.get_all_classes()
        methods = database.get_all_methods()
        
        print(f"  文件数: {len(files)}, 类数: {len(classes)}, 方法数: {len(methods)}")
        
        assert len(files) == 1
        assert len(classes) == 2
        
        print("✅ ArkTS分析器测试通过")
        return True
    except Exception as e:
        print(f"❌ ArkTS分析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_edge_cases():
    """测试边界条件"""
    temp_dir = tempfile.mkdtemp(prefix="test_edge_")
    test_db = os.path.join(temp_dir, "test.db")
    
    try:
        database.set_custom_db_path(test_db)
        database.init_database()
        
        # 空文件
        empty_file = os.path.join(temp_dir, "Empty.ets")
        open(empty_file, "w").close()
        arkts_analyzer.update_file_knowledge_graph(empty_file)
        
        # 只有注释
        comment_file = os.path.join(temp_dir, "Comment.ets")
        with open(comment_file, "w", encoding="utf-8") as f:
            f.write("// Only comments\n/* more comments */")
        arkts_analyzer.update_file_knowledge_graph(comment_file)
        
        # 特殊字符
        unicode_file = os.path.join(temp_dir, "Unicode.ets")
        with open(unicode_file, "w", encoding="utf-8") as f:
            f.write("class UnicodeClass { build() { Text('中文测试') } }")
        arkts_analyzer.update_file_knowledge_graph(unicode_file)
        
        print("✅ 边界条件测试通过")
        return True
    except Exception as e:
        print(f"❌ 边界条件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_query_validation():
    """测试查询验证"""
    temp_dir = tempfile.mkdtemp(prefix="test_query_")
    test_db = os.path.join(temp_dir, "test.db")
    
    try:
        database.set_custom_db_path(test_db)
        database.init_database()
        
        test_file = os.path.join(temp_dir, "QTest.ets")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("class QTest {}")
        
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        # 合法查询
        result = database.execute_custom_query("SELECT * FROM files")
        print(f"  合法查询结果: {len(result)} 行")
        
        # 非法查询（应该拒绝）
        try:
            database.execute_custom_query("DROP TABLE files")
            print("  ⚠️  DROP查询未被拒绝！")
            return False
        except ValueError:
            print("  非法查询被正确拒绝")
        
        print("✅ 查询验证测试通过")
        return True
    except Exception as e:
        print(f"❌ 查询验证测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_performance():
    """测试基本性能"""
    temp_dir = tempfile.mkdtemp(prefix="test_perf_")
    test_db = os.path.join(temp_dir, "test.db")
    
    try:
        database.set_custom_db_path(test_db)
        database.init_database()
        
        project_dir = os.path.join(temp_dir, "project")
        os.makedirs(project_dir, exist_ok=True)
        
        start = time.time()
        
        # 创建10个文件
        for i in range(10):
            fpath = os.path.join(project_dir, f"File{i:02d}.ets")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(f"""
class File{i:02d}Class {{
    func{i:02d}_a() {{ }}
    func{i:02d}_b() {{ }}
    build() {{ }}
}}
""")
            arkts_analyzer.update_file_knowledge_graph(fpath)
        
        elapsed = time.time() - start
        print(f"⏱️  分析10个文件耗时: {elapsed:.2f}秒")
        
        assert len(database.get_all_files()) == 10
        assert len(database.get_all_classes()) == 10
        
        print("✅ 性能测试通过")
        return True
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_llm_fallback():
    """测试LLM回退功能"""
    try:
        handler = llm_handler.LLMQueryHandler()
        sql = handler.natural_language_to_sql("Show all")
        
        # 即使网络不通，也应该返回默认查询
        assert "SELECT" in sql
        print(f"  LLM返回SQL: {sql}")
        
        print("✅ LLM回退测试通过")
        return True
    except Exception as e:
        print(f"❌ LLM回退测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_workflow():
    """完整工作流测试"""
    temp_dir = tempfile.mkdtemp(prefix="test_workflow_")
    test_db = os.path.join(temp_dir, "test.db")
    
    try:
        database.set_custom_db_path(test_db)
        database.init_database()
        
        project_dir = os.path.join(temp_dir, "project")
        os.makedirs(project_dir)
        
        # 1. 初始创建
        f1 = os.path.join(project_dir, "File1.ets")
        with open(f1, "w", encoding="utf-8") as f:
            f.write("class C1 { build() {} }")
        
        f2 = os.path.join(project_dir, "File2.ets")
        with open(f2, "w", encoding="utf-8") as f:
            f.write("@Component struct Comp1 { build() {} }")
        
        arkts_analyzer.update_file_knowledge_graph(f1)
        arkts_analyzer.update_file_knowledge_graph(f2)
        
        assert len(database.get_all_files()) == 2
        assert len(database.get_all_classes()) == 2
        
        # 2. 修改文件
        with open(f1, "w", encoding="utf-8") as f:
            f.write("class C1 { build() {} }\nclass C2 {}")
        
        arkts_analyzer.update_file_knowledge_graph(f1)
        
        assert len(database.get_all_files()) == 2
        assert len(database.get_all_classes()) == 3
        
        print("✅ 完整工作流测试通过")
        return True
    except Exception as e:
        print(f"❌ 完整工作流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def main():
    print("="*80)
    print("🚀 系统全面测试启动")
    print("="*80)
    
    tests = [
        ("数据库基础功能", test_database_basic),
        ("ArkTS分析器", test_arkts_analyzer),
        ("边界条件测试", test_edge_cases),
        ("查询验证", test_query_validation),
        ("性能测试", test_performance),
        ("LLM回退", test_llm_fallback),
        ("完整工作流", test_complete_workflow),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n{'='*80}")
        print(f"🧪  测试: {name}")
        print('='*80)
        
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌  测试异常: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*80)
    print("📊  测试汇总")
    print("="*80)
    print(f"  总测试: {len(tests)}")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    
    if failed == 0:
        print("\n🎉 所有测试完美通过！")
        return 0
    else:
        print(f"\n⚠️  {failed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
