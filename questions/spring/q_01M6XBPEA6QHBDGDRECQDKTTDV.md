---
id: q_01M6XBPEA6QHBDGDRECQDKTTDV
title: 为什么说 MyBatis 是半自动 ORM？
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
因为 MyBatis 只负责把 SQL 结果映射成对象，SQL 和关联查询要自己写；Hibernate 能根据对象关系自动生成 SQL，所以它是全自动、MyBatis 是半自动。

## 要点
- [kp1|3] MyBatis 的 SQL 都要手写，包括关联对象的查询
- [kp2|3] Hibernate 根据对象关系模型自动生成 SQL 并获取关联对象
- [kp3|2] "半自动"指结果映射自动，SQL 编写手动
- [kp4] 手写 SQL 换来对 SQL 的完全控制

## 详解
### 先搞懂：订单和用户的关联怎么查
做项目时，查订单常要把下单的用户一起带出来。这像做菜：Hibernate 是"你点菜名，厨房自己决定怎么做"；MyBatis 是"你自己写菜谱，厨房照着做并帮你装盘"。

后文用到的词：

- **关联对象**：一个对象里引用的另一个对象，比如订单里的用户。
- **对象关系模型**：对象之间一对一、一对多的关系描述。

### Hibernate：配好关系就自动查
在 Hibernate 里，你在订单类上声明"订单属于一个用户"。之后读取订单时，框架根据这个关系自己生成关联查询，也能在你访问用户属性时自动去取。你基本不用写 SQL。

### MyBatis：关联也得自己写
MyBatis 不理解"订单属于用户"这种关系。你要自己写 SQL，比如写一个联表查询，或者先查订单、再用订单里的用户 ID 去查用户。框架只负责把你查出来的结果装进对象。

### 为什么这被称为"半自动"
自动的部分是：连接管理、参数设置、结果封装成对象。手动的部分是：SQL 本身，包括关联的写法。所以叫"半自动"。

## 易错点
- 以为 MyBatis 完全不能处理关联；它能映射关联结果，只是 SQL 要自己写
- 以为"半自动"是缺点；它也带来了对 SQL 的完全控制

## 追问
### [f1] 手写 SQL 有什么好处？
可以针对具体场景优化 SQL，比如控制索引使用和只查需要的列；代价是换数据库时 SQL 可能要改。
