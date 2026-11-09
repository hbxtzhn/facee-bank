---
id: q_01M6ZYJF7SFNVYZGPH7TGW7F92
title: 线程池中的线程在核心、非核心、阻塞队列之间怎么转换状态？
type: concept
difficulty: medium
importance: 1
category: java-concurrency
tags: [thread-pool]
prerequisites: [q_01M6XBGWRM2BC8EG87VMJQZ9PV]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
线程创建是 NEW，启动是 RUNNABLE；空闲等任务时是 WAITING 或 TIMED_WAITING，超时退出后是 TERMINATED。

## 要点
- [kp1|3] 新建线程 NEW，调用 start 后进入 RUNNABLE，开始执行任务
- [kp2|3] 空闲时在队列上等任务：不超时是 WAITING，限时等待是 TIMED_WAITING
- [kp3|2] 排队的是任务，不是线程，任务本身没有线程状态
- [kp4] 空闲超时的线程退出，状态变为 TERMINATED

## 详解
### 先搞懂：员工的一天
员工上班前是还没入职（NEW）；入职后开始干活（RUNNABLE）；没活的时候在休息室等派活：正式员工可以一直等（WAITING），临时工只等一小时，没活就回家（TIMED_WAITING，之后下班）。

后文术语（Java 线程的六种状态）：

- **NEW**：线程对象创建了，还没启动。
- **RUNNABLE**：正在运行或随时可以被 CPU 运行。
- **WAITING**：无限期等待别的线程唤醒。
- **TIMED_WAITING**：限时等待，时间到了自己醒。
- **BLOCKED**：等待拿到锁。
- **TERMINATED**：线程执行结束。

### 核心线程：建好就常驻
提交任务时，如果线程数小于核心数，线程池新建线程，这个线程从 NEW 变为 RUNNABLE，先执行触发它创建的那个任务。任务做完，它回到队列上取下一个任务；队列里没有，就进入 WAITING 等着，直到有任务被放进来唤醒它。

### 任务进队列：任务在等，不是线程在等
线程数达到核心数后，新任务进入阻塞队列。有些资料说「队列里的任务是 waiting 状态」，更准确的说法是：任务只是队列里的一个对象，还没线程执行它，所以没有线程状态可言；真正在 WAITING 的是等任务的空闲线程。

### 非核心线程：限时等待，超时退出
队列满了、线程数还没到最大值，线程池创建新线程，新线程同样 NEW → RUNNABLE，先执行触发它创建的任务。做完后到队列上限时等待（TIMED_WAITING），时间等于 keepAliveTime。等到任务就回到 RUNNABLE；超时没等到，线程退出，变为 TERMINATED。

### 实际上并没有固定的核心非核心
线程创建后并不带「核心」「非核心」的标签。线程池只看当前线程总数：超过核心数时，空闲的线程用限时等待，谁先超时谁退出。设置了 `allowCoreThreadTimeOut(true)` 后，所有线程都会限时等待。

### 任务执行中的状态
线程执行任务时，如果任务代码里等锁，线程是 BLOCKED；调用 `wait()` 或 `Thread.sleep()`，是 WAITING 或 TIMED_WAITING；正常计算就是 RUNNABLE。

## 示例
```java
// 排查时可以打印工作线程状态
Thread t = Thread.currentThread();
System.out.println(t.getName() + " " + t.getState()); // 正在执行任务时通常是 RUNNABLE
```

## 易错点
- 以为队列里的任务也有 waiting 状态；任务不是线程，没有线程状态
- 以为线程创建时就被标记为核心线程；线程池只比较总数，不给线程贴标签
- 以为空闲线程一直是 RUNNABLE；它们阻塞在队列上，是 WAITING 或 TIMED_WAITING

## 追问
### [f1] 线程池里空闲线程为什么不消耗 CPU？
因为它们阻塞在队列的取任务操作上，处于 WAITING 或 TIMED_WAITING 状态，不会被 CPU 调度，直到有任务来唤醒它们。

### [f2] 线程被回收后状态是什么？
线程的 run 方法执行结束后，状态变为 TERMINATED，不可以再启动，需要的话线程池会新建线程。
