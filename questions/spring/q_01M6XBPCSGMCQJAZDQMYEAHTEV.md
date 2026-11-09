---
id: q_01M6XBPCSGMCQJAZDQMYEAHTEV
title: REQUIRED、REQUIRES_NEW 等传播行为有什么区别？
type: concept
difficulty: medium
importance: 3
category: spring
tags: [transaction-management]
prerequisites: [q_01M6XBHE0KYTEY69J81EKNB030]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 5
---

## 一句话
区别在于外层有没有事务时怎么处理：REQUIRED 有就加入、没有就新建，REQUIRES_NEW 总是新开独立事务。

## 要点
- [kp1|3] REQUIRED：有就加入，没有就新建，是默认值
- [kp2|3] REQUIRES_NEW：总是新开事务，外层事务被挂起，两者提交和回滚互不影响
- [kp3|2] SUPPORTS 有就加入、没有就不用事务；MANDATORY 没有就抛异常
- [kp4|2] NOT_SUPPORTED 以非事务运行，NEVER 有事务就抛异常，NESTED 在外层事务里嵌套子事务

## 详解
### 先搞懂：一个场景看懂区别
下单方法 `createOrder()` 调用“记日志”方法 `saveLog()`。分两种情况看：外层有事务，或者外层没有事务。传播行为就是在回答：此时 `saveLog()` 该怎么办。

后文用到的术语：
- **挂起**：暂时把外层事务放一边，先处理内层的，结束后再恢复外层。
- **保存点（savepoint）**：事务内部的一个“存档点”，可以只回滚到这里，而不是回滚整个事务。

### 方案对比：七种传播行为
| 传播行为 | 外层有事务 | 外层没有事务 |
|---|---|---|
| `REQUIRED`（默认） | 加入外层事务 | 新建事务 |
| `REQUIRES_NEW` | 挂起外层，新建独立事务 | 新建事务 |
| `SUPPORTS` | 加入外层事务 | 以非事务方式运行 |
| `MANDATORY` | 加入外层事务 | 抛出异常 |
| `NOT_SUPPORTED` | 挂起外层，以非事务方式运行 | 以非事务方式运行 |
| `NEVER` | 抛出异常 | 以非事务方式运行 |
| `NESTED` | 在外层事务里创建嵌套事务（保存点） | 新建事务 |

结论：绝大多数情况用默认的 `REQUIRED`；需要“不论主流程成败都要保存”（如操作日志）时，用 `REQUIRES_NEW`；其他的在特殊场景才用。

### REQUIRED 和 REQUIRES_NEW：最常被问
- **REQUIRED**：内外同一个事务。内层抛异常，整个事务会被标记为只能回滚，外层即使 catch 了异常，提交时也会失败（抛 `UnexpectedRollbackException`）。
- **REQUIRES_NEW**：内层单独一个事务，用单独的数据库连接。内层成功提交后，外层之后即使回滚，内层已经提交的数据也不会撤销；内层回滚，也不会自动连累外层，除非异常继续向外抛出。

注意：`REQUIRES_NEW` 会占用两个连接，如果连接池很小，高并发时可能出现外层持有一个连接、等待内层获取另一个连接的情况，要留意。

### NESTED：和 REQUIRES_NEW 不一样
`NESTED` 不是独立事务，而是在外层事务里设一个保存点。内层回滚只回到保存点，外层可以继续；但外层回滚时，内层也会一起回滚。它依赖底层事务管理器和数据库对保存点的支持（如 JDBC 的 `DataSourceTransactionManager`）。

### 常用选择小结
- 默认业务：`REQUIRED`
- 日志、审计这类不能被主流程回滚影响的：`REQUIRES_NEW`
- 必须在事务中被调用的方法：`MANDATORY`，起到约束作用

## 示例
```java
@Transactional
public void createOrder() {
    orderMapper.insert();
    try {
        logService.saveLog();   // REQUIRES_NEW：单独提交
    } catch (Exception ignore) { }
    throw new RuntimeException("下单失败"); // 外层回滚，日志仍然保留
}

@Transactional(propagation = Propagation.REQUIRES_NEW)
public void saveLog() { /* 写日志表 */ }
```

## 易错点
- 把 `NESTED` 当成 `REQUIRES_NEW`；前者是保存点，外层回滚会连带回滚它
- 以为 `REQUIRES_NEW` 一定更安全；它多占用连接，用多了会增加死锁和连接耗尽的风险
- 同类里 `this` 调用 `REQUIRES_NEW` 方法，以为会新开事务；绕过代理，不会生效

## 追问
### [f1] REQUIRED 里内层抛异常、外层 catch 了，会怎样？
内层已经把事务标记为只能回滚，外层 catch 后正常结束，提交时会抛出 `UnexpectedRollbackException`，整个事务回滚。

### [f2] REQUIRES_NEW 内层抛异常，一定会让外层回滚吗？
不一定。内层事务自己回滚；如果异常被外层 catch 住，外层事务可以正常提交；如果异常继续向外抛，外层按自己的回滚规则处理。
