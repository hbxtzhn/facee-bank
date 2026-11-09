---
id: q_01M6XBPCHDVPZ4HJFBP6PX6QC6
title: Spring 事务的 isolation 属性和数据库的隔离级别是什么关系？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [transaction-management, isolation-mvcc]
prerequisites: [q_01M6XCCT8E7EYYHFMN310PDB3W]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
references:
  - { title: "Spring Framework 参考文档：Transaction Propagation（REQUIRED 加入外层事务时忽略本地隔离级别）", url: "https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html" }
  - { title: "MySQL 8.4 手册：InnoDB Transaction Isolation Levels", url: "https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html" }
  - { title: "Oracle Database 19c Concepts：Data Concurrency and Consistency（隔离级别）", url: "https://docs.oracle.com/en/database/oracle/oracle-database/19/cncpt/data-concurrency-and-consistency.html" }
---

## 一句话
Spring 的 isolation 只是向数据库“申请”一个隔离级别，真正的隔离效果由数据库实现；默认值 DEFAULT 表示直接用数据库自己的默认级别。

## 要点
- [kp1|3] isolation 取值对应数据库四种隔离级别，Spring 在开启事务时通过连接设置给数据库
- [kp2|3] 默认 DEFAULT 用数据库默认级别：MySQL 可重复读，Oracle 读已提交
- [kp3|2] 隔离效果由数据库保证，数据库不支持的级别可能不生效或被替换
- [kp4|2] 只在事务开始时设置；加入已有事务时，通常沿用外层事务的级别

## 详解
### 先搞懂：Spring 只是传话的
隔离级别决定“一个事务能不能看到别的事务还没提交或刚提交的修改”，这是数据库的能力。Spring 本身不实现隔离，它像是点菜的服务员：你在 `@Transactional(isolation = ...)` 里写要几成熟，服务员把需求告诉厨房（数据库），能不能做到，是厨房说了算。

后文用到的术语：
- **隔离级别**：事务之间互相看到对方修改的程度，从弱到强：读未提交、读已提交、可重复读、串行化。
- **脏读**：读到别的事务还没提交的修改。
- **ISOLATION_DEFAULT**：不指定，用数据库默认。

### 方案对比：Spring 取值和数据库级别的对应
| Spring 取值 | 对应的数据库隔离级别 |
|---|---|
| `DEFAULT` | 使用数据库默认级别 |
| `READ_UNCOMMITTED` | 读未提交 |
| `READ_COMMITTED` | 读已提交 |
| `REPEATABLE_READ` | 可重复读 |
| `SERIALIZABLE` | 串行化 |

结论：想用数据库默认的就别写；确实需要不同级别，再显式指定，同时确认所用数据库支持它。

### Spring 具体怎么传达
开启事务时，如果设置了非默认的隔离级别，Spring 在拿到连接后，通过 JDBC 把这个连接的隔离级别设为指定值；事务结束后，会把连接恢复成原来的级别，避免影响到连接池里别的使用者。

### 几个容易忽略的限制
1. **数据库支持情况**：不同数据库支持的级别不同，比如 Oracle 主要支持读已提交和串行化，不是四种都有。写了数据库不支持的级别，结果取决于数据库和驱动，需要查阅对应数据库文档。
2. **只在新事务开始时生效**：方法加入外层已有事务（默认 REQUIRED）时，隔离级别沿用外层事务的，内层写了别的值通常不起作用。
3. **和数据库实现有关**：同样叫可重复读，不同数据库在幻读等细节上的表现可能不同。

## 示例
```java
// 不写 isolation，使用数据库默认级别
@Transactional
public void a() { /* ... */ }

// 显式要求读已提交
@Transactional(isolation = Isolation.READ_COMMITTED)
public void b() { /* ... */ }
```

## 易错点
- 以为 Spring 自己实现了隔离，和数据库无关；它只负责设置
- 以为在内层方法写了更高的隔离级别，就能抬高整个事务的级别；加入已有事务时通常不生效
- 以为各个数据库的默认级别都一样；MySQL InnoDB 默认可重复读，Oracle 默认读已提交

## 追问
### [f1] 不写 isolation，用的是什么级别？
用数据库的默认级别：MySQL InnoDB 是可重复读，Oracle 是读已提交。

### [f2] 为什么内层方法设置的隔离级别可能没用？
隔离级别是整个事务的属性，在开启事务时设置。内层方法加入的是已经开启的事务，Spring 一般不会再去修改它。
