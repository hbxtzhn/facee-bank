---
id: q_01M6XCCB9DWT1CMJKQHDGKQGQ0
title: 创建索引时应该怎么选择列？
type: concept
difficulty: medium
importance: 2
category: mysql
tags: [index-design]
prerequisites: [q_01M6XCCA15EH4N41RZG222R1R5, q_01M6XCCB1DEA2XV3GYDK3HKTHC]
references:
  - { title: "MySQL 8.4 手册：How MySQL Uses Indexes", url: "https://dev.mysql.com/doc/refman/8.4/en/mysql-indexes.html" }
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
优先给 WHERE、ORDER BY、GROUP BY 里常用的列建索引；区分度低或频繁修改的列不适合建。

## 要点
- [kp1|3] 经常出现在 WHERE、ORDER BY、GROUP BY 中的列是好候选
- [kp2|3] 区分度低的列（如性别）建索引收益很小
- [kp3|2] 频繁更新的列做索引，每次修改都要维护索引
- [kp4] 多个条件常一起出现时，考虑建联合索引而不是多个单列索引

## 详解
### 先搞懂：目录要给常查的词建
想象一本字典：你只会按「拼音」查字，那给拼音做目录就很有用；没人按「笔画数是否为偶数」查，给它做目录就是浪费。选索引列也是这个思路：看业务里到底怎么查。

几个术语：

- **区分度**：一列里不同值的多少。身份证号每人都不同，区分度高；性别只有两三个值，区分度低。
- **选择性**：和区分度同一个意思，表示按这列过滤后能剩下多少行。

### 适合建索引的列：查得多、过滤得准
- **WHERE 里常用的列**：按它过滤，索引能直接定位到少量数据行。
- **ORDER BY 的列**：索引本身是有序的，可以省掉再排序的步骤。
- **GROUP BY 的列**：同样利用有序性，减少临时表和排序。
- **关联查询的连接列**：`JOIN` 的 `ON` 条件列，建索引能避免被驱动表全表扫描。

### 不适合建索引的列
1. **区分度低的列**：比如性别，按它过滤一半数据还在，优化器往往宁可全表扫描，索引白占空间。
2. **频繁更新的列**：每次修改这一列，对应的索引也要改，写入成本高。
3. **很少出现在查询条件里的列**：建了也没人用。
4. **表很小的情况**：几十行的表全表扫描一样快。

### 一个实用的判断方式
先看慢查询，再决定建什么索引，而不是一开始给每一列都建。建完用 `EXPLAIN` 验证真的用上了。如果几个条件总是一起用，建一个联合索引，通常比分别建多个单列索引更有效。

## 示例
```sql
-- 常按 status 和 created_at 查询并排序
SELECT * FROM orders
WHERE user_id = 1001 AND status = 1
ORDER BY created_at DESC;

-- 建联合索引，同时服务过滤和排序
CREATE INDEX idx_user_status_time ON orders(user_id, status, created_at);
```

## 易错点
- 以为所有列都建索引最保险；索引越多，写入越慢，空间越大
- 以为区分度低的列加了索引也不亏；它很可能根本不被使用
- 只看列名选索引，不看实际查询；要按真实的查询语句来设计

## 追问
### [f1] 区分度低的列一定不能建索引吗？
不是绝对。如果某个值在表里占比很小，经常只查这个值，索引仍然有用；它也可以作为联合索引的一部分。关键看实际查询。
