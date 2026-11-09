---
id: q_01M6XCCHRJYYXKZNHJRNT73QFV
title: 怎么在业务服务里监控慢 SQL？
type: concept
difficulty: medium
importance: 1
category: mysql
tags: [sql-optimization]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
在业务服务里拦截每条 SQL 的执行并计时，超过阈值就记录和告警。常见切入点有字节码插桩、连接池扩展和 ORM 拦截。

## 要点
- [kp1|3] 监控的原理是在 SQL 执行前后计时，超过阈值就上报
- [kp2|3] 字节码插桩不改业务代码，在运行时给 JDBC 方法织入计时逻辑
- [kp3|2] 连接池扩展在连接池层统一统计，比如拦截语句执行
- [kp4|2] ORM 拦截器在 ORM 框架层统一拦截，能拿到完整的 SQL 和参数
- [kp5] 告警要带上 SQL、耗时和调用位置，方便定位

## 详解
### 先搞懂：为什么不能只靠 MySQL 的慢日志
MySQL 的慢查询日志是在数据库那一端记录的，要登录机器去翻文件。而且它不知道这条 SQL 是业务里哪段代码发出的。我们希望在业务服务里就能看到：哪个接口发出了慢 SQL，耗时多少，并且自动告警。

可以把它想成在每条订单流水线上装一个计时器，超时就亮灯。后文用到的术语：

- **拦截**：在 SQL 真正执行的前后插入自己的代码。
- **字节码插桩**：运行时修改已经编译好的类，把计时代码织进去。
- **阈值**：超过多长时间算慢。

### 三种常见的实现方式
**字节码插桩。** 通常借助 Java Agent，在程序启动时修改 JDBC 驱动里执行语句的方法，在方法前后加计时。优点是不用改业务代码，所有走这个驱动的 SQL 都能覆盖。很多 APM（应用性能监控）工具用的就是这种方式。

**连接池扩展。** 数据库连接池通常提供扩展点或监控能力，可以在语句执行时统计耗时。优点是在连接池这一层统一处理，只要用这个连接池，所有 SQL 都能覆盖。

**ORM 框架拦截。** 比如 MyBatis 的拦截器，能在 SQL 执行前后计时，并且拿到完整的 SQL 和参数。缺点是只覆盖通过这个框架发出的 SQL，绕过框架直接写的 JDBC 不在其内。

### 方案对比：三种方式怎么选
| 方式 | 在哪一层拦截 | 是否改业务代码 | 覆盖范围 | 特点 |
|---|---|---|---|---|
| 字节码插桩 | JDBC 驱动方法 | 不用改 | 所有走驱动的 SQL | 接入方便，实现较复杂 |
| 连接池扩展 | 连接池 | 通常只改配置 | 经过连接池的 SQL | 依赖所用连接池的能力 |
| ORM 拦截 | ORM 框架 | 加一个拦截器 | 只覆盖该框架的 SQL | 能拿到参数，容易实现 |

结论：项目只用一种 ORM 且想快速落地，用 ORM 拦截器最简单；要覆盖所有 SQL 且不动业务代码，考虑字节码插桩或成熟的 APM 工具。

### 告警里应该带什么信息
只告诉「有一条慢 SQL」没用。应该带上：SQL 语句（参数要脱敏）、耗时、调用它的接口或方法、发生时间。这样拿到告警就能直接去做 `EXPLAIN` 分析。

## 示例
```java
// MyBatis 拦截器的思路：执行前后计时，超过阈值就记录
@Intercepts(@Signature(type = Executor.class, method = "query",
        args = {MappedStatement.class, Object.class,
                RowBounds.class, ResultHandler.class}))
public class SlowSqlInterceptor implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return invocation.proceed();
        } finally {
            long cost = System.currentTimeMillis() - start;
            if (cost > 1000) {
                // 记录日志或上报告警
            }
        }
    }
}
```

## 易错点
- 以为 ORM 拦截能覆盖所有 SQL；直接用 JDBC 发出的语句它拦截不到
- 告警里直接打印完整参数；可能泄露手机号等敏感信息，要脱敏
- 监控本身耗时太长；拦截逻辑要轻量，不能拖慢业务

## 追问
### [f1] 监控发现慢 SQL 后下一步做什么？
拿到 SQL 后用 `EXPLAIN` 看执行计划，判断是没走索引、扫描行数多还是排序开销大，再针对性地加索引或改写。
