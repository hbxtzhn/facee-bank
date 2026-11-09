---
id: q_01M6ZYJENP71X58GK0EYY6D619
title: 线程池有哪几种状态，状态之间怎么切换？
type: concept
difficulty: medium
importance: 1
category: java-concurrency
tags: [thread-pool]
prerequisites: [q_01M6XBP4XS1188KQ5RJBMDKZDR]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "OpenJDK jdk-21-ga 源码：ThreadPoolExecutor.java（runState 注释、execute、getTask）", url: "https://raw.githubusercontent.com/openjdk/jdk/jdk-21-ga/src/java.base/share/classes/java/util/concurrent/ThreadPoolExecutor.java" }
  - { title: "JDK 21 API：ThreadPoolExecutor（Core and maximum pool sizes / Queuing / Rejected tasks / Keep-alive times）", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html" }
estimatedMinutes: 3
---

## 一句话
线程池有 RUNNING、SHUTDOWN、STOP、TIDYING、TERMINATED 五态，shutdown 与 shutdownNow 触发切换。

## 要点
- [kp1|3] 五种状态：RUNNING、SHUTDOWN、STOP、TIDYING、TERMINATED
- [kp2|3] `shutdown()` 让 RUNNING 进入 SHUTDOWN，`shutdownNow()` 进入 STOP
- [kp3|2] SHUTDOWN 状态继续处理队列任务，STOP 状态放弃队列并中断运行任务
- [kp4] TIDYING 状态会执行 `terminated()` 钩子，执行完进入 TERMINATED

## 详解
### 先搞懂：餐厅从营业到彻底关门
餐厅从营业到彻底关门，要经过几个阶段：正常营业；挂牌「不再接客」，但把已有客人服务完；直接清场；客人都走了，收拾卫生；最后锁门。线程池的状态就是这几个阶段。

后文术语：

- **状态**：线程池当前处于的生命周期阶段。
- **钩子方法**：框架预留、由子类选择性实现的方法，这里指 `terminated()`。

### 五种状态
| 状态 | 接收新任务 | 处理队列任务 | 含义 |
|---|---|---|---|
| RUNNING | 是 | 是 | 正常运行 |
| SHUTDOWN | 否 | 是 | 调用了 `shutdown()`，处理完队列即可结束 |
| STOP | 否 | 否 | 调用了 `shutdownNow()`，中断运行中的任务，丢弃队列 |
| TIDYING | 否 | 否 | 所有任务已终止，工作线程数为 0，将执行 `terminated()` |
| TERMINATED | 否 | 否 | `terminated()` 执行完毕，线程池彻底结束 |

### 状态怎么切换
- RUNNING → SHUTDOWN：调用 `shutdown()`；
- RUNNING 或 SHUTDOWN → STOP：调用 `shutdownNow()`；
- SHUTDOWN → TIDYING：队列和池里的线程都空了；
- STOP → TIDYING：池里的线程都空了；
- TIDYING → TERMINATED：`terminated()` 钩子方法执行完。

状态只会往后走，不会倒退，也不会重新回到 RUNNING。

### 实际能看到什么
`ThreadPoolExecutor` 有几个方法能查看状态：`isShutdown()`（已进入 SHUTDOWN 或之后）、`isTerminating()`（正在终止过程中）、`isTerminated()`（已是 TERMINATED）。

### 进阶：状态怎么存的（基础薄弱可先跳过）
源码里用一个 `AtomicInteger` 类型的 `ctl` 同时保存状态和工作线程数：高几位表示状态，低位表示线程数，这样一次原子操作就能同时读写两者。

## 示例
```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
        1, 1, 0, TimeUnit.SECONDS, new LinkedBlockingQueue<>());
pool.shutdown();
System.out.println(pool.isShutdown());    // true，已进入 SHUTDOWN
System.out.println(pool.isTerminated());  // 取决于任务是否已处理完
```

## 易错点
- 以为 SHUTDOWN 状态会立即停止；它会把队列里的任务处理完
- 以为 STOP 能强制杀死任务；它只是发送中断，任务要自己响应
- 以为关闭后的线程池可以重新使用；状态不可逆，需要新建

## 追问
### [f1] terminated() 有什么用？
它是线程池终止前的钩子方法，默认什么都不做。可以子类化后重写，用来释放资源或记录日志。

### [f2] isTerminated 为 true 的前提是什么？
必须先调用 `shutdown` 或 `shutdownNow`，并且所有任务都处理完；没有调用关闭方法时它永远是 false。
