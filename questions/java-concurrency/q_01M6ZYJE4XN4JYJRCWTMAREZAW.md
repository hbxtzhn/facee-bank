---
id: q_01M6ZYJE4XN4JYJRCWTMAREZAW
title: Java 中怎么保证原子性、可见性和有序性？
type: concept
difficulty: medium
importance: 3
category: java-concurrency
tags: [memory-model, synchronized]
prerequisites: [q_01M6XBGNRM8ZXT4BFXMFFB3T5V, q_01M6XBP39M3ZKGHE87ZQHE9Y0M]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "Java 语言规范 SE 21：17.4.5 Happens-before Order、17.5 final Field Semantics、17.7 Non-Atomic Treatment of double and long", url: "https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html" }
  - { title: "JSR-133 FAQ", url: "https://www.cs.umd.edu/~pugh/java/memoryModel/jsr-133-faq.html" }
---

## 一句话
原子性靠 synchronized 或原子类，可见性靠 volatile、synchronized 和 final，有序性靠 volatile 或 synchronized；synchronized 三个都能保证，volatile 管不了原子性。

## 要点
- [kp1|3] 原子性：用 synchronized、Lock 或 AtomicInteger 等原子类保证
- [kp2|3] 可见性：volatile、synchronized、final 都能保证
- [kp3|2] 有序性：volatile 禁止特定重排，synchronized 让同步块内串行执行
- [kp4|2] volatile 不保证复合操作的原子性，比如 i++
- [kp5] synchronized 三大特性都能保证，但开销比 volatile 大

## 详解
### 先搞懂：并发的三类麻烦
可以用「多人同时改一份在线文档」来类比这三个麻烦：

- **原子性**：一次修改要么整体完成，要么没发生。就像「删除一行再插入一行」不能只做一半让别人看到。
- **可见性**：我改完了，别人要能看到。别人看到的不能是几分钟前的旧版本。
- **有序性**：代码写的顺序和实际执行顺序，在别的线程看来不能乱到出错。

后文用到的几个词：
- **指令重排**：编译器或 CPU 为了效率调整指令执行顺序，单线程下结果不变，多线程下可能让别人看到「乱序」的中间状态。
- **互斥**：同一时刻只有一个线程执行某段代码。

### 原子性：别被打断
- `synchronized` / `Lock`：同一时刻只有一个线程执行同步块，整段代码就不会被打断；
- `AtomicInteger` 等原子类：用 CAS 保证单个变量的更新是原子的。

单次读写基本类型变量，Java 本身已经保证原子。非 volatile 的 long、double 除外。但 `i++` 这类「读—改—写」需要上面的手段。

### 可见性：改完能看到
- `volatile`：写完立即刷回主内存，读时总读最新值；
- `synchronized`：退出同步块时把修改刷回主内存，进入时重新读取；
- `final`：对象构造完成后，final 字段对其他线程可见（要求构造期间不把 this 泄漏出去）。

### 有序性：别乱序
- `volatile`：禁止编译器和 CPU 把它前后的某些读写重排，比如双重检查单例里靠它防止拿到半初始化的对象；
- `synchronized`：同一把锁保护的代码同一时刻只有一个线程在跑，所以对其他线程来说是按顺序执行的。

### 方案对比：各手段保证了什么
| 手段 | 原子性 | 可见性 | 有序性 |
|---|---|---|---|
| volatile | 不保证（单次读写可以） | 保证 | 保证（禁止特定重排） |
| synchronized | 保证 | 保证 | 保证 |
| 原子类（Atomic*） | 保证单个变量 | 保证 | 一般不单独依赖 |
| final | 不涉及 | 保证（构造正确时） | 不涉及 |

结论：只是一个状态标志，用 volatile；需要「读—改—写」整体不被打断，用 synchronized 或原子类。

## 示例
```java
volatile boolean flag = false;          // 可见性 + 有序性
AtomicInteger counter = new AtomicInteger(); // 原子性

synchronized void transfer() {          // 原子性 + 可见性 + 有序性
    // 多步操作整体不被打断
}
```

## 易错点
- 以为 volatile 也能保证原子性；volatile 修饰的 i，多线程 i++ 仍会丢更新
- 以为 synchronized 禁止了所有重排；同步块内部仍可能重排，只是保证单线程语义和对外的串行效果
- 以为 final 随时都保证可见；构造期间 this 泄漏出去的话，不保证

## 追问
### [f1] 为什么 volatile 不能保证 i++ 安全？
volatile 只保证每次读到最新值、每次写立刻可见，但 i++ 是读、加、写三步，两个线程仍可能同时读到同一个旧值，各自写回，导致丢更新。

### [f2] 什么情况下选 volatile，什么情况下选 synchronized？
只有一个线程写、其他线程读的状态标志，用 volatile 即可。多个线程读改写同一个变量，或需要多个变量一起保持一致，用 synchronized 或原子类。
