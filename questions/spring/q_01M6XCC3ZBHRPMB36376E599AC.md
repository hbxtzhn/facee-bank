---
id: q_01M6XCC3ZBHRPMB36376E599AC
title: MyBatis 的 environments 是做什么的？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [configuration, orm]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`environments` 用来配置多套数据库环境（开发、测试、生产），`default` 指定默认用哪一套，每套环境都包含事务管理器和数据源。

## 要点
- [kp1|3] `<environments default="...">` 下可以放多个 `<environment>`
- [kp2|3] `default` 指定默认环境的 id
- [kp3|2] 每个环境必须配事务管理器 `transactionManager` 和数据源 `dataSource`
- [kp4|2] 一个 `SqlSessionFactory` 只会使用其中一个环境
- [kp5] 和 Spring 整合后，数据源与事务通常由 Spring 提供

## 详解
### 先搞懂：为什么要多套环境
开发时连本地数据库，测试时连测试库，上线连生产库。三套的地址、账号都不一样。如果每次切换都改一遍配置，很容易改错。

把它们都写好，用一个开关选择，就像家里的总电闸：拨到哪一档，就通哪一路。

- **环境**：一套完整的数据库连接配置。
- **事务管理器**：决定事务怎么提交和回滚。
- **数据源**：提供数据库连接，可以是连接池。

### 怎么配
`<environments>` 里放多个 `<environment id="...">`，每个里面写两项：

- `transactionManager`：类型常见是 `JDBC` 或 `MANAGED`；
- `dataSource`：类型有 `UNPOOLED`（每次新建连接）、`POOLED`（使用连接池）、`JNDI`（从容器获取）。

外层的 `default` 写某个环境的 id，不指定时就用它。构建 `SqlSessionFactory` 时也可以传入环境 id，临时指定另一套。

### 和 Spring 整合后
Spring 项目里，数据源和事务都由 Spring 配置，MyBatis 的 `environments` 基本用不上，实际使用的是 Spring 注入的数据源。多环境切换改由 Spring 的 profile 来做。

## 示例
```xml
<environments default="dev">
    <environment id="dev">
        <transactionManager type="JDBC"/>
        <dataSource type="POOLED">
            <property name="driver" value="com.mysql.cj.jdbc.Driver"/>
            <property name="url" value="jdbc:mysql://localhost:3306/demo"/>
            <property name="username" value="root"/>
            <property name="password" value="${db.password}"/>
        </dataSource>
    </environment>
    <!-- 可以继续写 test、prod 环境 -->
</environments>
```

## 易错点
- 以为一个工厂能同时连多个环境；一个 `SqlSessionFactory` 只对应一个环境
- 密码直接写进配置文件并提交代码库；应使用外部配置
- Spring 整合后还在改 MyBatis 的 `environments`，却发现没有效果

## 追问
### [f1] 要同时访问两个数据库怎么办？
需要创建两个 `SqlSessionFactory`，各自配置自己的数据源，并让各自的 Mapper 包使用对应的工厂。
