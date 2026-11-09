---
id: q_01M6XCBS592QRJZ7Y4ZXRG0ZHA
title: 什么是 MyBatis 的一级缓存？
type: concept
difficulty: easy
importance: 3
category: spring
tags: [mybatis-cache, mybatis-internals]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
references:
  - { title: "MyBatis 3 文档：配置（settings：localCacheScope）", url: "https://mybatis.org/mybatis-3/configuration.html" }
  - { title: "MyBatis 3 源码：BaseExecutor（一级缓存的创建、缓存键与清空）", url: "https://github.com/mybatis/mybatis-3/blob/master/src/main/java/org/apache/ibatis/executor/BaseExecutor.java" }
  - { title: "MyBatis-Spring 文档：Using an SqlSession（SqlSessionTemplate 与事务）", url: "https://mybatis.org/spring/sqlsession.html" }
---

## 一句话
一级缓存是 SqlSession 自带的本地缓存，默认开启，同一个 Session 里重复执行相同的查询，第二次直接取缓存，不再访问数据库。

## 要点
- [kp1|3] 一级缓存的作用范围是一个 SqlSession，默认开启
- [kp2|3] 同一 Session 里，相同的 SQL 和参数，第二次直接取缓存
- [kp3|2] 底层是 `PerpetualCache`，内部就是一个 `HashMap`
- [kp4] 不同的 SqlSession 之间缓存互相隔离

## 详解
### 先搞懂：同一个人问两遍，不用再翻一次档案
一次请求里，代码可能先后两次查同一个用户。如果两次都去数据库，就是白白多一次往返。一级缓存就是给这次「对话」配一个小本子：第一次查完记下来，第二次先翻本子。

后文用到的术语：
- **SqlSession**：一次和数据库的会话，MyBatis 用它来执行语句。
- **本地缓存**：只存在于当前 Session 的内存里，Session 结束就没了。

### 怎么命中
缓存的 key 由几个部分组成：语句 id、分页参数、最终的 SQL 文本、传入的参数值等。只有这些都相同，才算同一个查询。

命中时，直接返回缓存里的对象；没命中，就查数据库，再把结果放进缓存。

### 作用范围和隔离
缓存放在 SqlSession 里，所以：
- 同一个 Session 内重复查询，可以命中。
- 两个 Session 各有一份，互不可见。
- Session 关闭，缓存随之丢掉。

在 Spring 里，Mapper 的每次调用，如果没有外层事务，通常会各自开关一个 Session，所以一级缓存看起来「没生效」；有事务包住多次查询时，它们共用一个 Session，一级缓存才起作用。

### 进阶：范围可以调整（基础薄弱可先跳过）
设置项 `localCacheScope` 默认是 `SESSION`，改成 `STATEMENT` 后，缓存只在一条语句执行期间有效，相当于关闭一级缓存。

## 易错点
- 以为一级缓存跨请求有效；它只在同一个 SqlSession 里有效
- 以为 Spring 里每次查询都命中；没有事务时每次调用可能是新 Session
- 以为缓存里的对象是拷贝；命中时返回同一个对象，修改它会影响后续的命中结果

## 追问
### [f1] 两次查询之间有别人改了数据库，一级缓存还能读到新数据吗？
读不到。一级缓存不知道其他 Session 做了修改，只有本 Session 自己做了增删改，或手动清空，缓存才会失效。
