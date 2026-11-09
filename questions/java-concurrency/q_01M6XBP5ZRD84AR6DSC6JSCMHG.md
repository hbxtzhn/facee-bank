---
id: q_01M6XBP5ZRD84AR6DSC6JSCMHG
title: synchronized 底层是怎么实现同步的？
type: concept
difficulty: hard
importance: 3
category: java-concurrency
tags: [synchronized, bytecode-execution]
prerequisites: [q_01M6XBGYPJXM20MV9Q8KEXDR5P]
appliesTo: ["HotSpot"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 5
references:
  - { title: "JVMS SE 21 §2.11.10 Synchronization", url: "https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-2.html#jvms-2.11.10" }
  - { title: "JVMS SE 21 §6.5 monitorenter / monitorexit", url: "https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-6.html#jvms-6.5.monitorenter" }
---

## 一句话
同步代码块编译成 monitorenter 和 monitorexit 两条指令，同步方法靠方法上的 ACC_SYNCHRONIZED 标志，背后都是每个对象关联的监视器（Monitor）。

## 要点
- [kp1|3] 代码块：字节码里 monitorenter 加锁，monitorexit 解锁
- [kp2|3] 方法：方法标志位 ACC_SYNCHRONIZED，由 JVM 在调用和返回时加解锁
- [kp3|2] 每个对象都关联一个监视器，加锁就是争夺监视器的所有权
- [kp4|2] 监视器记录持有线程和重入次数，因此可重入
- [kp5] 异常退出时也会释放锁，编译器为此生成额外的 monitorexit

## 详解
### 先搞懂：锁其实是对象身上的一个标记
前面讲 synchronized 的用法时，我们说「锁的是某个对象」。可以把它想成：每个对象身上都挂着一个看不见的「门卫」。进同步块之前要先问门卫：现在有人占着吗？没人，门卫登记你的名字，让你进；有人，你在门口等。出来时通知门卫销号。

那这件事是谁来做的？是 JVM。编译器只在字节码里留下记号，运行时由 JVM 去完成「问门卫」和「销号」。

后文用到的术语：

- **字节码**：Java 编译后的指令，JVM 按它执行。可以用 `javap` 查看。
- **监视器（Monitor）**：对象关联的门卫，记录谁持有锁，还有谁在排队。
- **所有权**：谁登记在门卫那里，谁就持有这把锁。

### 同步代码块：monitorenter 和 monitorexit
对于 `synchronized (obj) { ... }`，编译器在代码块开头生成 `monitorenter`，结尾生成 `monitorexit`。

- 执行 `monitorenter`：尝试获取 obj 关联的监视器。监视器没被占用，就记下当前线程是持有者，重入次数设为 1。当前线程已经是持有者，次数加 1。被别的线程占着，当前线程等待。
- 执行 `monitorexit`：重入次数减 1；减到 0，释放监视器，等待的线程可以来抢。

你用 `javap` 看字节码，通常会发现有两个 `monitorexit`：一个在正常结束的路径上，一个在异常路径上。这样不论代码正常走完还是抛出异常，锁都能释放，不会因为异常而一直占着。

### 同步方法：ACC_SYNCHRONIZED 标志
同步方法没有 `monitorenter`、`monitorexit`，而是在方法的访问标志里加上 `ACC_SYNCHRONIZED`。JVM 调用方法时看到这个标志，就先获取监视器（实例方法是 this 的，静态方法是 Class 对象的），方法返回或抛异常时再释放。效果和代码块一样，只是由方法调用机制隐式完成。

### 对比：两种写法的底层区别
| 对比项 | 同步代码块 | 同步方法 |
|---|---|---|
| 字节码标记 | `monitorenter` / `monitorexit` 指令 | 方法标志 `ACC_SYNCHRONIZED` |
| 加解锁由谁触发 | 执行指令 | JVM 调用方法、方法返回时 |
| 锁对象 | 括号里指定 | 实例方法 this，静态方法 Class 对象 |
| 本质 | 争夺同一个监视器 | 争夺同一个监视器 |

结论：写法不同，底层都是监视器所有权的获取与释放，所以语义一致。

### 进阶：监视器在哪里（基础薄弱可先跳过）
HotSpot 里，监视器是一个叫 ObjectMonitor 的 C++ 结构。里面大致有：持有者线程、重入计数、等待获取锁的线程队列、调用了 `wait()` 的线程队列。对象头的 Mark Word 在重量级锁状态下指向它。

不过 JVM 不会每次都创建监视器：没有竞争时用轻量级锁（较老版本默认还有偏向锁），有竞争才膨胀成真正的监视器，也就是所谓的锁升级。

## 示例
```java
public class Demo {
    private final Object lock = new Object();

    public void block() {
        synchronized (lock) {
            System.out.println("in block");
        }
    }

    public synchronized void method() {
        System.out.println("in method");
    }
}
// 查看字节码： javap -c -v Demo
// block() 里有 monitorenter / monitorexit
// method() 的 flags 里有 ACC_SYNCHRONIZED
```

## 易错点
- 以为同步方法也有 monitorenter 指令；它靠方法标志位实现
- 以为 synchronized 是 Java 代码层的锁；底层是 JVM 的监视器
- 以为抛异常后锁不会释放；字节码里异常路径也有 monitorexit，同步方法也由 JVM 释放
- 以为每次加锁都会创建操作系统级别的锁；没有竞争时 JVM 会用更轻的方式

## 追问
### [f1] 为什么字节码里有两个 monitorexit？
一个用于正常退出，一个用于异常退出，保证不论怎样离开同步块都会释放锁。

### [f2] synchronized 怎么做到可重入？
监视器记录持有线程和重入次数。同一个线程再次进入，次数加 1；每次退出减 1，减到 0 才真正释放。

### [f3] 为什么说 synchronized 的锁和对象有关？
因为监视器是跟对象关联的，锁信息保存在对象头里，所以锁的是对象，不是代码。
