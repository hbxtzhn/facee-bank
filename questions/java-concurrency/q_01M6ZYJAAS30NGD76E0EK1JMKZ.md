---
id: q_01M6ZYJAAS30NGD76E0EK1JMKZ
title: Java 中怎么创建并启动一个线程？
type: coding
difficulty: easy
importance: 2
category: java-concurrency
tags: [thread-basics]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
可以继承 Thread 重写 run()，也可以实现 Runnable 交给 Thread；无论哪种都要调用 start() 才会启动新线程，直接调用 run() 只是在当前线程里普通调用。

## 要点
- [kp1|3] 继承 Thread 并重写 run()，然后 new 出来调用 start()
- [kp2|3] 实现 Runnable 接口，作为参数传给 Thread，再调用 start()
- [kp3|2] start() 才会开新线程，直接调用 run() 只是普通方法调用
- [kp4|2] 实现 Runnable 更灵活，因为 Java 类只能单继承
- [kp5] 同一个 Thread 对象不能多次调用 start()

## 详解
### 先搞懂：run() 是“要做的事”，start() 是“开始干”
想象你写了一份任务清单（run 里的代码），但要有人去执行。`start()` 是“新招一个工人去做这份清单”，而直接调用 `run()` 是“你自己照着清单做”，根本没有多一个人。

术语：
- **run()**：线程要执行的任务代码；
- **start()**：通知 JVM 创建新线程并让它去执行 `run()`。

### 做法一：继承 Thread
定义一个类继承 `Thread`，重写 `run()`。缺点是 Java 只能单继承，继承了 `Thread` 就不能再继承别的类。

### 做法二：实现 Runnable
把任务写在 `Runnable` 的 `run()` 里，再交给 `Thread`。这种方式把“任务”和“线程”分开，更灵活，也方便交给线程池。

### 为什么不能直接调用 run()
`run()` 只是一个普通方法，直接调用时由当前线程执行，没有新线程产生。只有 `start()` 才会让 JVM 创建线程并在新线程里调用 `run()`。

## 示例
```java
// 方式一：继承 Thread
class MyThread extends Thread {
    @Override
    public void run() { System.out.println("run in " + getName()); }
}
new MyThread().start();

// 方式二：实现 Runnable（这里用 Lambda）
Thread t = new Thread(() -> System.out.println("run in " + Thread.currentThread().getName()));
t.start();
```

## 易错点
- 直接调用 `run()` 并以为是多线程；这实际上还是在当前线程里执行
- 对同一个 `Thread` 对象调用两次 `start()`；第二次会抛 `IllegalThreadStateException`
- 以为线程创建后会立刻执行；何时运行由系统调度决定

## 追问
### [f1] 为什么推荐实现 Runnable 而不是继承 Thread？
Runnable 把任务和线程分离，类还可以继承别的类，任务可以直接提交给线程池执行。
