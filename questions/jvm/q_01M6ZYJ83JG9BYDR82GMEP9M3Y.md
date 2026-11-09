---
id: q_01M6ZYJ83JG9BYDR82GMEP9M3Y
title: 出现 OOM 该怎么处理？
type: scenario
difficulty: medium
importance: 2
category: jvm
tags: [performance-diagnosis]
prerequisites: [q_01M6XBGGGEJ7230WN07ESPBDX7, q_01M6ZYJ7HH8HVKMT9W4H158GWE]
references:
  - { title: "Java SE 21 故障排查指南：Troubleshoot Memory Leaks", url: "https://docs.oracle.com/en/java/javase/21/troubleshoot/troubleshooting-memory-leaks.html" }
  - { title: "JDK 21 java 命令手册：-XX:+HeapDumpOnOutOfMemoryError", url: "https://docs.oracle.com/en/java/javase/21/docs/specs/man/java.html" }
  - { title: "JDK 21 jcmd 手册：GC.heap_dump", url: "https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
先看报错信息判断是哪块区域溢出，再用 dump 和监控找出大对象或泄漏点，修代码为主，调内存参数为辅。

## 要点
- [kp1|3] 第一步看异常信息，判断是堆、Metaspace、直接内存还是线程数问题
- [kp2|3] 提前配置 OOM 时自动生成堆 dump，事后才能分析
- [kp3|2] 用 MAT 或 VisualVM 分析 dump，找占用最多的对象和引用链
- [kp4|2] 是泄漏就修代码，是容量不够才调大内存或扩容
- [kp5] 结合 GC 日志和监控，看 Full GC 是否频繁、回收后是否下降

## 详解
### 先搞懂：OOM 像急诊，先判断“哪里出了问题”
线上服务突然 OOM，不要先调大内存。就像急诊先问“哪儿疼”：报错信息告诉你哪块区域出了事，不同区域的处理办法完全不同。

术语：
- **堆 dump**：某一时刻堆内存的快照文件，里面能看到有哪些对象、各占多少内存；
- **Full GC**：对整个堆做的大回收，频繁发生往往说明内存吃紧。

### 第一步：从异常信息判断类型
| 报错 | 区域 | 处理方向 |
|---|---|---|
| `Java heap space` | 堆 | 看 dump，找大对象或泄漏 |
| `Metaspace` | 元空间 | 检查动态生成类、类加载器泄漏 |
| `Direct buffer memory` | 直接内存 | 检查 NIO 缓冲区是否释放 |
| `unable to create native thread` | 线程数 | 检查是否无限创建线程 |

### 第二步：保留现场
提前加上 JVM 参数，让 OOM 时自动保存 dump：

```bash
-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/data/dump
```

没有这个参数，进程崩溃后现场就丢了。

### 第三步：定位问题
- 用 MAT 或 VisualVM 打开 dump，按对象数量或占用大小排序，看哪类对象最多；
- 顺着引用链找到是谁持有这些对象（常见是静态集合、缓存、ThreadLocal）；
- 结合 GC 日志或 `jstat`，看 Full GC 之后内存有没有降下来：降不下来，多半是泄漏。

### 第四步：修复
- **泄漏**：改代码，释放引用、关闭资源、给缓存加上限；
- **一次性数据太大**：分页、流式处理，不要一次性加载；
- **确实容量不够**：调大堆（`-Xmx`），或增加机器分担。调参数只是兜底，要先确认不是泄漏。

## 易错点
- 一出 OOM 就调大 `-Xmx`；泄漏场景下只是推迟再次发生
- 没配 dump 参数，出事后无从分析
- 只分析堆；Metaspace、直接内存的溢出不在堆里，dump 看不出来

## 追问
### [f1] 线上不能停，怎么拿堆 dump？
可以用 `jmap -dump` 或 `jcmd <pid> GC.heap_dump` 导出，导出期间应用会短暂停顿。生产环境建议先摘流量，或在其中一个实例上做。

### [f2] dump 文件很大，本地打不开怎么办？
可以在内存更大的机器上用 MAT 分析，或调大分析工具自身的堆内存。
