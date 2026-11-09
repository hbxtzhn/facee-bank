---
id: q_01M6ZYJAWQWJ650G2314KQJDCV
title: 线程的三种创建方式各有什么优缺点？
type: concept
difficulty: medium
importance: 2
category: java-concurrency
tags: [thread-basics]
prerequisites: [q_01M6ZYJAAS30NGD76E0EK1JMKZ]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
三种方式本质都是用 Thread 启动。继承 Thread 最简单但占掉唯一的父类名额；Runnable 更灵活；Callable 能返回结果、能抛受检异常，要配合 FutureTask 或线程池使用。

## 要点
- [kp1|3] 继承 Thread 后不能再继承别的类，任务和线程绑死在一起
- [kp2|3] Runnable 只描述任务，run() 没有返回值，也不能抛受检异常
- [kp3|2] Callable 的 call() 有返回值，可以抛受检异常，结果通过 Future 取
- [kp4|2] Callable 不能直接交给 Thread，要用 FutureTask 包一层
- [kp5] 实际开发多用 Runnable 或 Callable 提交给线程池，很少手写继承 Thread

## 详解
### 先搞懂：线程和任务是两件事
假设你要在后台发一封邮件。要做的事（发邮件）叫**任务**，干活的人叫**线程**。就像快递：包裹是任务，快递员是线程。三种创建方式的区别，其实就是「怎么把任务交给线程」：

- **继承 Thread**：把任务直接写进快递员本身，快递员和包裹是一体的。
- **Runnable**：包裹单独打包，谁有空谁来送。
- **Callable**：包裹送完还要带回一张签收单（返回值）。

后文用到的几个词：
- **run()**：线程要执行的代码入口，调用 `start()` 后由 JVM 在新线程里调用。
- **受检异常**：编译器强制你处理的异常，如 `IOException`。
- **Future**：一张「取货凭证」，任务还没跑完时先拿着，之后用 `get()` 取结果。

### 继承 Thread：最直接，但最死板
写一个子类，重写 `run()`，创建对象后调用 `start()`。

- 优点：写法最简单，在 run 里可以直接用 `this` 当前线程对象。
- 缺点：Java 只能单继承，继承了 Thread 就不能再继承别的类；任务和线程绑定，没法交给线程池复用线程。

### 实现 Runnable：任务和线程分开
写一个类实现 `Runnable`，重写 `run()`，再用 `new Thread(runnable)` 包起来调用 `start()`。

- 优点：类还可以继承别的类；同一个任务对象可以交给多个线程，也能提交给线程池。
- 缺点：`run()` 没有返回值，想拿结果只能靠共享变量；方法签名不允许抛受检异常，只能在里面自己处理。

### 实现 Callable：能带回结果
实现 `Callable<V>`，重写 `call()`，方法返回 `V`，并且可以抛出受检异常。`Thread` 的构造器只接受 `Runnable`，所以要先把它包进 `FutureTask`（`FutureTask` 同时实现了 `Runnable` 和 `Future`），再交给 Thread。

- 优点：有返回值，能抛异常，调用方用 `get()` 拿结果或捕获失败原因。
- 缺点：写法多一层；`get()` 会阻塞，任务没跑完调用方就得等。

### 方案对比：三种方式一览
| 方式 | 返回值 | 能否抛受检异常 | 能否继承其他类 | 能否交给线程池 |
|---|---|---|---|---|
| 继承 Thread | 没有 | 不能 | 不能 | 不适合 |
| 实现 Runnable | 没有 | 不能 | 能 | 能 |
| 实现 Callable | 有 | 能 | 能 | 能（`submit`） |

结论：默认用 Runnable，需要结果或要把异常传回调用方时用 Callable，两者都优先交给线程池；继承 Thread 只适合很小的演示代码。

## 示例
```java
// Runnable
Thread t1 = new Thread(() -> System.out.println("发邮件"));
t1.start();

// Callable + FutureTask
Callable<Integer> task = () -> 1 + 1;
FutureTask<Integer> ft = new FutureTask<>(task);
new Thread(ft).start();
Integer result = ft.get(); // 阻塞等待结果，得到 2
```

## 易错点
- 直接调用 `run()` 以为启动了线程；实际只是在当前线程里普通调用，必须调用 `start()`
- 以为 `new Thread(callable)` 可以编译；Thread 只接受 Runnable，要包 FutureTask
- 以为同一个 Thread 对象可以 `start()` 两次；第二次会抛 `IllegalThreadStateException`

## 追问
### [f1] 为什么说其实只有一种创建线程的方式？
真正在操作系统里创建线程的只有 `Thread.start()`。Runnable、Callable 只是描述「线程要执行什么」，最终都是被某个 Thread 对象调用。

### [f2] 平时开发怎么选？
通常不手动创建线程，而是把 Runnable 或 Callable 提交给线程池。不需要结果用 `execute`，需要结果用 `submit` 拿 Future。
