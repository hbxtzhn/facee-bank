---
id: q_01M6XCBXW82VF2V05X5NZWE6S0
title: SqlSessionFactory 是怎么从配置文件构建出来的？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [mybatis-internals, configuration]
prerequisites: [q_01M6XCBHSPR8QTEPTFSNWX8QQT]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
SqlSessionFactoryBuilder 读取配置文件，交给解析器生成 Configuration 对象，再用它创建 DefaultSqlSessionFactory，整个 MyBatis 的配置都存在这个对象里。

## 要点
- [kp1|3] 入口是 `SqlSessionFactoryBuilder.build`，参数是配置文件的输入流
- [kp2|3] `XMLConfigBuilder` 解析 `mybatis-config.xml`，生成 `Configuration`
- [kp3|2] 映射文件被解析成 `MappedStatement`，登记到 `Configuration` 里
- [kp4|2] 最后 `new DefaultSqlSessionFactory(configuration)` 返回工厂
- [kp5] 工厂只需创建一次，整个应用共用

## 详解
### 先搞懂：先把说明书读完，再开工厂
开一家工厂前，要先把说明书读透：用哪个数据库、有哪些 SQL、各种规则怎么定。读完后，把这些信息整理成一份总台账，之后所有工人都按台账干活。

MyBatis 也是这样：启动时把配置文件和 SQL 映射文件读一遍，整理成一个 `Configuration` 对象，再基于它创建工厂。

后文用到的词：

- **Configuration**：MyBatis 的总台账，所有配置、SQL 定义都存放在这里。
- **SqlSessionFactory**：会话工厂，用来创建 `SqlSession`。
- **MappedStatement**：对一条 SQL 的完整描述，比如 ID、SQL 文本、参数和结果类型。

### 构建过程：四步
1. **读文件**：用 `Resources.getResourceAsStream` 把 `mybatis-config.xml` 读成输入流。
2. **解析总配置**：`SqlSessionFactoryBuilder.build` 内部创建 `XMLConfigBuilder`，调用 `parse`，解析出数据源、事务、别名、插件、settings 等，填进 `Configuration`。
3. **解析映射文件**：配置里声明的 Mapper XML（或扫描到的接口注解）交给 `XMLMapperBuilder` 解析。每个 `<select>`、`<insert>` 等标签变成一个 `MappedStatement`，登记到 `Configuration` 中。
4. **创建工厂**：`build(Configuration)` 返回 `new DefaultSqlSessionFactory(configuration)`。

构建完成后，`Configuration` 里就有了运行需要的一切。

### 为什么这样设计
把“读配置”和“用配置”分开：解析在启动时一次完成，运行时只查表，不再读文件。

这样既快，也避免每次查询都解析 XML。

`SqlSessionFactory` 是线程安全的，创建一次、全应用共用即可。每次请求从它里面再取一个 `SqlSession`，用完关闭。

### 在 Spring 里怎么对应
用 Spring 时，不用手写这些步骤。`SqlSessionFactoryBean` 在内部做的是同样的事：设置数据源和 Mapper 文件位置，最终调用 builder 生成工厂。Spring Boot 的 starter 则把这一步也自动配置好了。

## 示例
```java
// 手写构建，Spring 项目里这一步由框架完成
InputStream in = Resources.getResourceAsStream("mybatis-config.xml");
SqlSessionFactory factory = new SqlSessionFactoryBuilder().build(in);

try (SqlSession session = factory.openSession()) {
    UserMapper mapper = session.getMapper(UserMapper.class);
    User user = mapper.findById(1L);
}
```

## 易错点
- 每次请求都重新构建一次 SqlSessionFactory，白白重复解析配置
- 把 SqlSession 当作和工厂一样的全局对象共用；实际 SqlSession 不是线程安全的
- 以为 Mapper XML 每次执行才解析；实际启动时就已全部解析完成

## 追问
### [f1] Configuration 里都存了什么？
数据源与事务配置、各种设置、类型别名、类型处理器、插件，以及所有 MappedStatement 和缓存的登记信息。

### [f2] 没有 XML，纯注解能构建吗？
可以。直接创建 `Configuration` 对象，往里注册 Mapper 接口，再传给 `build`。Spring Boot 默认也支持这种方式。
