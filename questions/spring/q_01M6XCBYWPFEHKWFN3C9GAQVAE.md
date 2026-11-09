---
id: q_01M6XCBYWPFEHKWFN3C9GAQVAE
title: StatementHandler 在 SQL 执行中做什么？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [mybatis-internals]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
StatementHandler 负责创建并预编译 JDBC 的 Statement，再触发执行，同时把参数设置交给 ParameterHandler、结果封装交给 ResultSetHandler。

## 要点
- [kp1|3] `prepare` 从连接创建 `Statement`，完成预编译
- [kp2|3] `parameterize` 给语句设置参数，实际交给 `ParameterHandler`
- [kp3|2] `query` 或 `update` 执行语句，查询的结果交给 `ResultSetHandler`
- [kp4|2] 默认实现 `PreparedStatementHandler`，由 `RoutingStatementHandler` 分发
- [kp5] 可以被插件拦截，常用来改写 SQL

## 详解
### 先搞懂：厨房里的“出餐窗口”
`Executor` 决定“要做一道菜”，但具体怎么下单、怎么出餐，要交给出餐窗口。`StatementHandler` 就是这个窗口：它拿着菜单（SQL），向数据库下单，再把结果交给下一个环节。

后文用到的词：

- **Statement**：JDBC 里代表一条 SQL 的对象。
- **预编译**：先把带问号的 SQL 交给数据库解析，之后只换参数值。
- **BoundSql**：保存最终 SQL 和参数信息的对象。

### 它在整个流程里的位置
`Executor` 执行一次查询时，大致顺序是：

1. 创建 `StatementHandler`；
2. 调用 `prepare`，从数据库连接创建 `Statement`；
3. 调用 `parameterize`，设置参数；
4. 调用 `query` 或 `update`，真正执行。

`StatementHandler` 是这几步的组织者。

### 主要方法分别做什么
- **prepare**：拿到数据库连接，创建对应类型的 `Statement`，设置超时、取数大小等。这一步完成 SQL 的预编译。
- **parameterize**：给预编译语句设置参数值。具体由内部的 `ParameterHandler` 完成。
- **query、update、batch**：执行语句。查询时把得到的结果集交给 `ResultSetHandler`；更新时返回影响行数；批处理则加入批次。
- **getBoundSql**：返回这次的 SQL 和参数信息，插件常通过它读取或修改 SQL。

### 串起参数映射和结果映射
创建 `StatementHandler` 时，它会同时创建好 `ParameterHandler` 和 `ResultSetHandler`，然后持有它们。

这样执行流程就是一条线：`StatementHandler` 组织流程，参数交给 `ParameterHandler`，结果交给 `ResultSetHandler`。每个对象只管自己那一段。

### 有几种实现
- `SimpleStatementHandler`：普通 `Statement`，SQL 直接拼好发送。
- `PreparedStatementHandler`：`PreparedStatement`，预编译加参数设置，是默认选项。
- `CallableStatementHandler`：调用存储过程。
- `RoutingStatementHandler`：本身不干活，根据映射语句里的 `statementType` 选择上面三种之一。

## 示例
```xml
<!-- statementType 默认是 PREPARED，用的就是 PreparedStatementHandler -->
<select id="findById" resultType="User" statementType="PREPARED">
    select * from user where id = #{id}
</select>
```

## 易错点
- 以为 StatementHandler 自己负责设置参数和封装结果；实际它分别交给 ParameterHandler 和 ResultSetHandler
- 以为 StatementHandler 等同于 Executor；Executor 管整体和缓存，StatementHandler 管单条语句
- 以为所有 SQL 都是预编译的；使用 `statementType="STATEMENT"` 时就不是

## 追问
### [f1] 为什么用 `#{}` 比 `${}` 安全？
`#{}` 走预编译，参数值是在 `ParameterHandler` 阶段设置的，不会被当成 SQL 结构。`${}` 是在生成 SQL 时直接拼进文本，有注入风险。

### [f2] 为什么插件常拦截 StatementHandler？
因为它能直接拿到 `BoundSql`，在预编译前改写 SQL，比在 `Executor` 层改更方便。
