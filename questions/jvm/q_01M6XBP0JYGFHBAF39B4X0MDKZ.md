---
id: q_01M6XBP0JYGFHBAF39B4X0MDKZ
title: 逃逸分析能带来哪些优化？
type: concept
difficulty: medium
importance: 1
category: jvm
tags: [memory-area, bytecode-execution]
prerequisites: [q_01M6XBG7C8KPSDAX0XYG3M9X25, q_01M6XBGEDG1D442TEBT506XS3M]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "Oracle JDK 8 文档：Java HotSpot VM Performance Enhancements（Escape Analysis）", url: "https://docs.oracle.com/javase/8/docs/technotes/guides/vm/performance-enhancements-7.html" }
  - { title: "JDK 21 java 命令手册：-XX:+DoEscapeAnalysis", url: "https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html" }
---

## 一句话
对象没有逃逸时，JIT 可以把它拆成基本变量（标量替换）、去掉不必要的加锁（锁消除）；传统说法里的"栈上分配"，HotSpot 实际上是通过标量替换实现的。

## 要点
- [kp1|3] 标量替换：把没逃逸的对象拆成几个基本变量，不再真的创建对象
- [kp2|3] 锁消除：对象只被一个线程用，上面的 synchronized 可以去掉
- [kp3|2] 栈上分配只是理论说法，HotSpot 靠标量替换达到类似效果
- [kp4|2] 这些优化由 JIT 编译器在热点代码上完成
- [kp5] 逃逸分析开关是 `-XX:+DoEscapeAnalysis`，默认开启

## 详解
### 先搞懂：既然没人会用，就别真造了
想象你在算一道题，需要临时用一张便签纸记下两个数，算完就扔。你完全可以直接在脑子里记这两个数，没必要真拿出一张纸。

对象也是：一个对象只在方法里用，没有逃逸，编译器就可以不真的创建它，而是把它的字段当作普通局部变量。这就是逃逸分析带来的好处。

后文用到的术语：
- **逃逸分析**：判断对象是否会被方法外、线程外访问。
- **标量**：不能再拆分的基本数据，如 int、long。
- **聚合量**：能继续拆分的数据，如对象。
- **JIT**：运行时把热点字节码编译成机器码的编译器。

### 标量替换：把对象拆成基本变量
对象没有逃逸时，JIT 把它拆成各个字段对应的局部变量，对象本身不再在堆上创建。好处是少了对象创建，也少了之后的垃圾回收压力。

### 锁消除：只有一个线程用，加锁没意义
如果一个对象没有线程逃逸，它身上的 `synchronized` 就不可能有竞争，JIT 可以直接去掉这个锁。比如方法里创建的局部 `StringBuffer`，它的同步方法就可能被优化掉。

### 栈上分配：理论上的做法
理论上，没逃逸的对象可以直接放在栈上，方法结束随栈帧销毁，不需要 GC。但是 HotSpot 并没有实现真正的栈上分配，而是用标量替换达到类似效果。面试中先说明这一点更严谨。

### 进阶：触发条件与限制（基础薄弱可先跳过）
- 优化只发生在被 JIT 编译的热点代码上，刚启动或很少执行的代码不会触发。
- 对象太复杂、逃逸分析判断不了时，不会优化。
- 这些优化是编译器自行决定的，不保证一定发生，也不能靠它写正确性依赖的代码。

## 示例
```java
// 可能被标量替换：p 不逃逸，JIT 可以不创建对象
static int sum() {
    Point p = new Point(1, 2);
    return p.x() + p.y();
}
record Point(int x, int y) {}
```

## 易错点
- 说 HotSpot 把对象分配在栈上；实际是标量替换，而不是真正的栈上分配
- 以为逃逸分析在编译 Java 源码时就完成了；它是运行时 JIT 做的
- 以为所有局部对象都会被优化；这依赖 JIT 的判断，不保证发生

## 追问
### [f1] 标量替换和栈上分配的区别？
栈上分配是把整个对象放到栈上；标量替换是不创建对象，把它的字段拆成局部变量。HotSpot 采用后者。

### [f2] 逃逸分析是在什么时候做的？
在 JIT 编译热点代码的时候，用来判断对象是否逃逸，然后决定是否做标量替换和锁消除。
