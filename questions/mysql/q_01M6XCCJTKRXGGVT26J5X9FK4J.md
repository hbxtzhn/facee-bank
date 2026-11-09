---
id: q_01M6XCCJTKRXGGVT26J5X9FK4J
title: 书签分页是怎么做的？
type: concept
difficulty: medium
importance: 2
category: mysql
tags: [pagination, index-design]
prerequisites: [q_01M6XCCJ9EJRQFSC0V08MV688Y]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "MySQL 8.4 手册：Row Constructor Expression Optimization", url: "https://dev.mysql.com/doc/refman/8.4/en/row-constructor-optimization.html" }
  - { title: "MySQL 8.4 手册：LIMIT Query Optimization", url: "https://dev.mysql.com/doc/refman/8.4/en/limit-optimization.html" }
---

## 一句话
书签分页是记住上一页最后一行的排序字段值，下一页用 `WHERE` 从这个值之后开始查，不再数偏移量，所以翻得再深也不会变慢。

## 要点
- [kp1|3] 用上一页最后一行的值作为「书签」，下一页从书签之后开始取
- [kp2|3] 用 `WHERE 排序列 > 书签` 代替 `OFFSET`，直接定位，不扫描被跳过的行
- [kp3|2] 排序列要有索引，且值要唯一，通常用 `(时间, id)` 组合
- [kp4] 缺点是只能上一页下一页顺序翻，不能直接跳到任意页

## 详解
### 先搞懂：书里夹一张书签
读一本很厚的书，不会每次都从第一页数到第 800 页，而是上次读到哪儿，夹张书签，下次直接翻到书签处接着读。书签分页就是这个做法。

后文用到的术语：

- **书签**：上一页最后一行的排序字段值，用来标记下一页从哪里开始。
- **偏移量（OFFSET）**：要跳过多少行。
- **唯一性**：排序依据的值不重复，才能准确标记位置。

### 机制：把 OFFSET 换成 WHERE
普通分页：

```sql
SELECT id, title FROM article ORDER BY id LIMIT 20 OFFSET 100000;
```

书签分页：上一页最后一行的 `id` 是 100000，下一页这样查：

```sql
SELECT id, title FROM article
WHERE id > 100000
ORDER BY id
LIMIT 20;
```

`id` 上有索引，MySQL 可以直接在索引里定位到 100000 之后的位置，往后取 20 行即可。被跳过的行根本没有读，所以无论翻到第几页，速度基本一样。

### 排序列不唯一怎么办
如果按 `create_time` 排序，可能有很多行时间相同，书签只记时间会漏行或重复。解决办法是用「排序列加主键」组合作为书签：

```sql
SELECT id, title, create_time FROM article
WHERE (create_time, id) > ('2026-11-08 10:00:00', 5000)
ORDER BY create_time, id
LIMIT 20;
```

要让这个条件高效，需要在 `(create_time, id)` 上建联合索引。

### 优点和限制
- **优点**：速度不随页码增加而变慢，适合无限滚动、数据导出这类场景；
- **限制**：只能一页一页顺序往后翻，没法直接跳到第 500 页；
- **注意**：如果前端需要显示总页数或页码跳转，书签分页不合适。

### 向前翻页怎么办
向上一页翻时，把比较符号反过来，并把排序也反过来，取出结果后在应用里再翻转顺序。逻辑比向后翻略复杂。

## 示例
```sql
-- 第一页：没有书签，直接取
SELECT id, title, create_time FROM article
ORDER BY create_time, id
LIMIT 20;

-- 下一页：带上上一页最后一行的 (create_time, id)
SELECT id, title, create_time FROM article
WHERE (create_time, id) > ('2026-11-08 10:00:00', 5000)
ORDER BY create_time, id
LIMIT 20;
```

## 易错点
- 排序列有重复值又只记一个字段；会漏行或重复，要加主键一起比较
- 以为书签分页能跳页；它只适合顺序翻页
- 排序列没有索引；这时 `WHERE` 仍然要扫描大量行，优势体现不出来

## 追问
### [f1] 书签分页遇到数据被删除或新增会怎样？
因为是按值定位而不是按行数，上一页最后一行即使被删，仍然能从那个值之后继续，不会重复也不会漏。这比偏移量分页更稳定。
