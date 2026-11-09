---
id: q_01M6XCC6NXE9P1VD9K3MPPGN3H
title: MySQL 的存储引擎是什么，常见的有哪几种？
type: concept
difficulty: easy
importance: 2
category: mysql
tags: [query-execution]
appliesTo: ["MySQL >= 5.5"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
存储引擎是 MySQL 里负责存取表数据的组件，常见的有 InnoDB、MyISAM 和 Memory，其中 InnoDB 支持事务和行锁，是现在的默认引擎。

## 要点
- [kp1|3] 存储引擎负责数据怎么存、怎么读，以表为单位选择
- [kp2|3] InnoDB 支持事务、行锁、外键，从 MySQL 5.5 起是默认引擎
- [kp3|2] MyISAM 不支持事务，也没有行锁，只有表锁
- [kp4] Memory 把数据放在内存里，重启后数据丢失；建表时用 `ENGINE=` 指定

## 详解
### 先搞懂：同样是存数据，可以有不同的存法
可以把 MySQL 想成一家图书馆：前台负责接待、查询，书库负责真正放书、取书。书库有不同的管理办法，有的整齐但手续多，有的随意但简单。

存储引擎就是这个书库的管理办法。MySQL 把「存取数据」这件事单独拆出来，做成可以替换的组件，所以同一个数据库里，不同的表可以用不同的引擎。

后文用到的术语：

- **事务**：一组操作要么全部成功，要么全部失败；
- **行锁**：只锁住正在修改的那一行，别的行不受影响；
- **表锁**：锁住整张表。

### 常见引擎：各管什么场景
- **InnoDB**：支持事务、行锁和外键，崩溃后能恢复数据。MySQL 5.5 起成为默认引擎，日常业务表基本都用它。
- **MyISAM**：不支持事务和外键，加锁以整张表为单位。较老的引擎，现在新项目很少选它。
- **Memory**：数据放在内存里，读写快，但服务重启后数据就没了，适合临时、可丢失的数据。

### 怎么指定和查看
建表时用 `ENGINE=` 指定；不写就用默认引擎。可以用 `SHOW ENGINES` 查看当前服务器支持哪些引擎。

## 示例
```sql
CREATE TABLE t_order (
    id BIGINT PRIMARY KEY,
    amount DECIMAL(10, 2)
) ENGINE = InnoDB;

SHOW ENGINES;
SHOW CREATE TABLE t_order;
```

## 易错点
- 以为存储引擎是整个数据库统一选一个；实际上可以按表分别指定
- 以为所有引擎都支持事务；MyISAM 和 Memory 都不支持
- 把重要数据放进 Memory 表，服务一重启数据就丢了

## 追问
### [f1] 为什么现在默认用 InnoDB？
因为它支持事务和行级锁，并发修改时互相影响小，崩溃后还能靠日志恢复。业务系统对数据可靠性的要求，基本都要用到这些能力。

### [f2] 怎么查看一张表用的是什么引擎？
执行 `SHOW CREATE TABLE 表名`，输出末尾的 `ENGINE=` 就是它的引擎。
