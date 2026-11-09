---
id: q_01M6XBPFACYGCDRM70JPK6FW19
title: Mapper 对象的生命周期有多长，应该在哪里使用？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mybatis-internals, bean-lifecycle]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Mapper 是方法级的短命对象：它依附在 SqlSession 上，会话结束就不能再用，所以只在一次事务方法里取用。

## 要点
- [kp1|3] Mapper 接口的实例从 SqlSession 中获取，不是自己 new
- [kp2|3] Mapper 的生命周期跟着 SqlSession，会话关闭后它就失效
- [kp3|2] 应在一次事务方法内获取并使用，用完不要长期持有
- [kp4] 整合 Spring 后，注入的 Mapper 是代理，每次调用自动取会话

## 详解
### 先搞懂：Mapper 像是借来的办事窗口
你写过 `UserMapper.selectById(1)` 这样的调用，感觉它就是个普通对象。其实它背后借用了一条数据库会话。可以把会话想成银行柜台前的一次办事排号：

- 办事期间，窗口属于你，可以连续办几件事；
- 办完离开，窗口就还给银行，你手里的号作废；
- 拿着旧号再去窗口，办不成事。

术语先说清：

- **SqlSession**：MyBatis 与数据库打交道的一次会话，里面包着一个数据库连接。
- **Mapper**：你写的接口，MyBatis 会为它生成代理对象，调用接口方法就是执行对应 SQL。
- **事务方法**：一个方法里的多条 SQL 要么一起成功，要么一起回滚。

### Mapper：用时取、用完扔
纯 MyBatis 里，流程是这样的：

1. 打开一个 SqlSession；
2. 调用 `getMapper` 拿到 Mapper 代理；
3. 调用 Mapper 方法执行 SQL；
4. 提交或回滚，关闭 SqlSession。

Mapper 代理里持有的是第 1 步那个会话。会话一关，Mapper 就没法再安全使用了。所以它的生命周期和一次会话一样短，通常就是一个方法的范围。

SqlSession 本身也不是线程安全的，不能在多个线程之间共享。拿 Mapper 长期存成字段，等于偷偷共享了会话。

### 整合 Spring 之后
Spring 项目里，你直接 `@Autowired` 注入 Mapper，看起来像是单例长期持有。其实注入的是一个代理，每次调用方法时，它会按当前事务去取对应的 SqlSession。有事务就复用同一个会话，没有事务就用完即关。

所以写业务代码时，仍然把 Mapper 方法放在 Service 的事务方法里调用，这样同一事务内的多条 SQL 才在同一个会话里。

## 示例
```java
try (SqlSession session = sqlSessionFactory.openSession()) {
    UserMapper mapper = session.getMapper(UserMapper.class);
    User user = mapper.selectById(1L);
    mapper.updateName(1L, "new");
    session.commit();
} // 会话关闭后，mapper 不能再使用
```

## 易错点
- 把 Mapper 存成静态变量或长期字段，等于长期占用一个会话
- 以为 Spring 注入的 Mapper 是普通单例，其实它每次调用都会按事务取会话
- 在多个线程里共用同一个 SqlSession 拿到的 Mapper，会出现并发问题

## 追问
### [f1] SqlSession 线程安全吗？
不安全。每个线程应该有自己的 SqlSession，用完就关。Spring 整合时由 SqlSessionTemplate 按线程和事务来管理会话，业务代码不用操心。
