---
id: q_01M6XBG5T1J0Z82256KJA4GC1T
title: String、StringBuilder、StringBuffer 有什么区别？
type: concept
difficulty: medium
importance: 3
category: java
tags: [type-system, thread-safety]
prerequisites: [q_01M6ZYJ4H3WKVHBAJZS21RYRAV, q_01M6ZYJ4SQDDZBAX1ZARG4B765]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
String 不可变；StringBuilder 和 StringBuffer 都可变，区别是 StringBuffer 的方法加了 synchronized，线程安全，StringBuilder 没加，单线程用更合适。

## 要点
- [kp1|3] String 不可变，StringBuilder、StringBuffer 可变
- [kp2|3] StringBuffer 的方法用 synchronized 修饰，线程安全；StringBuilder 不是
- [kp3|2] 大量拼接用可变的两个，不用 String
- [kp4|2] 局部变量单线程使用，首选 StringBuilder
- [kp5] 加同步会带来额外的开销，所以 StringBuilder 在单线程下通常更合适

## 详解
### 先搞懂：石头、白板、带锁的白板
- String 像刻在石头上的字：不能改，要改只能重刻；
- StringBuilder 像一块白板：随便擦写，但一个人用；
- StringBuffer 像带锁的白板：同一时刻只允许一个人写，别人要等，所以多人用也不会写乱，但每次写都要开锁关锁。

后文术语：
- **可变**：对象创建后内容可以修改。
- **线程安全**：多个线程同时操作也不会出错。
- **synchronized**：Java 的同步关键字，保证同一时刻只有一个线程执行这个方法。

### 区别一：可不可变
String 创建后不能改，拼接会产生新对象。StringBuilder 和 StringBuffer 内部是可变的字符序列，append、insert、delete 都在原对象上操作。

### 区别二：线程安全
StringBuffer 的公开方法加了 synchronized，多线程同时操作不会互相破坏。StringBuilder 没有这层保护，多线程共享同一个对象时可能得到错误结果。

### 方案对比：三者怎么选
| 类 | 可变 | 线程安全 | 适合 |
|---|---|---|---|
| String | 否 | 是（不可变） | 内容基本不变的字符串、常量、作为 key |
| StringBuilder | 是 | 否 | 单线程下的大量拼接 |
| StringBuffer | 是 | 是（方法加同步） | 需要多线程共享并修改同一个字符串 |

结论：默认选 StringBuilder；字符串基本不变就用 String；极少数需要多线程共享修改同一个对象时才用 StringBuffer。

### 为什么不是都用 StringBuffer
StringBuffer 加同步会带来额外开销，而绝大多数拼接都发生在方法内部的局部变量上，根本没有线程共享，这份开销是白花的。多个线程各用各的 StringBuilder，也不会冲突。

### 进阶：StringBuffer 的线程安全有边界（基础薄弱可先跳过）
StringBuffer 保证的是单个方法调用是原子的。如果你先 `length()` 再 `append()`，两个调用之间别的线程可能插入操作，组合起来仍然需要自己加锁。所以它的“线程安全”没有想象中那么万能。

## 易错点
- 以为 StringBuffer 的组合操作也线程安全；只有单个方法是同步的
- 以为 StringBuilder 一定比 StringBuffer 快很多；差别取决于场景，不要夸大
- 以为 String 可以直接修改内容；String 不可变

## 追问
### [f1] 为什么 String 是线程安全的？
因为它不可变，创建后内容不会变，多个线程只读不改，不会互相影响。
