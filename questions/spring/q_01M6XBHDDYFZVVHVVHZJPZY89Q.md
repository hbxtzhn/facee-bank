---
id: q_01M6XBHDDYFZVVHVVHZJPZY89Q
title: 编程式事务和声明式事务有什么区别？
type: concept
difficulty: medium
importance: 3
category: spring
tags: [transaction-management, aop]
prerequisites: [q_01M6XBHD5MJC4VZFMFPVN4VMKC]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
编程式事务在代码里显式写出开启、提交、回滚，控制精细但代码侵入多；声明式事务用 @Transactional 注解，靠 AOP 代理自动完成，代码更简洁，是日常首选。

## 要点
- [kp1|3] 编程式：用 TransactionTemplate 或 PlatformTransactionManager 手写事务边界
- [kp2|3] 声明式：用 @Transactional，基于 AOP 代理，业务代码里没有事务逻辑
- [kp3|2] 编程式可以只包住方法中的一小段代码；声明式的粒度通常是整个方法
- [kp4] 声明式会受代理限制（自调用、非 public 等），编程式不受影响

## 详解
### 先搞懂：自己开车和叫代驾
编程式事务像自己开车：每一个转弯、停车都自己控制，想怎么走都行，但全程都要自己操心。声明式事务像叫代驾：你只说去哪，路上的事由别人处理，省心，但只能按代驾的方式走。

后文用到的术语：
- **TransactionTemplate**：Spring 提供的模板类，把“开启、提交、回滚”封装好，你只需要传入业务代码。
- **PlatformTransactionManager**：事务管理器接口，可以手动调用开启、提交和回滚。
- **事务边界**：事务从哪里开始、到哪里结束。

### 编程式事务：自己写事务边界
用 `TransactionTemplate` 时，把需要事务的代码放进回调里，模板负责提交，出现异常时负责回滚。用 `PlatformTransactionManager` 则要自己调用 `getTransaction`、`commit`、`rollback`，更底层，也更容易漏写。

### 声明式事务：靠 AOP 自动处理
给方法加 `@Transactional`，Spring 为这个 Bean 创建代理。调用方法时，代理先开启事务，方法正常结束就提交，抛出需要回滚的异常就回滚。业务代码里完全看不到事务代码。

### 方案对比：编程式和声明式
| 维度 | 编程式事务 | 声明式事务 |
|---|---|---|
| 写法 | 代码里显式调用 | 加 `@Transactional` 注解 |
| 代码侵入 | 高，事务代码和业务混在一起 | 低，业务代码保持干净 |
| 控制粒度 | 灵活，可以只包住几行代码 | 一般按整个方法 |
| 失效风险 | 不依赖代理，自调用也可用 | 受代理限制，自调用、private 方法会失效 |
| 适合场景 | 事务范围要精细控制 | 绝大多数业务方法 |

结论：默认用声明式，简洁、不容易写错；只有事务范围需要精细控制（例如方法里只有一小段要事务，其他是耗时的远程调用）时，才用编程式。

### 为什么要精细控制范围
事务期间一直占用数据库连接。如果整个方法里夹杂耗时的远程调用，连接就被占着不放，用声明式没法只包住数据库操作的那几行；此时用 `TransactionTemplate` 把写库的部分单独包起来更合适。

## 示例
```java
// 编程式：只把写库部分放进事务
transactionTemplate.execute(status -> {
    stockMapper.decrease(skuId);
    orderMapper.insert(userId, skuId);
    return null;
});

// 声明式：一个注解搞定
@Transactional(rollbackFor = Exception.class)
public void createOrder() { /* ... */ }
```

## 易错点
- 以为编程式一定比声明式好；手写更容易漏掉回滚，也让业务代码变乱
- 以为两者原理完全不同；声明式内部最终也是调用事务管理器，只是由 AOP 代理代劳
- 在 `TransactionTemplate` 回调里吞掉异常，同样不会回滚；需要抛出或调用 `status.setRollbackOnly()`

## 追问
### [f1] 声明式事务底层用的就是事务管理器吗？
是的。代理里的事务拦截器会调用 `PlatformTransactionManager` 开启、提交、回滚，所以声明式可以看成是自动帮你调用编程式的那套 API。

### [f2] 什么情况下一定要用编程式？
通常是想在一个方法里精细控制事务范围，或者需要绕开代理限制、在循环里分批提交时。
