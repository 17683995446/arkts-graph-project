#!/usr/bin/env python3
import os
import sys
import random
import time
import tempfile
import shutil
import re
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from arkts_analyzer import ArkTSAnalyzer, update_file_knowledge_graph
import database as db
import os

class MegaScaleTest:
    def __init__(self):
        self.test_dir = tempfile.mkdtemp(prefix="mega_scale_test_")
        self.db_path = os.path.join(self.test_dir, "test.db")
        db.set_custom_db_path(self.db_path)
        db.init_database(self.db_path)
        self.stats = {
            "files_created": 0,
            "files_analyzed": 0,
            "classes_found": 0,
            "methods_found": 0,
            "calls_found": 0,
            "errors": 0,
            "test_runs": 0,
            "start_time": time.time()
        }
        print(f"🚀 超大规模测试开始！")
        print(f"📁 测试目录: {self.test_dir}")
        print(f"💾 数据库: {self.db_path}")
        print("=" * 80)
    
    def __del__(self):
        try:
            if os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
        except:
            pass
    
    def generate_random_name(self, prefix="", suffix=""):
        words = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
                 "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho",
                 "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega", "Red", "Blue",
                 "Green", "Yellow", "Purple", "Orange", "Black", "White", "Fast", "Slow",
                 "Smart", "Dumb", "Happy", "Sad", "Big", "Small", "Tall", "Short", "Wide",
                 "Narrow", "Hot", "Cold", "Warm", "Cool", "New", "Old", "First", "Last",
                 "Main", "Helper", "Utils", "Core", "Base", "Super", "Ultra", "Mega",
                 "Hyper", "Extreme", "Final", "Pro", "Lite", "Max", "Min", "Avg"]
        return prefix + random.choice(words) + random.choice(words) + suffix
    
    def generate_random_code(self, class_name, complexity=1):
        methods = []
        calls = set()
        method_names = []
        
        for i in range(random.randint(3, 8) * complexity):
            method_name = self.generate_random_name(suffix="Method")
            method_names.append(method_name)
            
            body_lines = []
            for j in range(random.randint(5, 15) * complexity):
                if random.random() < 0.3:
                    other_method = random.choice(method_names) if method_names and random.random() < 0.5 else self.generate_random_name(suffix="Util")
                    calls.add(other_method)
                    body_lines.append(f"    {other_method}();")
                elif random.random() < 0.2:
                    body_lines.append(f"    let x{j} = {random.randint(0, 100)};")
                elif random.random() < 0.1:
                    body_lines.append(f"    console.log('test {j}');")
                else:
                    body_lines.append(f"    // comment {j}")
            
            methods.append(f"""
  {method_name}() {{
{chr(10).join(body_lines)}
  }}""")
        
        call_list = list(calls)
        random.shuffle(call_list)
        
        code = f"""@Observed
export class {class_name} {{
  private name: string = '{class_name}';
  private value: number = {random.randint(0, 1000)};
{chr(10).join(methods)}

  build() {{
    Column() {{
      Text(this.name)
        .fontSize(20)
        .fontColor(Color.Blue);
    }}
    .width('100%')
    .height('100%');
  }}
}}
"""
        return code, method_names, call_list
    
    def create_massive_project(self, num_files=100, complexity=2):
        print(f"📦 创建超大规模项目，包含 {num_files} 个文件，复杂度级别 {complexity}")
        project_dir = os.path.join(self.test_dir, "massive_project")
        os.makedirs(project_dir, exist_ok=True)
        
        for i in range(num_files):
            class_name = self.generate_random_name(prefix="Class")
            file_name = f"{class_name}.ets"
            file_path = os.path.join(project_dir, file_name)
            code, methods, calls = self.generate_random_code(class_name, complexity)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            self.stats["files_created"] += 1
            
            if (i + 1) % 10 == 0:
                print(f"  ✓ 创建文件 {i + 1}/{num_files}")
        
        print(f"✅ 超大规模项目创建完成！")
        return project_dir
    
    def analyze_directory(self, dir_path):
        """分析目录下所有 .ets 文件"""
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.ets'):
                    full_path = os.path.join(root, file)
                    update_file_knowledge_graph(full_path)
    
    def test_full_analysis(self, project_dir):
        print(f"🔍 开始全面分析大规模项目...")
        start_time = time.time()
        
        try:
            self.analyze_directory(project_dir)
            
            files = db.get_all_files()
            classes = db.get_all_classes()
            methods = db.get_all_methods()
            calls = db.get_all_calls()
            
            self.stats["files_analyzed"] += len(files)
            self.stats["classes_found"] += len(classes)
            self.stats["methods_found"] += len(methods)
            self.stats["calls_found"] += len(calls)
            self.stats["test_runs"] += 1
            
            elapsed = time.time() - start_time
            
            print(f"✅ 分析完成！耗时: {elapsed:.2f}秒")
            print(f"   📄 文件: {len(files)}")
            print(f"   🏗️  类: {len(classes)}")
            print(f"   🔧 方法: {len(methods)}")
            print(f"   🔗 调用关系: {len(calls)}")
            
            return True
        except Exception as e:
            print(f"❌ 分析错误: {e}")
            self.stats["errors"] += 1
            import traceback
            traceback.print_exc()
            return False
    
    def create_chaos_project(self):
        print(f"🌪️  创建混乱场景项目...")
        chaos_dir = os.path.join(self.test_dir, "chaos_project")
        os.makedirs(chaos_dir, exist_ok=True)
        
        chaos_files = [
            ("EmptyClass.ets", """@Observed
export class EmptyClass {
}
"""),
            ("NoMethods.ets", """@Observed
export class NoMethods {
  private x: number = 0;
  private y: string = 'test';
}
"""),
            ("ManyMethods.ets", """@Observed
export class ManyMethods {
  m1() {}
  m2() {}
  m3() {}
  m4() {}
  m5() {}
  m6() {}
  m7() {}
  m8() {}
  m9() {}
  m10() {}
  m11() {}
  m12() {}
  m13() {}
  m14() {}
  m15() {}
  m16() {}
  m17() {}
  m18() {}
  m19() {}
  m20() {}
}
"""),
            ("DeepNesting.ets", """@Observed
export class DeepNesting {
  build() {
    Column() {
      Row() {
        Stack() {
          Column() {
            Text('Deep')
          }
        }
      }
    }
  }
}
"""),
            ("LongFile.ets", self._generate_long_file()),
            ("SpecialChars.ets", """@Observed
export class SpecialChars {
  private data: string = '!@#$%^&*()_+-=[]{}|;:,.<>?';
  test() {
    console.log('测试特殊字符: 中文 日本語 한국어');
  }
  build() {
    Text('测试')
      .fontSize(16);
  }
}
""")
        ]
        
        for filename, content in chaos_files:
            filepath = os.path.join(chaos_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.stats["files_created"] += 1
        
        print(f"✅ 混乱场景项目创建完成！")
        return chaos_dir
    
    def _generate_long_file(self):
        lines = []
        lines.append("@Observed")
        lines.append("export class LongFile {")
        for i in range(100):
            lines.append(f"  private field{i}: number = {i};")
        for i in range(50):
            lines.append(f"""
  method{i}() {{
    console.log('method {i}');
  }}""")
        lines.append("""
  build() {
    Column() {
      Text('Long File')
        .fontSize(20);
    }
  }
}
""")
        return "\n".join(lines)
    
    def test_edge_cases(self):
        print(f"🧪 测试各种边界条件...")
        
        edge_cases = [
            ("EmptyFile", "", "空文件"),
            ("OnlyComments", "// 只有注释\n// 没有代码", "只有注释的文件"),
            ("InvalidSyntax", "class BadClass {", "语法错误的文件"),
            ("MultiClass", """@Observed
export class FirstClass {
  build() { Text('First'); }
}

@Observed
export class SecondClass {
  build() { Text('Second'); }
}
""", "多个类的文件"),
            ("Component", """@Component
export struct MyComponent {
  build() {
    Text('Component');
  }
}
""", "组件而非类"),
        ]
        
        edge_dir = os.path.join(self.test_dir, "edge_cases")
        os.makedirs(edge_dir, exist_ok=True)
        
        for filename, content, desc in edge_cases:
            filepath = os.path.join(edge_dir, filename + ".ets")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.stats["files_created"] += 1
        
        try:
            self.analyze_directory(edge_dir)
            self.stats["test_runs"] += 1
            print(f"✅ 边界条件测试通过！")
            return True
        except Exception as e:
            print(f"❌ 边界条件测试错误: {e}")
            self.stats["errors"] += 1
            return False
    
    def test_incremental_updates(self, project_dir, num_updates=50):
        print(f"🔄 测试增量更新，进行 {num_updates} 次文件更新...")
        
        files = [f for f in os.listdir(project_dir) if f.endswith(".ets")]
        if not files:
            print("⚠️ 没有文件可更新")
            return False
        
        success_count = 0
        for i in range(num_updates):
            try:
                filename = random.choice(files)
                filepath = os.path.join(project_dir, filename)
                
                if random.random() < 0.5:
                    with open(filepath, "a", encoding="utf-8") as f:
                        f.write(f"\n// 更新 {datetime.now()}\n")
                else:
                    class_name = self.generate_random_name(prefix="UpdatedClass")
                    code, _, _ = self.generate_random_code(class_name, complexity=1)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(code)
                
                update_file_knowledge_graph(filepath)
                success_count += 1
                
                if (i + 1) % 10 == 0:
                    print(f"  ✓ 更新 {i + 1}/{num_updates}")
                
                time.sleep(0.01)
                
            except Exception as e:
                print(f"  ❌ 更新 {i + 1} 错误: {e}")
                self.stats["errors"] += 1
        
        self.stats["test_runs"] += 1
        print(f"✅ 增量更新测试完成！成功: {success_count}/{num_updates}")
        return True
    
    def test_rapid_changes(self, project_dir, num_changes=100):
        print(f"⚡ 测试快速连续文件变化...")
        
        filepath = os.path.join(project_dir, "RapidChanges.ets")
        
        for i in range(num_changes):
            try:
                class_name = f"RapidClass{i}"
                code = f"""@Observed
export class {class_name} {{
  private version: number = {i};
  build() {{
    Text('Version {i}');
  }}
}}
"""
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(code)
                
                update_file_knowledge_graph(filepath)
                
                if (i + 1) % 20 == 0:
                    print(f"  ✓ 快速变化 {i + 1}/{num_changes}")
                
            except Exception as e:
                print(f"  ❌ 快速变化 {i + 1} 错误: {e}")
                self.stats["errors"] += 1
        
        self.stats["test_runs"] += 1
        print(f"✅ 快速变化测试完成！")
        return True
    
    def test_database_integrity(self):
        print(f"🔍 检查数据库完整性...")
        
        try:
            files = db.get_all_files()
            classes = db.get_all_classes()
            methods = db.get_all_methods()
            
            for cls in classes:
                if cls['file_id']:
                    file_exists = any(f['id'] == cls['file_id'] for f in files)
                    if not file_exists:
                        print(f"⚠️  警告: 类 {cls['name']} 引用了不存在的文件 ID {cls['file_id']}")
            
            for method in methods:
                if method['class_id']:
                    class_exists = any(c['id'] == method['class_id'] for c in classes)
                    if not class_exists:
                        print(f"⚠️  警告: 方法 {method['name']} 引用了不存在的类 ID {method['class_id']}")
            
            print(f"✅ 数据库完整性检查完成")
            return True
        except Exception as e:
            print(f"❌ 数据库完整性检查错误: {e}")
            self.stats["errors"] += 1
            return False
    
    def print_summary(self):
        elapsed = time.time() - self.stats["start_time"]
        print("\n" + "=" * 80)
        print("📊 超大规模测试总结")
        print("=" * 80)
        print(f"⏱️  总耗时: {elapsed:.2f}秒")
        print(f"📁 创建文件: {self.stats['files_created']}")
        print(f"📄 分析文件: {self.stats['files_analyzed']}")
        print(f"🏗️  发现类: {self.stats['classes_found']}")
        print(f"🔧 发现方法: {self.stats['methods_found']}")
        print(f"🔗 发现调用: {self.stats['calls_found']}")
        print(f"🧪 测试运行: {self.stats['test_runs']}")
        print(f"❌ 错误数: {self.stats['errors']}")
        print("=" * 80)
        
        if self.stats["errors"] == 0:
            print("🎉 完美！所有测试通过！")
        else:
            print(f"⚠️  发现 {self.stats['errors']} 个错误需要处理")
    
    def run_full_suite(self):
        print("🚀 开始完整的超大规模测试套件！\n")
        
        project_dir = self.create_massive_project(num_files=50, complexity=2)
        self.test_full_analysis(project_dir)
        
        chaos_dir = self.create_chaos_project()
        self.test_full_analysis(chaos_dir)
        
        self.test_edge_cases()
        
        self.test_incremental_updates(project_dir, num_updates=30)
        
        self.test_rapid_changes(project_dir, num_changes=50)
        
        self.test_database_integrity()
        
        self.print_summary()
        
        return self.stats["errors"] == 0

def main():
    print("=" * 80)
    print("🚀 ARKTS 知识图谱系统 - 超大规模测试")
    print("=" * 80)
    
    test = MegaScaleTest()
    
    try:
        success = test.run_full_suite()
        
        if success:
            print("\n🎉 超大规模测试全部通过！系统非常稳定！")
            return 0
        else:
            print("\n⚠️  超大规模测试发现了一些问题")
            return 1
            
    except Exception as e:
        print(f"\n💥 测试过程发生严重错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
