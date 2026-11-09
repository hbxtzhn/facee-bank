---
id: q_01M6XBG0GJSYRZYJMNWKXA3NZH
title: 什么是 Error？
type: concept
difficulty: easy
importance: 2
category: java
tags: [exception, performance-diagnosis]
prerequisites: [q_01M6ZYJ32ZRHASWVX5Z89KBFGD]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Error 表示 JVM 层面的严重错误，如内存不足、栈溢出，业务代码一般没法恢复，通常不去捕获，而是排查原因。

## 要点
- [kp1|3] Error 是 Throwable 的子类，和 Exception 平级
- [kp2|3] 它表示 JVM 或系统级的严重问题，程序一般无法处理
- [kp3|2] 常见的有 OutOfMemoryError 和 StackOverflowError
- [kp4|2] 编译器不强制处理 Error
- [kp5] 出现 Error 应当排查并修复根因，而不是 catch 掉继续跑

## 详解
### 先搞懂：不是你的业务出错，是“房子”出问题
上线后的服务偶尔会突然报错：内存满了，或者调用层级太深栈用完了。这些不是用户输入错了或者数据库连接失败这类“业务问题”，而是运行程序的环境本身撑不住了。

打个比方：业务异常像是“快递地址写错了”，你可以改地址重发；Error 像是“仓库塌了”，换个地址没用。

后文用到的词：

- **JVM**：运行 Java 程序的虚拟机。
- **堆**：存放对象的内存区域。
- **栈**：每个线程调用方法时使用的内存区域。

### Error 在家族树里的位置
`Throwable` 下面分成 `Error` 和 `Exception` 两支。`Error` 一支表示严重的、通常与 JVM 运行状态有关的问题，编译器不要求你捕获或声明。

### 常见的两种
- **OutOfMemoryError**：内存不足。比如堆已经装满，又要创建新对象，JVM 又回收不出空间。
- **StackOverflowError**：栈溢出。最典型的是方法无限递归，调用层级太深，栈放不下了。

另外还有类加载失败等，也属于 Error 一支。

### 遇到 Error 怎么办
Error 说明有严重问题，这时程序的状态往往已经不可靠。一般的做法是：

- 不要用 `catch` 把它吞掉后继续运行；
- 查日志、看内存和线程情况，找到根因，比如内存泄漏、递归没有出口、堆设置过小；
- 在服务层面配合监控、告警和自动重启。

偶尔也有场景会捕获 Error，比如在最外层记录日志后让程序退出，但这是特例，不是日常做法。

## 示例
```java
static void recurse() {
    recurse(); // 没有出口的递归
}
public static void main(String[] args) {
    try {
        recurse();
    } catch (StackOverflowError e) {
        System.out.println("栈溢出，这是 Error，正常应该修复递归而不是捕获");
    }
}
```

## 易错点
- 以为 Error 是 Exception 的一种；它们是 Throwable 下平级的两支
- 以为捕获了 OutOfMemoryError 程序就恢复正常了；程序状态可能已经不可靠
- 把 Error 和运行时异常混为一谈；运行时异常通常是代码逻辑错误，Error 是 JVM 层面的严重问题
- 用 `catch (Throwable)` 兜底，不小心把 Error 一起吞掉

## 追问
### [f1] 线上出现 OutOfMemoryError 一般怎么排查？
先看是堆满了还是别的区域，再用堆转储工具分析哪些对象占得最多，判断是内存泄漏还是容量确实不够。常见做法是提前配置 OOM 时自动生成堆转储文件。
