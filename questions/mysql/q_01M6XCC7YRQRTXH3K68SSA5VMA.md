---
id: q_01M6XCC7YRQRTXH3K68SSA5VMA
title: 怎么用 SQL 创建和删除表？
type: concept
difficulty: easy
importance: 1
category: mysql
tags: [sql-basics]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
用 `CREATE TABLE` 定义表名、字段和类型来建表，用 `DROP TABLE` 删表；删表会把表里的数据一起删掉，执行前要确认。

## 要点
- [kp1|3] 建表：`CREATE TABLE 表名 (字段 类型, ...)`，每个字段要指定数据类型
- [kp2|3] 删表：`DROP TABLE 表名;`，表结构和数据都会丢失
- [kp3|2] 常见类型：整数用 `INT` 或 `BIGINT`，字符串用 `VARCHAR`，时间用 `DATETIME`
- [kp4] `IF NOT EXISTS`、`IF EXISTS` 可以避免表已存在或不存在时报错

## 详解
### 先搞懂：表就像一张 Excel 表格
可以把表想成一张 Excel 表格：

- 表头定义有哪几列、每一列放什么类型的内容（建表）；
- 表头下面的每一行就是一条数据；
- 删除表，就是把整张表格连表头带内容一起扔掉。

后文用到的术语：

- **字段**：表里的一列；
- **数据类型**：规定这一列能存什么，如数字、文字、日期；
- **主键**：能唯一确定一行的字段。

### 创建表
`CREATE TABLE` 后面写表名，括号里逐个写字段，每个字段是「字段名 类型」，可以再加约束，如 `PRIMARY KEY`（主键）、`NOT NULL`（不能为空）。

- 整数：`INT`，数据很大时用 `BIGINT`；
- 字符串：`VARCHAR(50)`，括号里是最多能存多少个字符；
- 金额：`DECIMAL(10, 2)`，保证小数计算准确；
- 时间：`DATETIME`。

### 删除表
`DROP TABLE 表名;` 会把表的结构和里面所有数据一起删掉。

- 想只清空数据、保留表结构，可以用 `TRUNCATE TABLE` 或带条件的 `DELETE`；
- 想避免表不存在时报错，写 `DROP TABLE IF EXISTS 表名;`。

## 示例
```sql
CREATE TABLE IF NOT EXISTS t_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    age INT,
    created_at DATETIME
);

DROP TABLE IF EXISTS t_user;
```

## 易错点
- 以为 `DROP TABLE` 只删数据；它连表结构一起删，表本身也不存在了
- 建表时忘记指定主键，后面查询和修改会很不方便
- 用 `FLOAT` 存金额，小数可能有误差，金额应该用 `DECIMAL`
- 在没有备份的生产库里直接执行 `DROP TABLE`

## 追问
### [f1] DROP、DELETE、TRUNCATE 有什么区别？
`DELETE` 按条件删除行，表还在。`TRUNCATE` 清空整张表的数据，保留表结构。`DROP` 把表整个删掉。

### [f2] 怎么查看一张表的结构？
执行 `DESC 表名;` 看字段和类型，或 `SHOW CREATE TABLE 表名;` 看完整的建表语句。
