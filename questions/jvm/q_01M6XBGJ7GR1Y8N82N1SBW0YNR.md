---
id: q_01M6XBGJ7GR1Y8N82N1SBW0YNR
title: JVM 常用的诊断工具有哪些？
type: concept
difficulty: easy
importance: 2
category: jvm
tags: [performance-diagnosis]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
命令行工具有 jps（看 Java 进程）、jstack（看线程栈）、jmap（看堆和导出 dump）、jstat（看 GC 统计）；图形化工具有 jconsole 和 VisualVM。

## 要点
- [kp1|3] jps 列出 Java 进程，jstack 查看线程堆栈，用来排查死锁和 CPU 飙高
- [kp2|3] jmap 查看堆对象统计并导出堆 dump，jstat 查看 GC 和内存区使用情况
- [kp3|2] jconsole 和 VisualVM 是图形化工具，可以监控内存、线程、类
- [kp4] VisualVM 还能加载离线的堆 dump 文件做分析

## 详解
### 先搞懂：这些工具就像“体检设备”
服务出问题时，不能凭感觉猜，要先给 JVM 做体检。JDK 自带了一批小工具，每个负责检查一项：进程在不在、线程在干嘛、堆里装了什么、GC 忙不忙。

术语：
- **线程栈**：线程当前正在执行的方法调用链，能看到它卡在哪一行；
- **堆 dump**：某一时刻堆内存的快照文件。

### 命令行工具
| 工具 | 用来看什么 | 典型场景 |
|---|---|---|
| `jps` | 当前机器上的 Java 进程及进程号 | 先找到要排查的进程 |
| `jstack` | 进程内各线程的堆栈 | 排查死锁、线程卡住、CPU 飙高 |
| `jmap` | 堆的对象统计，也能导出堆 dump | 排查内存泄漏 |
| `jstat` | GC 次数、耗时、各内存区使用率 | 判断 GC 是否异常 |

`jhat` 是旧版 JDK 里分析堆 dump 的工具，JDK 9 起已移除，现在通常改用 VisualVM 或 MAT。

### 图形化工具
- **jconsole**：JDK 自带，监控内存、线程、类加载等，可连接本地或远程进程；
- **VisualVM**：除了监控线程和内存，还能加载离线堆 dump，查看占用最多的对象。

## 示例
```bash
jps -l                    # 列出进程号和主类
jstack 12345              # 查看进程 12345 的所有线程栈
jstat -gc 12345 1000      # 每秒输出一次 GC 统计
jmap -histo 12345         # 按类统计对象数量和占用
```

## 易错点
- 把 jps 当成能看线程；它只列进程，看线程要用 jstack
- 在生产环境随意导出堆 dump；导出时应用会停顿，且文件可能很大

## 追问
### [f1] 怎么用工具发现死锁？
`jstack <pid>` 的输出末尾，如果有死锁，会明确提示 `Found one Java-level deadlock`，并列出相互等待的线程和锁。
