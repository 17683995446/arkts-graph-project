
#!/usr/bin/env python3
"""
基于第一性原理的真实项目测试 - 超大规模真实ArkTS项目模拟！
"""
import tempfile
import os
from pathlib import Path
import database
import arkts_analyzer

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def create_real_arkts_project(temp_dir):
    """创建一个真实的大规模ArkTS项目模拟！"""
    project_path = Path(temp_dir) / "my_arkts_app"
    project_path.mkdir(exist_ok=True)
    
    src_dir = project_path / "src"
    src_dir.mkdir(exist_ok=True)
    
    (src_dir / "pages").mkdir(exist_ok=True)
    (src_dir / "components").mkdir(exist_ok=True)
    (src_dir / "utils").mkdir(exist_ok=True)
    (src_dir / "models").mkdir(exist_ok=True)
    
    # 创建真实的Entry页面文件
    main_page = src_dir / "pages" / "Index.ets"
    main_page.write_text("""
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
""", encoding='utf-8')
    
    product_list_file = src_dir / "components" / "ProductList.ets"
    product_list_file.write_text("""
@Component
struct ProductList {
  @State products: Product[] = []
  @State loading: boolean = true

  async aboutToAppear() {
    await this.loadProducts()
  }

  async loadProducts() {
    this.products = await getProductsFromApi()
    this.loading = false
  }

  build() {
    if (this.loading) {
      LoadingIndicator()
    } else {
      List() {
        ForEach(this.products, (product: Product) => {
          ListItem() {
            ProductCard({ product: product })
          }
        })
      }
      .width('100%')
      .height('100%')
    }
  }
}

@Component
struct ProductCard {
  @Prop product: Product

  build() {
    Column() {
      Text(this.product.name)
        .fontSize(20)
      
      Text(`${this.product.price}`)
        .fontSize(16)
        .color(Color.Grey)
      
      Button('Add to cart')
        .onClick(() => {
          addToCart(this.product)
        })
    }
    .width('100%')
    .padding(15)
    .backgroundColor(Color.White)
    .borderRadius(8)
    .shadow({ radius: 3 })
  }
}
""", encoding='utf-8')
    
    # 创建产品API文件
    api_file = src_dir / "utils" / "ProductApi.ets"
    api_file.write_text("""
export class ProductApi {
  async getProducts(): Promise<Product[]> {
    let response = await fetch('https://api.example.com/products')
    let data = await response.json()
    return data.products as Product[]
  }
  
  async getProduct(id: number): Promise<Product> {
    let response = await fetch(`https://api.example.com/products/${id}`)
    let data = await response.json()
    return data as Product
  }
  
  async addToCart(product: Product): Promise<void> {
    await fetch('https://api.example.com/cart', {
      method: 'POST',
      body: JSON.stringify(product)
    })
  }
}

export function getProductsFromApi(): Promise<Product[]> {
  let api = new ProductApi()
  return api.getProducts()
}

export function addToCart(product: Product): Promise<void> {
  let api = new ProductApi()
  return api.addToCart(product)
}
""", encoding='utf-8')
    
    # 创建产品模型
    model_file = src_dir / "models" / "Product.ets"
    model_file.write_text("""
export interface Product {
  id: number
  name: string
  price: number
  description: string
}

export class ProductModel {
  id: number
  name: string
  price: number
  description: string
  
  constructor(id: number, name: string, price: number, desc: string) {
    this.id = id
    this.name = name
    this.price = price
    this.description = desc
  }
  
  getFormattedPrice(): string {
    return `${this.price} USD`
  }
  
  isAvailable(): boolean {
    return this.price > 0
  }
}
""", encoding='utf-8')
    
    # 创建另一个页面
    cart_page = src_dir / "pages" / "Cart.ets"
    cart_page.write_text("""
@Component
@Entry
struct CartPage {
  @State cartItems: CartItem[] = []
  @State total: number = 0

  build() {
    Column() {
      Text('Your Cart')
        .fontSize(28)
        .fontWeight(FontWeight.Bold)
      
      if (this.cartItems.length === 0) {
        Text('Your cart is empty')
          .fontSize(16)
          .color(Color.Grey)
      } else {
        List() {
          ForEach(this.cartItems, (item: CartItem) => {
            ListItem() {
              CartItemView({ item: item })
            }
          })
        }
        
        Text(`Total: ${this.total} USD`)
          .fontSize(24)
          .fontWeight(FontWeight.Bold)
          .margin(20)
      }
    }
    .width('100%')
    .height('100%')
    .padding(20)
  }
  
  calculateTotal(): void {
    this.total = this.cartItems
      .map(item => item.price * item.quantity)
      .reduce((sum, price) => sum + price, 0)
  }
}

@Component
struct CartItemView {
  @Prop item: CartItem
  
  build() {
    Row() {
      Text(this.item.product.name)
      
      Text(`${this.item.product.price}`)
      
      Text('x')
      
      Text(`${this.item.quantity}`)
    }
  }
}

interface CartItem {
  product: Product
  quantity: number
}
""", encoding='utf-8')
    
    # 加载指示器
    loading_file = src_dir / "components" / "LoadingIndicator.ets"
    loading_file.write_text("""
@Component
struct LoadingIndicator {
  build() {
    Column() {
      LoadingProgress()
        .width(60)
        .height(60)
        .color(Color.Blue)
      
      Text('Loading...')
        .fontSize(16)
        .margin(10)
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
""", encoding='utf-8')
    
    print(f"✅ 创建了真实ArkTS项目在: {project_path}")
    return project_path

def test_real_project():
    """测试真实项目 - 这是基于第一性原理的测试！"""
    print_header("🚀 真实项目测试 - 第一性原理验证")
    
    with tempfile.TemporaryDirectory(prefix="arkts_real_test_") as temp_dir:
        
        # 创建真实项目
        project_path = create_real_arkts_project(temp_dir)
        
        # 初始化数据库
        db_path = Path(temp_dir) / "real_test.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        
        # 扫描所有.ets文件
        ets_files = list(project_path.rglob("*.ets"))
        print(f"\n发现 {len(ets_files)} 个ArkTS源文件!")
        
        total_classes = 0
        total_methods = 0
        total_calls = 0
        total_components = 0
        
        # 处理每一个文件
        for ets_file in ets_files:
            print(f"\n📄 处理文件: {ets_file.relative_to(project_path)}")
            
            # 解析并更新知识图谱
            try:
                arkts_analyzer.update_file_knowledge_graph(str(ets_file))
                
                # 获取这个文件的结果
                file_record = database.get_file_by_path(str(ets_file))
                if file_record:
                    file_id = file_record["id"]
                    classes_for_file = [c for c in database.get_all_classes() if c["file_id"] == file_id]
                    
                    num_classes = len(classes_for_file)
                    num_methods = sum(len([m for m in database.get_all_methods() if m["class_id"] == c["id"]]) for c in classes_for_file)
                    
                    print(f"   - 找到 {num_classes} 个类/组件")
                    print(f"   - 找到 {num_methods} 个方法")
                    
                    total_classes += num_classes
                    total_methods += num_methods
                
            except Exception as e:
                print(f"❌ 文件处理错误: {e}")
                import traceback
                traceback.print_exc()
        
        # 最终数据库状态检查
        print_header("📊 最终知识图谱状态")
        
        all_files = database.get_all_files()
        all_classes = database.get_all_classes()
        all_methods = database.get_all_methods()
        all_calls = database.get_all_calls()
        all_components = database.get_all_components()
        
        print(f"📄 文件: {len(all_files)}")
        print(f"🏗️  类/组件: {len(all_classes)}")
        print(f"⚡ 方法: {len(all_methods)}")
        print(f"🔗 调用关系: {len(all_calls)}")
        print(f"🧩 组件关系: {len(all_components)}")
        
        # 检查是否发现Bug
        print_header("🔍 基于第一性原理的Bug检查")
        
        # 1. 调用关系构建检查
        if len(all_calls) == 0:
            print("⚠️ 警告: 没有找到任何调用关系!")
            print("   🐛 发现Bug: update_file_knowledge_graph中的调用构建逻辑有问题!")
            return False
        else:
            print("✅ 调用关系正常构建!")
        
        if len(all_components) == 0:
            print("⚠️ 警告: 没有找到任何组件关系!")
            return False
        else:
            print("✅ 组件关系正常构建!")
        
        print("\n🎉 真实项目测试完成!")
        
        if len(all_calls) == 0 or len(all_components) == 0:
            print("🐛 发现关键Bug! 需要修复!")
            return False
        
        return True

if __name__ == "__main__":
    test_real_project()
