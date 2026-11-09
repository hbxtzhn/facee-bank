---
id: q_01M6XCBH9V2HGVY0DB4Y56NSXP
title: SqlSession 用完为什么要关闭？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mybatis-internals, orm]
prerequisites: [q_01M6XCBGG2THFPCV9HY7RH11DQ]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`SqlSession` 持有数据库连接等资源，用完调用 `close()` 才会释放，不关闭就会造成连接泄漏。

## 要点
- [kp1|3] `SqlSession` 占用着数据库连接等资源
- [kp2|3] 调用 `close()` 释放资源，连接才能归还
- [kp3|2] 不关闭会导致连接泄漏，连接池最终耗尽
- [kp4] 推荐用 try-with-resources 自动关闭

## 详解
### 先搞懂：借了东西要还
做项目时，有时服务跑了一阵就报"拿不到连接"。这像图书馆借书：每个人借了不还，书很快就借光，后面的人无书可借。`SqlSession` 借走一个连接，`close()` 就是还书。

后文用到的词：

- **连接泄漏**：连接用完没有归还，一直被占着。
- **try-with-resources**：Java 语法，代码块结束时自动调用 `close()`。

### 不关闭会怎样
1. 连接一直被某个会话占着，池子里能用的越来越少；
2. 空闲连接用完后，新请求只能等待；
3. 最终等待超时报错，整个服务像卡住一样；
4. 数据库端的连接数也可能被占满。

### 怎么保证关闭
- 用 try-with-resources，即使中途抛异常也会关闭；
- 或者在 `finally` 里调用 `close()`；
- 整合 Spring 后，由框架负责关闭。

## 示例
```java
try (SqlSession session = factory.openSession()) {
    // 使用 session
} // 离开代码块时自动 close()
```

## 易错点
- 只在正常流程里关闭，异常路径漏掉
- 以为关闭会话会断开物理连接；使用连接池时只是归还

## 追问
### [f1] 关闭前没有提交的改动怎么处理？
会被回滚，所以增删改要先 `commit()` 再关闭。
