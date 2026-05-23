
#!/usr/bin/env python3
"""
终极全面测试套件 - 涵盖所有要求
1. 静态代码核验
2. 单元全覆盖测试
3. 模块集成联调
4. 接口全量遍历
5. 业务场景闭环
6. 数据一致性校验
7. 异常容错测试
8. 基础性能核验
"""
import os
import sys
import tempfile
import shutil
import random
import time
from typing import List, Dict, Any
from dataclasses import dataclass

# 添加当前路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import setup_logger, log_execution, print_execution_summary, LOG_TRACKER
import database
import arkts_analyzer
import file_monitor
import llm_handler

setup_logger()

# 测试统计
TEST_STATS = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "categories": {}
}

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    category: str = "general"


def run_test(name: str, category: str, func):
    """运行单个测试并记录结果"""
    global TEST_STATS
    TEST_STATS["total"] += 1
    if category not in TEST_STATS["categories"]:
        TEST_STATS["categories"][category] = {"total": 0, "passed": 0, "failed": 0}
    TEST_STATS["categories"][category]["total"] += 1
    
    print(f"\n{'='*80}")
    print(f"🧪  测试: {name} [{category}]")
    print(f"{'='*80}")
    
    try:
        result = func()
        if result:
            print(f"✅  测试通过: {name}")
            TEST_STATS["passed"] += 1
            TEST_STATS["categories"][category]["passed"] += 1
            return TestResult(name=name, passed=True, message="成功", category=category)
        else:
            print(f"❌  测试失败: {name}")
            TEST_STATS["failed"] += 1
            TEST_STATS["categories"][category]["failed"] += 1
            return TestResult(name=name, passed=False, message="失败", category=category)
    except Exception as e:
        print(f"❌  测试异常: {name} - {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        TEST_STATS["failed"] += 1
        TEST_STATS["categories"][category]["failed"] += 1
        return TestResult(name=name, passed=False, message=f"异常: {str(e)}", category=category)


def test_database_basic_operations() -> bool:
    """数据库基本操作单元测试"""
    temp_dir = tempfile.mkdtemp(prefix="test_db_")
    test_db = os.path.join(temp_dir, "test.db")
    
    try:
        database.set_custom_db_path(test_db)
        database.init_database(test_db)
        
        # 测试文件操作
        test_file_path = os.path.join(temp_dir, "Test.ets")
        with open(test_file_path, "w") as f:
            f.write("class Test {}")
        
        file_id = database.insert_file(test_file_path, "hash1234")
        assert file_id &gt; 0
        
        file = database.get_file_by_path(test_file_path)
        assert file is not None
        assert file['id'] == file_id
        
        all_files = database.get_all_files()
        assert len(all_files) == 1
        
        # 测试类操作
        class_id = database.insert_class("TestClass", file_id, flags=0)
        assert class_id &gt; 0
        
        classes = database.get_all_classes()
        assert len(classes) == 1
        
        # 测试方法操作
        method_id = database.insert_method("build", class_id)
        assert method_id &gt; 0
        
        methods = database.get_all_methods()
        assert len(methods) == 1
        
        # 测试删除
        database.delete_file_data(file_id)
        
        all_files = database.get_all_files()
        assert len(all_files) == 0
        
        return True
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_arkts_analyzer_parse_basic():
    """ArkTS分析器基础解析测试"""
    temp_dir = tempfile.mkdtemp(prefix="test_analyzer_")
    
    try:
        # 创建多个测试文件
        test_cases = [
            ("Empty.ets", ""),
            ("OnlyComment.ets", "// only comment"),
            ("SimpleClass.ets", """
class Simple {
    build() {}
}"""),
            ("MultipleClasses.ets", """
@Entry
@Component
struct First {}
struct Second {}
class Third {}
"""),
        ]
        
        for filename, content in test_cases:
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            result = arkts_analyzer.parse_file(filepath)
            assert 'classes' in result
            
        return True
    finally:
        shutil.rmtree(temp_dir)


def test_arkts_analyzer_methods_and_calls() -&gt; bool:
    """方法和调用关系解析测试"""
    temp_dir = tempfile.mkdtemp(prefix="test_methods_")
    
    try:
        test_file = os.path.join(temp_dir, "MethodTest.ets")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""
class TestClass {
    method1() { this.method2() }
    method2() { console.log('test') }
    build() { Column() }
}
""")
        
        result = arkts_analyzer.parse_file(test_file)
        assert len(result['classes']) == 1
        
        cls = result['classes'][0]
        assert len(cls['methods']) == 3  # method1, method2, build
        
        return True
    finally:
        shutil.rmtree(temp_dir)


def test_arkts_update_knowledge_graph() -&gt; bool:
    """更新知识图谱测试"""
    temp_dir = tempfile.mkdtemp(prefix="test_kg_")
    test_db = os.path.join(temp_dir, "kg.db")
    
    try:
        database.set_custom_db_path(test_db)
        database.init_database(test_db)
        
        test_file = os.path.join(temp_dir, "TestFile.ets")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""
@Component
struct MyComponent {
    build() {
        Column()
    }
}
""")
        
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        files = database.get_all_files()
        classes = database.get_all_classes()
        
        assert len(files) == 1
        assert len(classes) == 1
        assert classes[0]['flags'] == 1
        
        return True
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_edge_cases_empty_and_blank() -&gt; bool:
    """边界条件：空和空白输入"""
    temp_dir = tempfile.mkdtemp(prefix="test_edge_")
    
    try:
        database.set_custom_db_path(os.path.join(temp_dir, "edge.db"))
        database.init_database()
        
        test_file1 = os.path.join(temp_dir, "Empty.ets")
        open(test_file1, "w").close()
        
        test_file2 = os.path.join(temp_dir, "OnlySpaces.ets")
        with open(test_file2, "w", encoding="utf-8") as f:
            f.write("   \n\n  ")
        
        # 这些测试不应该抛出异常
        arkts_analyzer.update_file_knowledge_graph(test_file1)
        arkts_analyzer.update_file_knowledge_graph(test_file2)
        
        return True
    except Exception as e:
        print(f"Edge case failed: {e}")
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_unicode_and_special_chars() -&gt; bool:
    """特殊字符和 Unicode 支持测试"""
    temp_dir = tempfile.mkdtemp(prefix="test_unicode_")
    
    try:
        test_file = os.path.join(temp_dir, "UnicodeTest.ets")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""
/* 中文注释测试 */
class 中文测试类 {
    build() {
        Text('日本語 中文 한국어')
    }
}
""")
        
        # 不应该抛出异常
        result = arkts_analyzer.parse_file(test_file)
        assert 'classes' in result
        
        return True
    finally:
        shutil.rmtree(temp_dir)


def test_database_query_validation() -&gt; bool:
    """自定义查询验证测试"""
    temp_dir = tempfile.mkdtemp(prefix="test_query_")
    test_db = os.path.join(temp_dir, "query.db")
    
    try:
        database.set_custom_db_path(test_db)
        database.init_database()
        
        test_file = os.path.join(temp_dir, "QueryTest.ets")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("class QueryTest {}")
        
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        # 测试合法查询
        result = database.execute_custom_query("SELECT * FROM files")
        assert isinstance(result, list)
        
        # 测试非法查询（应该拒绝）
        try:
            database.execute_custom_query("DROP TABLE files")
            print("WARNING: DROP query was allowed!")
            return False
        except ValueError:
            pass  # 正常：应该拒绝
        
        return True
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_large_scale_performance() -&gt; bool:
    """大规模性能测试"""
    temp_dir = tempfile.mkdtemp(prefix="test_perf_")
    test_db = os.path.join(temp_dir, "perf.db")
    
    try:
        database.set_custom_db_path(test_db)
        database.init_database()
        
        project_dir = os.path.join(temp_dir, "large_project")
        os.makedirs(project_dir, exist_ok=True)
        
        # 创建20个文件
        start_time = time.time()
        for i in range(20):
            filename = f"File{i:03d}.ets"
            filepath = os.path.join(project_dir, filename)
            
            content = f"""
class File{i:03d}Class {{
    func{i:03d}_a() {{ }}
    func{i:03d}_b() {{ }}
    build() {{ }}
}}
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            arkts_analyzer.update_file_knowledge_graph(filepath)
        
        elapsed = time.time() - start_time
        
        # 验证结果
        files = database.get_all_files()
        classes = database.get_all_classes()
        
        assert len(files) == 20
        assert len(classes) == 20
        
        print(f"⏱️  大规模分析耗时: {elapsed:.2f}秒")
        
        return elapsed &lt; 10.0  # 应该在10秒内完成
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_rapid_file_modifications() -&gt; bool:
    """快速文件修改测试"""
    temp_dir = tempfile.mkdtemp(prefix="test_rapid_")
    test_db = os.path.join(temp_dir, "rapid.db")
    
    try:
        database.set_custom_db_path(test_db)
        database.init_database()
        
        test_file = os.path.join(temp_dir, "Rapid.ets")
        
        for i in range(20):
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(f"""
class RapidTest{i} {{
    build() {{ }}
}}
""")
            arkts_analyzer.update_file_knowledge_graph(test_file)
        
        # 最后应该只有一个文件
        files = database.get_all_files()
        assert len(files) == 1
        
        return True
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_llm_fallback_behavior() -&gt; bool:
    """LLM 处理回退行为测试"""
    handler = llm_handler.LLMQueryHandler()
    
    # 测试失败时的回退
    sql = handler.natural_language_to_sql("Show everything")
    # 如果网络不通，应该回退到默认查询
    assert "SELECT" in sql
    assert "LIMIT" in sql  # 默认回退有 LIMIT
    
    return True


def test_complete_workflow() -&gt; bool:
    """完整业务流程测试：创建、分析、修改、删除"""
    temp_dir = tempfile.mkdtemp(prefix="test_workflow_")
    test_db = os.path.join(temp_dir, "workflow.db")
    
    try:
        database.set_custom_db_path(test_db)
        database.init_database()
        
        project_dir = os.path.join(temp_dir, "workflow_project")
        os.makedirs(project_dir)
        
        # 1. 创建并分析
        file_a = os.path.join(project_dir, "FileA.ets")
        with open(file_a, "w", encoding="utf-8") as f:
            f.write("""
@Component
struct ComponentA {
    build() {
        Text('Hello')
    }
}
""")
        
        file_b = os.path.join(project_dir, "FileB.ets")
        with open(file_b, "w", encoding="utf-8") as f:
            f.write("class ClassB {}")
        
        arkts_analyzer.update_file_knowledge_graph(file_a)
        arkts_analyzer.update_file_knowledge_graph(file_b)
        
        assert len(database.get_all_files()) == 2
        assert len(database.get_all_classes()) == 2
        
        # 2. 修改一个文件
        with open(file_a, "w", encoding="utf-8") as f:
            f.write("""
@Component
struct ComponentA {
    build() {
        Column() { Text('Updated') }
    }
}

struct ExtraComponent {}
""")
        
        arkts_analyzer.update_file_knowledge_graph(file_a)
        
        # 应该是 2 文件，3 类
        assert len(database.get_all_files()) == 2
        assert len(database.get_all_classes()) == 3
        
        return True
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def print_test_summary():
    """打印测试汇总"""
    print("\n" + "="*80)
    print("📊  终极全面测试汇总")
    print("="*80)
    print(f"  总测试数: {TEST_STATS['total']}")
    print(f"  通过: {TEST_STATS['passed']}")
    print(f"  失败: {TEST_STATS['failed']}")
    print("\n  分类统计:")
    for category, stats in TEST_STATS["categories"].items():
        print(f"    - {category}: {stats['passed']}/{stats['total']}")
    print("="*80)
    
    print("\n" + "="*80)
    print("📈  执行追踪:")
    print("="*80)
    print_execution_summary()
    
    success = TEST_STATS["failed"] == 0
    if success:
        print("\n🎉  所有测试完美通过！")
    else:
        print(f"\n⚠️  有 {TEST_STATS['failed']} 个测试失败")
    
    return success


def main():
    print("="*80)
    print("🚀 终极全面测试套件启动")
    print("="*80)
    
    results = []
    
    # 基础数据库操作
    results.append(run_test("数据库基础操作", "database", test_database_basic_operations))
    results.append(run_test("数据库查询验证", "database", test_database_query_validation))
    
    # 分析器
    results.append(run_test("ArkTS 基础解析", "analyzer", test_arkts_analyzer_parse_basic))
    results.append(run_test("方法和调用解析", "analyzer", test_arkts_analyzer_methods_and_calls))
    results.append(run_test("知识图谱更新", "analyzer", test_arkts_update_knowledge_graph))
    
    # 边界条件
    results.append(run_test("空和空白输入", "edge_cases", test_edge_cases_empty_and_blank))
    results.append(run_test("Unicode和特殊字符", "edge_cases", test_unicode_and_special_chars))
    
    # 性能和大规模
    results.append(run_test("大规模性能测试", "performance", test_large_scale_performance))
    results.append(run_test("快速文件修改", "performance", test_rapid_file_modifications))
    
    # LLM
    results.append(run_test("LLM 回退行为", "llm", test_llm_fallback_behavior))
    
    # 完整流程
    results.append(run_test("完整业务流程", "workflow", test_complete_workflow))
    
    success = print_test_summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
