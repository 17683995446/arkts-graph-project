
@Component
struct GreetingCard {
  @Prop name: string = ''

  build() {
    Column() {
      Text(`Hello, ${this.name}!`)
        .fontSize(24)
        .padding(20)
      
      Counter()
    }
    .border({ width: 2, color: '#333' })
    .borderRadius(10)
    .padding(20)
  }
}

@Component
struct Counter {
  @State value: number = 0

  build() {
    Row() {
      Button('-')
        .onClick(() =&gt; {
          this.decrement()
        })
      
      Text(`${this.value}`)
        .fontSize(30)
        .margin({ left: 20, right: 20 })
      
      Button('+')
        .onClick(() =&gt; {
          this.increment()
        })
    }
  }

  increment() {
    this.value++
  }

  decrement() {
    this.value--
  }
}
