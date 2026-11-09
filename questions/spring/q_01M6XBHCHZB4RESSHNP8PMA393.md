---
id: q_01M6XBHCHZB4RESSHNP8PMA393
title: 抛出检查异常时，@Transactional 为什么不回滚？
type: concept
difficulty: medium
importance: 3
category: spring
tags: [transaction-management, exception]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
@Transactional 默认只在抛出运行时异常（RuntimeException）和 Error 时回滚；检查异常默认不回滚，要用 rollbackFor 指定。

## 要点
- [kp1|3] 默认回滚：RuntimeException 及其子类、Error
- [kp2|3] 默认不回滚：检查异常，如 IOException、SQLException
- [kp3|2] 想让检查异常也回滚，写 `@Transactional(rollbackFor = Exception.class)`
- [kp4] 反过来，noRollbackFor 可指定某些异常不回滚

## 详解
### 先搞懂：两种异常
Java 的异常分两类：

- **运行时异常**：不强制处理，比如空指针、数组越界、非法参数，一般表示程序出错了；
- **检查异常**：编译器强制你处理（要么 catch，要么在方法上声明 throws），比如读文件时的 `IOException`，一般表示可预期的外部问题。

可以这么理解 Spring 的默认设定：运行时异常是“严重事故”，必须撤销重来；检查异常是“可预期的业务情况”，调用方可能有自己的处理办法，所以默认不回滚。这个默认规则沿用自 EJB 的惯例。

后文用到的术语：
- **rollbackFor**：指定哪些异常类型也要回滚。
- **noRollbackFor**：指定哪些异常类型即使抛出也不回滚。

### 实际会遇到什么问题
一个方法声明了 `throws Exception`，里面先插入订单，再做一步会抛 `IOException` 的操作。出异常后，订单记录依然被提交，因为 `IOException` 是检查异常，默认不触发回滚。

### 怎么解决
在注解里指定回滚的异常类型：

```java
@Transactional(rollbackFor = Exception.class)
public void createOrder() throws Exception {
    orderMapper.insert();
    writeFile();   // 可能抛 IOException
}
```

`rollbackFor = Exception.class` 表示所有异常（包括检查异常）都回滚。很多团队习惯统一这样写，避免遗漏。

### 回滚规则怎么判断
异常抛出后，Spring 先看有没有匹配 `rollbackFor`、`noRollbackFor` 的规则，匹配到就按规则；都没匹配，就用默认规则：运行时异常和 `Error` 回滚，其他不回滚。

## 易错点
- 以为只要抛异常就回滚；检查异常默认会提交
- 配了 `rollbackFor` 却在方法里把异常 catch 掉；异常没有抛出来，同样不会回滚
- 以为 `Exception` 一定被默认覆盖；默认只覆盖 `RuntimeException` 和 `Error`

## 追问
### [f1] Error 会回滚吗？
会。默认规则是 `RuntimeException` 和 `Error` 都回滚。

### [f2] 为什么 Spring 默认不回滚检查异常？
设计上认为检查异常是业务上可预期、调用方可以处理的情况，不一定意味着数据有问题；需要回滚的话由开发者显式声明。
