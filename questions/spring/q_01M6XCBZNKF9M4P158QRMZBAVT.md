---
id: q_01M6XCBZNKF9M4P158QRMZBAVT
title: MyBatis 的功能架构分为哪几层，各层负责什么？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [mybatis-internals]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 3 文档：Configuration（objectFactory、plugins、jdbcTypeForNull）", url: "https://mybatis.org/mybatis-3/configuration.html" }
  - { title: "MyBatis 3 文档：Java API（SqlSession、ExecutorType、Mapper 注解）", url: "https://mybatis.org/mybatis-3/java-api.html" }
estimatedMinutes: 3
---

## 一句话
MyBatis 的功能架构常被划分为三层：API 接口层给开发者提供调用入口，数据处理层负责 SQL 解析、执行和结果映射，基础支撑层提供连接、事务、配置、缓存等底层能力。

## 要点
- [kp1|3] API 接口层：`SqlSession` 等对外接口，接收调用请求
- [kp2|3] 数据处理层：参数映射、SQL 解析、SQL 执行、结果映射
- [kp3|2] 基础支撑层：连接管理、事务管理、配置加载、缓存
- [kp4|2] 上层调用下层，开发者主要接触最上面一层
- [kp5] 分层让每层可以单独替换或扩展

## 详解
### 先搞懂：一家餐厅的前台、后厨和仓库
- 前台接待客人，只管下单和上菜；
- 后厨负责按订单备料、炒菜、装盘；
- 仓库和水电设备提供食材、燃气、冷藏等基础条件。

MyBatis 的三层，就是这个分工。

后文用到的词：

- **SqlSession**：开发者调用 MyBatis 的入口对象。
- **Executor**：执行器，负责真正执行 SQL。
- **Configuration**：保存所有配置和 SQL 定义的总台账。

### API 接口层：前台
这是开发者直接打交道的一层。提供 `SqlSession` 接口，里面有查询、插入、更新、删除、提交、回滚等方法，也能获取 Mapper 代理对象。

你调用 `session.selectList` 或 Mapper 接口方法时，就是从这一层进入。它接收请求后，交给下一层处理。

### 数据处理层：后厨
这是 MyBatis 最核心的一层，负责把一次调用变成数据库操作，再变回 Java 对象。主要包括：

- **参数映射**：把传入的参数设置到 SQL 的占位符上。
- **SQL 解析**：根据映射文件和动态标签，生成最终要执行的 SQL。
- **SQL 执行**：由 `Executor` 和 `StatementHandler` 完成。
- **结果映射**：把结果集转成 Java 对象。

对应前面讲的 `ParameterHandler`、`StatementHandler`、`ResultSetHandler` 等对象，都在这一层。

### 基础支撑层：仓库和设施
为上面两层提供通用能力：

- **连接管理**：获取和管理数据库连接，可以对接连接池。
- **事务管理**：提交、回滚等。
- **配置加载**：读取 XML 和注解配置，生成 `Configuration`。
- **缓存**：一级缓存和二级缓存。

### 一次查询怎么穿过三层
调用 Mapper 方法，先进入接口层的 `SqlSession`；它交给数据处理层，解析 SQL、设置参数、执行并映射结果；执行过程中，需要的连接、事务和缓存由基础支撑层提供。结果再逐层返回给调用方。

### 为什么分层
每层职责单一：上层不用关心下层怎么实现。你换连接池、换缓存方案，只改基础支撑层的配置，上面的代码不用动。

## 易错点
- 把 SqlSession 当成真正干活的对象；它只是接口层，执行在数据处理层
- 把缓存当作数据处理层的内容；它属于基础支撑层
- 以为三层是三个独立的包；这是功能上的划分，不是严格的包结构

## 追问
### [f1] 插件拦截的是哪一层的对象？
拦截的四类对象 `Executor`、`StatementHandler`、`ParameterHandler`、`ResultSetHandler`，都属于数据处理层。

### [f2] 和 Spring 整合后，是哪一层有变化？
主要是接口层和基础支撑层：Spring 管理 `SqlSession`、事务和数据源，数据处理层的执行流程不变。
