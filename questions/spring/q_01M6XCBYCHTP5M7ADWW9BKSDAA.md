---
id: q_01M6XCBYCHTP5M7ADWW9BKSDAA
title: MyBatis 的 SimpleExecutor 和 ReuseExecutor 有什么区别？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [mybatis-internals]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 源码：ReuseExecutor.java", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/executor/ReuseExecutor.java" }
  - { title: "MyBatis 3 手册：Configuration（Plugins、settings）", url: "https://mybatis.org/mybatis-3/configuration.html" }
estimatedMinutes: 3
---

## 一句话
SimpleExecutor 每执行一次 SQL 就新建一个 Statement、用完立刻关闭；ReuseExecutor 以 SQL 文本为 key 缓存 Statement，同一会话里相同 SQL 可以复用。

## 要点
- [kp1|3] `SimpleExecutor` 每次执行都新建 `Statement`，用完即关闭
- [kp2|3] `ReuseExecutor` 以 SQL 文本为 key，把 `Statement` 放进 Map 缓存
- [kp3|2] 复用只发生在同一个 `SqlSession` 内，会话结束后缓存清空
- [kp4|2] `SimpleExecutor` 是默认执行器
- [kp5] 切换执行器通过 settings 或 `openSession` 参数指定

## 详解
### 先搞懂：每次都洗新碗，还是洗完留着接着用
想象你反复给同一个顾客上同一道汤：

- 每次都拿一个新碗，用完马上洗掉：这是 `SimpleExecutor`。
- 碗用完先放在架子上，下次同样的汤还用这个碗：这是 `ReuseExecutor`。

后文用到的词：

- **Statement**：JDBC 里代表一条 SQL 语句的对象，由它把 SQL 发给数据库。
- **预编译**：数据库先解析一遍 SQL 的结构，后面只换参数值。
- **执行器类型**：决定 MyBatis 用哪种 `Executor`。

### SimpleExecutor：每次新建，用完就关
这是默认的执行器。每次执行查询或更新：

1. 创建一个新的 `Statement`；
2. 设置参数、执行；
3. 在 `finally` 里立刻关闭它。

简单直接，不用管理缓存，也不会有泄漏的担心。

### ReuseExecutor：以 SQL 为 key，缓存复用
`ReuseExecutor` 内部有一个 Map，key 是 SQL 文本，value 是对应的 `Statement`。

执行时：

1. 用 SQL 文本去 Map 里找；
2. 找到就复用，找不到才新建并放进 Map；
3. 执行完不关闭，留给下一次使用。

在同一个 `SqlSession` 里反复执行相同的 SQL，可以省掉重复创建的开销。

缓存的 `Statement` 在会话提交、回滚或关闭等时机被统一关闭并清空，所以复用只在一个会话内部有效。

### 方案对比：三种执行器
| 执行器 | Statement 怎么处理 | 适合 |
|---|---|---|
| `SimpleExecutor` | 每次新建，用完关闭 | 默认，大多数场景 |
| `ReuseExecutor` | 按 SQL 缓存复用，会话结束才关 | 同一会话反复执行相同 SQL |
| `BatchExecutor` | 更新语句攒成批，统一执行 | 大批量插入或更新 |

结论：默认用 `SimpleExecutor`；同一会话里确实重复执行相同 SQL 才考虑 `ReuseExecutor`，批量写入用 `BatchExecutor`。

### 怎么切换
- 全局设置：在 settings 里配置 `defaultExecutorType`，可选 `SIMPLE`、`REUSE`、`BATCH`。
- 单次设置：`factory.openSession(ExecutorType.REUSE)`。

## 示例
```java
// 这个会话使用 ReuseExecutor
try (SqlSession session = factory.openSession(ExecutorType.REUSE)) {
    UserMapper mapper = session.getMapper(UserMapper.class);
    for (long id = 1; id <= 3; id++) {
        mapper.findById(id); // SQL 文本相同，Statement 可以复用
    }
}
```

## 易错点
- 以为 ReuseExecutor 的缓存能跨会话共享；实际只在同一个 SqlSession 内有效
- 以为复用就一定更快；只有重复执行相同 SQL 时才有意义
- 把 Statement 的复用和连接池混为一谈；它们是两个层面的东西

## 追问
### [f1] 复用 Statement 的好处是什么？
省掉重复创建 `Statement` 对象的开销。如果数据库驱动支持预编译，复用同一个预编译语句，还可能省掉重复解析 SQL 的工作，具体效果取决于驱动和数据库。

### [f2] 为什么默认不用 ReuseExecutor？
大部分请求里同一会话不会反复执行完全相同的 SQL，复用带来的好处有限，而且需要维护缓存。
