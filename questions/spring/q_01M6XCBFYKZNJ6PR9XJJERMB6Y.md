---
id: q_01M6XCBFYKZNJ6PR9XJJERMB6Y
title: MyBatis 和 Hibernate 在 SQL 优化和数据库移植性上有什么区别？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [orm]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
MyBatis 手写 SQL，优化容易但换数据库要改 SQL；Hibernate 用 HQL 封装 SQL，换数据库方便但 SQL 优化困难。

## 要点
- [kp1|3] MyBatis 的 SQL 自己写，想怎么优化就怎么优化
- [kp2|3] MyBatis 的 SQL 常含数据库特有写法，移植性差
- [kp3|2] Hibernate 提供 HQL，由框架翻译成各数据库的 SQL
- [kp4|2] Hibernate 生成的 SQL 不好控制，优化较困难

## 详解
### 先搞懂：自己写 SQL 与让框架写 SQL
做项目时，常遇到"这条查询太慢，要调一下"，或者"客户要求把 MySQL 换成别的数据库"。这像出行：自己开车可以挑最快的路线，但换一个城市要重新熟悉路；坐网约车不用管路线，到哪个城市都能叫，但你没法指定走哪条路。

后文用到的词：

- **HQL**：Hibernate 自己的查询语言，面向对象写法，由框架翻译成具体数据库的 SQL。
- **移植性**：换数据库时，代码不用大改就能继续运行。

### 方案对比：优化与移植
| 方案 | SQL 来源 | SQL 优化 | 数据库移植性 |
|---|---|---|---|
| MyBatis | 开发者手写 | 容易，直接改 SQL | 差，SQL 与数据库绑定 |
| Hibernate | HQL 由框架生成 | 困难，不易控制生成的 SQL | 好，由框架适配方言 |

结论：对性能要求高、需要精细调 SQL 的项目选 MyBatis；需要经常切换数据库的项目，Hibernate 更省力。

### 为什么会这样
MyBatis 的 SQL 是你写的，所以可以用索引提示、数据库特有函数、分页语法等。这些写法换数据库后可能不兼容，所以移植性差。

Hibernate 面向对象写 HQL，框架按数据库方言生成对应 SQL，所以换库方便。代价是生成的 SQL 你控制不了，遇到慢查询时只能绕着框架想办法。

## 易错点
- 以为 MyBatis 完全不能换数据库；只是 SQL 里的特有写法要逐条检查
- 以为 Hibernate 生成的 SQL 一定慢；只是出问题时难以调整

## 追问
### [f1] 用 MyBatis 怎样减少换数据库的改动？
尽量使用标准 SQL，把分页等数据库特有写法集中在少数几处，换库时只改这几处。
