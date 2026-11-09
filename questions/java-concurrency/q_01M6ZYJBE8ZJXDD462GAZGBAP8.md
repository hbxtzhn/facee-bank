---
id: q_01M6ZYJBE8ZJXDD462GAZGBAP8
title: 怎么实现线程安全的单例模式？
type: coding
difficulty: medium
importance: 2
category: java-concurrency
tags: [design-pattern, thread-safety]
prerequisites: [q_01M6XBGP9EBY9TXR9PAZH7WJ3G]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "Java 语言规范 SE 21：12.4.2 Detailed Initialization Procedure", url: "https://docs.oracle.com/javase/specs/jls/se21/html/jls-12.html" }
  - { title: "Java 序列化规范：1.12 Serialization of Enum Constants", url: "https://docs.oracle.com/en/java/javase/21/docs/specs/serialization/serial-arch.html" }
  - { title: "JSR-133 FAQ：Double-checked locking", url: "https://www.cs.umd.edu/~pugh/java/memoryModel/jsr-133-faq.html" }
---

## 一句话
饿汉式靠类加载保证线程安全；懒汉式要加锁，推荐双重检查加锁并给实例变量加 volatile，或者用静态内部类、枚举。

## 要点
- [kp1|3] 饿汉式：静态字段在类加载时初始化，JVM 保证只执行一次
- [kp2|3] 双重检查加锁：外层判空避免每次加锁，锁内再判空防止重复创建
- [kp3|2] 双重检查中实例变量必须加 volatile，防止拿到半初始化的对象
- [kp4|2] 静态内部类：用到时才加载，既延迟创建又线程安全
- [kp5] 枚举单例写法最简洁，还能防止反射和序列化破坏

## 详解
### 先搞懂：多线程下单例哪里会破
基础懒汉式是「先判断有没有，没有就创建」。这是一个**先检查再行动**的组合，两步之间别人可以插进来。

比如两个线程同时调用获取方法：都判断为空，都执行创建，结果创建了两个实例。就像两个人同时发现前台没人，都去招了一个，前台就有两个了。

后文用到的几个词：
- **类加载**：JVM 第一次用到某个类时，把它加载并初始化的过程，这个过程 JVM 保证线程安全。
- **指令重排**：为了效率，编译器或 CPU 可能调整指令执行顺序，单线程看不出差别，多线程可能看到中间状态。

### 饿汉式：交给类加载
把实例定义成 `static final` 字段，在声明时直接创建。类初始化只会执行一次，所以没有线程安全问题。缺点是类一加载就创建，没用到也占资源。

### 懒汉式加 synchronized：安全但每次都加锁
给获取方法加 `synchronized`，保证一次只有一个线程进入。简单可靠，缺点是实例创建好之后，每次获取也要抢锁，多余。

### 双重检查加锁：只在创建时加锁
做法是：

1. 先在锁外判断实例是否为空，不为空直接返回，绝大多数调用走这里，没有锁开销；
2. 为空才进入 `synchronized`；
3. 进锁后**再判断一次**，因为可能在等锁期间别的线程已经创建好了；
4. 仍为空才创建。

实例变量必须用 `volatile`。原因是 `new` 一个对象大致分三步：分配内存、初始化对象、把引用指向内存。如果发生重排，引用可能先赋值、对象还没初始化完，另一个线程在锁外判断「不为空」后直接拿去用，就会拿到半成品对象。`volatile` 禁止这种重排。

### 静态内部类：延迟加上安全
把实例放在一个静态内部类的字段里。外部类加载时不会加载内部类，第一次调用获取方法时才加载内部类并创建实例，类加载的线程安全保证了只创建一次。

### 方案对比：几种线程安全写法
| 写法 | 延迟创建 | 线程安全靠什么 | 特点 |
|---|---|---|---|
| 饿汉式 | 否 | 类加载 | 最简单 |
| synchronized 方法 | 是 | 锁 | 每次获取都加锁 |
| 双重检查加锁 | 是 | 锁加 volatile | 写法稍复杂，要加 volatile |
| 静态内部类 | 是 | 类加载 | 简洁，常用 |
| 枚举 | 否 | 类加载 | 能防反射和序列化破坏 |

结论：不需要延迟创建就用饿汉式或枚举；需要延迟创建时优先用静态内部类，面试常考双重检查加锁。

## 示例
```java
public class Singleton {
    private static volatile Singleton instance;
    private Singleton() {}

    public static Singleton getInstance() {
        if (instance == null) {                  // 第一次检查，不加锁
            synchronized (Singleton.class) {
                if (instance == null) {          // 第二次检查，加锁后
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

## 易错点
- 双重检查加锁漏写 volatile；可能返回尚未初始化完成的对象
- 以为只要锁里判空就够；锁外的判空是为了避免每次加锁，不能省
- 以为所有写法都能防反射；只有枚举等少数写法能防住

## 追问
### [f1] 为什么枚举单例能防止反射和序列化破坏？
JDK 禁止通过反射创建枚举实例，序列化枚举时只写入名字，反序列化按名字找回原来的实例，所以不会产生新对象。

### [f2] 双重检查里第二次判空能去掉吗？
不能。两个线程可能同时通过第一次检查，一个线程创建完释放锁后，另一个拿到锁，如果不再判空就会再创建一个。
