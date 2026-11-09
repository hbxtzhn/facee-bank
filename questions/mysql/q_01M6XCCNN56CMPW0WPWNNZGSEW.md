---
id: q_01M6XCCNN56CMPW0WPWNNZGSEW
title: ORDER BY 排序是怎么完成的？
type: concept
difficulty: easy
importance: 2
category: mysql
tags: [query-execution, index-design]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
如果走的索引本身就是有序的，MySQL 按索引顺序读出来就是排好的；否则要把数据取出来再排序，这一步叫 filesort。

## 要点
- [kp1|3] 索引本身有序，按索引顺序读取，不需要额外排序
- [kp2|3] 没有可用的有序索引，就要读出数据再排序，即 filesort
- [kp3|2] filesort 数据量小时在内存里排，太大就借助磁盘临时文件
- [kp4] EXPLAIN 的 Extra 出现 Using filesort，说明有额外排序
- [kp5] filesort 只是名字，不一定真的写了文件

## 详解
### 先搞懂：已经排好队的和没排队的
举个例子：查某个用户最近的订单，按下单时间排序。

类比：图书馆的书如果按编号摆好，你要「按编号取 20 本」，顺着书架拿就行。如果书是乱放的，就得先全部搬出来，在桌子上排好序再取。

后文会用到这几个词：

- **索引有序**：索引里的数据，本来就是按索引列的值排好的。
- **filesort**：MySQL 里「额外排序」的名字，不代表一定用到文件。
- **排序缓冲区**：MySQL 给每个查询分配的、用来排序的一块内存。

### 方式一：按索引顺序读取
InnoDB 的二级索引，是按索引列的值排好序的。如果查询的排序要求，正好与某个索引的顺序一致，MySQL 顺着这个索引读，读出来的数据本来就是有序的，不需要排序。

这是最快的情况。`EXPLAIN` 的 `Extra` 里不会出现 `Using filesort`。

### 方式二：filesort，读出来再排
没有可用的有序索引时，MySQL 要这样做：

1. 按条件取出需要的行（或行的关键列）；
2. 放进排序缓冲区，在内存里排序；
3. 如果数据太多，缓冲区放不下，就把一部分排好序写到磁盘临时文件，最后再合并。

所以 filesort 里的「file」，表示在放不下的情况下会用到文件。数据量不大时，它完全在内存里完成。

### 怎么判断
用 `EXPLAIN` 看 `Extra` 列。出现 `Using filesort` 就是用了额外排序；没有出现，说明直接利用了索引的顺序。

## 示例
```sql
-- 假设有索引 idx_user_time(user_id, created_at)
-- 这条查询可以直接按索引顺序读取，不需要 filesort
EXPLAIN SELECT id FROM orders
WHERE user_id = 7
ORDER BY created_at;
```

## 易错点
- 以为 filesort 就是文件排序、一定很慢；数据量小时它在内存里完成
- 以为 ORDER BY 的列上有索引就一定不排序，还要看查询条件和索引顺序是否配合
- 以为排序是数据库自动完成的、不用关心；排序列没有索引时，大表上的排序会变得很慢

## 追问
### [f1] 排序数据太多放不下内存怎么办？
MySQL 会把数据分批在内存里排好序，写到磁盘上的临时文件，最后合并得到完整结果。这会增加磁盘读写，所以优先靠索引避免排序，或者用 `LIMIT` 缩小数据量。
