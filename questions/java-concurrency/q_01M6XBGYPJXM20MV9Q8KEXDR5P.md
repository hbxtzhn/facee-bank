---
id: q_01M6XBGYPJXM20MV9Q8KEXDR5P
title: synchronized 关键字怎么用，能加在哪些地方？
type: concept
difficulty: easy
importance: 2
category: java-concurrency
tags: [synchronized, thread-safety]
prerequisites: [q_01M6ZYJD225G3XCV57DBNCGCQJ]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
synchronized 可以加在实例方法、静态方法和代码块上，分别锁当前对象、类对象和你指定的对象，同一时刻只允许一个线程进入。

## 要点
- [kp1|3] 修饰实例方法：锁的是当前对象 this
- [kp2|3] 修饰静态方法：锁的是这个类的 Class 对象
- [kp3|2] 修饰代码块：锁的是括号里指定的对象，范围可以更小
- [kp4|2] 只有争用同一把锁的线程才会互斥，不同的锁互不影响
- [kp5] 构造方法不能用 synchronized 修饰

## 详解
### 先搞懂：多个线程同时改一份数据会出什么事
假设商城扣库存：库存是 10，两个线程同时读到 10，各自减 1 再写回，结果是 9 而不是 8，少扣了一次。这就是多线程下的**线程安全**问题。

解决办法是让「读、改、写」这一整段代码一次只允许一个线程执行。可以把它想成公共厕所：门上只有一把锁，谁拿到锁谁进去，别人在门口等，出来之后下一个人才能进。

后文用到的术语：

- **锁**：一个对象身上带的「门锁」，Java 里每个对象都可以当锁用。
- **临界区**：需要一次只让一个线程执行的那段代码。
- **互斥**：一个线程在临界区里时，别的线程要等它出来。

### 实例方法：锁的是当前对象
在实例方法上加 `synchronized`，进入方法前要先拿到 `this` 这个对象的锁。

同一个对象的两个 synchronized 实例方法互相排斥；但是对象 a 和对象 b 是两把不同的锁，它们的方法可以同时执行。

### 静态方法：锁的是类对象
静态方法不属于某个具体对象，所以它锁的是这个类对应的 `Class` 对象（例如 `Counter.class`）。整个 JVM 里一个类只有一个这样的对象，所以不管你 new 了多少个实例，静态同步方法一次也只有一个线程能进。

### 代码块：自己指定锁，范围更小
```java
synchronized (lock) { ... }
```
括号里写哪个对象，就锁哪个对象。好处是只把真正需要保护的几行放进去，方法里其他代码不用排队，效率更高。

### 三种写法对比
| 写法 | 锁是谁 | 影响范围 | 适合 |
|---|---|---|---|
| 修饰实例方法 | 当前对象 `this` | 同一对象的同步方法 | 整个方法都要保护 |
| 修饰静态方法 | 类的 `Class` 对象 | 这个类所有实例共享 | 保护静态变量 |
| 同步代码块 | 括号里指定的对象 | 想锁多大锁多大 | 只保护方法里的几行 |

结论：能用代码块缩小范围就用代码块；整个方法都要保护时，直接加在方法上最省事。

注意：实例方法锁 `this`，静态方法锁 `Class` 对象，这是两把不同的锁，所以一个线程在执行静态同步方法时，另一个线程仍然可以同时执行同步的实例方法。

## 示例
```java
public class Counter {
    private int count;
    private static int total;
    private final Object lock = new Object();

    public synchronized void inc() {        // 锁 this
        count++;
    }

    public static synchronized void incTotal() {  // 锁 Counter.class
        total++;
    }

    public void incBlock() {
        // 这里可以做不需要保护的事
        synchronized (lock) {               // 锁 lock 对象
            count++;
        }
    }
}
```

## 易错点
- 以为 synchronized 锁的是代码；其实锁的是对象，两个线程用的不是同一个对象，就不会互斥
- 用 `new Object()` 或每次都新建的对象当锁，每个线程拿到的都是自己的锁，等于没加
- 拿字符串常量或装箱后的 `Integer` 当锁，别处的代码可能恰好共用同一个对象，造成莫名其妙的互相阻塞
- 以为 synchronized 可以修饰构造方法；构造方法不允许这样写，需要的话在内部用代码块

## 追问
### [f1] 一个线程执行静态同步方法时，另一个线程能同时执行同步的实例方法吗？
可以。静态方法锁的是 Class 对象，实例方法锁的是 this，是两把不同的锁，不会互相阻塞。

### [f2] synchronized 同步代码块和同步方法选哪个？
只有部分代码需要保护时用代码块，范围小，其他线程等待的时间短；整个方法都要保护就直接加在方法上，写法更简单。
