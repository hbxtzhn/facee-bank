---
id: q_01M6XCC373WPD05WD9JHJ9PT93
title: SqlSessionTemplate 为什么线程安全，并支持事务？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [mybatis-internals, thread-safety, transaction-management]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
`SqlSessionTemplate` 自己不保存会话。每次调用都去 Spring 的事务上下文里取当前线程的 `SqlSession`，所以多线程共用它也安全，还能跟着 Spring 事务提交和回滚。

## 要点
- [kp1|3] `SqlSession` 本身不是线程安全的，`SqlSessionTemplate` 是
- [kp2|3] 每次调用都获取与当前线程、当前事务绑定的 `SqlSession`
- [kp3|2] 有事务时，同一事务里复用同一个会话，由 Spring 统一提交或回滚
- [kp4|2] 没有事务时，每次调用用一个新会话，调用完就提交并关闭
- [kp5] 它会把 MyBatis 异常转换成 Spring 的数据访问异常

## 详解
### 先搞懂：为什么原生 SqlSession 不能共享
`SqlSession` 内部带着缓存和数据库连接，是为“一个线程一次使用”设计的。把一个 `SqlSession` 放进单例 Bean 让所有线程共用，就像多人共用一支笔写不同的文件，内容会串。

可 Spring 的 Bean 默认是单例，Service、Mapper 都被很多线程同时使用，所以需要一个能安全共享的东西。

- **线程安全**：多个线程同时用也不会互相干扰。
- **事务绑定**：同一个事务里的所有数据库操作用同一个连接，才能一起提交或回滚。

### 它怎么做到线程安全：代理加线程绑定
`SqlSessionTemplate` 内部是一个代理。你调用 `selectOne` 之类的方法时，代理会：

1. 看当前线程有没有绑定好的 `SqlSession`（Spring 事务开始时会绑定）；
2. 有就复用，没有就新建一个；
3. 执行真正的 SQL；
4. 如果不在事务里，就提交并关闭会话；在事务里就留给事务结束时处理。

所以它自己是个“无状态的调度员”，真正干活的会话始终属于某个线程。

### 它和 Mapper 的关系
你注入的 Mapper 代理，底层就是通过 `SqlSessionTemplate` 来执行的。这就是为什么注入的 Mapper 能放心在单例 Service 里使用。

### 进阶：没有事务时的缓存表现（基础薄弱可先跳过）
没有事务时，每次调用都是新会话，一级缓存不会跨调用生效。需要缓存效果的话，把调用放进同一个事务里。另外，不能对 `SqlSessionTemplate` 手动调用 `commit`、`rollback`、`close`，它会抛异常，事务由 Spring 管。

## 示例
```java
@Service
public class OrderService {
    private final OrderMapper orderMapper;

    public OrderService(OrderMapper orderMapper) {
        this.orderMapper = orderMapper;
    }

    @Transactional
    public void create(Order order) {
        orderMapper.insert(order);      // 同一事务里共用一个 SqlSession
        orderMapper.insertLog(order);   // 一起提交或一起回滚
    }
}
```

## 易错点
- 以为自己 new 一个原生 `SqlSession` 放进单例也安全；它不是线程安全的
- 在 `SqlSessionTemplate` 上手动调用 `commit`，会抛异常
- 以为不加 `@Transactional` 多个 Mapper 调用也在同一事务；实际每次各用各的会话

## 追问
### [f1] 为什么一个事务里的多次查询能用一级缓存？
因为事务里复用同一个 `SqlSession`，一级缓存挂在会话上。没有事务时每次新会话，缓存就用不上。
