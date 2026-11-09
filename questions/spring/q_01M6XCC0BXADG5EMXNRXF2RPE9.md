---
id: q_01M6XCC0BXADG5EMXNRXF2RPE9
title: MapperMethod 为什么采用命令模式，它做什么？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [mybatis-internals, design-pattern]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
MapperMethod 把一次 Mapper 方法调用封装成对象，里面记着方法签名和 SQL 命令类型，再统一交给 SqlSession 执行，这种做法常被归为命令模式。

## 要点
- [kp1|3] `MapperMethod` 封装了一次 Mapper 方法调用需要的信息
- [kp2|3] 内部有 `SqlCommand`（语句 ID 和命令类型）和 `MethodSignature`（方法签名）
- [kp3|2] 命令类型有 SELECT、INSERT、UPDATE、DELETE、FLUSH
- [kp4|2] `execute` 按命令类型分发给 `SqlSession` 的方法
- [kp5] 命令对象可以缓存复用，调用方不关心执行细节

## 详解
### 先搞懂：点菜单就是一份“命令”
你在餐厅点菜，服务员把你的需求写在一张菜单上交给后厨。菜单把“要什么、怎么做”记录下来，后厨照着做，不用关心是谁点的。

命令模式的想法就是：**把“要做的事”写成一个对象**，谁来执行、什么时候执行，可以分开处理。

后文用到的词：

- **命令模式**：把一个请求封装成对象，让发出请求的一方和执行请求的一方解耦。
- **SqlCommand**：记录这条 SQL 的 ID 和命令类型。
- **MethodSignature**：记录方法的返回类型、参数信息。

### MapperMethod 里装了什么
创建 `MapperMethod` 时，要传入 Mapper 接口、方法和 `Configuration`。它内部会组装两样东西：

- **SqlCommand**：包含 SQL 的全名（接口全名加方法名）和命令类型。命令类型来自 XML 标签或注解：`<select>` 是 SELECT，`<insert>` 是 INSERT，以此类推。
- **MethodSignature**：分析方法的返回类型是列表、单个对象、Map 还是游标，以及参数里有没有特殊的 `RowBounds` 或 `ResultHandler`。

这两样合起来，就是“要做什么”的完整描述。

### 怎么执行
执行时调用 `execute(sqlSession, args)`，它的逻辑是：

1. 看 `SqlCommand` 的命令类型；
2. INSERT、UPDATE、DELETE 分别调用 `SqlSession` 的 `insert`、`update`、`delete`；
3. SELECT 再根据 `MethodSignature` 的返回类型选择 `selectList`、`selectOne` 等；
4. FLUSH 调用 `flushStatements`。

所有 SQL 类型都走同一个入口，由 `SqlSession` 统一执行。

### 为什么这样设计
- **调用方只管发命令**：`MapperProxy` 不需要知道每种 SQL 怎么执行，只要创建或取出 `MapperMethod`，调用 `execute`。
- **新增类型好扩展**：以后加一种命令类型，在 `execute` 里加一个分支。
- **方便缓存**：命令对象创建一次，反复使用，每次只传不同的参数。

需要说明的是，它和教科书中的命令模式不完全一样：这里没有一排独立的命令类，而是一个类内部按类型分支。说它“采用命令模式”，指的是把调用封装成对象这一核心思想。

## 示例
```java
// MapperProxy 内部的使用方式（示意）
MapperMethod mapperMethod = new MapperMethod(mapperInterface, method, configuration);
Object result = mapperMethod.execute(sqlSession, args); // 统一入口，内部按命令类型分发
```

## 易错点
- 以为 MapperMethod 自己执行 SQL；实际它只分发，执行由 SqlSession 完成
- 以为命令类型是从方法名推断的；实际来自 XML 标签或注解
- 把它和教科书的命令模式完全等同；这里是简化的实现

## 追问
### [f1] 命令模式一般解决什么问题？
让发出请求的一方不依赖具体的执行者。典型例子有任务队列、撤销重做、事务日志。

### [f2] MapperMethod 为什么要缓存？
创建时要分析方法签名和查找配置，开销较大。缓存后每个方法只做一次，之后直接复用。
