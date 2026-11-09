---
id: q_01M6XCBH1SQJDAYRZXZ0T62KGE
title: MyBatis 增删改为什么要提交事务？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [transaction-management, mybatis-internals]
prerequisites: [q_01M6XCBGG2THFPCV9HY7RH11DQ]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`openSession()` 默认不自动提交，增删改的结果只在当前事务里，必须调用 `commit()` 才会真正写进数据库。

## 要点
- [kp1|3] 默认关闭自动提交，增删改在事务中暂存
- [kp2|3] 调用 `session.commit()` 才会真正写入数据库
- [kp3|2] 不提交就关闭会话，改动会被回滚
- [kp4] 查询不改数据，不需要提交

## 详解
### 先搞懂：像编辑文档要点保存
做项目时，你可能遇到"代码执行成功了，数据库却没变化"。这像编辑文档：你改了很多内容，但没按保存就关掉了窗口，改动就丢了。事务提交就是那个保存按钮。

后文用到的词：

- **事务**：一组要么全部生效、要么全部取消的操作。
- **提交**：确认事务，让改动真正写入数据库。
- **回滚**：取消事务，撤销没提交的改动。

### 为什么默认不自动提交
通过无参 `openSession()` 创建的会话，默认关闭自动提交。这样几条相关的 SQL 可以放在同一个事务里，全部成功再一起提交，中途出错就整体回滚，保证数据一致。

### 怎么处理
- 手动调用 `session.commit()`；
- 或使用 `openSession(true)` 开启自动提交，每条语句立即生效，但失去了多条语句一起回滚的能力；
- 整合 Spring 后，由事务注解统一管理提交。

## 示例
```java
try (SqlSession session = factory.openSession()) {
    session.getMapper(UserMapper.class).insert(new User("Tom"));
    session.commit(); // 没有这一行，插入不会生效
}
```

## 易错点
- 以为没报错就一定保存成功；没提交的改动会被丢弃
- 全程开启自动提交，导致多条 SQL 无法整体回滚

## 追问
### [f1] 出错时怎么办？
抛出异常时不提交；关闭会话时未提交的改动会回滚。需要时也可以显式调用 `rollback()`。
