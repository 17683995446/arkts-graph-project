#!/usr/bin/env python3
"""
超级详细深度测试 - 注重每个细节！
测试系统的每一个细节功能和边界情况
"""
import os
import sys
import tempfile
import shutil
import random
import time
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import arkts_analyzer

print("=" * 100)
print("SUPER DETAILED DEEP TESTING - EVERY SINGLE DETAIL!")
print("=" * 100)


def test_detail_1_basic_parsing():
    """测试1: 基础解析 - class和struct"""
    print("\n--- 测试1: 基础解析 class和struct ---")
    temp_dir = tempfile.mkdtemp(prefix="test1_")
    db_path = os.path.join(temp_dir, "test1.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        test_file = os.path.join(temp_dir, "Test1.ets")
        
        # 测试class
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""
class SimpleClass {
    build() { }
}

@Component
class ComponentClass {
    build() { }
}

@Entry
@Component
class EntryComponentClass {
    build() { }
}
""")
        
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        files = database.get_all_files()
        classes = database.get_all_classes()
        
        print(f"  文件数: {len(files)}")
        print(f"  类数: {len(classes)}")
        
        for cls in classes:
            print(f"    - {cls['name']}, flags={cls['flags']}")
        
        assert len(classes) == 3, f"应该找到3个类，找到 {len(classes)}"
        
        print("  ✅ 测试1通过!")
        return True
    except Exception as e:
        print(f"  ❌ 测试1失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_detail_2_method_extraction():
    """测试2: 方法提取 - 所有类型"""
    print("\n--- 测试2: 方法提取 ---")
    temp_dir = tempfile.mkdtemp(prefix="test2_")
    db_path = os.path.join(temp_dir, "test2.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        test_file = os.path.join(temp_dir, "Test2.ets")
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""
class MethodTest {
    // 普通方法
    normalMethod() { }
    
    // 带参数的方法
    methodWithParams(a: number, b: string) { }
    
    // 带返回值的方法
    methodWithReturn(): number { return 1; }
    
    // 异步方法
    async asyncMethod() { }
    
    // build方法
    build() { Column() { } }
    
    // 嵌套方法调用
    caller() {
        this.callee();
    }
    
    callee() { }
}
""")
        
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        classes = database.get_all_classes()
        methods = database.get_all_methods()
        
        print(f"  类数: {len(classes)}")
        print(f"  方法数: {len(methods)}")
        
        for method in methods:
            print(f"    - {method['name']}")
        
        # 应该至少有: normalMethod, methodWithParams, methodWithReturn, asyncMethod, build, caller, callee
        assert len(methods) >= 7, f"应该找到至少7个方法，找到 {len(methods)}"
        
        print("  ✅ 测试2通过!")
        return True
    except Exception as e:
        print(f"  ❌ 测试2失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_detail_3_call_relationships():
    """测试3: 调用关系 - 方法间调用"""
    print("\n--- 测试3: 调用关系 ---")
    temp_dir = tempfile.mkdtemp(prefix="test3_")
    db_path = os.path.join(temp_dir, "test3.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        test_file = os.path.join(temp_dir, "Test3.ets")
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""
class CallTest {
    methodA() {
        this.methodB();
        this.methodC();
    }
    
    methodB() {
        console.log('B');
    }
    
    methodC() {
        console.log('C');
    }
    
    methodD() {
        // 调用不存在的方法 - 应该被忽略
        this.nonExistentMethod();
    }
    
    build() { }
}
""")
        
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        calls = database.get_all_calls()
        
        print(f"  调用关系数: {len(calls)}")
        
        for call in calls:
            print(f"    - {call['caller_id']} -> {call['callee_id']}")
        
        # methodA调用methodB和methodC
        assert len(calls) >= 2, f"应该找到至少2个调用关系，找到 {len(calls)}"
        
        print("  ✅ 测试3通过!")
        return True
    except Exception as e:
        print(f"  ❌ 测试3失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_detail_4_edge_cases():
    """测试4: 边界情况 - 空文件、特殊字符"""
    print("\n--- 测试4: 边界情况 ---")
    temp_dir = tempfile.mkdtemp(prefix="test4_")
    db_path = os.path.join(temp_dir, "test4.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        # 空文件
        f1 = os.path.join(temp_dir, "Empty.ets")
        open(f1, "w").close()
        
        # 只有空格和换行
        f2 = os.path.join(temp_dir, "Spaces.ets")
        with open(f2, "w") as f:
            f.write("   \n\n  \t  \n")
        
        # 只有注释
        f3 = os.path.join(temp_dir, "Comments.ets")
        with open(f3, "w") as f:
            f.write("// single line comment\n/* multi\nline\ncomment */")
        
        # Unicode和特殊字符
        f4 = os.path.join(temp_dir, "Unicode.ets")
        with open(f4, "w", encoding="utf-8") as f:
            f.write("""
class 中文类名 {
    中文方法() {
        Text('中文测试 日本語 한국어');
    }
    build() { }
}
""")
        
        # 分析所有文件 - 不应该崩溃
        for f in [f1, f2, f3, f4]:
            arkts_analyzer.update_file_knowledge_graph(f)
        
        files = database.get_all_files()
        classes = database.get_all_classes()
        
        print(f"  文件数: {len(files)}")
        print(f"  类数: {len(classes)}")
        
        for cls in classes:
            print(f"    - {cls['name']}")
        
        # 应该找到至少中文类
        assert len(classes) >= 1, f"应该找到至少1个类 (中文类)"
        
        print("  ✅ 测试4通过!")
        return True
    except Exception as e:
        print(f"  ❌ 测试4失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_detail_5_file_update():
    """测试5: 文件更新 - 修改文件内容"""
    print("\n--- 测试5: 文件更新 ---")
    temp_dir = tempfile.mkdtemp(prefix="test5_")
    db_path = os.path.join(temp_dir, "test5.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        test_file = os.path.join(temp_dir, "UpdateTest.ets")
        
        # 初始版本
        with open(test_file, "w") as f:
            f.write("class Version1 { build() { } }")
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        files1 = database.get_all_files()
        classes1 = database.get_all_classes()
        print(f"  初始: 文件={len(files1)}, 类={len(classes1)}")
        
        # 更新版本
        with open(test_file, "w") as f:
            f.write("class Version2 { build() { } }\nclass ExtraClass { build() { } }")
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        files2 = database.get_all_files()
        classes2 = database.get_all_classes()
        print(f"  更新后: 文件={len(files2)}, 类={len(classes2)}")
        
        # 应该只有1个文件，但有2个类
        assert len(files2) == 1, f"文件数应该为1，{len(files2)}"
        assert len(classes2) == 2, f"类数应该为2，{len(classes2)}"
        
        print("  ✅ 测试5通过!")
        return True
    except Exception as e:
        print(f"  ❌ 测试5失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_detail_6_hash_change_detection():
    """测试6: Hash变化检测 - 文件未变时跳过"""
    print("\n--- 测试6: Hash变化检测 ---")
    temp_dir = tempfile.mkdtemp(prefix="test6_")
    db_path = os.path.join(temp_dir, "test6.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        test_file = os.path.join(temp_dir, "HashTest.ets")
        
        content = "class HashTest { build() { } }"
        with open(test_file, "w") as f:
            f.write(content)
        
        # 第一次分析
        arkts_analyzer.update_file_knowledge_graph(test_file)
        files1 = database.get_all_files()
        
        # 第二次分析 - 内容没变
        arkts_analyzer.update_file_knowledge_graph(test_file)
        files2 = database.get_all_files()
        
        print(f"  第一次: {len(files1)} 文件")
        print(f"  第二次 (内容未变): {len(files2)} 文件")
        
        # 应该只有1个文件
        assert len(files1) == 1
        assert len(files2) == 1
        
        # 修改内容
        with open(test_file, "w") as f:
            f.write("class HashTest { modified() { } build() { } }")
        
        arkts_analyzer.update_file_knowledge_graph(test_file)
        files3 = database.get_all_files()
        classes3 = database.get_all_classes()
        
        print(f"  修改后: {len(files3)} 文件, {len(classes3)} 类")
        
        # 应该有1个文件，但有2个方法
        assert len(files3) == 1
        assert len(classes3) == 1
        
        print("  ✅ 测试6通过!")
        return True
    except Exception as e:
        print(f"  ❌ 测试6失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_detail_7_database_integrity():
    """测试7: 数据库完整性"""
    print("\n--- 测试7: 数据库完整性 ---")
    temp_dir = tempfile.mkdtemp(prefix="test7_")
    db_path = os.path.join(temp_dir, "test7.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        test_file = os.path.join(temp_dir, "IntegrityTest.ets")
        
        with open(test_file, "w") as f:
            f.write("""
class ClassA {
    methodA() { this.methodB(); }
    methodB() { }
    build() { }
}

class ClassB {
    methodC() { }
    build() { }
}
""")
        
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        # 验证所有数据
        files = database.get_all_files()
        classes = database.get_all_classes()
        methods = database.get_all_methods()
        calls = database.get_all_calls()
        
        print(f"  文件: {len(files)}")
        print(f"  类: {len(classes)}")
        print(f"  方法: {len(methods)}")
        print(f"  调用: {len(calls)}")
        
        # 验证数据一致性
        assert len(files) == 1, "应该有1个文件"
        assert len(classes) == 2, "应该有2个类"
        assert len(methods) >= 5, "应该至少有5个方法"
        
        # 验证外键关系
        for cls in classes:
            file_exists = any(f['id'] == cls['file_id'] for f in files)
            assert file_exists, f"类 {cls['name']} 引用了不存在的文件"
        
        for method in methods:
            class_exists = any(c['id'] == method['class_id'] for c in classes)
            assert class_exists, f"方法 {method['name']} 引用了不存在的类"
        
        print("  ✅ 测试7通过!")
        return True
    except Exception as e:
        print(f"  ❌ 测试7失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_detail_8_query_validation():
    """测试8: 查询验证 - SQL注入防护"""
    print("\n--- 测试8: 查询验证 ---")
    temp_dir = tempfile.mkdtemp(prefix="test8_")
    db_path = os.path.join(temp_dir, "test8.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        test_file = os.path.join(temp_dir, "QueryTest.ets")
        with open(test_file, "w") as f:
            f.write("class QueryTest { build() { } }")
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        # 合法查询
        result = database.execute_custom_query("SELECT * FROM files")
        print(f"  合法查询: {len(result)} 行")
        
        # 尝试危险查询 - 应该被拒绝
        dangerous_queries = [
            "DROP TABLE files",
            "DELETE FROM files",
            "INSERT INTO files VALUES(1, 'test', 'hash')",
            "UPDATE files SET path = 'hacked'",
            "DROP DATABASE knowledge_graph",
        ]
        
        for query in dangerous_queries:
            try:
                database.execute_custom_query(query)
                print(f"  ⚠️  危险查询未被拒绝: {query}")
                return False
            except ValueError:
                print(f"  ✅ 正确拒绝危险查询: {query[:30]}...")
        
        print("  ✅ 测试8通过!")
        return True
    except Exception as e:
        print(f"  ❌ 测试8失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_detail_9_rapid_modifications():
    """测试9: 快速连续修改"""
    print("\n--- 测试9: 快速连续修改 ---")
    temp_dir = tempfile.mkdtemp(prefix="test9_")
    db_path = os.path.join(temp_dir, "test9.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        test_file = os.path.join(temp_dir, "Rapid.ets")
        
        # 快速修改100次
        for i in range(100):
            with open(test_file, "w") as f:
                f.write(f"class Rapid{i} {{ build() {{ }} }}")
            arkts_analyzer.update_file_knowledge_graph(test_file)
        
        files = database.get_all_files()
        
        print(f"  快速修改100次后: {len(files)} 文件")
        
        # 应该只有1个文件
        assert len(files) == 1, f"应该只有1个文件，实际 {len(files)}"
        
        print("  ✅ 测试9通过!")
        return True
    except Exception as e:
        print(f"  ❌ 测试9失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def test_detail_10_complex_nesting():
    """测试10: 复杂嵌套结构"""
    print("\n--- 测试10: 复杂嵌套结构 ---")
    temp_dir = tempfile.mkdtemp(prefix="test10_")
    db_path = os.path.join(temp_dir, "test10.db")
    
    try:
        database.set_custom_db_path(db_path)
        database.init_database(db_path)
        
        test_file = os.path.join(temp_dir, "Nesting.ets")
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""
class DeepNesting {
    level1() {
        Column() {
            Row() {
                Stack() {
                    Column() {
                        this.level2();
                    }
                }
            }
        }
    }
    
    level2() {
        if (true) {
            while (true) {
                for (let i = 0; i < 10; i++) {
                    this.level3();
                }
            }
        }
    }
    
    level3() {
        console.log('deep');
    }
    
    build() { }
}
""")
        
        arkts_analyzer.update_file_knowledge_graph(test_file)
        
        classes = database.get_all_classes()
        methods = database.get_all_methods()
        
        print(f"  类数: {len(classes)}")
        print(f"  方法数: {len(methods)}")
        
        for method in methods:
            print(f"    - {method['name']}")
        
        # 应该有4个方法
        assert len(methods) == 4, f"应该找到4个方法，实际 {len(methods)}"
        
        print("  ✅ 测试10通过!")
        return True
    except Exception as e:
        print(f"  ❌ 测试10失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        database.set_custom_db_path(None)
        shutil.rmtree(temp_dir)


def main():
    tests = [
        ("基础解析 class/struct", test_detail_1_basic_parsing),
        ("方法提取", test_detail_2_method_extraction),
        ("调用关系", test_detail_3_call_relationships),
        ("边界情况", test_detail_4_edge_cases),
        ("文件更新", test_detail_5_file_update),
        ("Hash变化检测", test_detail_6_hash_change_detection),
        ("数据库完整性", test_detail_7_database_integrity),
        ("查询验证", test_detail_8_query_validation),
        ("快速连续修改", test_detail_9_rapid_modifications),
        ("复杂嵌套结构", test_detail_10_complex_nesting),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ 测试异常: {e}")
            results.append((name, False))
            failed += 1
    
    print("\n" + "=" * 100)
    print("SUPER DETAILED TEST SUMMARY")
    print("=" * 100)
    print(f"  Total: {len(tests)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  - {name}: {status}")
    
    print("=" * 100)
    
    if failed == 0:
        print("🎉 ALL SUPER DETAILED TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  {failed} tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
