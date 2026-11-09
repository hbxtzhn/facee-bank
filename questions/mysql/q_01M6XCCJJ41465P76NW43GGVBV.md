---
id: q_01M6XCCJJ41465P76NW43GGVBV
title: 延迟关联分页是怎么做的？
type: concept
difficulty: medium
importance: 2
category: mysql
tags: [pagination, clustered-index]
prerequisites: [q_01M6XCCJ9EJRQFSC0V08MV688Y]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "MySQL 8.4 手册：LIMIT Query Optimization", url: "https://dev.mysql.com/doc/refman/8.4/en/limit-optimization.html" }
---

## 一句话
延迟关联是先在索引上只查出目标行的主键，再拿主键去取完整数据。这样大偏移量时不用对被跳过的行逐行回表。

## 要点
- [kp1|3] 先用子查询只查主键，再用主键关联原表取完整行
- [kp2|3] 子查询只读索引，被跳过的行不需要回表
- [kp3|2] 回表只发生在最终要返回的那一页行上
- [kp4] 适合偏移量大、需要很多列的深翻页场景
- [kp5] 子查询里的排序和过滤条件最好能走同一个索引

## 详解
### 先搞懂：先查名单，再按名单取资料
学校要翻出第 10000 到 10020 名学生的完整档案。笨办法是把前 10020 份档案都从柜子里一份份搬出来，再丢掉前 10000 份。聪明的办法是：先看一张只有学号的名单，数到第 10000 位，抄下后面 20 个学号，再按这 20 个学号去柜子里取档案。

延迟关联就是这个思路。后文用到的术语：

- **回表**：通过索引找到主键后，再回到完整数据行取其他列。
- **覆盖索引**：查询所需的列都在索引里，不用回表。
- **偏移量**：要跳过多少行。

### 普通分页为什么慢
```sql
SELECT * FROM article ORDER BY create_time LIMIT 100000, 20;
```

如果要取全部列，对每一行 MySQL 都要先在索引里找到主键，再回表读整行。偏移量是 10 万，就要对 10 万行都做回表，然后把它们丢掉，只留 20 行。回表是随机读，代价不小。

### 延迟关联：把回表推迟到最后
```sql
SELECT a.*
FROM article a
JOIN (
    SELECT id FROM article
    ORDER BY create_time
    LIMIT 100000, 20
) t ON a.id = t.id;
```

分两步理解：

1. **子查询**：只查 `id`。只要 `create_time` 上有索引，这一步通常只读索引就够，不用回表。扫描并丢掉前 10 万行也只是在索引里走，轻得多。
2. **外层关联**：拿到那 20 个 `id`，再去原表取完整的行，只回表 20 次。

回表这个重活被「延迟」到只剩目标行，所以叫延迟关联。

### 什么时候适合用
- 偏移量大，翻页很深；
- 查询要返回很多列，回表代价高；
- 排序和过滤的列有合适的索引，子查询能只靠索引完成。

偏移量很小时，普通分页已经够快，没必要多写一层。

### 它的局限
延迟关联只是减少回表，并没有消除对前面行的扫描。偏移量大到一定程度，索引里的扫描也会变慢。要彻底避开，需要用书签方式，只记录上一页最后一行的位置。

## 示例
```sql
-- 取第 5001 页，每页 20 条，偏移量是 5000 * 20 = 100000
SELECT a.id, a.title, a.content, a.create_time
FROM article a
JOIN (
    SELECT id
    FROM article
    ORDER BY create_time, id
    LIMIT 100000, 20
) t ON a.id = t.id
ORDER BY a.create_time, a.id;
```

## 易错点
- 以为延迟关联让偏移量不再有影响；索引里的扫描仍然要走过前面的行
- 子查询里选了很多列；一旦要读索引以外的列，就又要回表，失去意义
- 外层关联后忘了再排序；关联结果的顺序不保证和子查询一致

## 追问
### [f1] 延迟关联和书签分页有什么区别？
延迟关联只是把回表推迟，仍然需要从头数偏移量；书签分页记住上一页最后一行，直接从那个位置往后取，不再数偏移量。
