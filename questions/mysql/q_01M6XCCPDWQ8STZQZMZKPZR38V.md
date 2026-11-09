---
id: q_01M6XCCPDWQ8STZQZMZKPZR38V
title: UNION 的条件下推是什么？
type: concept
difficulty: medium
importance: 1
category: mysql
tags: [sql-optimization]
prerequisites: [q_01M6XCCP5FEBGXX2VT1NDF5ZV2]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MySQL 8.4 手册：Derived Condition Pushdown Optimization（含 UNION）", url: "https://dev.mysql.com/doc/refman/8.4/en/derived-condition-pushdown-optimization.html" }
estimatedMinutes: 3
---

## 一句话
条件下推就是把外层的 WHERE、LIMIT 等条件，手动写进 UNION 的每个分支里，让每个分支先过滤、先截取，少产生无用的数据。

## 要点
- [kp1|3] 条件下推：把外层的过滤和限制写进 UNION 的每个分支
- [kp2|3] 每个分支只处理需要的数据，合并和去重的数据量更小
- [kp3|2] LIMIT 下推时，每个分支要取够 offset 加 n 行
- [kp4] 外层条件要在最终结果上保留一份，保证结果正确
- [kp5] 下推后用 EXPLAIN 对比，确认每个分支都走了索引

## 详解
### 先搞懂：先在源头筛，别等汇总后再筛
假设有两张日志表（本月和上月），要查「用户 7 的最新 10 条日志」。

最直接的写法是：先把两张表全部拼起来，再在外面筛用户、排序、取 10 条。

类比：两个部门各有一万份文件，你要「小王经手的最近 10 份」。不好的做法是把两万份全搬到一张桌上再挑；好的做法是让每个部门先挑出小王的，再合起来选 10 份。

后文会用到这几个词：

- **外层**：包在 UNION 外面的那层查询，里面通常有 WHERE、ORDER BY、LIMIT。
- **分支**：UNION 里的每一个 SELECT。
- **下推**：把本来写在外层的条件，往里挪到每个分支。

### 过滤条件的下推
不推的写法：

- 先对两张表整表 UNION，再用外层 `WHERE user_id = 7` 过滤。
- 每个分支都把整张表的数据取出来，合并后才过滤，中间数据很多。

下推之后：

- 每个分支自己带上 `WHERE user_id = 7`，只取需要的行；
- 分支内部还能用上 `user_id` 上的索引。
- 合并的数据量大大减少。

### LIMIT 的下推：每个分支要多取一点
LIMIT 的下推要小心。「最新 10 条」要在合并后才能确定，但每个分支最多只可能贡献 10 条。所以每个分支都可以先排序，各自取前 10 条，再合并后排序、取前 10 条。

如果有 `OFFSET`，每个分支要取够「offset + n」行，不能只取 n 行，否则会漏掉应当出现在结果里的行。

### 外层的条件要保留
下推只是提前缩小数据。最终的 ORDER BY 和 LIMIT 仍然要在外层写一份，因为合并后还要重新排序，才能得到正确的前 N 条。

### MySQL 会自动做吗
优化器在一些情况下能自动把条件下推到派生表中，但不保证每种写法都能下推。不依赖自动优化，自己手动写进分支，意图明确，结果更可控。

## 示例
```sql
-- 每个分支先过滤、排序、各取 10 条，外层再排序取前 10 条
(SELECT id, created_at FROM log_current
 WHERE user_id = 7 ORDER BY created_at DESC LIMIT 10)
UNION ALL
(SELECT id, created_at FROM log_last
 WHERE user_id = 7 ORDER BY created_at DESC LIMIT 10)
ORDER BY created_at DESC
LIMIT 10;
```

## 易错点
- 只在分支里下推 LIMIT，外层没有再排序和 LIMIT，结果条数和顺序都不对
- 有 OFFSET 时每个分支只取 n 行，会漏数据
- 下推了条件，但分支里的条件列没有索引，仍然全表扫描
- 误以为优化器一定会自动下推，不去检查执行计划

## 追问
### [f1] 条件下推适合所有 UNION 吗？
不是。过滤条件下推通常都安全。LIMIT 下推要保证每个分支取够行数，并在外层重新排序。如果合并后还要去重，下推 LIMIT 可能影响去重后的行数，要谨慎。

### [f2] 怎么验证下推有效？
用 `EXPLAIN` 看每个分支是否用上索引，再对比下推前后的执行时间和扫描行数。
