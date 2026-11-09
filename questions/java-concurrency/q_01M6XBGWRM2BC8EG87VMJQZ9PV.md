---
id: q_01M6XBGWRM2BC8EG87VMJQZ9PV
title: 线程池里的空闲线程什么时候会被回收？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-pool]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
超过核心线程数的线程，空闲时间超过 keepAliveTime 就会被回收；核心线程默认一直保留，除非设置了允许核心线程超时。

## 要点
- [kp1|3] 线程数超过核心数时，多出的线程空闲超过 keepAliveTime 被终止
- [kp2|3] 核心线程默认空闲也不回收
- [kp3|2] 存活时间的单位由构造器的 unit 参数指定
- [kp4] 调用 `allowCoreThreadTimeOut(true)` 后核心线程也会超时回收，要求存活时间大于 0

## 详解
### 先搞懂：临时工没活就回家
商店忙时招了几个临时工，客人少了，临时工闲着没事做。老板不会立刻辞退，而是等一段时间，如果一直没活，才让他回家。这段等待的时间就是 keepAliveTime。正式员工则一直留着。

后文术语：

- **空闲线程**：执行完任务后，没有新任务可取，在等待的线程。
- **存活时间**：线程闲置多久后可以被回收。

### 什么线程会被回收
线程池每个线程执行完任务，就去队列里取下一个任务。取任务时有两种等法：

- 线程数不超过核心数：一直等，直到有任务，这样核心线程就一直保留；
- 线程数超过核心数：只等 keepAliveTime 这么久，超时没取到任务，这个线程就结束退出。

所以回收的是「多出来的那部分」，具体是哪个线程并没有固定，谁先超时谁退出。

### 时间单位怎么指定
构造器里 `keepAliveTime` 和 `unit` 两个参数合在一起，比如 `60, TimeUnit.SECONDS` 表示 60 秒。只写数字不写单位是不行的。

### 让核心线程也能回收
默认核心线程永不回收。如果线程池流量很不均匀，想让它空闲时也释放资源，可以调用：

```java
pool.allowCoreThreadTimeOut(true);
```

调用前必须保证 `keepAliveTime` 大于 0，否则抛出 `IllegalArgumentException`。

## 示例
```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
        2, 4, 30, TimeUnit.SECONDS,   // 非核心线程空闲 30 秒后回收
        new ArrayBlockingQueue<>(10));
pool.allowCoreThreadTimeOut(true);     // 可选：核心线程空闲 30 秒也回收
```

## 易错点
- 以为 keepAliveTime 对所有线程都生效；默认只对超过核心数的线程有效
- 以为超时后回收的是「非核心线程」这个特定的对象；实际是谁先超时谁退出，池里只保证总数
- 不设时间单位或设成 0 就期望核心线程回收；`allowCoreThreadTimeOut` 要求时间大于 0

## 追问
### [f1] 如果任务量大，线程被回收后又来任务怎么办？
任务队列满了或线程数不足时，线程池会再创建新线程。所以回收不影响正确性，只是重新建线程有些开销。

### [f2] keepAliveTime 应该设多大？
没有固定值。流量波动频繁、希望线程常在，就设长一点；资源紧张、希望尽快释放，就设短一点，要结合业务观察调整。
