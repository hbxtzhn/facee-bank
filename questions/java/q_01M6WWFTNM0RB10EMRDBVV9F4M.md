---
id: q_01M6WWFTNM0RB10EMRDBVV9F4M
title: 为什么创建线程时推荐实现 Runnable 接口？
type: concept
difficulty: medium
importance: 2
category: java
tags: [thread-basics, oop]
prerequisites: [q_01M6WWFSNX7B3320340RSAHY1W, q_01M6ZYJAAS30NGD76E0EK1JMKZ]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Java SE 21 API：java.lang.Thread（start 与 run，Thread 实现 Runnable）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html" }
  - { title: "Java SE 21 API：java.lang.Runnable", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Runnable.html" }
---

## 一句话
推荐实现 Runnable，因为 Java 类只能单继承，实现接口不占父类名额，线程类还能继承别的类，同时把「要做的任务」和「执行任务的线程」分开。

## 要点
- [kp1|3] Java 类只能单继承，继承 Thread 就不能再继承别的类
- [kp2|3] 实现 Runnable 不占继承名额，线程类还可以继承其他类
- [kp3|2] Runnable 只描述任务，线程池等执行方式都可以直接接收它
- [kp4] 多个线程可以共用同一个 Runnable 对象，共享其中的数据

## 详解
### 先搞懂：任务和工人是两回事
做项目时，「发送验证码」是一件要做的事；谁去做、怎么做（新开线程、放进线程池）是另一回事。类比：公司接了一个活（任务），可以派正式员工、外包或者实习生去做。活本身不该和某个具体的人绑死。

`Runnable` 就是「活」，`Thread` 是「工人」。

后文要用的词：
- **Runnable**：只有一个 `run()` 方法的接口，描述一段要执行的任务。
- **单继承**：一个类只能有一个直接父类。
- **线程池**：复用一组线程来执行任务的工具。

### 两种写法
```java
// 方式一：继承 Thread
class MyThread extends Thread {
    public void run() { /* 任务 */ }
}
// 方式二：实现 Runnable
class MyTask implements Runnable {
    public void run() { /* 任务 */ }
}
new Thread(new MyTask()).start();
```

### 对比：为什么选 Runnable
| 维度 | 继承 Thread | 实现 Runnable |
|---|---|---|
| 继承限制 | 占用唯一父类名额 | 不占用，还能继承其他类 |
| 任务与线程 | 绑在一起 | 分开，任务可以单独复用 |
| 线程池 | 能提交，但把线程当任务用不合适 | 可以直接提交 |
| 共享数据 | 每个对象各一份 | 同一个任务对象可交给多个线程 |

结论：默认实现 Runnable；Java 8 起简单任务可直接写成 Lambda。需要返回值或抛出受检异常时，用 Callable。

### 为什么这样设计更好
任务只关心「做什么」，执行方式可以后期灵活替换：今天直接 `new Thread`，明天换成线程池，任务类一行不用改。而继承 Thread，任务和线程绑死，想放进线程池还得把线程对象当成任务，既浪费又别扭。

### 进阶：Thread 本身也实现了 Runnable（基础薄弱可先跳过）
`Thread` 类自己就实现了 `Runnable` 接口。`new Thread(runnable)` 时，线程启动后会去调用传入对象的 `run()`。

## 示例
```java
Runnable task = () -> System.out.println("发送验证码 " + Thread.currentThread().getName());

new Thread(task).start();                 // 直接用线程跑
ExecutorService pool = Executors.newFixedThreadPool(2);
pool.execute(task);                       // 同一个任务，换成线程池跑
pool.shutdown();
```

## 易错点
- 以为继承 Thread 才是真正的多线程；两种方式启动后都是新线程
- 直接调用 `run()` 以为启动了线程；那只是普通方法调用，要调用 `start()`
- 以为 Runnable 能返回结果；需要返回值用 Callable

## 追问
### [f1] Runnable 和 Callable 有什么区别？
Runnable 的 run 没有返回值，也不能抛出受检异常；Callable 的 call 有返回值，可以抛出异常，配合 Future 取结果。

### [f2] 为什么调用 start 而不是 run？
`start()` 才会让 JVM 创建新线程并在其中执行 `run()`；直接调用 `run()` 只是在当前线程里执行了一个普通方法。
