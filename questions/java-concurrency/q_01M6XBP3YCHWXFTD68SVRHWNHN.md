---
id: q_01M6XBP3YCHWXFTD68SVRHWNHN
title: happens-before 规则是什么？
type: concept
difficulty: medium
importance: 2
category: java-concurrency
tags: [memory-model]
prerequisites: [q_01M6XBGT0NVE9CGQS5B8H06FHB]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
happens-before 是 Java 内存模型规定的一组规则：只要操作 A happens-before 操作 B，A 的结果就一定对 B 可见，且逻辑上 A 排在 B 前面。

## 要点
- [kp1|3] A happens-before B：A 的结果对 B 可见，A 的顺序排在 B 前
- [kp2|3] 常见规则：程序顺序、锁、volatile、线程启动、线程 join、传递性
- [kp3|2] 它是判断多线程读到的数据对不对的依据，不是真实时间先后
- [kp4] 具体实现可以重排，只要结果和按规则执行一样

## 详解
### 先搞懂：交接班的承诺
想象医院换班：上一班护士写好交接单，下一班护士一定能看到交接单上的内容。这里不管两个护士实际几点到岗，重点是「交接」这个动作，保证后者能看到前者做的事。

happens-before 就是 Java 给多线程定的这种「交接承诺」。后文术语：

- **可见**：一个线程改了变量，另一个线程读到的是改过的值。
- **规则**：什么情况下算「交接」。有这些规则，才可以放心依赖可见性。

### 它到底保证了什么
如果操作 A happens-before 操作 B，那么：

1. A 的执行结果对 B 可见；
2. A 的执行顺序排在 B 前面。

注意两点。第一，它说的不是「时间上先发生」，而是「结果可见性的保证」。第二，它也不要求 JVM 必须严格按这个顺序执行：如果重排后的结果和按规则执行的结果一样，重排是允许的。

### 常用的几条规则
- **程序顺序规则**：同一个线程里，前面的操作 happens-before 后面的操作。
- **监视器锁规则**：对一个锁，解锁 happens-before 之后对同一个锁的加锁。
- **volatile 规则**：对 volatile 变量的写，happens-before 之后对它的读。
- **线程启动规则**：主线程调用 `start()` 之前做的事，对被启动的线程可见。
- **线程终止规则**：线程里做的所有事，对调用它 `join()` 并成功返回的线程可见。
- **传递性**：A happens-before B，B happens-before C，则 A happens-before C。

### 规则怎么用：把它们串起来
线程 A 写普通变量 `data`，再写 volatile 变量 `ready`；线程 B 读到 `ready` 为 true 后读 `data`。

- 程序顺序：写 `data` happens-before 写 `ready`；
- volatile 规则：写 `ready` happens-before 读 `ready`；
- 传递性：写 `data` happens-before B 读 `data`，所以 B 一定能读到最新的 `data`。

### 进阶：没有规则会怎样（基础薄弱可先跳过）
两个线程之间如果找不到任何一条 happens-before 链，对共享变量的读写就没有可见性保证，这叫数据竞争，结果取决于编译器、CPU 和调度，可能偶尔正确、偶尔出错。

## 示例
```java
int data = 0;
volatile boolean ready = false;

// 线程 A
data = 42;
ready = true;

// 线程 B
if (ready) {
    System.out.println(data); // 通过 volatile 规则加传递性，必为 42
}
```

## 易错点
- 把 happens-before 当成时间先后；它说的是可见性和顺序保证
- 以为 A happens-before B 就必须严格先执行 A；结果等价的重排是允许的
- 以为只要读写了同一个变量就有保证；没有规则连接的两个线程，不保证可见

## 追问
### [f1] happens-before 和 volatile 是什么关系？
volatile 只是 happens-before 的规则之一：写 volatile 变量先于后续对它的读，并且借助传递性，写之前的普通变量修改也能被读线程看到。

### [f2] synchronized 能提供哪些保证？
同一把锁的解锁 happens-before 后续的加锁。所以线程 A 在锁里改的数据，线程 B 之后拿到同一把锁时一定能看到。
