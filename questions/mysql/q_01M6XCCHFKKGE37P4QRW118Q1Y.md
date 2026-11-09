---
id: q_01M6XCCHFKKGE37P4QRW118Q1Y
title: 怎么定位和分析慢 SQL？
type: scenario
difficulty: medium
importance: 3
category: mysql
tags: [sql-optimization]
prerequisites: [q_01M6XCC86NH3XC896A6W9QDAP7, q_01M6XCCH64M0MSBJHQYKHYVS1A]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
先靠慢查询日志或服务监控找到慢 SQL，再用 EXPLAIN 看执行计划，找出没走索引、扫描行数过多等原因，最后针对性优化。

## 要点
- [kp1|3] 慢查询日志记录执行时间超过阈值的 SQL，可用 `mysqldumpslow` 汇总分析
- [kp2|3] 找到慢 SQL 后，用 `EXPLAIN` 看 MySQL 实际打算怎么执行
- [kp3|2] 业务里可以加慢 SQL 监控和告警，不用等用户反馈才发现
- [kp4] 分析重点是有没有走索引、扫描行数多不多、有没有额外排序

## 详解
### 先搞懂：先找到哪条慢，再看为什么慢
线上接口变慢，你不能凭感觉改。就像车坏了，要先确定是哪个零件，再决定怎么修。定位慢 SQL 分两步：先找出「哪几条 SQL 慢」，再分析「它们为什么慢」。

后文用到的术语：

- **慢查询日志**：MySQL 把执行时间超过设定阈值的 SQL 记录下来的日志文件。
- **执行计划**：MySQL 决定的查询步骤，用 `EXPLAIN` 查看。
- **阈值**：超过多长时间算慢，可以自己设置。

### 第一步：找出慢 SQL
**方式一：慢查询日志。** 开启后，MySQL 会把执行时间超过阈值的语句写进日志。日志里条目很多，可以用自带的 `mysqldumpslow` 工具，按出现次数或总耗时汇总，找出最该处理的几条。

**方式二：服务监控。** 在业务服务里采集每条 SQL 的耗时，超过阈值就告警。这样问题出现时马上知道，不用等到查日志。

两种方式常配合使用：日志适合事后分析，监控适合及时发现。

### 第二步：分析为什么慢
拿到慢 SQL，在前面加 `EXPLAIN` 看执行计划，重点看这几项：

1. `key` 是否为 NULL：为 NULL 说明没用上索引；
2. `type` 是否是 `ALL`：是的话是全表扫描；
3. `rows` 是否很大：说明要扫描很多行；
4. `Extra` 里有没有 `Using filesort`：说明有额外排序。

### 第三步：针对性优化
- 没走索引：给查询条件的列加合适的索引，或者改写写法，避免在索引列上用函数；
- 扫描行数太多：缩小查询范围，只查需要的列；
- 分页越翻越慢：改用延迟关联或书签方式；
- 子查询慢：改写成 JOIN。

优化后再跑一次 `EXPLAIN`，对比 `key` 和 `rows` 的变化，确认真的变好了。

## 示例
```sql
-- 查看慢查询日志是否开启，以及阈值
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- 开启慢查询日志，并设置阈值（单位：秒）
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

```bash
# 汇总慢日志，按查询耗时排序，只看前 10 条
mysqldumpslow -s t -t 10 /var/lib/mysql/slow.log
```

## 易错点
- 以为开启慢日志就万事大吉；日志要有人定期分析才有价值
- 阈值设得过大，真正有问题的 SQL 都没有被记录下来
- 只看单次执行耗时；一条不算太慢但调用极频繁的 SQL，累计影响也很大

## 追问
### [f1] 慢查询日志开启后对性能有影响吗？
会有一些额外的写日志开销，所以阈值不宜设得过低。生产环境一般设置一个合理的阈值，只记录真正偏慢的语句。
