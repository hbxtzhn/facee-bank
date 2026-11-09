---
id: q_01M6XCCH64M0MSBJHQYKHYVS1A
title: 怎么用 EXPLAIN 查看 SQL 的执行计划？
type: concept
difficulty: easy
importance: 3
category: mysql
tags: [sql-optimization]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
在 SELECT 语句前加 `EXPLAIN` 就能看到 MySQL 打算怎么执行它。重点看 `type`、`key`、`rows`，判断有没有用上索引、要扫多少行。

## 要点
- [kp1|3] `EXPLAIN SELECT ...` 只展示执行计划，不会真正返回查询结果
- [kp2|3] `key` 列显示实际用的索引，为 NULL 说明没用上索引
- [kp3|2] `type` 列表示访问方式，`ALL` 是全表扫描，越靠近 `const` 越好
- [kp4|2] `rows` 是预估要扫描的行数，越小越好
- [kp5] `Extra` 列会提示 `Using filesort`、`Using index` 等额外信息

## 详解
### 先搞懂：先看路线图，再决定要不要改
一条 SQL 很慢，你不知道慢在哪。好比导航软件给出一条路线：走哪条路、大概多远。`EXPLAIN` 就是 MySQL 给出的「查询路线图」，告诉你它准备怎么找数据。

后文用到的术语：

- **执行计划**：MySQL 决定的查询步骤，比如用哪个索引、先查哪张表。
- **全表扫描**：不用索引，从头到尾一行一行看。
- **索引**：帮助快速定位数据的目录。

### 怎么用
在原来的 SELECT 前面加上 `EXPLAIN`，其他都不用改：

```sql
EXPLAIN SELECT * FROM user WHERE name = '张三';
```

执行后返回一张表，每一行对应查询里的一个步骤。简单查询通常只有一行。

### 最常看的几列
| 列 | 含义 | 怎么看 |
|---|---|---|
| `id` | 查询步骤的编号 | 有子查询或联表时会有多行 |
| `select_type` | 查询的类型 | 比如简单查询 `SIMPLE`、子查询 `SUBQUERY` |
| `table` | 这一行针对哪张表 | 联表时看表的访问顺序 |
| `type` | 访问方式 | `ALL` 全表扫描最差，`const`、`ref`、`range` 较好 |
| `possible_keys` | 可能用到的索引 | 为空说明没有可用索引 |
| `key` | 实际使用的索引 | NULL 说明没走索引 |
| `rows` | 预估扫描行数 | 越小越好 |
| `Extra` | 补充信息 | `Using filesort` 表示要额外排序 |

### 怎么判断有没有用上索引
1. 先看 `key`：有索引名，说明用了；是 NULL，说明没用。
2. 再看 `type`：如果是 `ALL`，就是全表扫描，要考虑加索引或改写 SQL。
3. 最后看 `rows`：数字很大，说明要扫很多行，即使用了索引也可能不理想。

`rows` 是估算值，不是精确值，但足够用来比较改动前后的变化。

### 一个典型的优化流程
先用 `EXPLAIN` 看到 `type` 是 `ALL`、`key` 是 NULL，说明没用索引。给查询条件的列加上索引，再执行一次 `EXPLAIN`，看到 `key` 变成索引名、`rows` 明显下降，说明优化有效。

## 示例
```sql
-- 没有索引时：type = ALL，key = NULL
EXPLAIN SELECT * FROM user WHERE name = '张三';

-- 给 name 加索引后再看：key 变成 idx_name，rows 变小
CREATE INDEX idx_name ON user (name);
EXPLAIN SELECT * FROM user WHERE name = '张三';
```

## 易错点
- 以为 `EXPLAIN` 会执行查询并返回数据；它只给出计划，不返回结果行
- 把 `possible_keys` 当成实际用到的索引；真正用到的是 `key` 这一列
- 把 `rows` 当成精确值；它只是估算，只适合做相对比较

## 追问
### [f1] type 列从好到差大致是什么顺序？
常见的是 `system`、`const`、`eq_ref`、`ref`、`range`、`index`、`ALL`，越靠前越好。日常至少要避免 `ALL`，尽量做到 `range` 或 `ref` 以上。
