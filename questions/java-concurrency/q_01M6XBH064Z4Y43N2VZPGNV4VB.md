---
id: q_01M6XBH064Z4Y43N2VZPGNV4VB
title: synchronized 是怎么保证可见性、有序性和可重入性的？
type: concept
difficulty: medium
importance: 2
category: java-concurrency
tags: [synchronized, memory-model]
prerequisites: [q_01M6XBGYPJXM20MV9Q8KEXDR5P]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "JLS SE 21 §17.4.4 Synchronization Order（解锁 synchronizes-with 后续加锁）", url: "https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.4.4" }
  - { title: "JLS SE 21 §17.1 Synchronization（监视器可被同一线程多次加锁）", url: "https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html#jls-17.1" }
  - { title: "JVMS SE 21 §6.5 monitorenter / monitorexit", url: "https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-6.html#jvms-6.5.monitorenter" }
---

## 一句话
一个线程释放锁之前做的修改，下一个拿到同一把锁的线程一定能看到；同一时刻只有一个线程执行同步代码，所以顺序不会被打乱；锁里记着持有者和次数，所以可重入。

## 要点
- [kp1|3] 可见性：线程 A 释放锁后，线程 B 获取同一把锁，就能看到 A 的修改
- [kp2|3] 有序性：同步块排他执行，其他线程看不到块内被重排的中间状态
- [kp3|2] 可重入：监视器记录持有线程和重入次数，同线程再进次数加 1
- [kp4] 可见性只对用同一把锁的线程成立，读的线程不加锁就没有保证
- [kp5] synchronized 同时还保证原子性

## 详解
### 先搞懂：公共白板和交接班
想象一个办公室，每个人手里有自己的小本子（线程的工作内存），还有一块公共白板（主内存）。你改了数据，可能只先写在自己的小本子上，别人看白板，看到的还是旧的。

synchronized 就像规定了一套交接班流程：

- 下班（释放锁）前，必须把本子上的改动抄到白板上；
- 上班（获取锁）后，必须把本子清空，重新从白板上读。

这样下一个人接班，一定看到的是上一个人改完的最新内容。

说明一下：「工作内存」是 Java 内存模型为了讲解方便设计的抽象概念，实际对应的是 CPU 缓存、寄存器等，不是一块真的独立内存。

后文用到的术语：

- **可见性**：一个线程改了数据，其他线程能看到。
- **有序性**：代码执行的先后顺序，别的线程观察到的结果不会乱。
- **可重入**：同一个线程可以重复获取自己已持有的锁。
- **指令重排**：编译器和 CPU 为了提高速度，可能调整没有依赖关系的指令的执行顺序。

### 可见性：释放前刷新，获取后重读
Java 内存模型规定：对一个锁的解锁，要先于后面对同一把锁的加锁。具体效果就是：

- 线程加锁后，会重新从主内存读取共享变量；
- 线程解锁前，会把修改的共享变量刷新回主内存。

所以线程 A 在同步块里改了变量，退出后线程 B 进入同一把锁的同步块，就能读到新值。

注意前提：A 和 B 必须用**同一把锁**。如果 B 读变量时没有加锁，就得不到这个保证。

### 有序性：排他执行，外面看不到乱序
指令重排在单个线程内部不会改变结果，但在多线程下，别的线程可能看到乱掉的中间状态。

synchronized 的做法是：同步块里一次只有一个线程在执行。块里的指令仍然可能被重排，但只要是用同一把锁的线程，就看不到这个乱序，因为它们要么看到块执行前的状态，要么看到块执行完的状态。

所以更准确的说法是：synchronized 保证的是同步块之间的有序，而不是禁止块内部的重排。

### 可重入：记着是谁，记着几次
监视器除了记录哪个线程持有锁，还记录**重入次数**。同一个线程再次进入同步块，只是次数加 1；每次退出减 1，减到 0 才真正释放。这样一个同步方法调用另一个同步方法也不会卡住自己。

### 对比：三个特性分别靠什么
| 特性 | 靠什么保证 | 前提 |
|---|---|---|
| 可见性 | 释放锁前刷新、获取锁后重读 | 读写双方用同一把锁 |
| 有序性 | 同一时刻只有一个线程执行同步块 | 访问共享数据都要在同步块里 |
| 可重入 | 记录持有线程和重入次数 | 同一个线程 |

结论：这三点都建立在「用同一把锁」之上，同步块之外的访问不在保护范围内。

## 示例
```java
public class Demo {
    private int value;

    public synchronized void set(int v) { value = v; }

    public synchronized int get() { return value; } // 读也要加同一把锁

    public synchronized void outer() {
        inner();   // 同一线程再次获取 this 锁，不会卡住
    }

    public synchronized void inner() { }
}
```

## 易错点
- 只给写方法加 synchronized，读方法不加；读线程没有可见性保证
- 以为 synchronized 禁止了块内的指令重排；它保证的是别的线程观察不到乱序
- 把「清空工作内存」当成真实存在的一块内存；它是模型里的抽象说法
- 以为可重入是靠 JVM 偷偷忽略加锁；其实是靠重入计数

## 追问
### [f1] synchronized 和 volatile 有什么区别？
volatile 只保证可见性和一定程度的有序，不保证复合操作的原子性；synchronized 还能保证原子性和互斥。

### [f2] 可重入锁为什么要记录次数？
因为进几次就要退几次。只有退到次数归零，才算真正释放，否则内层方法一返回，外层还在用的锁就被放掉了。
