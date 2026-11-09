---
id: q_01M6ZYJ7HH8HVKMT9W4H158GWE
title: Java 中常见的 OOM 有哪些类型？
type: concept
difficulty: easy
importance: 2
category: jvm
tags: [performance-diagnosis, memory-area]
prerequisites: [q_01M6XBG0GJSYRZYJMNWKXA3NZH]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
常见的有堆溢出、元空间溢出和直接内存溢出；栈太深抛的 StackOverflowError 不叫 OOM，但同样是内存区域不足。

## 要点
- [kp1|3] 堆满了抛 OutOfMemoryError: Java heap space，对象太多或泄漏最常见
- [kp2|3] 报错信息里冒号后面的文字，说明是哪块区域出了问题
- [kp3|2] 类加载太多会抛 OutOfMemoryError: Metaspace
- [kp4|2] 栈深度超限抛 StackOverflowError，常见于无限递归
- [kp5] 直接内存不足会抛 OutOfMemoryError: Direct buffer memory

## 详解
### 先搞懂：不同的“房间”满了，报错不一样
JVM 把内存分成好几个区域，像一栋楼里不同的房间：放对象的、放类信息的、放方法调用的、放 NIO 缓冲区的。哪个房间满了，就抛对应的错，所以看到报错先读后半句。

术语：
- **堆**：放对象和数组的地方；
- **元空间**：放类信息的地方，用的是操作系统的本地内存；
- **栈**：每个线程自己的，方法调用一层一层往里放。

### 常见类型对照
| 报错信息 | 哪块区域 | 常见原因 |
|---|---|---|
| `OutOfMemoryError: Java heap space` | 堆 | 一次创建大量对象，或内存泄漏 |
| `OutOfMemoryError: Metaspace` | 元空间 | 加载的类太多，如动态生成类不停增加 |
| `StackOverflowError` | 线程栈 | 递归没有出口，调用层数过深 |
| `OutOfMemoryError: Direct buffer memory` | 直接内存 | NIO 缓冲区申请过多、没有及时释放 |
| `OutOfMemoryError: unable to create native thread` | 操作系统线程 | 创建的线程太多 |
| `OutOfMemoryError: GC overhead limit exceeded` | 堆 | 花了大量时间做 GC，却几乎回收不到空间 |

注意：`StackOverflowError` 是 `Error` 的子类，但不是 `OutOfMemoryError`；口头回答时说清楚这一点更准确。

## 示例
```java
// 无限递归：每次调用压入一个栈帧，最终抛 StackOverflowError
static void f() { f(); }

// 不断往集合里放对象，且集合一直被引用：最终抛 OutOfMemoryError: Java heap space
List<byte[]> list = new ArrayList<>();
while (true) { list.add(new byte[1024 * 1024]); }
```

## 易错点
- 把所有内存问题都叫“堆溢出”；先看报错文字，Metaspace 和直接内存溢出调堆参数没用
- 把 StackOverflowError 当作 OutOfMemoryError；前者是栈调用太深，后者是申请不到空间

## 追问
### [f1] 遇到 StackOverflowError 一般怎么处理？
先看堆栈信息里重复出现的方法，检查递归的终止条件；确实需要深层调用时，可以改成循环，或者用 `-Xss` 调大线程栈大小。
