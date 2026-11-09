---
id: q_01M6ZYJDK449M15DQ675MXAN4D
title: sleep 和 wait 有什么区别？
type: concept
difficulty: medium
importance: 3
category: java-concurrency
tags: [thread-basics, synchronized]
prerequisites: [q_01M6XBGQKEDGQ0JDPW9RZHXVT2]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Java SE 21 API：Object.wait", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html" }
  - { title: "Java SE 21 API：Thread.sleep", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html" }
---

## 一句话
sleep 是 Thread 的静态方法，只是睡一会儿，不释放锁；wait 是 Object 的方法，必须在 synchronized 里调用，会释放锁并等别人通知。

## 要点
- [kp1|3] sleep 属于 Thread 类，wait 属于 Object 类
- [kp2|3] sleep 不释放已持有的锁，wait 会释放对象锁
- [kp3|2] wait 必须在 synchronized 里调用，sleep 可以在任何地方调用
- [kp4|2] sleep 时间到自动醒，wait 要靠 notify、notifyAll 或超时、中断醒来
- [kp5] 两者被中断时都会抛 InterruptedException

## 详解
### 先搞懂：「睡觉」和「排队等叫号」
都是让线程暂停，但目的完全不同：

- **sleep**：我想歇 1 秒，时间到了自己起来。像在办公室打盹，手里的钥匙还拿着，别人进不了你锁着的房间。
- **wait**：我在等某个条件，条件满足了请叫醒我。像在银行取号后去沙发坐着等，把柜台让出来给别人办业务，叫到号再回去。

后文用到的几个词：
- **监视器锁**：`synchronized` 使用的锁。
- **notify / notifyAll**：唤醒在某个对象上等待的线程的方法。

### sleep：只负责暂停
`Thread.sleep(ms)` 让当前线程暂停指定时间，期间**不释放**持有的锁。时间到后自动回到可运行状态。它不依赖锁，可以在任何地方调用。

### wait：为了协作而等待
`obj.wait()` 要在拿到 obj 的锁（synchronized）的情况下调用。调用后会**释放 obj 的锁**并进入等待，等其他线程调用 `obj.notify()` 或 `notifyAll()` 才可能被唤醒；也可以用 `wait(毫秒)` 设置超时。

必须在 synchronized 中，是因为要保证「检查条件」和「进入等待」不被别人插队，否则可能错过通知。没拿到锁就调用会抛 `IllegalMonitorStateException`。

### 方案对比：一张表看区别
| 对比项 | sleep | wait |
|---|---|---|
| 所属类 | Thread | Object |
| 是否释放锁 | 不释放 | 释放 |
| 使用位置 | 任意位置 | 必须在 synchronized 中 |
| 如何结束等待 | 时间到 | 被唤醒、超时或被中断 |
| 典型用途 | 暂停一会儿 | 线程之间协作 |

结论：只想让线程暂停一段时间用 sleep；要等别的线程改变条件再继续，用 wait（或更高层的并发工具）。

## 示例
```java
synchronized (lock) {
    Thread.sleep(1000);   // 睡 1 秒，仍然持有 lock，别的线程进不来
}

synchronized (lock) {
    lock.wait();          // 释放 lock，等待通知
}
```

## 易错点
- 在 synchronized 里 sleep，以为别的线程能进来；锁没释放，其他线程只能等
- 在 synchronized 外调用 wait；会抛 IllegalMonitorStateException
- 以为 wait 只能靠 notify 醒；也可能超时或被中断醒来

## 追问
### [f1] 为什么 wait 定义在 Object 里而不是 Thread 里？
因为 wait 等的是「某个对象上的锁和条件」，每个对象都有自己的锁，所以方法放在 Object 上，任何对象都能当作等待的对象。
