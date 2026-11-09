---
id: q_01M6ZYJNPC7ZE4W4RTV7SM2DHB
title: 什么是 JOIN 连接，怎么用？
type: concept
difficulty: easy
importance: 2
category: mysql
tags: [sql-basics]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
JOIN 把两张表按条件拼在一起。`INNER JOIN` 只保留两边都匹配的行，`LEFT JOIN` 保留左表所有行，右边没匹配上的列显示为 NULL。

## 要点
- [kp1|3] `INNER JOIN` 只返回两张表按 `ON` 条件都匹配的行
- [kp2|3] `LEFT JOIN` 保留左表全部行，右表没匹配的列填 NULL
- [kp3|2] `ON` 写表之间的关联条件，通常是外键等于主键
- [kp4] 联表的关联列最好有索引，否则查询会很慢

## 详解
### 先搞懂：用户表和订单表要拼起来看
做项目时，用户信息在 `user` 表，订单在 `orders` 表，订单里只存了 `user_id`。想看「每个订单是谁下的」，就要把两张表拼起来，这就是 JOIN。

可以想成两张名单对照：左边是学生名单，右边是成绩单，按学号把两边的行对上。后文用到的术语：

- **JOIN 连接**：按条件把两张表的行拼成一行。
- **ON 条件**：说明两张表怎么对上，比如 `orders.user_id = user.id`。
- **NULL**：表示「没有值」。

### INNER JOIN：只要两边都有的
```sql
SELECT u.name, o.id, o.amount
FROM user u
INNER JOIN orders o ON o.user_id = u.id;
```

只返回能对上的行。没下过单的用户不会出现，没有对应用户的订单也不会出现。`INNER` 可以省略，直接写 `JOIN`。

### LEFT JOIN：左边的一个都不能少
```sql
SELECT u.name, o.id
FROM user u
LEFT JOIN orders o ON o.user_id = u.id;
```

左表 `user` 的每一行都会出现。没下过单的用户，右表的列（如 `o.id`）显示为 NULL。常用来找「没有订单的用户」：再加上 `WHERE o.id IS NULL` 即可。

### 对比两种 JOIN
| 类型 | 保留哪些行 | 没匹配上时 | 常见用途 |
|---|---|---|---|
| `INNER JOIN` | 两边都匹配的行 | 该行不出现 | 查有关联的数据 |
| `LEFT JOIN` | 左表全部行 | 右表列为 NULL | 查可能没有关联的数据 |

结论：默认用 `INNER JOIN` 查有关联的数据；需要保留左表全部行、包括没有关联的行时，换成 `LEFT JOIN`。

### ON 条件怎么写
`ON` 写两张表之间的关联条件，通常是一张表的外键等于另一张表的主键。如果漏写了 `ON`，两张表会被两两全部拼接，结果行数暴增，要特别避免。

### 写 JOIN 时要注意
- 关联列要有索引，否则每次匹配都要扫描整张表；
- 一次连的表不宜太多，表多了查询变慢，结果也难以处理；
- 只选需要的列，不要用 `SELECT *`。

## 示例
```sql
-- 查每个订单对应的用户名
SELECT o.id, u.name, o.amount
FROM orders o
JOIN user u ON u.id = o.user_id
WHERE o.amount > 100;
```

## 易错点
- 把 `LEFT JOIN` 右表的过滤条件写在 `WHERE` 里；这会把 NULL 的行滤掉，效果变得和 `INNER JOIN` 一样
- 漏写 `ON` 条件；会得到两表的全部组合，行数暴增
- 关联列类型不一致或没有索引；匹配很慢，还可能让索引失效

## 追问
### [f1] RIGHT JOIN 是什么？
和 `LEFT JOIN` 相反，保留右表的所有行。把两张表的位置对调，`RIGHT JOIN` 就可以改写成 `LEFT JOIN`，所以实际更常用 `LEFT JOIN`。
