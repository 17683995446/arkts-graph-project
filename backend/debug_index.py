
#!/usr/bin/env python3
"""
专门调试 Index.ets 文件！
"""
import tempfile
from pathlib import Path
import database
import arkts_analyzer

def debug_index():
    index_content = """
@Component
@Entry
struct Index {
  @State message: string = 'Hello World'
  @State count: number = 0

  build() {
    Column() {
      Text(this.message)
        .fontSize(30)
        .fontWeight(FontWeight.Bold)
      
      Button('Click me')
        .onClick(() => {
          this.count++
        })
      
      Counter({ initialCount: this.count })
      
      ProductList()
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}

struct Counter {
  @Prop initialCount: number
  @State localCount: number = 0

  aboutToAppear() {
    this.localCount = this.initialCount
  }

  build() {
    Row() {
      Button('-')
        .onClick(() => {
          this.decrement()
        })
      
      Text(`${this.localCount}`)
        .fontSize(24)
      
      Button('+')
        .onClick(() => {
          this.increment()
        })
    }
    .padding(20)
  }

  increment() {
    this.localCount++
  }

  decrement() {
    this.localCount--
  }
}
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ets', delete=False, encoding='utf-8') as f:
        f.write(index_content)
        temp_path = Path(f.name)
    
    print("=== 正在分析 Index.ets ===")
    result = arkts_analyzer.parse_file(str(temp_path))
    for cls in result['classes']:
        print(f"  🏗️  {cls['name']} - 组件: {cls['is_component']}")
        print(f"    方法: {cls['methods']}")
        print(f"    子组件: {cls['child_components']}")
        print(f"    调用: {cls['calls']}")
    
    print("\n=== 现在尝试构建知识图谱 ===")
    db_path = temp_path.parent / "debug_db.sqlite"
    database.set_custom_db_path(str(db_path))
    database.init_database()
    
    print(f"数据库文件: {db_path}")
    arkts_analyzer.update_file_knowledge_graph(str(temp_path))
    
    print("\n=== 数据库内容 ===")
    classes = database.get_all_classes()
    components = database.get_all_components()
    calls = database.get_all_calls()
    
    print(f"类: {len(classes)}")
    print(f"组件关系: {len(components)}")
    print(f"调用关系: {len(calls)}")
    print("\n组件关系:")
    for comp in components:
        print(f"  {comp}")

if __name__ == "__main__":
    debug_index()
