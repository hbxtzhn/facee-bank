---
id: q_01M6XCC4QX0J6CS8RW73Y2NHJN
title: 为什么 BatchExecutor 拿不到自增主键？
type: concept
difficulty: hard
importance: 1
category: spring
tags: [mybatis-internals, sql-mapping]
prerequisites: [q_01M6XCBMJG7AYNSVCRE5AM6X2K, q_01M6XCBYMN7AJFH9904AHT0TG6]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
批量执行器把 SQL 攒在一起，到刷新或提交时才真正发给数据库。自增主键是数据库执行后才生成的，所以在刷新之前，实体里的主键还是空的。

## 要点
- [kp1|3] `BatchExecutor` 先把语句 `addBatch` 攒起来，不立即执行
- [kp2|3] 自增主键由数据库在执行时生成，没执行就没有值
- [kp3|2] 刷新批次（`flushStatements`）或提交之后，主键才可能回填
- [kp4|2] 是否能回填还取决于 JDBC 驱动对批量返回主键的支持
- [kp5] 需要立刻用主键时，换成非批量插入，或由应用生成 id

## 详解
### 先搞懂：先攒着，再一起发
你要插入 1000 条数据。一条一条发，要和数据库来回 1000 次；攒成一批一起发，只需要几次。这就是批量执行。

这像寄快递：每件都单独跑一趟邮局很慢，不如攒一箱一次寄走。但代价是：东西没寄出前，你拿不到快递单号。

- **自增主键**：数据库在插入时自动分配的 id。
- **useGeneratedKeys**：让 MyBatis 在插入后取回这个 id，并写进对象。

### 为什么拿不到：主键要等 SQL 真正执行
批量模式下，调用 `insert` 只是把语句和参数放进批次，并没有发给数据库。数据库还没执行，就还没生成主键，对象的 `id` 属性自然是空的。

所以这类写法会出问题：先插入订单，马上用订单 id 去插入订单明细。因为订单 id 还没生成，明细拿到的是 `null`。

### 什么时候能拿到
批次被刷新后才能拿到。刷新有三种情况：

- 手动调用 `flushStatements()`；
- 事务提交或会话关闭时；
- 同一会话里发起了查询，查询前会先刷新批次。

刷新后，较新的 MyBatis 会尝试把主键回填到对象里，但要看 JDBC 驱动是否支持批量返回主键。这点要实测。

### 另外的限制：影响行数也不准
批量模式下，`insert` 和 `update` 的返回值不是真实的影响行数，而是一个固定的占位值。需要精确行数时要看刷新后返回的批处理结果。

### 怎么办
- 需要马上用主键：这一步用非批量的会话插入。
- 先手动刷新：插完父表后调用 `flushStatements()`，再继续用主键。
- 应用自己生成 id：用雪花算法或 UUID，不依赖数据库自增。

## 示例
```java
try (SqlSession session = factory.openSession(ExecutorType.BATCH)) {
    OrderMapper mapper = session.getMapper(OrderMapper.class);
    mapper.insert(order);          // 只加入批次，order.getId() 仍为 null
    session.flushStatements();     // 此时才真正执行
    // 刷新后主键是否已回填，取决于 JDBC 驱动，需要实测
    session.commit();
}
```

## 易错点
- 在批量会话里插入后立刻读取 id，得到的是空值
- 把批量模式下的返回值当成影响行数使用
- 以为所有数据库驱动在批量时都能返回主键，没有实测就上线

## 追问
### [f1] 批量插入的数据量太大怎么办？
不要一次攒太多，内存会涨。按固定数量分批，每批调用一次 `flushStatements()`，全部结束后再提交。
