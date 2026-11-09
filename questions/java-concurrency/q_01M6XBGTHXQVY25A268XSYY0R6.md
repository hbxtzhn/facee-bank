---
id: q_01M6XBGTHXQVY25A268XSYY0R6
title: 双重检查单例为什么要给实例加 volatile？
type: scenario
difficulty: medium
importance: 2
category: java-concurrency
tags: [memory-model, design-pattern]
prerequisites: [q_01M6ZYJBE8ZJXDD462GAZGBAP8, q_01M6XBGT0NVE9CGQS5B8H06FHB]
appliesTo: ["Java >= 5"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "JSR-133 FAQ：Double-checked locking", url: "https://www.cs.umd.edu/~pugh/java/memoryModel/jsr-133-faq.html" }
  - { title: "Java 语言规范 SE 21：17.4.5 Happens-before Order", url: "https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html" }
---

## 一句话
`new` 一个对象分三步，可能被重排成先把引用赋给变量、后初始化；加 volatile 禁止这种重排，别的线程就不会拿到还没初始化好的对象。

## 要点
- [kp1|3] `instance = new Singleton()` 分三步：分配内存、初始化对象、引用指向内存
- [kp2|3] 第二、三步可能被重排，别的线程读到非 null 但未初始化的对象
- [kp3|2] 外层 `if` 没加锁，读取不受同步保护，所以会撞上这个问题
- [kp4] 给 instance 加 volatile，禁止创建过程的重排，Java 5 起有效

## 详解
### 先搞懂：新房子先发钥匙，后装修
想象开发商卖房：正常流程是先盖好、装修好，再发钥匙。如果有个开发商为了抢进度，先把钥匙发给你、再去装修，你一进门看到的就是毛坯房，却以为是成品。

双重检查单例里的 `instance = new Singleton()` 就有这个风险：引用已经赋值了（钥匙发了），对象还没初始化完（房子没装修）。后文术语：

- **单例**：整个程序里只允许存在一个的对象。
- **双重检查**：先不加锁判断一次，为空再加锁，加锁后再判断一次。
- **重排序**：实际执行顺序和代码书写顺序不一样。

### 问题出在哪：new 不是一步完成的
```java
instance = new Singleton();
```
这一行在 JVM 里大致分三步：

1. 给对象分配内存空间；
2. 初始化对象（执行构造方法，给字段赋值）；
3. 让 `instance` 指向这块内存。

在单线程里，第 2、3 步对调结果一样，所以允许被重排成 1 → 3 → 2。

### 多线程下怎么出事
线程 A 进入同步块，执行到 1 → 3，此时 `instance` 已经不是 null，但对象还没初始化。线程 B 在最外层判断 `instance == null`，发现不为空，直接返回，拿着这个半成品去用，就可能读到字段的默认值，甚至抛异常。

关键是线程 B 的第一次判断没有加锁，不受 synchronized 保护，A 的重排就暴露给了 B。

### volatile 怎么解决
给 `instance` 加 `volatile` 后，Java 内存模型规定：对 volatile 变量的写入，前面的普通写操作不能被重排到它后面。也就是初始化对象（第 2 步）必须先完成，才能把引用赋给 `instance`（第 3 步）。线程 B 一旦看到 `instance` 不为 null，就一定能看到完整初始化的对象。

这个保证从 Java 5（JSR-133 修订内存模型）开始才可靠，更老的版本里 volatile 的语义不够强。

## 示例
```java
public class Singleton {
    private static volatile Singleton instance;

    private Singleton() {}

    public static Singleton getInstance() {
        if (instance == null) {                 // 第一次检查，不加锁
            synchronized (Singleton.class) {
                if (instance == null) {         // 第二次检查，加锁后再确认
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

## 易错点
- 以为 synchronized 已经够了；外层判断没有加锁，读到的可能是半成品
- 以为 volatile 的作用是让只创建一次；防止创建两次靠的是加锁和第二次检查
- 以为所有单例都要 volatile；用静态内部类或枚举实现的单例，不需要双重检查

## 追问
### [f1] 去掉第二次检查会怎样？
两个线程可能同时通过第一次检查，一个创建完后另一个拿到锁，又创建一次，单例被破坏。所以第二次检查也不能省。

### [f2] 有没有不用 volatile 的单例写法？
有。静态内部类由类加载机制保证只初始化一次，枚举单例也一样，写法更简单，不需要手写双重检查。
