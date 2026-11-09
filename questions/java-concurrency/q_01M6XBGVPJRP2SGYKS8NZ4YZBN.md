---
id: q_01M6XBGVPJRP2SGYKS8NZ4YZBN
title: 怎么把任务交给线程池执行？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-pool]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
用 `execute(Runnable)` 提交没有返回值的任务；用 `submit()` 可以提交 Runnable 或 Callable，并拿到 Future 来取结果或异常。

## 要点
- [kp1|3] `execute()` 只接收 Runnable，没有返回值
- [kp2|3] `submit()` 返回 Future，可接收 Runnable 或 Callable
- [kp3|2] Callable 能返回结果和抛受检异常，Runnable 不能
- [kp4] `submit` 里任务抛的异常被包在 Future 里，要调用 `get()` 才会看到

## 详解
### 先搞懂：把活交给餐厅服务员
你去餐厅点菜，有两种方式：一种是点完就走，不管什么时候上菜（不关心结果）；另一种是拿个取餐号，之后凭号码来取菜，或者问菜做好了没有（要拿结果）。

线程池里，`execute` 是第一种，`submit` 是第二种，取餐号就是 `Future`。后文术语：

- **Runnable**：一个没有返回值的任务，只有 `run()` 方法。
- **Callable**：一个有返回值的任务，`call()` 方法返回结果，还允许抛出受检异常。
- **Future**：代表任务的「取餐号」，可以获取结果、查询是否完成、取消任务。

### execute：提交就走，不要结果
`execute` 定义在 `Executor` 接口里，只能提交 Runnable。提交后不返回任何东西。任务里抛出异常，会交给线程的未捕获异常处理器，一般表现为日志里打印异常。

### submit：提交后拿 Future
`submit` 定义在 `ExecutorService` 里，有三种形式：传 Runnable、传 Callable、传 Runnable 加固定结果值。返回一个 Future：

- `future.get()`：等待任务完成并拿到结果，会阻塞调用者；
- `future.isDone()`：查询任务是否完成；
- `future.cancel(true)`：尝试取消任务。

任务如果抛了异常，异常会被捕获并放进 Future，只有调用 `get()` 时才会以 `ExecutionException` 的形式抛出。所以只 `submit` 不 `get`，异常会悄悄消失。

### 批量提交
`invokeAll` 一次提交一批 Callable，等它们全部完成后返回 Future 列表；`invokeAny` 只要有一个成功就返回它的结果。

## 示例
```java
ExecutorService pool = Executors.newFixedThreadPool(2);

// 不关心结果
pool.execute(() -> System.out.println("hello"));

// 要结果
Future<Integer> f = pool.submit(() -> 1 + 1);
System.out.println(f.get()); // 2，get 会等任务完成

pool.shutdown();
```

## 易错点
- 以为 `submit` 和 `execute` 没区别；任务异常的处理方式不同
- 提交后不调用 `get()`，任务出错却没人知道
- 在提交线程里马上调用 `get()` 等结果，把异步写成了同步

## 追问
### [f1] execute 和 submit 抛出的异常处理有什么不同？
`execute` 的异常会直接抛到工作线程里，由未捕获异常处理器处理，通常会打印日志。`submit` 的异常被封装在 Future 中，调用 `get()` 才会抛出 `ExecutionException`。

### [f2] 为什么实际开发里 Runnable 和 Callable 要区分？
Runnable 没有返回值，也不能抛受检异常；Callable 可以返回结果，也能抛出受检异常，适合需要拿到计算结果的任务。
