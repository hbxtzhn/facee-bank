---
id: q_01M6XBNWPCY2YAMPPACF1XC28Y
title: 什么是编译时异常（受检异常）？
type: concept
difficulty: easy
importance: 2
category: java
tags: [exception]
prerequisites: [q_01M6ZYJ32ZRHASWVX5Z89KBFGD]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
编译时异常（受检异常）是编译器强制你处理的异常，要么用 try-catch 捕获，要么在方法上用 throws 声明，否则编译不通过，典型的是 IOException。

## 要点
- [kp1|3] 编译时异常是 Exception 中除 RuntimeException 及其子类以外的部分
- [kp2|3] 编译器强制处理：用 try-catch 捕获，或用 throws 声明抛出
- [kp3|2] 常见的有 IOException、SQLException
- [kp4|2] 通常代表外部环境可能出问题，如文件、网络、数据库
- [kp5] 不处理会编译失败，而不是运行时才报错

## 详解
### 先搞懂：编译器当“质检员”
做项目时读文件、连数据库、调用网络，这些事都可能因为外部原因失败：文件不存在、网络断了。Java 的设计者认为，这类问题是可以预见的，所以让编译器提前检查你有没有想过它失败了怎么办。

打个比方：编译器像质检员，看到“读文件”这一步，就问你：“失败了怎么办？要么你自己处理，要么明确告诉调用者你不处理。”你什么都不说，它就不放行。

后文用到的词：

- **编译**：把源代码翻译成可运行的字节码，这一步会做语法和类型检查。
- **捕获**：用 `try-catch` 在当前方法里处理异常。
- **声明抛出**：用 `throws` 告诉调用者“我这里可能抛出这个异常”。

### 哪些是编译时异常
`Exception` 的子类中，除了 `RuntimeException` 及其子类，其余都是编译时异常，也叫受检异常。常见的有：

- `IOException`：读写文件、网络时出错；
- `SQLException`：操作数据库出错；
- `ClassNotFoundException`：找不到类。

### 必须怎么处理：二选一
当调用的代码可能抛出受检异常，你有两种选择：

1. **捕获**：用 `try-catch` 在当前方法里处理，处理完程序继续；
2. **声明抛出**：在方法签名上写 `throws 异常类型`，交给调用方处理。调用方同样要在这两种方式中选一种。

两者都不做，编译器直接报错。

### 它和运行时异常的区别
运行时异常（如空指针）编译器不强制处理，通常是代码写错了，应当修复代码。受检异常通常是环境的原因，代码没错，所以要求写出应对办法。

## 示例
```java
// 方式一：捕获
void read1() {
    try {
        java.nio.file.Files.readString(java.nio.file.Path.of("a.txt"));
    } catch (java.io.IOException e) {
        System.out.println("读取失败：" + e.getMessage());
    }
}
// 方式二：声明抛出，交给调用者
void read2() throws java.io.IOException {
    java.nio.file.Files.readString(java.nio.file.Path.of("a.txt"));
}
```

## 易错点
- 以为受检异常是运行到才报错；它是编译阶段就报错
- 为了编译通过，catch 之后什么也不做；这样出了问题没有任何线索
- 以为所有 Exception 都是受检的；RuntimeException 不受检
- 在 throws 里声明了异常，就以为自己已经处理好了；这只是把责任转交给了调用者

## 追问
### [f1] 为什么有人不喜欢受检异常？
因为它会让调用链上每一层都要写 try-catch 或 throws，代码变得啰嗦，不少框架因此把受检异常包装成运行时异常再抛出。
