---
id: q_01M6XBGJH7GT4JNQYFH4X6MHMY
title: 什么是堆转储（Heap Dump）？
type: concept
difficulty: easy
importance: 1
category: jvm
tags: [performance-diagnosis]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
堆转储（Heap Dump）是某一时刻 JVM 堆内存的快照文件，里面记录了所有存活对象，用来分析哪些对象占内存最多、是谁引用了它们。

## 要点
- [kp1|3] 堆转储是堆内存在某个时刻的快照，通常保存为 .hprof 文件
- [kp2|3] 可以用 jmap 手动导出，或用 -XX:+HeapDumpOnOutOfMemoryError 在 OOM 时自动生成
- [kp3|2] 用 VisualVM、MAT 等工具打开，可以看对象数量、大小和引用关系
- [kp4] 导出时应用会停顿，文件大小与堆中数据量相关

## 详解
### 先搞懂：dump 就是给堆“拍一张照片”
排查内存问题时，只看数字不知道堆里到底装了什么。堆转储就像给堆拍了一张全景照片，之后可以慢慢看：哪种对象最多，谁占的位置最大。

术语：
- **hprof**：HotSpot 堆转储常见的文件格式，后缀是 `.hprof`；
- **引用链**：从某个对象往回找，是谁拿着它不放。

### 怎么得到堆转储
- **手动导出**：`jmap -dump:live,format=b,file=heap.hprof <pid>`；`live` 表示只导出存活对象；
- **自动导出**：启动参数加 `-XX:+HeapDumpOnOutOfMemoryError`，可以再用 `-XX:HeapDumpPath` 指定保存路径。

### 拿到后怎么用
1. 用 VisualVM、MAT 等工具打开 `.hprof` 文件；
2. 按类统计对象数量和占用大小，找最多、最大的；
3. 顺着引用链往回查，找到是哪个静态集合、缓存或 ThreadLocal 持有；
4. 回到对应代码修复。

## 示例
```bash
# 手动导出
jmap -dump:live,format=b,file=heap.hprof 12345

# 启动时配置：OOM 自动导出
java -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/data/dump -jar app.jar
```

## 易错点
- 以为 dump 只是日志；它是完整的堆快照，可能包含敏感数据，要注意保管
- 出事后才想起导出；进程崩溃后现场已经没了，应提前配置自动导出

## 追问
### [f1] 堆转储和线程转储有什么区别？
堆转储记录的是堆里的对象，用于排查内存问题；线程转储（jstack）记录的是各线程的调用栈，用于排查死锁、卡顿和 CPU 飙高。
