---
id: q_01M6ZYJP9P4D447V10JAY488CJ
title: 子查询为什么会慢，怎么优化？
type: concept
difficulty: medium
importance: 2
category: mysql
tags: [sql-optimization]
prerequisites: [q_01M6XCCMEG0EFAYYT7CJA55CKP]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MySQL 8.4 手册：Optimizing Subqueries（semijoin、materialization、EXISTS 策略）", url: "https://dev.mysql.com/doc/refman/8.4/en/subquery-optimization.html" }
  - { title: "MySQL 8.4 手册：Optimizing Derived Tables, View References, and CTEs", url: "https://dev.mysql.com/doc/refman/8.4/en/derived-table-optimization.html" }
estimatedMinutes: 3
---

## 一句话
相关子查询要对外层的每一行都执行一次，外层行数多就慢。优化办法是改写成 JOIN，或先把子查询结果算好一次再关联。

## 要点
- [kp1|3] 相关子查询引用了外层的列，逻辑上外层每行都要执行一次
- [kp2|3] 外层行数越多，子查询执行次数越多，耗时越长
- [kp3|2] 优化办法一：改写成 JOIN，让优化器一次处理
- [kp4|2] 优化办法二：先用分组算出所有结果，再关联外层
- [kp5] 优化器会自动改写部分子查询，是否变慢以 `EXPLAIN` 为准

## 详解
### 先搞懂：每个学生都去办公室问一遍
老师要给每个学生写评语，需要知道「这个学生的缺勤次数」。如果每写一个学生，就跑一趟办公室翻考勤本统计一次，学生越多，跑得越多。更好的办法是：先把全班的缺勤次数统计成一张表，写评语时直接查这张表。

相关子查询就是前一种做法。后文用到的术语：

- **相关子查询**：子查询里用到了外层查询的列，没有外层的值它没法单独运行。
- **执行次数**：外层有多少行，子查询逻辑上就要执行多少次。
- **JOIN**：把两张表按条件拼起来。

### 为什么会慢
看这条查询，统计每个用户的订单数：

```sql
SELECT u.name,
       (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS cnt
FROM user u;
```

子查询里的 `u.id` 来自外层。外层有 10 万个用户，子查询逻辑上就要执行 10 万次，每次都去 `orders` 表里统计。如果 `orders.user_id` 还没有索引，每次都要扫整张表，代价会非常大。

`SELECT` 列表和 `WHERE` 子句里的子查询都可能出现这个问题。

### 优化办法一：改写成 JOIN
```sql
SELECT u.name, COUNT(o.id) AS cnt
FROM user u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name;
```

JOIN 让优化器一次性处理两张表，可以选择更合适的连接方式，而不是机械地逐行执行。注意用 `LEFT JOIN` 保留没有订单的用户。

### 优化办法二：先算好，再关联
先用分组一次算出所有用户的订单数，得到一张小结果表，再关联：

```sql
SELECT u.name, IFNULL(t.cnt, 0) AS cnt
FROM user u
LEFT JOIN (
    SELECT user_id, COUNT(*) AS cnt
    FROM orders GROUP BY user_id
) t ON t.user_id = u.id;
```

子查询只执行一次，不再依赖外层的行。

### 不要忘了索引
无论哪种写法，`orders.user_id` 这类关联列都要有索引。有了索引，即使每行执行一次子查询，每次也只是一次快速定位，没那么慢。

### 也不是一定要改
有些情况下，优化器会自动把子查询改写成 JOIN 一类的执行方式。是否需要改写，要用 `EXPLAIN` 看实际的执行计划，并对比改写前后的耗时。

## 示例
```sql
-- 慢：外层每行都要执行一次子查询
SELECT id, name FROM user u
WHERE (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) > 5;

-- 改写：先分组，再关联
SELECT u.id, u.name FROM user u
JOIN (
    SELECT user_id FROM orders GROUP BY user_id HAVING COUNT(*) > 5
) t ON t.user_id = u.id;
```

## 易错点
- 以为所有子查询都慢；非关联子查询只需执行一次，影响不大
- 改写成 JOIN 后结果行数变多；一对多的关联会让外层行重复，要用 `GROUP BY` 或 `DISTINCT` 处理
- 改写后不验证；要用 `EXPLAIN` 和实际耗时对比，不要凭印象判断

## 追问
### [f1] 改写成 JOIN 后，为什么要用 LEFT JOIN？
原来的子查询对没有订单的用户也会返回结果（数量为 0）。如果改成 `INNER JOIN`，这些用户会被丢掉，结果就不一致了。
