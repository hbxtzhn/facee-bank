---
id: q_01M6XCC2PJW5M4W1TYNDVYVR7W
title: SqlSessionFactoryBean 做了什么？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [mybatis-internals, ioc-di]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
`SqlSessionFactoryBean` 是 mybatis-spring 提供的工厂 Bean，它在 Spring 里创建 `SqlSessionFactory`，并把数据源、映射文件等配置组装进去。

## 要点
- [kp1|3] 它实现 `FactoryBean`，往容器里放的是它创建的 `SqlSessionFactory`
- [kp2|3] 必须注入 `DataSource`，MyBatis 靠它拿数据库连接
- [kp3|2] 可配置映射文件位置、类型别名包、插件、全局配置文件
- [kp4|2] 事务交给 Spring 管理，不再用 MyBatis 自带的事务
- [kp5] Spring Boot 的 starter 会自动创建，一般不用手写

## 详解
### 先搞懂：SqlSessionFactory 是什么
`SqlSessionFactory` 是 MyBatis 的核心对象：有了它才能开会话（`SqlSession`），才能执行 SQL。纯 MyBatis 项目里，你要自己读配置文件、手动构建它。

放到 Spring 项目里，就希望由 Spring 来创建并管理它，别的 Bean 要用时直接注入。`SqlSessionFactoryBean` 就是干这个的。

- **FactoryBean**：一种特殊的 Bean，容器里取到的不是它自己，而是它“生产”的对象。
- **SqlSession**：和数据库的一次会话，里面执行 SQL。

### 它做了什么
Spring 启动时，`SqlSessionFactoryBean` 初始化会按你给的配置构建 MyBatis 的 `Configuration`：

1. 使用你注入的数据源作为连接来源；
2. 读取 `mapperLocations` 指向的 XML 映射文件并解析；
3. 注册类型别名、类型处理器、插件等；
4. 最后构建出 `SqlSessionFactory`，放进容器。

### 和 Spring 事务的关系
它默认使用 Spring 提供的事务工厂，让 MyBatis 使用 Spring 事务管理的连接。这样 `@Transactional` 才能管到 MyBatis 的操作，提交和回滚由 Spring 统一负责。

### 进阶：Spring Boot 里怎么没看到它（基础薄弱可先跳过）
Spring Boot 的 mybatis starter 会自动创建 `SqlSessionFactory`，配置写在 `application.yml` 的 `mybatis.*` 里。只有需要自己控制构建过程时，才会手写这个 Bean。

## 示例
```java
@Bean
public SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
    SqlSessionFactoryBean bean = new SqlSessionFactoryBean();
    bean.setDataSource(dataSource);
    bean.setMapperLocations(new PathMatchingResourcePatternResolver()
            .getResources("classpath:mapper/*.xml"));
    return bean.getObject();
}
```

## 易错点
- 忘了设置数据源，启动时报错
- `mapperLocations` 路径写错，运行时才报“找不到语句”
- 在 Spring 里还保留 MyBatis 自己的 `environments` 配置，以为它会生效；数据源以 Spring 注入的为准

## 追问
### [f1] 为什么通常不直接用 SqlSessionFactory 操作数据库？
业务代码里直接管会话要自己处理关闭和事务，容易出错。mybatis-spring 提供了 `SqlSessionTemplate` 和 Mapper 代理，让会话随 Spring 事务自动管理。
