---
id: q_01M6XBGXA2TFD1GDK9DN0HYTRH
title: 怎么给线程池里的线程起一个有意义的名字？
type: concept
difficulty: easy
importance: 1
category: java-concurrency
tags: [thread-pool]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
自己实现 ThreadFactory，在 `newThread` 里给线程设置有业务含义的名字，再把它传给线程池构造器，日志和线程转储里就能一眼认出线程属于谁。

## 要点
- [kp1|3] 线程池通过 ThreadFactory 创建线程，传入自定义工厂就能改名字
- [kp2|3] 在 `newThread` 里用 `new Thread(r, name)` 设置名字，用计数器区分序号
- [kp3|2] 有意义的名字便于看日志、线程转储排查问题
- [kp4] 工厂里还可以设置优先级、是否守护线程、异常处理器

## 详解
### 先搞懂：工牌上写名字
公司一百个员工都叫「员工」，出了问题根本不知道是谁。给每个人发工牌，写上部门和编号，比如「订单组-3」，一眼就知道责任在哪。

线程池里的线程默认也有名字（形如 `pool-1-thread-1`），但看不出业务。给线程起业务名，就是发工牌。后文术语：

- **ThreadFactory**：创建线程的工厂接口，只有一个方法 `newThread(Runnable r)`。
- **线程转储（thread dump）**：把所有线程当前在干什么打印出来的快照，排查卡死、死锁时常用。

### 做法：自定义 ThreadFactory
线程池每次需要新线程，都会调用工厂的 `newThread`。你在这里创建线程时指定名字即可：用一个 `AtomicInteger` 计数，名字写成「业务名 + 序号」。

然后把工厂对象传给 `ThreadPoolExecutor` 的 `threadFactory` 参数。

### 为什么值得做
- 日志里打印线程名，一眼看出这条日志来自订单线程池还是短信线程池；
- 线程转储里线程名能直接定位到业务，排查线程卡住、CPU 飙高时省很多时间；
- 多个线程池混用时，默认名字都是 `pool-N-thread-M`，难以区分。

### 还能设置什么
在工厂里，除了名字，还可以设置线程的优先级、是否守护线程（`setDaemon`），以及给线程设置未捕获异常处理器（`setUncaughtExceptionHandler`），统一记录异常日志。

## 示例
```java
ThreadFactory factory = new ThreadFactory() {
    private final AtomicInteger seq = new AtomicInteger(1);

    @Override
    public Thread newThread(Runnable r) {
        Thread t = new Thread(r, "order-worker-" + seq.getAndIncrement());
        t.setDaemon(false);
        return t;
    }
};

ThreadPoolExecutor pool = new ThreadPoolExecutor(
        2, 4, 60, TimeUnit.SECONDS,
        new ArrayBlockingQueue<>(100), factory);
```

## 易错点
- 所有线程都用同一个固定名字，没有序号，排查时依旧分不清
- 序号用普通 int 自增；多线程下会重复，要用 AtomicInteger
- 以为改名要在任务里改；应该在线程创建时就指定名字

## 追问
### [f1] 默认的线程名是什么样？
没有传工厂时，使用默认工厂，名字形如 `pool-1-thread-1`，前一个数字是线程池序号，后一个是线程序号。

### [f2] 除了自己写，还有别的办法吗？
很多工具库（如 Guava 的 `ThreadFactoryBuilder`）提供现成的命名工厂，几行代码就能设置名字格式。
