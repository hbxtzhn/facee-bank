---
id: q_01M6XCBNB0AHTKQ1YXGQ7WRCPW
title: 怎么让 MyBatis 打印执行的 SQL 和参数？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [configuration, sql-optimization]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
在 settings 里配置 `logImpl`，选 `STDOUT_LOGGING` 或 `SLF4J`，执行时就能看到 MyBatis 发出的 SQL 和参数。

## 要点
- [kp1|3] `logImpl` 用来指定 MyBatis 使用的日志实现
- [kp2|3] `STDOUT_LOGGING` 直接打印到控制台，适合本地快速查看
- [kp3|2] `SLF4J` 等接入项目日志框架，适合正式项目统一管理
- [kp4] 打印的 SQL 里参数是 `?`，参数值在后面单独一行列出

## 详解
### 先搞懂：想知道 MyBatis 到底发了什么 SQL
写 MyBatis 时，你写的是 XML 或注解里的 SQL，运行时 MyBatis 还会改写它：把 `#{}` 换成 `?`，把动态标签拼好。结果对不对，光看代码不一定看得出来，最直接的办法是让它把实际的 SQL 打印出来。

这就像调试时的“监控录像”：想知道刚才发生了什么，调出录像来看。日志就是 MyBatis 的录像。

术语说明：

- **日志实现**：MyBatis 把日志交给哪个组件输出，例如控制台、SLF4J；
- **SLF4J**：Java 常用的日志门面，背后可接 Logback 等。

### 两种常用做法
**临时调试**：把 `logImpl` 设为 `STDOUT_LOGGING`，MyBatis 会直接把 SQL 和参数打到控制台，不需要装日志框架。简单，但不能控制级别，也不适合上线。

**正式项目**：把 `logImpl` 设为 `SLF4J`，让 MyBatis 的日志走项目已有的日志框架。再把 Mapper 所在的包（或命名空间）的日志级别设为 `debug`，SQL 才会输出。

### 日志里能看到什么
大致有三类信息：预编译的 SQL，里面参数是 `?`；参数值和类型列表；返回的行数。这样你能核对 SQL 拼得对不对、参数传得对不对。

`logImpl` 支持的常见取值有 `SLF4J`、`LOG4J2`、`JDK_LOGGING`、`STDOUT_LOGGING` 等。

## 示例
```yaml
# 临时调试：直接打印到控制台
mybatis:
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

```yaml
# Spring Boot 里用项目日志框架，并让 Mapper 包输出 debug 日志
logging:
  level:
    com.example.mapper: debug
```

## 易错点
- 用 SLF4J 却没把 Mapper 的日志级别调到 debug，所以什么也看不到
- 把 `STDOUT_LOGGING` 带到生产环境，日志无法控制，也不好收集
- 以为日志里的 SQL 已经把参数拼好了，其实参数值是单独列出的

## 追问
### [f1] 线上排查慢 SQL，应该开着 debug 日志吗？
不建议长期开。debug 日志量大，会影响性能。更常见的做法是只在排查时临时调高某个包的日志级别，或使用数据库的慢查询日志。
