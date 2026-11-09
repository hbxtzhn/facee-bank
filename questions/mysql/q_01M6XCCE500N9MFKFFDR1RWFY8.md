---
id: q_01M6XCCE500N9MFKFFDR1RWFY8
title: 什么是索引下推（ICP）优化？
type: concept
difficulty: medium
importance: 2
category: mysql
tags: [index-design, query-execution]
prerequisites: [q_01M6XCC75ZFAENX4G76CYPG536, q_01M6XCC7E14K9WXXGVWT9T24GD, q_01M6XCCDMCBWPR2CJKH38F68RB]
appliesTo: ["MySQL >= 5.6"]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MySQL 8.4 手册：Index Condition Pushdown Optimization", url: "https://dev.mysql.com/doc/refman/8.4/en/index-condition-pushdown-optimization.html" }
  - { title: "MySQL 8.4 手册：EXPLAIN Output Format（Extra 列）", url: "https://dev.mysql.com/doc/refman/8.4/en/explain-output.html" }
estimatedMinutes: 3
---

## 一句话
索引下推（ICP）是把能在索引里判断的过滤条件交给存储引擎处理，先过滤再回表，减少回表次数和返回给 Server 层的行数。

## 要点
- [kp1|3] MySQL 分 Server 层和存储引擎层，没有 ICP 时条件都在 Server 层判断
- [kp2|3] 有 ICP 时，索引列上的条件在存储引擎里提前判断，不满足的行不回表
- [kp3|2] InnoDB 里 ICP 只对二级索引有用，对聚簇索引没有意义
- [kp4] `EXPLAIN` 的 `Extra` 出现 `Using index condition` 表示用了 ICP

## 详解
### 先搞懂：保安先筛一遍，还是全放进来再筛
公司前台（Server 层）要找「姓张、年龄大于 20」的人。没有 ICP 时，仓库管理员（存储引擎）凭目录找出所有姓张的人，每个人都去仓库取出完整档案，交给前台，前台再看年龄。有 ICP 时，目录上本来就写着年龄，管理员在目录上先筛掉年龄不对的，剩下的才去取档案。

几个术语：

- **Server 层**：负责解析 SQL、优化、执行过滤的上层。
- **存储引擎层**：负责实际读写数据，比如 InnoDB。
- **回表**：根据二级索引的主键值再回聚簇索引取整行。

### 没有 ICP 的流程
设有联合索引 `(name, age)`，查询 `WHERE name LIKE '张%' AND age > 20`。`name` 前缀匹配能定位，但 `age` 条件在 `name` 用了范围后，无法继续缩小扫描范围。

没有 ICP 时：

1. 存储引擎按 `name` 在索引里找到所有姓张的项；
2. 每一项都回表取整行，返回给 Server 层；
3. Server 层再判断 `age > 20`，不满足就丢弃。

### 有 ICP 的流程
1. 存储引擎在索引里找到姓张的项；
2. 因为索引里就有 `age`，它直接判断 `age > 20`；
3. 只有满足的才回表，再返回给 Server 层。

不该回表的行没有回表，省了很多读。

### 适用范围
- 在 InnoDB 里只对二级索引有效；
- 条件涉及的列必须在这个索引里；
- 默认开启，可以用 `optimizer_switch` 里的 `index_condition_pushdown` 开关控制。

### 进阶：和覆盖索引的区别（基础薄弱可先跳过）
覆盖索引是查询的所有列都在索引里，完全不回表，`Extra` 显示 `Using index`。ICP 是仍然要回表，但先在索引里过滤掉一部分，`Extra` 显示 `Using index condition`。

## 示例
```sql
CREATE INDEX idx_name_age ON user(name, age);
EXPLAIN SELECT * FROM user WHERE name LIKE '张%' AND age > 20;
-- Extra: Using index condition
```

## 易错点
- 以为 ICP 能省掉回表；它只是减少不必要的回表，满足条件的行仍要回表
- 把 `Using index condition` 和 `Using index` 混为一谈；前者是 ICP，后者是覆盖索引
- 以为 ICP 对主键查询也有用；聚簇索引的叶子就是整行，没有回表可省

## 追问
### [f1] ICP 对哪些查询帮助最大？
联合索引中前面列用范围条件后，后面的列无法定位但还在索引里的情形，可以先过滤、少回表。
