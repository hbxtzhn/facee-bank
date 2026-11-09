---
id: q_01M6XCCDMCBWPR2CJKH38F68RB
title: 什么是联合索引，怎么创建？
type: concept
difficulty: easy
importance: 2
category: mysql
tags: [index-design]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
联合索引是包含多列的索引，用 `CREATE INDEX idx ON t(a, b, c)` 创建；列的先后顺序决定它能服务哪些查询条件。

## 要点
- [kp1|3] 联合索引把多列组合起来建在同一棵 B+ 树上
- [kp2|3] 创建语法是 `CREATE INDEX idx ON t(a, b, c)`，括号里的顺序就是索引顺序
- [kp3|2] 索引先按第一列排序，第一列相同再按第二列排序，依此类推
- [kp4] 多个条件经常一起使用时，联合索引通常比多个单列索引更合适

## 详解
### 先搞懂：电话簿先按姓、再按名排
电话簿先按姓排序，姓相同的再按名排序。你知道姓和名，能很快找到；只知道姓，也能找到那一段；只知道名，就没法直接找了，因为名字在不同姓下是分散的。联合索引的排序方式就是这样。

几个术语：

- **单列索引**：只包含一列的索引。
- **联合索引**：也叫复合索引，包含多列。
- **索引顺序**：创建时列出的先后，它决定了索引内部的排序方式。

### 怎么创建
和普通索引一样，只是括号里写多列。建表时也可以直接定义：

```sql
CREATE INDEX idx_abc ON t(a, b, c);

CREATE TABLE t (
  id BIGINT PRIMARY KEY,
  a INT, b INT, c INT,
  INDEX idx_abc (a, b, c)
);
```

### 列的顺序为什么重要
索引 `(a, b, c)` 里的数据是先按 `a` 排，`a` 相同再按 `b` 排，`b` 也相同再按 `c` 排。所以：

- 条件含 `a`、`a, b`、`a, b, c`：可以利用；
- 只有 `b` 或只有 `c`：没法直接利用，因为它们不是整体有序的。

所以建联合索引要想清楚：最常用、最能过滤的条件列放前面。

### 和多个单列索引的区别
几个条件一起查时，建一个联合索引，一次树查找就能同时用上多个条件。分别建多个单列索引，一般一条查询只会选用其中一个，另一些条件还要再过滤。联合索引还可能做成覆盖索引。

## 示例
```sql
CREATE INDEX idx_user_status ON orders(user_id, status);
-- 可以用上联合索引
SELECT * FROM orders WHERE user_id = 1001 AND status = 1;
SELECT * FROM orders WHERE user_id = 1001;
```

## 易错点
- 以为列的顺序无所谓；顺序决定了能服务哪些查询
- 以为联合索引等于多个单列索引；它是一棵按多列排序的树
- 以为列越多越好；列多了索引变大，写入也更慢

## 追问
### [f1] 联合索引里列的顺序怎么定？
一般把经常作为等值条件、区分度高的列放前面；还要看有没有排序、范围条件需求，最终以实际查询为准。
