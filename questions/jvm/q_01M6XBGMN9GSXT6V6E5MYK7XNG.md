---
id: q_01M6XBGMN9GSXT6V6E5MYK7XNG
title: 什么是直接内存？
type: concept
difficulty: easy
importance: 1
category: jvm
tags: [memory-area, io-multiplexing]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
直接内存是 JVM 堆之外的系统内存，不由 GC 直接管理，NIO 用它做数据缓冲区，读写 IO 时可以少一次拷贝。

## 要点
- [kp1|3] 直接内存不在 JVM 堆里，而是操作系统的本地内存
- [kp2|3] NIO 的 ByteBuffer.allocateDirect 就是在申请直接内存
- [kp3|2] 它不由 GC 直接回收，需要等对应的 Java 对象被回收时才释放
- [kp4|2] 分配和回收成本较高，但读写 IO 时可以少一次拷贝
- [kp5] 用完太多会抛 OutOfMemoryError: Direct buffer memory

## 详解
### 先搞懂：堆外的“临时仓库”
Java 程序读写网络或文件时，数据要经过缓冲区。普通缓冲区在堆里，数据要先从系统内存拷贝到堆；直接内存相当于在堆外开一个“临时仓库”，数据直接放在系统内存，少搬一次。

术语：
- **NIO**：Java 的非阻塞 IO 体系，用缓冲区读写数据；
- **堆外内存**：不在 JVM 堆里的内存，GC 不会整理它。

### 怎么使用
通过 `ByteBuffer.allocateDirect(size)` 申请。Netty 等网络框架大量使用直接内存，减少 IO 时的数据拷贝。

### 优缺点
| 对比项 | 堆内缓冲区 | 直接内存缓冲区 |
|---|---|---|
| 位置 | JVM 堆 | 操作系统本地内存 |
| 分配和回收 | 较快 | 成本较高 |
| IO 读写 | 多一次拷贝 | 可以少一次拷贝 |
| GC 管理 | 由 GC 管理 | 不由 GC 直接管理 |

结论：需要频繁做大块网络或文件 IO 时，直接内存更合适；一般场景用堆内缓冲区即可。

### 怎么释放，又怎么限制
直接内存本身 GC 不扫描，但 Java 里持有它的 `ByteBuffer` 对象在堆里；该对象被回收时，才会触发直接内存的释放。可用 `-XX:MaxDirectMemorySize` 设置上限，超限则抛 `OutOfMemoryError: Direct buffer memory`。

## 示例
```java
ByteBuffer buf = ByteBuffer.allocateDirect(1024); // 申请 1KB 直接内存
buf.put("hello".getBytes());
```

## 易错点
- 以为直接内存不会 OOM；它有上限，用太多也会抛 OOM
- 以为堆设得大就够了；堆外内存不算在 `-Xmx` 里，进程总内存要把它算上

## 追问
### [f1] 直接内存泄漏怎么排查？
堆 dump 里看不到直接内存本体，要看是不是有大量 ByteBuffer 对象没被回收，或使用框架提供的堆外内存监控；也要检查是否频繁手动调用 `System.gc()`。
