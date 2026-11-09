---
id: q_01M6XBGTZGQFK0YR3W1G79JE9T
title: volatile 关键字是做什么的？
type: concept
difficulty: easy
importance: 3
category: java-concurrency
tags: [memory-model]
prerequisites: [q_01M6ZYJD225G3XCV57DBNCGCQJ, q_01M6XBP3HD2B1K80Z0JGQYTYXV]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
volatile 让一个线程对变量的修改马上被其他线程看到，并禁止相关的指令重排序，但它不能保证 `i++` 这类复合操作是原子的。

## 要点
- [kp1|3] volatile 保证可见性：一个线程改了，别的线程读到最新值
- [kp2|3] volatile 禁止相关指令重排序，保证有序性
- [kp3|2] volatile 不保证原子性，`i++` 仍然会丢更新
- [kp4] 适合做状态标志位；要原子自增用 AtomicInteger 或加锁

## 详解
### 先搞懂：为什么线程会看不到别人的修改
想象一间办公室，大家共用一块白板（主内存），但每个人为了省事，会把白板上的数字抄在自己的便签纸上（线程自己的缓存），之后一直看便签。别人把白板上的数字改了，你还在看自己的旧便签，就不知道。

volatile 就像一条规矩：「这个数字不许抄便签，每次都直接看白板、改完立刻写回白板」。后文术语：

- **可见性**：一个线程改了变量，别的线程能看到新值。
- **有序性**：代码执行顺序不被随意打乱。
- **原子性**：一个操作要么全部完成，要么完全没做，中间不会被别的线程插进来。

### 作用一：保证可见性
变量加了 volatile，一个线程写入后，其他线程再读就能读到新值。常见场景是停止标志：

线程 A 把 `running` 设为 false，线程 B 的循环 `while (running)` 马上就能看到并退出；没有 volatile，B 可能一直读到旧值，永远停不下来。

### 作用二：禁止指令重排序
编译器和 CPU 为了效率可能调整指令顺序。volatile 变量的读写会限制它前后的重排：写之前的操作不会被排到写之后，读之后的操作不会被排到读之前。双重检查单例里给实例加 volatile，防的就是对象创建过程被重排。

### 不保证原子性：i++ 为什么还是会出错
`i++` 其实是三步：读出 `i`，加 1，写回。volatile 保证每一步读到的是最新值，但不能阻止两个线程同时读到同一个值，各自加 1 后写回，结果只加了一次。

要解决这类问题，用 `AtomicInteger`，或者用 `synchronized` 加锁。

## 示例
```java
class Worker implements Runnable {
    private volatile boolean running = true; // 状态标志，适合用 volatile

    public void run() {
        while (running) {
            // 干活
        }
    }

    public void stop() {
        running = false; // 其他线程调用后，run 里能马上看到
    }
}
```

## 易错点
- 以为 volatile 能让 `count++` 线程安全；它只保证可见和有序，不保证原子
- 以为 volatile 等于加锁；它不会让代码互斥，也不会阻塞线程
- 以为 volatile 只在多核下有用；它同时限制编译器重排，对单核也有意义

## 追问
### [f1] volatile 和 synchronized 有什么区别？
volatile 只作用于变量，保证可见和有序，不保证原子。synchronized 作用于代码块，同一时刻只有一个线程进入，同时保证原子、可见和有序。

### [f2] 什么场景适合用 volatile？
一个线程写、多个线程读的状态标志，或者一次性发布的配置对象引用。写入的新值不依赖旧值，才适合用 volatile。
