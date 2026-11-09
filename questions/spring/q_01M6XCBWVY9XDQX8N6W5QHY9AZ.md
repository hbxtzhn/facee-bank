---
id: q_01M6XCBWVY9XDQX8N6W5QHY9AZ
title: 内存分页（RowBounds）是怎么工作的，为什么不推荐？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [pagination]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
RowBounds 是 MyBatis 的内存分页：数据库仍然按完整 SQL 查询，MyBatis 在读结果集时跳过前面的行、只取需要的几行，数据量大时浪费资源，所以不推荐。

## 要点
- [kp1|3] `RowBounds` 带 offset 和 limit 两个参数，作为 Mapper 方法的参数传入
- [kp2|3] SQL 里没有分页条件，数据库照常执行完整查询
- [kp3|2] MyBatis 读结果集时跳过 offset 前的行，读够 limit 行就停
- [kp4|2] 大表上耗时和内存随数据量增长，不适合生产分页
- [kp5] 只适合数据量很小的场景

## 详解
### 先搞懂：从一整本书里翻到第几页
想象你要看一本 1000 页的书的第 11 到第 20 页。

- 物理分页：让图书管理员直接把这 10 页复印给你。
- 内存分页：管理员把整本书搬给你，你自己从头一页页翻到第 11 页，数 10 页，然后丢掉其余的。

RowBounds 就是后者：数据库把全部数据交过来，MyBatis 再自己截取。

后文用到的词：

- **ResultSet**：数据库返回的结果集，可以一行一行往下读。
- **offset**：跳过多少行。
- **limit**：最多取多少行。
- **物理分页**：由数据库在 SQL 里完成分页。

### RowBounds 是怎么工作的
用法很简单：在 Mapper 接口方法里多加一个 `RowBounds` 参数，例如 `new RowBounds(20, 10)`，表示跳过 20 行、取 10 行。

执行流程：

1. SQL 原样发给数据库，没有 `limit`。
2. 数据库执行完整查询，返回结果集。
3. MyBatis 处理结果集时，先跳过 offset 条，再往下读 limit 条映射成对象。
4. 读够就停止，剩下的不再映射。

不带 `RowBounds` 时，默认值是跳过 0 行、不限制行数，也就是全部取回。

### 为什么不推荐
- **数据库没少干活**：完整查询和排序照常执行，分页只发生在 MyBatis 里。
- **网络和内存浪费**：数据库驱动可能把大量结果传回应用端，具体取决于驱动的读取方式。
- **页码越大越慢**：要跳过的行越多，读取的越多。
- **不能直接得到总数**：想知道一共多少页，还要另写一条统计查询。

### 方案对比：两种分页怎么选
| 方案 | 谁来分页 | 数据库返回 | 适合 |
|---|---|---|---|
| `RowBounds` 内存分页 | MyBatis | 完整结果集 | 数据量很小、临时用 |
| 物理分页（`limit` 或分页插件） | 数据库 | 只返回当前页 | 生产环境默认 |

结论：生产环境默认用物理分页；只有数据量确定很小、不想引入分页插件时，才考虑 `RowBounds`。

## 示例
```java
// Mapper 接口：多加一个 RowBounds 参数
List<User> selectAll(RowBounds rowBounds);
```

```java
// 跳过前 20 行，取 10 行（相当于第 3 页，每页 10 条）
List<User> page = userMapper.selectAll(new RowBounds(20, 10));
```

## 易错点
- 以为传了 RowBounds 数据库就只查一页；实际 SQL 没有变，数据库照样执行完整查询
- 在百万级表上用 RowBounds，数据量增大后耗时和内存明显上升
- 以为 RowBounds 能给出总条数；它只截取，不统计

## 追问
### [f1] 真正想要物理分页，有哪些做法？
在 SQL 里直接写 `limit`，或使用 PageHelper 这类分页插件自动改写 SQL。两种都由数据库完成分页。

### [f2] RowBounds 在什么情况下可以接受？
结果集本来就很小，比如几十条配置数据，分页只为前端展示。这时引入分页插件反而是多余的复杂度。
