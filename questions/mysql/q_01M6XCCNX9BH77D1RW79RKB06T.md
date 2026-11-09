---
id: q_01M6XCCNX9BH77D1RW79RKB06T
title: 怎么让 ORDER BY 利用索引避免额外排序？
type: concept
difficulty: medium
importance: 2
category: mysql
tags: [sql-optimization, index-design]
prerequisites: [q_01M6XCCNN56CMPW0WPWNNZGSEW]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
让 ORDER BY 的列顺序和某个索引的列顺序一致，并且等值条件的列放在排序列前面，就可以直接按索引顺序读，不用 filesort。

## 要点
- [kp1|3] 排序列的顺序要和索引列的顺序一致
- [kp2|3] 联合索引里，等值查询的列放前面，排序列放后面
- [kp3|2] 范围条件之后的列，通常没法再用来保证排序
- [kp4] 升降序混用时，要看索引是否按同样方向建立
- [kp5] 用 EXPLAIN 检查 Extra，没有 Using filesort 才算达标

## 详解
### 先搞懂：索引是先按谁、再按谁排好的
联合索引 `(user_id, created_at)` 可以想象成电话簿：先按「姓」排，同姓的人再按「名」排。

如果要找「所有姓张的人，按名字排序」，直接翻到姓张那一页，名字本来就是排好的，不用再排。但如果要「所有人按名字排序」，电话簿就帮不上忙了，因为名字在整本书里并不是连续有序的。

后文会用到这几个词：

- **联合索引**：由多个列组成的索引，按列的先后顺序排序。
- **最左前缀**：从索引最左边的列开始，连续使用的那些列。
- **回表**：二级索引查到主键后，再回主键索引取整行数据。

### 能用索引排序的几种情况
假设有索引 `(a, b, c)`：

- `ORDER BY a`、`ORDER BY a, b`：排序列是索引的最左前缀，可以。
- `WHERE a = 1 ORDER BY b`：a 固定成一个值之后，b 在这一段里是有序的，可以。
- `WHERE a = 1 ORDER BY b, c`：同理，可以。

### 用不上索引排序的常见情况
- `ORDER BY b`：跳过了最左的 a，b 在整个索引里不是连续有序的。
- `WHERE a > 1 ORDER BY b`：a 是范围，满足条件的行里 b 不是整体有序的。
- `ORDER BY a, c`：跳过了中间的 b。
- `ORDER BY a ASC, b DESC`：升降序方向不同。MySQL 8.0 支持建立降序索引，可以建成 `(a ASC, b DESC)` 来匹配。

### 即使排序列对了，优化器也可能选 filesort
排序列和索引匹配，只是「可以」用索引排序。如果查询还要 `SELECT *`，按索引顺序读，每一行都要回表，成本可能反而更高，优化器有时会选择全表扫描再 filesort。

想让索引排序真正生效，常见做法是只查需要的列，让它们都在索引里（覆盖索引），或者配合 `LIMIT`，只读前面少量行。

## 示例
```sql
CREATE INDEX idx_user_time ON orders (user_id, created_at);

-- 等值列在前，排序列在后，可以直接按索引顺序读取
SELECT id, created_at FROM orders
WHERE user_id = 7
ORDER BY created_at DESC
LIMIT 20;
```

## 易错点
- 排序列上建了单列索引，同时又有 WHERE 条件走了别的索引，结果还是 filesort
- 把范围条件的列放在排序列前面，导致排序用不上索引
- 排序方向混用，没有对应方向的索引
- 只看索引设计，不用 `EXPLAIN` 验证

## 追问
### [f1] WHERE 是范围条件，ORDER BY 怎么办？
范围条件的列后面，索引顺序就不再整体有序了，排序通常要 filesort。常见做法是把查询改成等值条件，或者让业务接受一次排序。

### [f2] 怎么确认没有 filesort？
执行 `EXPLAIN`，看 `Extra` 列。没有出现 `Using filesort`，说明直接利用了索引顺序。
