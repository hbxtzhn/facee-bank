---
id: q_01M6XCBY4FWEVTADX7BS6Y3X7Z
title: SqlSession 和 Executor 是什么关系？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [mybatis-internals]
prerequisites: [q_01M6XCBJ1YNEQMS9SQBE4YZFD7]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 源码：DefaultSqlSession.java", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/session/defaults/DefaultSqlSession.java" }
  - { title: "MyBatis 源码：Configuration.java（newExecutor）", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/session/Configuration.java" }
  - { title: "MyBatis-Spring 文档：Using an SqlSession（SqlSessionTemplate）", url: "https://mybatis.org/spring/sqlsession.html" }
estimatedMinutes: 3
---

## 一句话
SqlSession 是 MyBatis 对外的门面接口，只负责接收调用；真正执行 SQL 的是它内部持有的 Executor，SqlSession 把活交给 Executor 去做。

## 要点
- [kp1|3] `SqlSession` 提供 `selectOne`、`insert`、`commit` 等对外 API
- [kp2|3] 默认实现 `DefaultSqlSession` 内部持有一个 `Executor`
- [kp3|2] 查询和更新最终都委托给 `Executor` 的 `query` 和 `update`
- [kp4|2] `Executor` 在 `openSession` 时创建，并被插件包装
- [kp5] `SqlSession` 不是线程安全的，不能多线程共享

## 详解
### 先搞懂：前台和后厨
去餐厅点餐，你只和前台服务员打交道：说你要什么、结账。至于怎么备料、怎么炒菜，是后厨的事。

`SqlSession` 就是前台，`Executor` 就是后厨。对外的方法都在 `SqlSession` 上，真正干活的是 `Executor`。

后文用到的词：

- **门面**：对外只露一个简单入口，把内部复杂的步骤藏起来。
- **Executor**：执行器，负责真正执行 SQL，同时管理缓存和事务。
- **MappedStatement**：对一条 SQL 的完整描述。

### SqlSession：只管接待
`SqlSession` 接口提供查询、插入、修改、删除、提交、回滚、获取 Mapper 等方法。

它的默认实现 `DefaultSqlSession` 里，持有两样东西：`Configuration` 和 `Executor`。

调用 `selectList` 时，它做的事很少：

1. 根据语句 ID 从 `Configuration` 里取出 `MappedStatement`。
2. 调用 `executor.query(...)`，把结果返回。

插入、修改、删除都走 `update`：`DefaultSqlSession` 的 `insert`、`delete` 内部都是调用 `update`，最后交给 `executor.update`。

### Executor：真正干活
`Executor` 负责：

- 生成缓存的 key，检查一级缓存；
- 创建 `StatementHandler`，预编译并执行 SQL；
- 管理事务的提交和回滚；
- 关闭相关资源。

### 两者是怎么关联起来的
调用 `SqlSessionFactory.openSession()` 时，工厂会：

1. 从 `Configuration` 取事务配置，创建事务对象；
2. 调用 `configuration.newExecutor`，根据执行器类型（默认是 `SimpleExecutor`）创建 `Executor`；
3. 如果开启了二级缓存，再套一层 `CachingExecutor`；
4. 所有插件在这一步被应用，包装在 `Executor` 外面；
5. 用 `new DefaultSqlSession(configuration, executor, ...)` 返回。

所以每一个 `SqlSession` 都有自己独享的 `Executor`，里面的一级缓存也只属于这个会话。

### 为什么这样设计
把“对外接口”和“具体执行”分开：以后换一种执行方式（比如批量），只要换 `Executor`，调用方的代码一行都不用改。插件也只需要拦截 `Executor`，就能管到所有查询和更新。

## 示例
```java
try (SqlSession session = factory.openSession()) {
    // 看起来是 SqlSession 在查询，实际由内部的 Executor 完成
    List<User> users = session.selectList("com.example.UserMapper.findAll");
}
```

## 易错点
- 以为 SqlSession 自己直接执行 SQL；实际它只是委托给 Executor
- 把 SqlSession 做成单例在多线程里共用，它不是线程安全的
- 以为不同 SqlSession 共享一级缓存；实际每个会话各用各的

## 追问
### [f1] Executor 有哪几种？
`SimpleExecutor`、`ReuseExecutor`、`BatchExecutor`，另有 `CachingExecutor` 用来包装它们提供二级缓存。默认用 `SimpleExecutor`。

### [f2] 用 Spring 时 SqlSession 是怎么管理的？
Spring 注入的是 `SqlSessionTemplate`，它是线程安全的代理，每次调用会按当前事务取出或创建真正的 `SqlSession`，用完自动关闭。
