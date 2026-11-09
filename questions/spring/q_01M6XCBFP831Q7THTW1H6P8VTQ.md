---
id: q_01M6XCBFP831Q7THTW1H6P8VTQ
title: Hibernate 和 MyBatis 的映射方式有什么不同？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [orm]
prerequisites: [q_01M6XBPE22165T2XWWCENFW4KD]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "MyBatis 3 文档：Introduction", url: "https://mybatis.org/mybatis-3/index.html" }
  - { title: "Hibernate ORM 6.6 Introduction：Entities and associations", url: "https://docs.hibernate.org/orm/6.6/introduction/html_single/Hibernate_Introduction.html" }
---

## 一句话
MyBatis 配置的是"对象与 SQL 结果"的对应，Hibernate 配置的是"对象与整张表"的对应，所以前者灵活，后者多表关联配置更复杂。

## 要点
- [kp1|3] MyBatis 是半自动映射，配置 Java 对象与 SQL 执行结果的对应
- [kp2|3] Hibernate 是全表映射，配置 Java 对象与数据库表的对应
- [kp3|2] 多表关联时 MyBatis 靠手写 SQL，配置相对简单
- [kp4|2] Hibernate 的多表关联要在对象关系上配置，较复杂

## 详解
### 先搞懂：对着"表"还是对着"查询结果"
做项目时，页面常要展示"订单加用户名"这种来自多张表的数据。这像做报表：Hibernate 是先把每张原始表都登记好档案，再从档案里拼；MyBatis 是你先写好查询，拿到一张临时表，再说明这张临时表怎么对应到对象。

后文用到的词：

- **全表映射**：对象和数据库表一一对应，对象代表整张表的一行。
- **半自动映射**：对象对应的是某条 SQL 的结果，哪些列由 SQL 决定。

### 方案对比：两种映射方式
| 方案 | 映射对象是什么 | SQL 谁写 | 多表关联 |
|---|---|---|---|
| MyBatis | SQL 的执行结果 | 开发者手写 | 写联表 SQL，配置简单 |
| Hibernate | 数据库的整张表 | 框架生成 | 要配置对象间关系，较复杂 |

结论：查询形态多变、常常联表时，MyBatis 更直接；表结构清晰、以单表增删改查为主时，Hibernate 省事。

### 为什么会有这种差别
MyBatis 不要求对象和表一一对应，只要查询结果的列能对上属性就行，所以同一张表可以映射成不同的对象。Hibernate 要先知道对象和表的完整关系，才能自己生成 SQL，所以关系配置越多越复杂。

## 易错点
- 以为 MyBatis 也要一张表对应一个类；它只关心查询结果的列
- 以为 Hibernate 一定更简单；多表关联配置反而更繁琐

## 追问
### [f1] 为什么多表关联 MyBatis 更简单？
因为你直接写联表 SQL，把需要的列查出来，再把结果列对应到对象属性即可，不用先描述表与表的关系。
