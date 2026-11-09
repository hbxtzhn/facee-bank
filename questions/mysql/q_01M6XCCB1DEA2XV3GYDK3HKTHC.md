---
id: q_01M6XCCB1DEA2XV3GYDK3HKTHC
title: 怎么给表创建和删除索引？
type: concept
difficulty: easy
importance: 1
category: mysql
tags: [index-structure, sql-basics]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
建表时用 `INDEX` 或 `KEY` 定义，建表后用 `CREATE INDEX` 或 `ALTER TABLE ... ADD INDEX` 创建；删除用 `DROP INDEX`。

## 要点
- [kp1|3] 建表时可在 `CREATE TABLE` 里直接写 `INDEX 索引名 (列)`
- [kp2|3] 建表后用 `CREATE INDEX 索引名 ON 表(列)` 添加，用 `DROP INDEX 索引名 ON 表` 删除
- [kp3|2] 唯一索引写 `CREATE UNIQUE INDEX`，主键索引随 `PRIMARY KEY` 自动建立
- [kp4] 索引占磁盘，增删改时也要维护，不要乱建

## 详解
### 先搞懂：索引就像书的目录
一本书没有目录，找一个词只能一页页翻。加了目录，就能直接翻到那一页。但目录要占纸张，书内容改了，目录也要跟着改。数据库的索引也是这样：查询变快，代价是占磁盘、写入变慢。

几个术语：

- **索引名**：给索引起的名字，删除时靠它指定要删哪个。
- **唯一索引**：不允许两行在这一列上有相同的值。
- **联合索引**：一个索引里包含多列。

### 创建索引：两种时机
**建表时**，在列定义后面直接写：

```sql
CREATE TABLE user (
  id BIGINT PRIMARY KEY,
  name VARCHAR(50),
  email VARCHAR(100),
  INDEX idx_name (name),
  UNIQUE INDEX uk_email (email)
);
```

**建表后**，用下面两种写法，效果一样：

```sql
CREATE INDEX idx_name ON user(name);
ALTER TABLE user ADD INDEX idx_name (name);
```

### 删除索引
```sql
DROP INDEX idx_name ON user;
ALTER TABLE user DROP INDEX idx_name;
```

主键索引一般不用 `DROP INDEX` 删，要用 `ALTER TABLE user DROP PRIMARY KEY`。

### 建索引前想一想
- 每个索引都是一棵独立的树，要占磁盘空间；
- 表里每次插入、修改、删除，相关索引都要同步更新，写入会变慢；
- 在大表上建索引会花不少时间，要选业务低峰期做。

## 示例
```sql
-- 查看某张表有哪些索引
SHOW INDEX FROM user;
```

## 易错点
- 以为索引只有好处；索引占空间，还会拖慢增删改
- 删除索引时忘了写 `ON 表名`；`DROP INDEX` 必须说明是哪张表的索引
- 以为在业务高峰期给大表加索引没影响；建索引期间会占用大量资源

## 追问
### [f1] 怎么确认一条查询用上了索引？
在查询前加 `EXPLAIN`，看结果里的 `key` 列，它显示实际使用的索引名；为空说明没用上索引。
