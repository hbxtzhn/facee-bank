---
id: q_01M6XBHD5MJC4VZFMFPVN4VMKC
title: 怎么用 @Transactional 给方法加上事务？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [transaction-management]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
在 Service 的方法或类上加 @Transactional，方法开始前自动开启事务，正常结束就提交，出现异常就回滚，这就是声明式事务。

## 要点
- [kp1|3] 在方法或类上加 @Transactional，不用手写开启、提交、回滚的代码
- [kp2|3] 方法正常结束则提交，抛出运行时异常则回滚
- [kp3|2] 加在类上，表示这个类的方法都带事务；方法上的注解优先
- [kp4] 可通过 rollbackFor、propagation、isolation 等属性调整行为

## 详解
### 先搞懂：两步操作要么都成功，要么都不做
下单要扣库存、再写订单。如果扣完库存、写订单时出错，库存就白扣了。你希望的是：两步要么都完成，要么都撤销，这就是事务要解决的事。

声明式的意思是“你只声明想要什么，不写怎么做”：像打车时只说目的地，路线和计费由司机和平台处理。你在方法上加一个注解，剩下的由 Spring 完成。

后文用到的术语：
- **事务**：一组操作，要么全部成功，要么全部撤销。
- **提交**：确认事务内的所有修改生效。
- **回滚**：撤销事务内的所有修改。

### 怎么用
1. 项目里使用了事务管理器（Spring Boot 引入 JDBC 或 JPA 相关依赖后，会自动配置）；
2. 在 Service 层的 public 方法上加 `@Transactional`；
3. 通过 Spring 容器里的 Bean 调用该方法。

执行过程：调用方法前自动开启事务；方法正常返回时提交；抛出运行时异常时回滚。

### 常用属性
| 属性 | 作用 |
|---|---|
| `rollbackFor` | 指定哪些异常需要回滚（如检查异常） |
| `propagation` | 事务传播行为，默认 REQUIRED |
| `isolation` | 事务隔离级别，默认用数据库的 |
| `readOnly` | 声明只读事务，供底层优化参考 |
| `timeout` | 事务超时时间，单位秒 |

### 放在哪一层
一般加在 Service 层：一个业务操作通常包含多个数据库操作，要放在同一个事务里。不要加在 Controller 层或只执行单条 SQL 的 DAO 层方法上。

## 示例
```java
@Service
public class OrderService {
    @Transactional(rollbackFor = Exception.class)
    public void createOrder(Long userId, Long skuId) {
        stockMapper.decrease(skuId);     // 扣库存
        orderMapper.insert(userId, skuId); // 写订单：这里抛异常，库存扣减也会回滚
    }
}
```

## 易错点
- 以为加了注解就一定生效；异常被 catch 吞掉、自调用、非 public 方法等情况都会失效
- 以为检查异常也默认回滚；需要写 `rollbackFor`
- 在方法里开新线程操作数据库，以为在同一个事务内；新线程用不同的连接

## 追问
### [f1] @Transactional 加在类上和方法上有什么区别？
加在类上，类里的方法默认都带事务；方法上也有注解时，以方法上的为准。

### [f2] 它是怎么实现的？
通过 AOP：Spring 为 Bean 创建代理，代理在方法前后开启、提交或回滚事务。
