---
id: q_01M6XCCDWTB1H19821JBVA0GXF
title: 联合索引的最左前缀原则是什么？
type: concept
difficulty: medium
importance: 3
category: mysql
tags: [index-design]
prerequisites: [q_01M6XCCDMCBWPR2CJKH38F68RB]
appliesTo: ["跳跃扫描部分：MySQL >= 8.0.13"]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MySQL 8.4 手册：Multiple-Column Indexes", url: "https://dev.mysql.com/doc/refman/8.4/en/multiple-column-indexes.html" }
  - { title: "MySQL 8.4 手册：Range Optimization（Skip Scan）", url: "https://dev.mysql.com/doc/refman/8.4/en/range-optimization.html" }
estimatedMinutes: 3
---

## 一句话
联合索引要从最左边的列开始、连续使用，才能用上前面几列；跳过中间的列，后面的列就帮不上定位了。

## 要点
- [kp1|3] 联合索引 `(a, b, c)` 能服务 `a`、`a, b`、`a, b, c` 的条件
- [kp2|3] 只用 `b` 或 `c`，没有最左列 `a`，通常无法用索引快速定位
- [kp3|2] 跳过中间列，如只写 `a` 和 `c`，只有 `a` 能用来定位
- [kp4] 条件写的先后顺序不影响，优化器会自己调整

## 详解
### 先搞懂：电话簿先按姓、再按名
电话簿先按姓排，姓相同再按名排。你给出姓，我能翻到那一段；给出姓和名，我能精确定位。但你只告诉我名，我就得从头翻到尾。联合索引 `(a, b, c)` 的规矩就是：先用 `a`，再用 `b`，再用 `c`，不能跳。

几个术语：

- **最左前缀**：从联合索引最左边开始、连续的若干列。
- **等值条件**：写成 `列 = 值` 的条件。
- **范围条件**：写成 `>`、`<`、`BETWEEN` 的条件。

### 哪些查询能用上
以索引 `(a, b, c)` 为例：

| 查询条件 | 能用到的索引列 |
|---|---|
| `a = 1` | a |
| `a = 1 AND b = 2` | a、b |
| `a = 1 AND b = 2 AND c = 3` | a、b、c |
| `b = 2` | 通常用不上 |
| `a = 1 AND c = 3` | 只有 a 用来定位，c 不行 |

### 为什么会这样
因为索引里先按 `a` 排，`a` 相同才按 `b` 排。没有 `a` 的限定，`b` 相同的行分散在各个 `a` 下面，没法连续找到。同样，`a` 确定了但 `b` 不确定，`c` 也是分散的。

### 遇到范围条件
当某一列用了范围条件，比如 `a = 1 AND b > 2 AND c = 3`，`a`、`b` 可以用来定位，`b` 之后的 `c` 不能继续用来缩小扫描范围。但 `c` 的条件还可以在索引里直接过滤，这就和索引下推有关。

### 一些补充
- WHERE 里条件的先后顺序无所谓，`WHERE b = 2 AND a = 1` 和 `a = 1 AND b = 2` 一样；
- 判断是否用上，最可靠是看 `EXPLAIN` 的 `key_len`，它能反映用了几列。

### 进阶：跳跃扫描（基础薄弱可先跳过）
MySQL 8.0.13 起，优化器有时会采用跳跃扫描，对最左列的每个不同取值分别扫描一段范围，让缺了最左列的查询也能用上索引。它有使用条件（如查询只用到这个索引里的列），是否采用由优化器按代价决定，不是保证，设计索引时不要依赖它。

## 示例
```sql
CREATE INDEX idx_abc ON t(a, b, c);
SELECT * FROM t WHERE a = 1 AND b = 2;   -- 用到 a、b
SELECT * FROM t WHERE b = 2 AND c = 3;   -- 缺少最左列 a
```

## 易错点
- 以为 WHERE 里条件顺序必须和索引顺序一致；优化器会自动调整
- 以为遇到范围条件，后面的列完全没用；它们还可以在索引里过滤
- 以为只要写了联合索引的某一列就能用上；必须有最左列

## 追问
### [f1] 怎么设计联合索引的列顺序？
等值条件的列放前面，范围条件的列放在后面；在此基础上把区分度高的、使用频率高的列放前面。
