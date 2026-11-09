---
id: q_01M6ZYJD225G3XCV57DBNCGCQJ
title: 多个线程怎么通过共享对象传递信息？
type: concept
difficulty: easy
importance: 1
category: java-concurrency
tags: [thread-basics, thread-safety]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
多个线程都访问同一个对象，一个线程往里写、另一个读，就能传递信息；要保证读到最新值用 volatile，要保证多步操作不被打断用 synchronized。

## 要点
- [kp1|3] 线程间传信息最直接的办法：多个线程访问同一个共享对象
- [kp2|3] volatile 保证一个线程的修改，其他线程能马上看到
- [kp3|2] synchronized 保证同一时刻只有一个线程执行某段代码，同时保证修改可见
- [kp4] volatile 只保证可见，不保证 i++ 这类复合操作的原子性

## 详解
### 先搞懂：线程之间怎么「说话」
线程之间没法直接发消息，但它们共享同一块堆内存。就像同事之间用白板留言：A 在白板上写「数据准备好了」，B 看到后开始处理。

这个「白板」就是共享对象，里面的字段就是要传递的信息。后文用到的几个词：

- **共享对象**：多个线程都持有引用的同一个对象。
- **可见性**：一个线程改了值，其他线程能及时看到。
- **互斥**：同一时刻只允许一个线程执行某段代码。

### 光共享不够：会看不见、会写乱
直接共享有两个坑：

1. **看不见**：线程为了速度，可能把变量缓存起来，A 改了之后，B 一直读到旧值；
2. **写乱了**：两个线程同时改，步骤交错，数据出错。

### volatile：保证看得见
给成员变量加 `volatile`，每次读都从主内存读最新值，每次写都立即刷回主内存，所以一个线程的修改，别的线程马上可见。适合「一个线程写、其他线程读」的状态标志，比如「是否停止」。

### synchronized：保证不乱，也保证看得见
给方法或代码块加 `synchronized`，同一时刻只能有一个线程进入；线程退出同步块前，修改会同步到主内存，下一个进入的线程能看到。适合多个线程都要读改写的场景。

### 方案对比：volatile 和 synchronized
| 手段 | 保证可见性 | 保证互斥 | 适合场景 |
|---|---|---|---|
| volatile | 是 | 否 | 状态标志，一写多读 |
| synchronized | 是 | 是 | 多步读改写 |

结论：只是传一个状态标志用 volatile；需要整体不被打断就用 synchronized。

## 示例
```java
class Signal {
    private volatile boolean ready = false; // 一个线程写，另一个线程读

    void prepare() { ready = true; }
    boolean isReady() { return ready; }
}
```

## 易错点
- 以为 volatile 能保证 count++ 安全；它不保证原子性，多线程自增仍会丢失更新
- 不同线程用不同的锁对象保护同一份数据；等于没加锁
- 以为共享了对象就一定能读到最新值；没有 volatile 或锁，可能一直读到旧值

## 追问
### [f1] 除了共享对象，线程间还有哪些通信方式？
常见的有 wait/notify、`Condition`、`BlockingQueue`、`CountDownLatch` 等并发工具，也有管道流。实际开发里阻塞队列用得最多。
