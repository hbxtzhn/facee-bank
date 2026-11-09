---
id: q_01M6XBHE0KYTEY69J81EKNB030
title: 什么是事务传播机制？
type: concept
difficulty: easy
importance: 3
category: spring
tags: [transaction-management]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
事务传播机制规定：一个事务方法被另一个事务方法调用时，是加入对方的事务，还是自己新开事务；默认的 REQUIRED 是有事务就加入，没有就新建。

## 要点
- [kp1|3] 传播机制解决“事务方法调用事务方法”时，事务怎么衔接的问题
- [kp2|3] 默认是 REQUIRED：已有事务就加入，没有就新建
- [kp3|2] 通过 @Transactional(propagation = ...) 设置，共有七种
- [kp4] 加入同一个事务后，任何一个方法回滚，整个事务都回滚

## 详解
### 先搞懂：下单里再调用“记日志”
下单方法 `createOrder()` 有事务，它里面又调用了“扣库存”和“记操作日志”，这两个方法也各自带事务。问题来了：它们是和下单共用一个事务，还是各开各的？

可以类比公司报销：一种是所有费用合进同一张报销单，一起批或一起驳回（加入同一个事务）；另一种是每笔费用单独走一张单子，互不影响（各自新开事务）。传播机制就是在规定走哪种。

后文用到的术语：
- **传播行为**：被调用方法如何对待已有事务。
- **外层方法**：调用别人的方法；**内层方法**：被调用的方法。
- **加入事务**：内层方法和外层方法共用同一个事务。

### 默认行为：REQUIRED
`REQUIRED` 是默认值：

- 调用时已经有事务：内层方法**加入**这个事务，两者同成功、同失败；
- 调用时没有事务：内层方法自己**新建**一个事务。

绝大多数业务用这个就够了，保证整个业务流程在同一个事务里。

### 其他传播行为一览
共有七种：`REQUIRED`、`SUPPORTS`、`MANDATORY`、`REQUIRES_NEW`、`NOT_SUPPORTED`、`NEVER`、`NESTED`。比较常用的是：

- `REQUIRES_NEW`：不管有没有事务，都新开一个独立事务，外层事务会被暂时挂起；常用于记日志这类“不管主业务成败都要保存”的操作。
- `SUPPORTS`：有事务就加入，没有就不用事务。

各种行为的具体区别，下一题会细讲。

### 要注意的地方
传播机制同样靠代理实现，所以同一个类内部的 `this` 调用不会触发传播行为的设置。

## 示例
```java
@Transactional                       // 默认 REQUIRED
public void createOrder() {
    stockService.decrease();         // REQUIRED：加入下单事务
    logService.saveLog();            // 若是 REQUIRES_NEW，则单独提交
}

@Transactional(propagation = Propagation.REQUIRES_NEW)
public void saveLog() { /* ... */ }
```

## 易错点
- 以为每个 `@Transactional` 方法都会新开一个事务；默认是加入已有的事务
- 在同一个类里 `this` 调用并期待传播行为生效；会绕过代理，不会生效
- 以为 REQUIRED 加入后，内层单独回滚不影响外层；内层抛异常通常会让整个事务回滚

## 追问
### [f1] 默认的传播行为是什么？
`REQUIRED`：有事务就加入，没有就新建。

### [f2] 传播机制和隔离级别是一回事吗？
不是。传播机制管“事务怎么嵌套衔接”，隔离级别管“事务之间能看到对方什么数据”。
