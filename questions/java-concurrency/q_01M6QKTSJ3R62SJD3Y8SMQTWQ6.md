---
id: q_01M6QKTSJ3R62SJD3Y8SMQTWQ6
title: Java 中应该如何创建线程池？
type: concept
difficulty: medium
importance: 3
category: java-concurrency
tags: [thread-pool]
prerequisites: [q_01M6QN340WG0YA61PMDT8P22FT]
appliesTo: ["Java >= 8", "虚拟线程部分：Java >= 21"]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Java 21 API：ThreadPoolExecutor", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html" }
  - { title: "Java 21 API：Executors", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Executors.html" }
  - { title: "OpenJDK 21 源码：Executors.java", url: "https://github.com/openjdk/jdk21u/blob/master/src/java.base/share/classes/java/util/concurrent/Executors.java" }
  - { title: "JEP 444：Virtual Threads", url: "https://openjdk.org/jeps/444" }
reviewedAt: 2026-11-06
estimatedMinutes: 5
---

## 一句话
用 ThreadPoolExecutor 构造器显式指定核心线程数、最大线程数、有界队列和拒绝策略，不要直接用 Executors 的工厂方法。

## 要点
- [kp1|3] 用 ThreadPoolExecutor 构造器显式传参，不用 Executors 工厂方法
- [kp2|3] 提交顺序：先建核心线程，再入队，队列满了才扩到最大线程数
- [kp3|2] 用有界队列，防止任务无限堆积导致 OOM
- [kp4|2] 线程和队列都满时走拒绝策略，默认 AbortPolicy 抛异常
- [kp5] 自定义线程工厂，给线程起能看出业务的名字

## 详解
### 先搞懂：线程池就是一家餐厅的排班规则
还是用餐厅类比：线程是服务员，任务是客人，任务队列是门口的等位区。创建线程池，就是定好这家店的规则：

- 平时固定雇几个服务员（**核心线程**）；
- 等位区最多坐几个人（**队列容量**）；
- 忙不过来时最多临时加几个人（**最大线程数**），闲下来多久后辞退临时工（**空闲存活时间**）；
- 等位区也满了、人也加满了，新来的客人怎么办（**拒绝策略**）。

`ThreadPoolExecutor` 的构造器就是让你把这几条规则逐条写清楚。

### 七个参数：对应上面的规则
| 参数 | 含义 |
|---|---|
| `corePoolSize` | 核心线程数，默认空闲时也不回收 |
| `maximumPoolSize` | 线程总数上限（核心 + 临时） |
| `keepAliveTime` + `unit` | 临时线程空闲多久后回收 |
| `workQueue` | 任务队列；有界队列就是「等位区有座位上限」 |
| `threadFactory` | 怎么创建线程，常用来给线程起名字 |
| `handler` | 拒绝策略，不传时默认 `AbortPolicy`，直接抛异常 |

### 提交顺序：先排队，排满了才加人
提交一个任务时，线程池依次判断：

1. 线程数没到核心数：**新建一个线程**来执行（即使有别的线程空闲）；
2. 到了核心数：任务**放进队列**等待；
3. 队列满了：线程数没到最大值就**再建线程**，到了就**拒绝**。

容易反直觉的是第 2、3 步：先排队，队列满了才加线程。所以如果队列没有上限，第 3 步永远不会发生，最大线程数设了等于没设。

### 为什么不用 Executors 的工厂方法
`Executors` 的工厂方法一行就能建好线程池，但它们都有一个「无上限」：

| 方法 | 无上限的部分 | 后果 |
|---|---|---|
| `newFixedThreadPool` / `newSingleThreadExecutor` | 队列（`LinkedBlockingQueue`） | 任务越积越多，耗尽内存 |
| `newCachedThreadPool` | 线程数（`Integer.MAX_VALUE`） | 线程无限增加 |
| `newScheduledThreadPool` | 延迟队列 | 任务越积越多 |

自己调构造器把每个上限写清楚，出问题时是可控的拒绝，而不是整个服务挂掉。

### 进阶：参数怎么定、虚拟线程（基础薄弱可先跳过）
- 计算密集型任务：线程数接近 CPU 核数；IO 密集型任务：线程大多在等待，可以更多，具体数值靠压测确定。
- 上线后监控 `getQueue().size()`、`getActiveCount()` 和拒绝次数；运行中可以调 `setCorePoolSize` / `setMaximumPoolSize` 修改。
- Java 21 起，阻塞 IO 型任务可以用 `Executors.newVirtualThreadPerTaskExecutor()`，每个任务一个虚拟线程。JEP 444 说明虚拟线程不应池化；要限制并发数，用 `Semaphore`。

## 示例
```java
// 参数数值仅为示例，需按压测结果确定
ThreadFactory factory = new ThreadFactory() {
    private final AtomicInteger seq = new AtomicInteger(1);

    @Override
    public Thread newThread(Runnable r) {
        return new Thread(r, "order-worker-" + seq.getAndIncrement());
    }
};

ThreadPoolExecutor pool = new ThreadPoolExecutor(
        8,                                   // corePoolSize
        16,                                  // maximumPoolSize
        60, TimeUnit.SECONDS,                // 非核心线程空闲 60 秒后回收
        new ArrayBlockingQueue<>(1000),      // 有界队列
        factory,
        new ThreadPoolExecutor.CallerRunsPolicy()); // 满了由提交线程自己执行，减缓提交速度

pool.execute(() -> handleOrder());

// 应用关闭时：不再接收新任务，等待已提交任务完成
pool.shutdown();
if (!pool.awaitTermination(30, TimeUnit.SECONDS)) {
    pool.shutdownNow();
}
```

## 易错点
- 以为线程数先涨到最大值再排队；实际是先排队，队列满了才继续创建线程
- 用无界队列又设置了 maximumPoolSize，以为能扩容；实际最大线程数永远用不上
- 以为核心线程一定不会回收；调用 allowCoreThreadTimeOut(true) 后，核心线程空闲超时也会回收
- 用 submit 提交任务后不调用 Future.get，任务抛出的异常被封装在 Future 里，日志中看不到

## 追问
### [f1] 核心线程 2、最大线程 4、队列容量 2，同时提交 7 个长任务，第 7 个会怎样？
第 1、2 个创建核心线程，第 3、4 个进入队列，第 5、6 个因队列满而新建线程，线程数达到 4。第 7 个时线程和队列都满了，被拒绝；默认 `AbortPolicy` 会抛出 `RejectedExecutionException`。

### [f2] JDK 内置了哪几种拒绝策略？
- `AbortPolicy`：抛出 `RejectedExecutionException`，是默认策略；
- `CallerRunsPolicy`：由提交任务的线程自己执行，能减缓提交速度；
- `DiscardPolicy`：直接丢弃；
- `DiscardOldestPolicy`：丢弃队头最老的任务，然后重试提交。

### [f3] shutdown 和 shutdownNow 有什么区别？
`shutdown` 不再接收新任务，已提交的任务（包括队列中的）会继续执行完。`shutdownNow` 会尝试中断正在执行的任务，并把队列中还没执行的任务作为列表返回。两者都不会等待，需要配合 `awaitTermination` 使用。

### [f4] 有了虚拟线程，还需要线程池吗？
阻塞 IO 型任务可以直接每个任务一个虚拟线程，不需要池化。计算密集型任务仍然适合用固定大小的平台线程池，因为它的瓶颈是 CPU 核数，虚拟线程帮不上忙。
