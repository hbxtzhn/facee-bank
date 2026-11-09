---
id: q_01M6XCBJ1YNEQMS9SQBE4YZFD7
title: SqlSession 是做什么的？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mybatis-internals]
prerequisites: [q_01M6XCBGG2THFPCV9HY7RH11DQ]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`SqlSession` 代表程序与数据库之间的一次会话，可以执行 SQL、获取 Mapper、提交和关闭，但它不是线程安全的，不能共享。

## 要点
- [kp1|3] 代表一次与数据库的会话，是执行 SQL 的入口
- [kp2|3] 非线程安全，不能在多个线程间共享
- [kp3|2] 请求或方法级生命周期，每次请求创建新的
- [kp4] 提供 `selectOne`、`getMapper`、`commit`、`close` 等方法

## 详解
### 先搞懂：像一次通话
做项目时，每个请求要和数据库说上几句话。这像打电话：一通电话属于一个人，别人不能插进来用同一通电话，否则内容就乱了。通话结束要挂断。`SqlSession` 就是这样一通电话。

后文用到的词：

- **会话**：一段连续的、与数据库交互的过程。
- **线程安全**：多个线程同时使用，不会出错。

### 它能做什么
- 执行 SQL：`selectOne`、`selectList`、`insert`、`update`、`delete`；
- 获取 Mapper：`getMapper`；
- 提交或回滚事务：`commit`、`rollback`；
- 关闭会话：`close`。

### 为什么不能共享
会话内部有事务状态，还持有一个数据库连接。多个线程共用时，事务会互相干扰，操作也可能乱序。所以每个请求或每个方法里创建自己的会话，用完关闭。

不要把它放在类的成员变量里，也不要放进静态变量。

## 示例
```java
public User find(long id) {
    try (SqlSession session = factory.openSession()) {
        return session.getMapper(UserMapper.class).findById(id);
    }
}
```

## 易错点
- 把会话放在静态变量里被多线程共用
- 以为会话和工厂一样可以长期共享

## 追问
### [f1] 与 Spring 整合后，会话还是线程不安全的吗？
整合后注入的是线程安全的代理，每次调用会按当前事务获取属于自己的会话，所以可以放心注入共用。
