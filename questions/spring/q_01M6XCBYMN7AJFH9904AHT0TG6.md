---
id: q_01M6XCBYMN7AJFH9904AHT0TG6
title: BatchExecutor 是怎么批量执行更新语句的？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [mybatis-internals]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 源码：BatchExecutor.java", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/executor/BatchExecutor.java" }
  - { title: "MyBatis 3 文档：Java API（SqlSession、ExecutorType、Mapper 注解）", url: "https://mybatis.org/mybatis-3/java-api.html" }
estimatedMinutes: 3
---

## 一句话
BatchExecutor 不会每条更新语句马上发给数据库，而是用 addBatch 先攒起来，到 flushStatements 或提交时统一 executeBatch 发送，攒的批次只在一个 SqlSession 内有效。

## 要点
- [kp1|3] `BatchExecutor` 执行更新时调用 `addBatch`，只攒不发
- [kp2|3] 统一由 `executeBatch` 一次性发给数据库
- [kp3|2] 连续相同的 SQL 和同一个映射语句，会放进同一批
- [kp4|2] 提交、`flushStatements` 或执行查询时会触发发送
- [kp5] 批处理的生命周期限定在当前 `SqlSession`

## 详解
### 先搞懂：攒够一车再送，而不是来一件送一件
网店发货：每来一个订单就派一辆车送一件，运费很高。更省的办法是先把订单攒在仓库里，攒一批后一车送走。

`BatchExecutor` 就是后一种：你连续插入 1000 条数据，它先全部记在“批处理”里，最后一次性发给数据库。

后文用到的词：

- **批处理**：JDBC 提供的功能，把多条语句攒在一起，一次发送。
- **addBatch**：把一条语句加入批处理，但不执行。
- **executeBatch**：把攒好的语句一次性执行。

### 执行过程
1. **加入批处理**：调用 Mapper 的插入或更新方法时，`BatchExecutor` 不会直接执行，而是给 `Statement` 设置好参数，调用 `addBatch`。
2. **同类合并**：如果这次的 SQL 和映射语句，与上一次一样，就继续往同一个 `Statement` 里添加。换了不同的语句，才会新建一个批次。
3. **统一执行**：调用 `flushStatements`、`commit` 时，会对每个批次调用 `executeBatch`，把数据真正发给数据库。
4. **遇到查询**：在 `BatchExecutor` 里执行查询，会先把已攒的批次执行掉，保证查询看到前面的写入。

### 几个行为特点
- **更新的返回值不是影响行数**：因为语句还没真正执行，插入或更新方法的返回值没有实际意义。真实结果要通过 `flushStatements` 返回的批处理结果去看。
- **不 flush 或提交就不会发送**：只攒不提交，数据库里什么也没有。
- **生命周期在 SqlSession 内**：批次的缓存属于这个会话，会话关闭后就没有了。

### 怎么使用
需要大量插入或更新时，用 `ExecutorType.BATCH` 打开一个会话，循环调用 Mapper 方法，定期 `flushStatements`，最后 `commit`。

批处理能减少和数据库之间的往返次数。具体提升多少，取决于数据库和驱动，需要实际测。

## 示例
```java
try (SqlSession session = factory.openSession(ExecutorType.BATCH)) {
    UserMapper mapper = session.getMapper(UserMapper.class);
    for (int i = 0; i < 1000; i++) {
        mapper.insert(new User("name" + i)); // 只是 addBatch，没有发出
        if (i % 200 == 199) {
            session.flushStatements();      // 每攒一批，统一发出
        }
    }
    session.commit();                       // 提交时发送剩余的
}
```

## 易错点
- 以为每次 insert 都已写入数据库；批处理模式下要等 flush 或 commit 才发送
- 依赖 insert 返回的影响行数做判断；批处理下这个返回值没有实际意义
- 一次攒太多不 flush，占用较多内存

## 追问
### [f1] 批处理可以和 Spring 结合吗？
可以。用 `SqlSessionTemplate` 并指定 `ExecutorType.BATCH` 创建一个批量专用的模板，批量操作用它，其他操作仍用默认的。

### [f2] 为什么插入的主键回填需要注意？
批处理模式下，生成的主键要等语句真正执行后才能拿到，具体行为取决于数据库驱动，使用前要实际验证。
