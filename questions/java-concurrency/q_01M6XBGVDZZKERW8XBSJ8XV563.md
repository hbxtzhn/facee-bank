---
id: q_01M6XBGVDZZKERW8XBSJ8XV563
title: volatile 是怎么保证有序性的？
type: concept
difficulty: medium
importance: 2
category: java-concurrency
tags: [memory-model]
prerequisites: [q_01M6XBGTZGQFK0YR3W1G79JE9T]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
volatile 通过限制重排序保证有序性：写 volatile 之前的操作不会被排到写之后，读 volatile 之后的操作不会被排到读之前。

## 要点
- [kp1|3] 写 volatile 前的普通读写，不能被重排到这次写之后
- [kp2|3] 读 volatile 后的普通读写，不能被重排到这次读之前
- [kp3|2] 写 volatile 先于后续对它的读，读线程能看到写前的所有修改
- [kp4] 限制的是 volatile 前后的重排，其他无关语句仍可调整

## 详解
### 先搞懂：关卡的比喻
把代码执行想成一队人过马路，平时大家可以互相换位置，只要最终都过去就行。volatile 变量的读写像一个红绿灯关卡：关卡前面的人不能跑到关卡后面，关卡后面的人也不能抢到关卡前面。

这样，别的线程只要看到「关卡」已经通过（volatile 变量变了），就能确定关卡前的事都已经做完。后文术语：

- **有序性**：代码执行顺序不被打乱到出错的程度。
- **重排序**：编译器和 CPU 为提高效率调整指令顺序。

### 写 volatile：前面的事先做完
对 volatile 变量的写操作，它之前的读写操作不会被重排到写之后。

典型例子是线程 A 先给普通变量 `data` 赋值，再把 volatile 变量 `ready` 设为 true。因为有这个规则，`data = 42` 不会跑到 `ready = true` 后面。

### 读 volatile：后面的事晚点做
对 volatile 变量的读操作，它之后的读写操作不会被重排到读之前。

线程 B 读到 `ready` 为 true，之后读 `data`。这个读 `data` 的动作不会被提前到读 `ready` 之前，所以不会读到旧值。

### 合起来：写在前，读在后，能看到全部
线程 A 的写 volatile 变量，先于线程 B 之后对它的读。结合上面两条，B 读到新值时，A 在写 volatile 之前做的所有修改，B 也能看到。这就是 volatile 对有序性的贡献，也是双重检查单例里 volatile 能防止「拿到半成品对象」的原因。

### 进阶：只限制一侧，不是完全禁止重排（基础薄弱可先跳过）
volatile 只约束它前后的操作，并没有禁止所有重排：两个互不相关的普通变量读写，只要都在同一侧，仍然可能互换。另外，两个 volatile 变量的读写之间，顺序不会被重排。

## 示例
```java
int data = 0;
volatile boolean ready = false;

void writer() {
    data = 42;       // 1：不会被重排到 2 之后
    ready = true;    // 2：volatile 写
}

void reader() {
    if (ready) {     // 3：volatile 读
        int r = data; // 4：不会被重排到 3 之前，r 一定是 42
    }
}
```

## 易错点
- 以为 volatile 完全禁止了所有重排；只限制它前后的读写，同侧的无关操作仍可调整
- 以为读线程先读 data 也没事；读 volatile 之后的操作才有保证
- 以为 volatile 能让多个步骤原子执行；它只保证顺序，中间仍可能被别的线程插入

## 追问
### [f1] 有序性和可见性是什么关系？
可见性说的是值能不能被别的线程看到，有序性说的是操作顺序有没有被打乱。volatile 靠规则把两者绑在一起：读到新值，就同时看到它之前的修改。

### [f2] synchronized 能保证有序性吗？
能。同一把锁的解锁先于后续的加锁，锁内的操作对下一个拿锁的线程来说是按顺序完成的。
