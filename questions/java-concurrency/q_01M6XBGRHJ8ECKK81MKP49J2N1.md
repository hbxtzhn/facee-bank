---
id: q_01M6XBGRHJ8ECKK81MKP49J2N1
title: Thread.join() 是做什么的？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-basics]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
t.join() 会让调用它的线程停下来，等线程 t 执行结束后再继续往下走，常用来等子线程把活干完。

## 要点
- [kp1|3] A 线程里调用 t.join()，A 会阻塞，直到 t 线程结束
- [kp2|3] 常用于主线程等待子线程完成后再汇总结果
- [kp3|2] join(毫秒) 可以设置最长等待时间，超时就不再等
- [kp4|2] 等待时被中断会抛 InterruptedException
- [kp5] 如果 t 还没 start 或已经结束，join 会立刻返回

## 详解
### 先搞懂：先干完再往下走
比如你要统计一个大文件，主线程开了两个子线程分别统计前半段和后半段，最后要把两个结果加起来。如果主线程不等，可能子线程还没算完，主线程就开始汇总了，结果不对。

这就像装修：水电工没做完，不能让瓦工进场。join 就是「等他做完再说」。

后文用到的几个词：
- **主线程**：执行 main 方法的线程。
- **阻塞**：线程暂停，不往下执行，直到条件满足。

### join 怎么工作
线程 A 执行到 `t.join()` 时：

1. A 进入等待状态，不再往下执行；
2. 线程 t 执行完毕（run 方法结束或异常退出）；
3. A 被唤醒，从 `join()` 返回，继续执行后面的代码。

注意：阻塞的是**调用 join 的线程**，不是 t。

### 带超时的 join
`t.join(1000)` 表示最多等 1 秒，超时后即使 t 没结束，也会返回。适合不想无限等待的情况，返回后可以用 `t.isAlive()` 判断 t 是否还在运行。

### 原理（了解即可）
`join` 内部是在 t 对象上用 `wait` 等待，t 线程结束时 JVM 会唤醒等待者。所以它本质上也是一种等待通知。

## 示例
```java
Thread t = new Thread(() -> System.out.println("子线程干活"));
t.start();
t.join(); // 主线程在这里等 t 结束
System.out.println("子线程结束了，主线程继续");
```

## 易错点
- 在 start 之前调用 join；线程还没启动，join 会直接返回，起不到等待作用
- 以为 join 让 t 线程暂停；阻塞的是调用 join 的当前线程
- 忽略 InterruptedException；等待期间被中断时要正确处理

## 追问
### [f1] 除了 join，还有什么办法等待多个线程结束？
可以用 `CountDownLatch`，每个线程结束时 countDown，主线程 await 等到计数为 0。线程池场景用 `Future.get()` 等结果。
