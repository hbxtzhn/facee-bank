---
id: q_01M6XCCP5FEBGXX2VT1NDF5ZV2
title: UNION 和 UNION ALL 有什么区别？
type: concept
difficulty: easy
importance: 1
category: mysql
tags: [sql-basics]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
UNION 把几个查询的结果合并后去重，UNION ALL 直接拼在一起、保留重复行，所以 UNION ALL 更快，确定没有重复时优先用它。

## 要点
- [kp1|3] UNION 合并结果并去掉完全重复的行
- [kp2|3] UNION ALL 只拼接，不去重，通常更快
- [kp3|2] 各个 SELECT 的列数必须一致，对应列类型要兼容
- [kp4] 结果的列名取自第一个 SELECT
- [kp5] 最后的 ORDER BY 或 LIMIT 作用在合并后的整体结果上

## 详解
### 先搞懂：把两份名单合成一份
假设两个活动各有一份报名名单，现在要一份总名单。

- 有人两个活动都报了：如果希望他只出现一次，就是 **UNION**（合并并去重）；
- 如果就想原样拼起来，同一个人出现两次也无所谓，就是 **UNION ALL**。

后文会用到这几个词：

- **去重**：完全相同的行只保留一行。
- **临时表**：MySQL 执行过程中，临时存放中间结果的表。

### UNION：合并并去重
UNION 会把多个查询的结果放在一起，再把每一列都完全相同的行去掉。为了去重，MySQL 通常要借助临时表，需要额外的时间和空间。

### UNION ALL：只拼接
UNION ALL 把结果直接首尾相接，不做去重，也不需要去重用的临时表。所以同样的数据量，它通常比 UNION 更快。

选择原则很简单：
- 业务上明确不会重复（比如两个条件互斥），用 UNION ALL；
- 必须保证结果唯一，才用 UNION。

### 两者共同的规则
- 每个 SELECT 返回的**列数必须相同**；
- 对应位置的列，**类型要兼容**（不一定完全相同，MySQL 会做类型转换）；
- 结果的**列名**取自第一个 SELECT；
- 想对整个结果排序或限制行数，要把 `ORDER BY` / `LIMIT` 放在最后，它作用在合并后的结果上。

## 示例
```sql
-- 去重：同一个用户只出现一次
SELECT user_id FROM signup_a
UNION
SELECT user_id FROM signup_b;

-- 不去重：两个互斥条件，没有重复，用 UNION ALL 更快
SELECT id FROM orders WHERE status = 1
UNION ALL
SELECT id FROM orders WHERE status = 2;
```

## 易错点
- 以为 UNION 只是简单拼接；它会去重，行数可能比两边加起来少
- 明明没有重复数据，还用 UNION，白白多一次去重
- 各 SELECT 列数不一致，直接报错
- 按两边各自的列名取结果，其实只认第一个 SELECT 的列名

## 追问
### [f1] UNION 去重是按哪一列去重？
是按整行去重：所有列的值都相同，才算重复。只有一列相同不会被去掉。

### [f2] 为什么说能用 UNION ALL 就用它？
UNION 为了去重，要多做一次比较和临时表处理。数据量大时，这部分开销会很明显。如果业务上本来就不会出现重复，这些开销就是白白浪费。
