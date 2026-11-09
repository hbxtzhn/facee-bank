---
id: q_01M6XCBXCBRGX36RJVRGVR98ES
title: 怎么用 PageHelper 实现分页查询？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [pagination, interceptor]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
引入 PageHelper 后，在查询前调用 PageHelper.startPage 指定页码和每页条数，紧跟着的那条查询就会被插件自动改写成分页 SQL。

## 要点
- [kp1|3] 先引入 PageHelper 依赖，Spring Boot 项目用对应的 starter
- [kp2|3] 查询前调用 `PageHelper.startPage(页码, 每页条数)`
- [kp3|2] `startPage` 之后紧跟的第一条查询才会分页
- [kp4|2] 用 `PageInfo` 包装结果，可以拿到总数和总页数
- [kp5] 页码从 1 开始，不是从 0 开始

## 详解
### 先搞懂：先挂个“分页牌子”，再查询
网页上的列表要分页：用户选了第 2 页，每页 10 条。你不想在每个 SQL 里手写 `limit`。

PageHelper 的做法像是在门口先挂一块牌子：“下一位客人只要第 2 页，每页 10 条”。接着你正常调用查询，插件看到牌子，就自动改写 SQL。

后文用到的词：

- **PageHelper**：流行的 MyBatis 分页插件。
- **startPage**：挂牌子的方法，告诉插件页码和每页条数。
- **PageInfo**：分页结果的包装类，带总数、总页数等信息。

### 使用步骤
1. **引入依赖**：Maven 里加入 PageHelper，Spring Boot 项目通常用它提供的 starter，基本不用另外配置。
2. **调用 startPage**：在查询之前执行 `PageHelper.startPage(2, 10)`，表示第 2 页，每页 10 条。
3. **正常调用 Mapper**：Mapper 里仍然是普通的 `select`，不用写 `limit`。
4. **取结果**：返回的列表就是当前页数据。把它交给 `new PageInfo<>(list)`，可以得到总条数、总页数、当前页码等。

插件在执行时，会先自动补一条统计总数的查询，再执行分页查询。所以你一次调用，就能拿到总数。

### 为什么必须紧跟查询
`startPage` 把页码信息存在当前线程里，只有下一条查询会用到它，用完就清掉。

所以 `startPage` 和查询之间不要插入别的查询，否则分页会被前一条查询“抢走”。

如果调用了 `startPage` 却没有紧跟查询，这个设置会留在线程里，线程被复用时，可能影响后面不相关的查询。所以要保证两行代码连在一起。

## 示例
```java
// Service 方法：查询第 2 页，每页 10 条
public PageInfo<User> listUsers() {
    PageHelper.startPage(2, 10);          // 页码从 1 开始
    List<User> list = userMapper.selectAll(); // 紧跟着的查询会被分页
    return new PageInfo<>(list);          // 包含总数、总页数等信息
}
```

## 易错点
- `startPage` 和查询之间夹了别的查询，分页作用到了错误的 SQL 上
- 页码从 0 开始传，实际页码是从 1 开始计
- 调用了 `startPage` 却不执行查询，设置残留在线程中

## 追问
### [f1] 拿总条数是额外写 SQL 吗？
不用。插件会在分页查询前自动补一条统计总数的查询，结果放进 `PageInfo`。如果不需要总数，可以选择关闭统计，减少一次查询。

### [f2] 传不同数据库要改代码吗？
不用。插件会根据数据库类型选择方言，生成对应的分页语法，业务代码不变。
