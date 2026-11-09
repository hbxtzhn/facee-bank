---
id: q_01M6ZYJ5X1T6WDBX4D8SZYGBHS
title: static 关键字是做什么的？
type: concept
difficulty: easy
importance: 2
category: java
tags: [oop, memory-area]
prerequisites: [q_01M6ZYJ5C0FSMD30KVY64VC6A9]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
static 修饰的成员属于类本身而不属于某个对象，所有对象共享这一份，不用创建对象，直接用类名就能访问。

## 要点
- [kp1|3] static 成员属于类，不属于某个具体对象
- [kp2|3] 所有对象共享同一份 static 变量，一处修改，处处可见
- [kp3|2] 可以直接通过类名访问，如 Math.max
- [kp4|2] static 方法里不能直接用非 static 成员，因为可能没有对象
- [kp5] 静态变量随类加载初始化，存放在类的信息里，而不是每个对象里

## 详解
### 先搞懂：班级公告栏和个人课本
一个班里，每个学生有自己的课本（各人一份），但教室墙上的公告栏只有一块，大家共用，谁改了大家都看到。

对象的普通属性像课本，每个对象一份；static 属性像公告栏，整个类共用一份。

后文术语：
- **实例成员**：没有 static 的成员，属于每个对象。
- **静态成员**：有 static 的成员，属于类。

### static 变量：全员共享
```java
class Counter {
    static int total = 0;   // 所有对象共用
    int id;                 // 每个对象一份
}
```
不管 new 多少个 Counter，`total` 只有一份。常用来放计数器、常量（如 `static final`）。

### static 方法：不用对象就能调
`Math.max(1, 2)` 没有创建 Math 对象，直接用类名调用。工具类里的方法通常都是 static。

### 为什么 static 方法不能直接访问实例成员
实例成员属于某个对象，static 方法被调用时可能根本没有对象存在，它不知道该用哪个对象的数据。所以要访问，必须自己先拿到一个对象。

### static 代码块
`static { ... }` 在类第一次被使用、完成加载初始化时执行，用来做一次性的初始化。

## 示例
```java
class Config {
    static final int MAX = 100;
    static int count = 0;

    static void hit() { count++; }
}

Config.hit();
System.out.println(Config.count);
```

## 易错点
- 在 static 方法里直接用 this 或实例变量；编译报错
- 以为每个对象都有自己的 static 变量；全员共享一份
- 滥用 static 变量保存可变状态；多线程下会互相干扰

## 追问
### [f1] static 变量在内存里放哪？
它属于类，和类的信息一起管理，不在每个对象里。具体存放位置随 JVM 版本实现有差异，面试时说“属于类、被所有对象共享”即可。
