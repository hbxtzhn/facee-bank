---
id: q_01M6XBHC92C8WJJA32XPB5WG17
title: 在 catch 中吞掉异常，为什么事务不会回滚？
type: scenario
difficulty: medium
importance: 3
category: spring
tags: [transaction-management, exception]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Spring Framework 参考文档：Rolling Back a Declarative Transaction", url: "https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html" }
estimatedMinutes: 3
---

## 一句话
Spring 靠方法抛出的异常来决定回滚；异常在 catch 里被吞掉，事务代理看到的是方法正常结束，就会提交事务。

## 要点
- [kp1|3] 事务代理只能感知方法抛出来的异常，感知不到被 catch 掉的异常
- [kp2|3] 方法正常返回，代理就提交事务，即使里面有 SQL 已经失败
- [kp3|2] 解决办法：catch 后重新抛出异常，或手动标记回滚
- [kp4] 手动标记用 TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()

## 详解
### 先搞懂：代理只看“有没有报错出来”
假设下单方法里要扣库存、写订单。为了不让用户看到报错，开发者在外面包了 try-catch，出错就打一行日志。库存扣了，订单没写成，但用户看不到异常，数据库里却留下了半截数据。

这就像快递站只检查有没有人喊“出事了”：你在车间里发现问题自己悄悄处理了，没往外喊，站点就按“一切正常”收货。事务代理就是这个站点。

后文用到的术语：
- **事务代理**：包在业务方法外面，负责提交或回滚的那一层。
- **回滚标记（rollback-only）**：告诉事务“最后必须回滚”的标志。

### 为什么会提交
代理的执行流程是：调用目标方法，再根据结果处理。

- 目标方法抛出异常（并且是需要回滚的类型）：代理捕获后回滚；
- 目标方法正常返回：代理提交。

方法里的 `try { ... } catch (Exception e) { log.error(...) }` 把异常吃掉了，对代理来说，方法就是正常返回，所以走提交。已经执行成功的 SQL 被一并提交，失败那条没生效，数据就不完整。

### 怎么解决
1. **catch 后重新抛出**：把异常包装成运行时异常再抛，代理就能感知并回滚。
2. **手动标记回滚**：不想抛异常时，在 catch 里调用 `setRollbackOnly()`，代理在方法结束时会据此回滚。
3. **缩小 try-catch 范围**：只把真正需要容错的、与事务无关的操作包起来，数据库操作的异常让它直接往外抛。

## 示例
```java
@Transactional
public void createOrder() {
    try {
        stockMapper.decrease();
        orderMapper.insert();
    } catch (Exception e) {
        log.error("下单失败", e);
        // 方式一：重新抛出，让事务回滚
        throw new RuntimeException(e);
        // 方式二（二选一）：
        // TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
    }
}
```

## 易错点
- 只打日志不抛异常，以为事务会自动回滚；代理看到方法正常返回就会提交
- catch 后抛出的是检查异常，却没配置 `rollbackFor`；检查异常默认也不回滚
- 以为 `@Transactional` 方法里吞掉异常，事务最终会提示报错；通常只会静默提交

## 追问
### [f1] 内层方法抛异常、外层 catch 住，为什么会出现 UnexpectedRollbackException？
内层方法加入了外层事务，抛异常时已把事务标记为只能回滚。外层吞掉异常后正常结束，想提交时发现被标记了，就抛出 `UnexpectedRollbackException`。

### [f2] 为什么不推荐在 Service 里随便 try-catch？
容易吞掉异常导致事务不回滚。更好的做法是让异常向上抛，由统一的异常处理器处理并返回给调用方。
