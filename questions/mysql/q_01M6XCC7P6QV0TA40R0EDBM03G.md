---
id: q_01M6XCC7P6QV0TA40R0EDBM03G
title: 怎么用 SQL 创建、切换和删除数据库？
type: concept
difficulty: easy
importance: 1
category: mysql
tags: [sql-basics]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
用 `CREATE DATABASE` 创建数据库，`USE` 切换，`DROP DATABASE` 删除；删除会把库里所有的表和数据一起清掉，不能随便执行。

## 要点
- [kp1|3] 创建：`CREATE DATABASE 库名;`
- [kp2|3] 切换：`USE 库名;`，之后的 SQL 默认在这个库里执行
- [kp3|2] 删除：`DROP DATABASE 库名;`，库里的表和数据一起丢失
- [kp4] 用 `IF NOT EXISTS`、`IF EXISTS` 可以避免库已存在或不存在时报错

## 详解
### 先搞懂：数据库就像一个文件夹
可以把数据库想成电脑里的一个文件夹：

- 创建数据库，相当于新建一个文件夹；
- `USE`，相当于双击进入这个文件夹；
- 删除数据库，相当于把整个文件夹连同里面的所有文件一起删除。

数据库里存放的是表，表里存放的是数据。

### 创建数据库
`CREATE DATABASE shop;` 就创建了一个叫 `shop` 的库。库已经存在时再创建会报错，加上 `IF NOT EXISTS` 就不会报错：

`CREATE DATABASE IF NOT EXISTS shop;`

### 切换数据库
一个 MySQL 里可以有很多库。要操作哪个库的表，先用 `USE shop;` 进入它。进入之后写的 `SELECT * FROM t_order`，查的就是 `shop` 库里的表。也可以不切换，直接写 `shop.t_order` 带上库名。

### 删除数据库
`DROP DATABASE shop;` 会删掉这个库，库里所有的表和数据一起没有了，而且通常不能撤销。

- 执行前确认库名，最好先做备份；
- 想避免库不存在时报错，写 `DROP DATABASE IF EXISTS shop;`。

## 示例
```sql
CREATE DATABASE IF NOT EXISTS shop;
USE shop;
SHOW DATABASES;
DROP DATABASE IF EXISTS shop;
```

## 易错点
- 以为 `DROP DATABASE` 只删库本身；库里的所有表和数据也会一起被删掉
- 忘记 `USE` 就直接建表，表会报没有选择数据库的错误
- 在生产环境手滑执行 `DROP DATABASE`，没有备份就很难找回

## 追问
### [f1] 怎么查看有哪些数据库？
执行 `SHOW DATABASES;`。想看当前正在使用哪个库，执行 `SELECT DATABASE();`。

### [f2] 创建数据库时怎么指定字符集？
可以在建库时写 `CHARACTER SET`，例如 `CREATE DATABASE shop CHARACTER SET utf8mb4;`，库里新建的表默认使用这个字符集。
