---
id: q_01M6XBGNB27WYSX5DKS7D6CWC3
title: 怎么让线程执行完后拿到返回值？
type: coding
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-basics, thread-pool]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
实现 Callable，在 call() 里返回结果，用 FutureTask 包装后交给 Thread 启动，线程执行完再通过 get() 拿到返回值。

## 要点
- [kp1|3] Callable 的 call() 有返回值，还能抛出受检异常，Runnable 的 run() 做不到
- [kp2|3] 用 FutureTask 包装 Callable，再作为任务交给 Thread
- [kp3|2] 线程执行完后调用 futureTask.get() 获取返回值
- [kp4|2] get() 会阻塞等待，任务还没完成时调用线程会一直等
- [kp5] 提交给线程池时，用 submit() 即可直接得到 Future

## 详解
### 先搞懂：Future 像“取餐小票”
你点了餐，店员给你一张小票，说“好了叫你”。你可以先去干别的事，等餐好了拿小票去取。`Future` 就是这张小票，`get()` 就是拿小票取餐：餐没做好，你就得等。

术语：
- **Callable**：有返回值的任务接口；
- **Future**：代表任务未来的结果；
- **FutureTask**：既是 `Runnable` 又是 `Future`，所以能交给 `Thread`，也能取结果。

### 为什么 Runnable 不行
`Runnable.run()` 的返回类型是 `void`，没法把结果交回来。`Callable.call()` 返回泛型 `V`，也允许抛出异常。

### 具体步骤
1. 写一个实现 `Callable<T>` 的类（或 Lambda），在 `call()` 里返回结果；
2. 用 `new FutureTask<>(callable)` 包装；
3. 把 `FutureTask` 传给 `Thread`，调用 `start()`；
4. 需要结果时调用 `futureTask.get()`，任务没完成会阻塞等待。

### 线程池里怎么取
线程池的 `submit(Callable)` 直接返回 `Future`，不需要自己写 `FutureTask`：

`Future<Integer> f = pool.submit(() -> 1 + 1);`

## 示例
```java
Callable<Integer> task = () -> 1 + 1;
FutureTask<Integer> futureTask = new FutureTask<>(task);
new Thread(futureTask).start();

Integer result = futureTask.get(); // 阻塞直到任务完成，得到 2
```

## 易错点
- 直接把 `Callable` 传给 `Thread`；`Thread` 只接收 `Runnable`，要先包装成 `FutureTask`
- 在主线程过早调用 `get()`；会一直阻塞，抵消了并行的好处
- 忽略异常；任务里抛出的异常会被封装，调用 `get()` 时抛出 `ExecutionException`

## 追问
### [f1] get() 可以设置超时吗？
可以，`get(timeout, unit)` 在指定时间内没拿到结果会抛 `TimeoutException`，避免无限等待。
