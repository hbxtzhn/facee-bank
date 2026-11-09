---
id: q_01M6XCBSDJMX69N18GN808F9M2
title: 一级缓存什么时候会被清空？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [mybatis-cache, cache-consistency]
prerequisites: [q_01M6XCBS592QRJZ7Y4ZXRG0ZHA]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "MyBatis 3 源码：BaseExecutor（一级缓存的创建、缓存键与清空）", url: "https://github.com/mybatis/mybatis-3/blob/master/src/main/java/org/apache/ibatis/executor/BaseExecutor.java" }
  - { title: "MyBatis 3 文档：Mapper XML 文件（select / insert 的 flushCache 默认值）", url: "https://mybatis.org/mybatis-3/sqlmap-xml.html" }
---

## 一句话
同一个 Session 里只要执行了 insert、update、delete，一级缓存就整体清空；提交、回滚、关闭 Session 或手动 `clearCache` 也会清空。

## 要点
- [kp1|3] 同一 Session 里执行增删改，整个一级缓存被清空
- [kp2|3] Session 的提交、回滚、关闭或调用 `clearCache` 也会清空
- [kp3|2] 清空的是这个 Session 的全部缓存，不是只清相关的那条
- [kp4] 查询语句上设置 `flushCache="true"`，查询前也会清空

## 详解
### 先搞懂：为什么一定要清
你先查了用户 A，缓存里存着「A 的年龄是 20」。接着你把 A 的年龄改成 21。如果缓存不清，下一次再查 A，读到的还是 20，和数据库不一致。

可以把它想成便利贴：你贴了一张「库存 20」，之后库存变了，就得把旧便利贴撕掉，否则看的永远是旧数据。

后文用到的术语：
- **失效**：缓存里的内容不再被使用，下次查询重新访问数据库。

### 会清空的几种情况
- **增删改**：同一 Session 里执行了 insert、update、delete，不管改的是不是缓存里的那一行，整个缓存都清空。
- **提交和回滚**：事务提交或回滚时，缓存清空。
- **关闭 Session**：Session 关闭后缓存随之丢弃。
- **手动清空**：调用 `session.clearCache()`。
- **语句配置**：在 `<select>` 上写 `flushCache="true"`，这条查询执行前清空缓存。增删改默认就是 `flushCache="true"`。

### 为什么清整个缓存，而不是只清相关的
MyBatis 不解析 SQL 的内容，没法知道一次更新影响了哪些缓存项。最稳妥的做法就是全部清掉。代价是缓存命中率可能下降，换来的是不会读到本 Session 自己改前的旧数据。

### 清空只管本 Session
其他 Session 里的缓存不会被清。所以 Session A 缓存了数据，Session B 更新了数据库，A 的缓存仍然是旧的。这是一级缓存在多个 Session 之间的不一致风险。

## 示例
```java
User u1 = mapper.selectById(1L);   // 查库，放进缓存
User u2 = mapper.selectById(1L);   // 命中缓存，u1 == u2
mapper.updateName(2L, "new");      // 增删改，整个缓存清空
User u3 = mapper.selectById(1L);   // 重新查库
```

## 易错点
- 以为只清被修改的那一行；实际是整个 Session 的一级缓存全清
- 以为 Session 里改了数据，其他 Session 的缓存也会清；不会
- 以为查询语句不会清缓存；设置了 `flushCache="true"` 的查询会

## 追问
### [f1] 一级缓存会导致脏读吗？
同一个 Session 里自己的修改会清缓存，不会读到自己改前的值。但别的 Session 提交的修改，本 Session 的缓存感知不到，可能读到旧数据。
