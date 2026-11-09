---
id: q_01M6ZYJ3C3Y1WZXJ6BB8CNC0TE
title: 什么是运行时异常？
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
运行时异常是 RuntimeException 及其子类，在程序运行时才抛出，通常是代码逻辑有问题，比如空指针、数组越界，编译器不强制你处理。

## 要点
- [kp1|3] 运行时异常指 RuntimeException 及其子类
- [kp2|3] 运行时才抛出，编译不检查，不强制 try-catch 或 throws
- [kp3|2] 常见的有空指针、数组越界、类型转换异常
- [kp4|2] 通常说明代码有缺陷，应修复代码，而不是靠 catch 掩盖
- [kp5] 也叫非受检异常

## 详解
### 先搞懂：代码自己写错了
做项目时最常见的报错是什么？大概是“空指针”：一个变量还没有对象就拿来用。还有数组下标超出范围、类型强转不对。这些问题的共同点是：不是外面的环境出了问题，而是代码本身有错。

打个比方：受检异常像是“快递可能晚到”，是外部原因，需要预案；运行时异常像是“你把收件地址写漏了一栏”，是自己的疏忽，应该改正，而不是准备预案。

后文用到的词：

- **运行时**：程序已经启动、正在执行的阶段。
- **非受检异常**：编译器不检查你有没有处理的异常，运行时异常就属于这一类。

### 有哪些常见的
- `NullPointerException`：对 null 调用方法或访问字段；
- `ArrayIndexOutOfBoundsException`：数组下标超出范围；
- `ClassCastException`：把对象强转成不兼容的类型；
- `IllegalArgumentException`：方法收到了不合法的参数；
- `ArithmeticException`：如整数除以零。

### 为什么编译器不强制处理
这类异常几乎出现在每一行代码的潜在位置，如果每处都要求写 try-catch，代码会变得非常臃肿。而且它们本来就是 bug，更合理的做法是在代码里提前避免，比如判空、检查下标。

### 怎么处理
- 优先**预防**：判空、校验参数、检查范围；
- 不要用 `catch` 随便吞掉，那样会把 bug 藏起来；
- 在系统入口（如接口的统一异常处理层）捕获，记录日志并返回友好的错误信息。

也可以在方法里主动抛出运行时异常，来表示参数或状态不合法，比如 `throw new IllegalArgumentException("age 不能为负")`。

## 示例
```java
String s = null;
// s.length();          // 编译通过，运行时抛 NullPointerException
if (s != null) {        // 预防比捕获更好
    System.out.println(s.length());
}
int[] arr = new int[3];
// arr[3] = 1;          // ArrayIndexOutOfBoundsException
```

## 易错点
- 以为运行时异常不用管；它们同样会让程序崩溃，只是编译器不提醒
- 用 try-catch 包住整段代码，把所有 RuntimeException 悄悄吞掉
- 以为只有 Java 内置的才是运行时异常；自定义异常继承 RuntimeException 也是
- 以为运行时异常不能捕获；可以捕获，只是通常不该依赖捕获来规避 bug

## 追问
### [f1] 自定义异常应该继承 Exception 还是 RuntimeException？
调用者能合理地处理或恢复，并希望编译器提醒，就继承 Exception。多数业务异常由统一入口处理，继承 RuntimeException 更省事，也更常见。
