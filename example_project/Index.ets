
@Entry
@Component
struct Index {
  @State message: string = 'Hello World'
  @State count: number = 0

  build() {
    Column() {
      Text(this.message)
        .fontSize(50)
        .fontWeight(FontWeight.Bold)
      
      Button('Increment')
        .onClick(() =&gt; {
          this.incrementCount()
        })
      
      Text(`Count: ${this.count}`)
        .fontSize(30)
      
      GreetingCard(name='ArkTS')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }

  incrementCount() {
    this.count++
  }
}
