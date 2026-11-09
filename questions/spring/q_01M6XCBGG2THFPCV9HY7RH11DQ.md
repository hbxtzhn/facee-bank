---
id: q_01M6XCBGG2THFPCV9HY7RH11DQ
title: MyBatis 的基本使用步骤是什么？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mybatis-internals]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
MyBatis 的使用分五步：创建 `SqlSessionFactory`，获取 `SqlSession`，执行 SQL 或获取 Mapper，增删改后提交事务，最后关闭会话。

## 要点
- [kp1|3] 先读配置创建 `SqlSessionFactory`
- [kp2|3] 从工厂获取 `SqlSession`，再执行 SQL 或获取 Mapper
- [kp3|2] 增删改之后要调用 `commit()` 提交事务
- [kp4|2] 最后一定要关闭 `SqlSession`
- [kp5] 与 Spring 整合后，这些步骤由框架代劳

## 详解
### 先搞懂：像去银行办业务
做项目时，你可能只写过 `mapper.findById(1)`。这像去银行办业务：先有营业厅（工厂），进门取号（拿会话），办理业务（执行 SQL），重要业务要签字确认（提交），办完离开让窗口空出来（关闭）。

后文用到的词：

- **SqlSessionFactory**：生产会话的工厂，由配置文件构建。
- **SqlSession**：一次和数据库交互的会话。
- **Mapper**：Mapper 接口，通过它调用 SQL。

### 五步的顺序
1. 读取配置文件，创建 `SqlSessionFactory`；
2. 调用 `openSession()` 创建 `SqlSession`；
3. 用 `selectOne` 等方法直接执行 SQL，或用 `getMapper` 取得接口；
4. 增删改后调用 `commit()`；
5. 调用 `close()` 关闭会话。

### 为什么这样分层
工厂创建代价高，整个应用只建一次；会话轻量但不线程安全，每次请求用完就关。提交和关闭是资源与数据一致性的需要，下面几题会逐个讲。

## 示例
```java
try (SqlSession session = factory.openSession()) {
    UserMapper mapper = session.getMapper(UserMapper.class);
    mapper.insert(new User("Tom"));
    session.commit();
}
```

## 易错点
- 增删改后忘了 `commit()`，数据没有真正保存
- 用完不关闭会话，造成连接泄漏

## 追问
### [f1] 和 Spring 整合后还需要自己写这些步骤吗？
不需要。Spring 管理工厂和会话，事务由 Spring 的事务管理统一提交和回滚。
