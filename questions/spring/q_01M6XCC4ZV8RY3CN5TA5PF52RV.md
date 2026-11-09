---
id: q_01M6XCC4ZV8RY3CN5TA5PF52RV
title: 为什么 select 语句不支持批处理？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [mybatis-internals]
prerequisites: [q_01M6XCBYMN7AJFH9904AHT0TG6]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
批处理的原理是把多条“修改类”语句攒起来一起发送，而查询要立刻拿到结果，没法等到后面再执行，所以 `select` 不能放进批次。

## 要点
- [kp1|3] JDBC 批处理的 `addBatch` 只适用于增删改类语句
- [kp2|3] 查询需要立即返回结果，不能延迟到批次执行时
- [kp3|2] 批量会话里发起查询，MyBatis 会先把已攒的批次刷新，再执行查询
- [kp4] 批处理的目的是减少和数据库的往返次数

## 详解
### 先搞懂：批处理是怎么省时间的
一条一条发 SQL，每条都要和数据库来回一趟。批处理是先把几百条增删改攒在一起，一次发送，往返次数就少了很多。

这像点菜：你一道道喊服务员，不如写在一张单子上一次递过去。

- **批处理**：把多条语句攒成一批，一次提交给数据库。
- **addBatch**：JDBC 里“加入批次”的方法。

### 为什么查询不行
批处理有个前提：**发出去之后，不需要立刻知道每条的结果内容**。增删改只关心有没有成功，晚一点知道没关系。

查询不同，你发一条 `select` 就是为了拿到数据，下一行代码就要用。如果把它攒进批次，结果就得等到批次执行才有，代码就卡住了。而且 JDBC 的批量接口本来就是按“返回更新计数”设计的，不负责返回结果集。

### MyBatis 里发生了什么
在批量会话里，如果中间穿插了一条查询，MyBatis 不会把它放进批次，而是：

1. 先把前面已经攒着的增删改都刷新，发给数据库；
2. 再马上执行这条查询。

这样保证了执行顺序，查询也能读到前面刚改的数据。代价是批次被提前打断，批量的效果会打折扣。

## 示例
```java
try (SqlSession session = factory.openSession(ExecutorType.BATCH)) {
    UserMapper mapper = session.getMapper(UserMapper.class);
    mapper.insert(u1);                 // 加入批次
    mapper.insert(u2);                 // 加入批次
    User u = mapper.selectById(1);     // 先刷新前面的批次，再立即查询
    session.commit();
}
```

## 易错点
- 在批量循环里每次插入后都查一次，批次被反复打断，等于没批处理
- 以为批量模式下查询也会被延迟执行
- 把批量模式用在以查询为主的场景，没有任何好处

## 追问
### [f1] 那批量插入时怎么避免被查询打断？
先把所有插入攒完并刷新、提交，再统一查询。或者把需要的查询放在批量操作之前完成。
