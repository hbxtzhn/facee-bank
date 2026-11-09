---
id: q_01M6XCCKG7WEDN67NTVMTXTPNG
title: 前缀索引的长度怎么选，有什么取舍？
type: concept
difficulty: medium
importance: 1
category: mysql
tags: [index-design]
prerequisites: [q_01M6XCCK7WD6RKSBP8NZY9YBMP]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MySQL 8.4 手册：CREATE INDEX Statement（Prefix Indexes）", url: "https://dev.mysql.com/doc/refman/8.4/en/create-index.html" }
  - { title: "MySQL 8.4 手册：Column Indexes（前缀索引）", url: "https://dev.mysql.com/doc/refman/8.4/en/column-indexes.html" }
estimatedMinutes: 3
---

## 一句话
前缀越短，索引越省空间，但区分度越低、回表越多。选长度的办法是统计前缀的区分度，找一个接近整列区分度的最短长度。

## 要点
- [kp1|3] 前缀越短越省空间，但相同前缀的行变多，区分度下降
- [kp2|3] 区分度用 `COUNT(DISTINCT 前缀) / COUNT(*)` 计算，越接近 1 越好
- [kp3|2] 做法：试几个长度，选区分度接近整列、又足够短的那个
- [kp4|2] 前缀相同的行越多，要回表核对的行越多，查询越慢
- [kp5] 数据分布变化后，要重新评估前缀长度

## 详解
### 先搞懂：用几个字就能分清人
班里同学找人，只说名字的第一个字，「张」可能有七八个人，还要一个个对；说前两个字，可能只剩一两个人；说完整的名字，肯定只有一个。前缀越长越准，但要记的字也越多。

后文用到的术语：

- **区分度**：不同值的数量占总行数的比例，越接近 1，说明重复越少。
- **前缀**：字符串开头的若干字符。
- **回表**：通过索引找到主键后，回到完整数据行取数据。

### 取舍：省空间和查得准是两头
- **前缀太短**：索引小，但很多行的前缀相同，索引筛选不出多少行，查询时要对这些行逐一回表核对；
- **前缀太长**：筛选很准，但索引接近整列大小，省空间的目的就落空了。

所以要找一个平衡点：尽量短，同时区分度接近整列。

### 怎么确定长度
先算整列的区分度，再试几个不同的前缀长度，对比它们的区分度：

```sql
SELECT
  COUNT(DISTINCT email) / COUNT(*)           AS full_ratio,
  COUNT(DISTINCT LEFT(email, 4)) / COUNT(*)  AS p4,
  COUNT(DISTINCT LEFT(email, 8)) / COUNT(*)  AS p8,
  COUNT(DISTINCT LEFT(email, 12)) / COUNT(*) AS p12
FROM user;
```

看哪个长度的结果最接近 `full_ratio`。如果 8 个字符已经和整列差不多，就没必要取 12 个。

### 要结合真实数据来选
同样是 `email`，如果所有邮箱都是同一家公司，后缀一样，前缀部分才有区别；如果前缀几乎都以相同的字符开头，就要取得更长。长度没有通用的标准值，要看自己表里的数据分布。

### 局限和维护
- 前缀索引只存了前缀，没法单靠索引给出完整值，查询仍要回表核对；
- 业务数据变化后，原来的区分度可能下降，要定期复查。

## 示例
```sql
-- 确定取 8 个字符后创建索引
ALTER TABLE user ADD INDEX idx_email (email(8));

-- 创建后，用 EXPLAIN 确认索引被使用
EXPLAIN SELECT id FROM user WHERE email = 'tom@example.com';
```

## 易错点
- 凭感觉随便取一个长度；没统计区分度，可能取得太短，索引筛选不出多少行
- 一味追求省空间，把前缀取得很短；筛选效果差，反而更慢
- 以为取定长度后永远有效；数据分布变了，需要重新评估

## 追问
### [f1] 区分度算出来是 1 就一定最好吗？
区分度越接近 1 说明重复越少，但前缀长度也会随之变长。要在区分度和索引大小之间权衡，选「接近整列、又尽量短」的长度，不必追求绝对的 1。
