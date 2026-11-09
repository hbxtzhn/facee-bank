---
id: q_01M6XCCD3W2QA60ENVXHPRAT7R
title: 什么是回表？
type: concept
difficulty: medium
importance: 3
category: mysql
tags: [clustered-index]
prerequisites: [q_01M6XCCAS9HXP87X9TZ76ZQZG9]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MySQL 8.4 手册：Clustered and Secondary Indexes", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html" }
  - { title: "MySQL 8.4 手册：EXPLAIN Output Format（Extra 列）", url: "https://dev.mysql.com/doc/refman/8.4/en/explain-output.html" }
estimatedMinutes: 2
---

## 一句话
回表就是用普通索引查到主键值后，还要再拿主键值去主键索引里取整行数据，一共查了两棵树。

## 要点
- [kp1|3] 二级索引的叶子节点只有索引列和主键值，没有整行数据
- [kp2|3] 查询需要其他列时，要拿主键值回到聚簇索引取整行，叫回表
- [kp3|2] 回表多一次树查找，通常还是随机读，结果行多时代价明显
- [kp4] 查询的列都在二级索引里时，用覆盖索引可以避免回表

## 详解
### 先搞懂：先查目录，再翻正文
你想找作者叫「张三」的书。先在作者目录里找，目录只告诉你这本书的编号，不告诉你书的内容。拿到编号后，你还要去书架按编号取书，这才看到内容。「按编号再取一次书」就是回表。

几个术语：

- **二级索引**：除主键外建的索引，叶子节点存索引列和主键值。
- **聚簇索引**：主键索引，叶子节点存整行。
- **回表**：二级索引查完后，回聚簇索引再查一次。

### 回表的过程
执行 `SELECT * FROM user WHERE name = 'Tom'`，`name` 上有普通索引：

1. 在 `idx_name` 这棵树里找到 `name = 'Tom'` 的叶子项，拿到主键 `id`；
2. 拿 `id` 到聚簇索引里再查一遍，得到整行数据；
3. 如果有多行匹配，每个主键都要回表一次。

### 为什么回表有代价
- 多查了一棵树，多读了页；
- 二级索引里相邻的几项，它们的主键往往不连续，回表时是在聚簇索引里跳着读，属于随机读；
- 匹配的行越多，回表次数越多，代价越明显。

### 怎么避免或减轻
1. **用覆盖索引**：把要查的列都放进索引，查询直接从二级索引拿结果。
2. **少查列**：不要总是 `SELECT *`，只写需要的列。
3. **条件更精确**：让命中的行变少，回表次数自然变少。

## 示例
```sql
CREATE INDEX idx_name_age ON user(name, age);
-- 回表：要的列 address 不在索引里
SELECT * FROM user WHERE name = 'Tom';
-- 不回表：name、age、主键 id 都在 idx_name_age 里
SELECT id, name, age FROM user WHERE name = 'Tom';
```

## 易错点
- 以为所有索引查询都会回表；按主键查、或覆盖索引查询不需要回表
- 以为回表是两次磁盘 IO 一定很慢；页常在内存缓存里，真正的代价取决于回表行数
- 以为 `SELECT *` 和只查几列没有区别；前者往往无法用覆盖索引

## 追问
### [f1] 怎么确认一条查询有没有回表？
用 `EXPLAIN` 看 `Extra` 列，出现 `Using index` 说明用了覆盖索引、没有回表；没有它则通常需要回表取数据。
