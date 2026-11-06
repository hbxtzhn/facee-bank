---
id: q_01M6QN340WG0YA61PMDT8P22FT
title: 为什么要用线程池，而不是每个任务都新建一个线程？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-pool]
appliesTo: ["Java >= 8"]
related: [q_01M6QKTSJ3R62SJD3Y8SMQTWQ6]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Java 21 API：ThreadPoolExecutor（类说明）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html" }
  - { title: "JEP 444：Virtual Threads（平台线程与操作系统线程）", url: "https://openjdk.org/jeps/444" }
reviewedAt: 2026-11-06
estimatedMinutes: 2
---

## 一句话
线程创建和销毁都有开销，数量也受操作系统限制；线程池复用一组线程执行任务，既减少开销，又能限制线程总数，避免把系统拖垮。

## 要点
- [kp1|3] Java 线程对应操作系统线程，创建、销毁和切换都有成本
- [kp2|3] 线程池复用已有线程，省去每个任务创建线程的开销
- [kp3|2] 线程池能限制线程数和排队数，防止任务突增耗尽资源
- [kp4] 线程池统一管理线程，便于监控、命名和关闭

## 详解
### 先搞懂：线程是什么，为什么不能随便建
**线程**是程序里一条独立执行的路线：一个线程执行一段代码时，另一个线程可以同时执行另一段。Web 服务器同时处理很多请求，就是靠多个线程。

在 Java 里，`new Thread()` 创建的（平台）线程背后对应一个**操作系统线程**，新建一个线程，就是请操作系统分配一份资源。可以把它想成餐厅雇服务员：

- 每来一桌客人就新招一个服务员、吃完就解雇：招聘和辞退的成本很高，客人一多，餐厅还会被挤爆；
- 线程池就是固定雇几个服务员，客人来了谁有空谁接待，都忙就让客人排队。

### 每个任务新建线程有什么问题
- **开销大**：创建和销毁线程要和操作系统打交道，任务本身很短时，花在建线程上的时间可能比干活还多。
- **数量失控**：请求突增时线程数跟着暴涨。每个线程都占内存，线程多了，CPU 也要在它们之间频繁切换，整体反而变慢，严重时直接耗尽内存。
- **不好管理**：线程散落在各处，没法统一查看有多少任务在跑、统一关闭。

### 线程池解决了什么
Java 文档对线程池作用的概括是两点：

1. **复用线程**：执行大量异步任务时，减少每个任务的调用开销，性能更好；
2. **限制和管理资源**：给线程数、排队任务数设上限，资源占用是可控的。

此外，线程池还提供统计信息（例如已完成任务数），方便监控。

### 进阶：虚拟线程（基础薄弱可先跳过）
Java 21 引入了虚拟线程。它不和操作系统线程一一对应，创建成本很低，JEP 444 明确说明虚拟线程不应池化。所以对大量阻塞 IO 的任务，Java 21 起可以每个任务一个虚拟线程。计算密集型任务仍然用平台线程池。

## 示例
```java
// 不推荐：每个任务一个新线程
for (Order order : orders) {
    new Thread(() -> handle(order)).start();
}

// 推荐：固定数量的线程复用执行（参数如何设置见「如何创建线程池」）
ExecutorService pool = new ThreadPoolExecutor(
        4, 4, 0, TimeUnit.SECONDS, new ArrayBlockingQueue<>(1000));
for (Order order : orders) {
    pool.execute(() -> handle(order));
}
pool.shutdown();
```

## 易错点
- 以为线程越多处理越快；线程超过 CPU 能并行执行的数量后，切换开销会让整体变慢
- 以为用了线程池就不会出问题；队列无界或线程数无上限时，照样会耗尽内存

## 追问
### [f1] 线程池里的线程执行完任务后去哪了？
不会销毁，而是回到池中，从任务队列里取下一个任务继续执行。超过核心线程数的那部分线程，空闲超过 keepAliveTime 才会被回收。
