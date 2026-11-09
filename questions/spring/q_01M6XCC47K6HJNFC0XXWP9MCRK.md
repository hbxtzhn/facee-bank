---
id: q_01M6XCC47K6HJNFC0XXWP9MCRK
title: JDBC 和 MANAGED 事务管理器有什么区别？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [transaction-management, configuration]
prerequisites: [q_01M6XCC3ZBHRPMB36376E599AC]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
`JDBC` 事务管理器由 MyBatis 自己调用连接的提交和回滚；`MANAGED` 则什么都不做，事务交给外部容器来管。

## 要点
- [kp1|3] `JDBC`：MyBatis 直接用数据库连接的 `commit` 和 `rollback`
- [kp2|3] `MANAGED`：MyBatis 不提交也不回滚，由容器负责
- [kp3|2] `MANAGED` 默认会在会话结束时关闭连接，可用 `closeConnection` 关掉
- [kp4|2] 和 Spring 整合后，实际用的是 Spring 提供的事务管理
- [kp5] 单独使用 MyBatis 时，一般选 `JDBC`

## 详解
### 先搞懂：谁来决定“提交”
你转账：扣 A 的钱、加 B 的钱，两步必须一起成功或一起失败。这叫**事务**。最后要有人说一句“确认提交”或“全部撤销”。

问题是：这句话由谁来说。是 MyBatis 自己说，还是别人说？这就是两种事务管理器的区别。

- **提交**：把改动正式保存到数据库。
- **回滚**：撤销本次事务里的所有改动。
- **容器**：运行你程序的环境，如应用服务器或 Spring。

### JDBC：MyBatis 自己管
选 `JDBC` 后，MyBatis 会在你调用 `commit` 时去提交连接，调用 `rollback` 时回滚。

适合没有别的框架帮忙管事务的场景，比如单独写的小工具或测试代码。

### MANAGED：交给外部
选 `MANAGED` 后，MyBatis 的 `commit` 和 `rollback` 实际什么也不做，由外部容器决定何时提交。

它还有个细节：默认会在会话关闭时关闭连接。如果连接是容器提供的、不想让 MyBatis 关，就把 `closeConnection` 设为 `false`。

### 方案对比：两个事务管理器
| 类型 | 谁提交回滚 | 适合场景 | 注意点 |
|---|---|---|---|
| `JDBC` | MyBatis | 单独使用 MyBatis | 手动调用 `commit` |
| `MANAGED` | 外部容器 | 应用服务器管理事务 | 默认会关闭连接 |

结论：单独使用 MyBatis 选 `JDBC`；事务已由外部容器管理时选 `MANAGED`。用了 Spring 就用 Spring 的事务，不需要在这里选。

## 示例
```xml
<transactionManager type="JDBC"/>

<transactionManager type="MANAGED">
    <property name="closeConnection" value="false"/>
</transactionManager>
```

## 易错点
- 用 `JDBC` 管理器却忘了 `commit`，增删改的数据没有保存
- 用 `MANAGED` 却没有容器管事务，改动不会被提交
- 在 Spring 里还纠结选哪个；实际生效的是 Spring 的事务工厂

## 追问
### [f1] 和 Spring 整合后事务由谁管？
由 Spring 管。mybatis-spring 使用 Spring 的事务工厂，`@Transactional` 决定何时提交或回滚，MyBatis 自己的事务配置不再起作用。
