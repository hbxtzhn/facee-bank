---
id: q_01M6ZYJ32ZRHASWVX5Z89KBFGD
title: Java 的异常分为哪几类？
type: concept
difficulty: easy
importance: 3
category: java
tags: [exception]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Java 所有异常和错误的根类是 Throwable，下分 Error 和 Exception；Exception 又分编译时异常（受检异常）和运行时异常。

## 要点
- [kp1|3] Throwable 是根类，下分 Error 和 Exception
- [kp2|3] Error 是 JVM 级严重错误，程序一般不处理，如内存溢出
- [kp3|2] 编译时异常（受检异常）必须捕获或用 throws 声明，否则编译不过
- [kp4|2] 运行时异常是 RuntimeException 及其子类，编译器不强制处理
- [kp5] 只有 Throwable 及其子类才能被 throw 和 catch

## 详解
### 先搞懂：程序出事，分几种
做项目时，程序出问题的原因各不相同：磁盘读不到文件、数据库连不上、代码里访问了空对象、服务器内存耗尽。Java 把这些情况归成一棵“家族树”，好让你对不同的问题采取不同的办法。

打个比方：把它看成家里出了状况——停电、水管漏了、房子塌了。有的你能自己处理，有的只能等专业人员。

后文用到的词：

- **异常**：程序运行中出现的不正常情况，可以被捕获处理。
- **捕获**：用 `try-catch` 接住异常，不让程序直接中断。
- **受检异常**：编译器检查你有没有处理的异常。

### 这棵树长什么样
```text
Throwable
├── Error
└── Exception
    ├── RuntimeException（运行时异常）
    └── 其他（编译时异常 / 受检异常）
```

### Error：程序处理不了的严重错误
`Error` 表示 JVM 层面的严重问题，如内存不足（`OutOfMemoryError`）、栈溢出（`StackOverflowError`）。这类问题通常不是业务代码能恢复的，一般不去捕获。

### Exception：程序可以处理的异常
`Exception` 表示程序有机会处理的情况，又分两类：

- **编译时异常（受检异常）**：除了 `RuntimeException` 及其子类以外的 `Exception`，如 `IOException`。编译器强制你要么 `try-catch`，要么在方法上 `throws`，否则编译不通过。
- **运行时异常（非受检异常）**：`RuntimeException` 及其子类，如 `NullPointerException`、`ArrayIndexOutOfBoundsException`。编译器不强制处理，通常是代码逻辑有问题。

### 怎么记
看名字，不看根：`Error` 是“出大事了”，受检异常是“外部环境可能出问题，你得有预案”，运行时异常是“代码自己写错了”。

## 示例
```java
try {
    java.nio.file.Files.readString(java.nio.file.Path.of("a.txt")); // IOException：必须处理
} catch (java.io.IOException e) {
    System.out.println("读文件失败");
}
int[] arr = new int[1];
// arr[2] = 1; // ArrayIndexOutOfBoundsException：编译不报错，运行时才抛
```

## 易错点
- 以为 Exception 都是受检异常；RuntimeException 属于 Exception，却不受检
- 以为 Error 是 Exception 的子类；两者平级，都是 Throwable 的子类
- 以为运行时异常不能 catch；可以捕获，只是编译器不强制
- 用 catch (Throwable) 把 Error 也一起吞掉，会掩盖严重的问题

## 追问
### [f1] 编译时异常和运行时异常的区别是什么？
编译器是否强制处理。编译时异常不处理就编译不通过，运行时异常编译器不管。前者通常指外部环境导致的问题，后者通常是代码缺陷。
