---
id: q_01M6XCC2EBJ61Z1XNRJ8F3DTN7
title: MyBatis 支持哪些日志实现，怎么选择？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [configuration]
prerequisites: [q_01M6XCBNB0AHTKQ1YXGQ7WRCPW]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
MyBatis 支持 SLF4J、Log4j2、JDK Logging、STDOUT 等多种日志实现。一般不用选，跟着项目已有的日志框架走；要强制指定就设置 `logImpl`。

## 要点
- [kp1|3] 在 `<settings>` 里用 `logImpl` 指定日志实现
- [kp2|3] 不设置时，MyBatis 会按顺序自动找项目里有的日志框架
- [kp3|2] `STDOUT_LOGGING` 直接打到控制台，只适合本地调试
- [kp4|2] 日志级别按 Mapper 的包名或 namespace 设置，调试时开 DEBUG 看 SQL
- [kp5] 生产环境日志级别过细会增加输出量，按需开关

## 详解
### 先搞懂：为什么要看 MyBatis 的日志
接口返回的数据不对，你首先想知道的是：MyBatis 到底发出了什么 SQL，参数是什么。这些信息都靠日志输出。

日志就像行车记录仪，平时不看，出问题时要靠它还原现场。

- **日志门面**：像 SLF4J 这样的统一接口，底层可以换不同实现。
- **logImpl**：MyBatis 配置项，指定用哪种日志。

### 支持哪些，怎么选
常见取值有：`SLF4J`、`LOG4J2`、`JDK_LOGGING`、`COMMONS_LOGGING`、`STDOUT_LOGGING`、`NO_LOGGING`，另外还有 `LOG4J`。

- 项目里已经有日志框架：直接沿用，让 MyBatis 的日志和业务日志在一起。
- 没有明确配置：MyBatis 会按内部顺序，在类路径里找第一个能用的。
- 只想临时看一眼：用 `STDOUT_LOGGING`，不用加依赖。
- 不想要日志：`NO_LOGGING`。

### 怎么看到 SQL
MyBatis 的日志记录器以 Mapper 的包名或 namespace 命名。把这个包的级别调成 DEBUG，就能看到执行的 SQL 和参数；更细的结果行需要 TRACE 级别。

调试和性能要权衡：日志越细，输出越多，线上一般只在排查问题时临时调高。

## 示例
```xml
<settings>
    <setting name="logImpl" value="SLF4J"/>
</settings>
```

```yaml
# Spring Boot：把 Mapper 所在包调成 DEBUG，才能看到 SQL
logging:
  level:
    com.example.mapper: debug
```

## 易错点
- 配了 `logImpl` 却看不到 SQL；多半是日志级别没调到 DEBUG
- 线上长期开启 `STDOUT_LOGGING`，日志无法统一管理
- 配置值写成小写或拼错，启动时报错

## 追问
### [f1] 日志里会不会泄露敏感数据？
会。DEBUG 日志包含 SQL 参数，手机号、密码等可能被打印出来。线上应关闭或脱敏，不要长期开着 DEBUG。
