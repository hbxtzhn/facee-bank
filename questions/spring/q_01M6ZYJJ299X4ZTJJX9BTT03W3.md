---
id: q_01M6ZYJJ299X4ZTJJX9BTT03W3
title: 调用 Mapper 方法时，MapperProxy 是怎么一步步执行到 SQL 的？
type: concept
difficulty: hard
importance: 2
category: spring
tags: [mybatis-internals, dynamic-proxy]
prerequisites: [q_01M6XCBZY1WK6GVWPKRHFZH7S3]
appliesTo: ["MyBatis >= 3.5"]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 源码：MapperProxy.java", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/binding/MapperProxy.java" }
  - { title: "MyBatis 源码：MapperMethod.java", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/binding/MapperMethod.java" }
  - { title: "MyBatis 源码：MapperProxyFactory.java", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/binding/MapperProxyFactory.java" }
estimatedMinutes: 5
---

## 一句话
调用 Mapper 方法会进入 MapperProxy 的 invoke，它取出或新建缓存的 MapperMethod 并调用 execute。execute 按 SQL 命令类型选择 SqlSession 的方法去执行。

## 要点
- [kp1|3] 方法调用先进 `MapperProxy.invoke`，`Object` 和 default 方法在这里直接处理
- [kp2|3] 其余方法取出缓存的 `MapperMethod`，没有就新建并放入缓存
- [kp3|2] `MapperMethod.execute` 按命令类型走 INSERT、UPDATE、DELETE、SELECT 分支
- [kp4|2] 分支内转换参数后调用 `SqlSession` 的对应方法，再交给 `Executor`
- [kp5] `MapperMethod` 缓存按方法保存，避免每次重复解析方法签名

## 详解
### 先搞懂：点菜单到出菜的完整路线
你在餐厅点了一道“宫保鸡丁”，服务员接单后要先查这道菜属于凉菜还是热菜，再把单子递给对应的窗口。同一道菜以后再点，不用重新查，直接用上次的记录。

Mapper 方法调用也是这样：代理接单，查出这个方法对应的 SQL 类型，转交给 `SqlSession`；这次查的结果缓存起来，下次直接用。

后文用到的词：

- **MapperProxy**：Mapper 接口的代理对象，实现了 `InvocationHandler`。
- **MapperMethod**：把一个 Mapper 方法的 SQL 信息和方法签名包装起来的对象。
- **SqlCommand**：`MapperMethod` 里记录 SQL 的 ID 和命令类型的对象。

### 第一步：进入 invoke
调用 `userMapper.findById(1)` 时，JDK 代理把调用转给 `MapperProxy.invoke`。

这里先做分流：

- 如果是 `Object` 类的方法，比如 `toString`，直接在代理上调用；
- 如果是接口的 default 方法，调用它自己的默认实现；
- 其余的，才是真正要执行 SQL 的 Mapper 方法。

### 第二步：取出或创建 MapperMethod
对真正的 Mapper 方法，`invoke` 会从一个按 `Method` 为 key 的缓存里找 `MapperMethod`。

- 找到了，直接用；
- 没找到，新建一个 `MapperMethod` 并放进缓存。

新建时，会解析接口全名加方法名，得到 SQL 的 ID。再从 `Configuration` 里查出命令类型。同时分析方法的参数和返回值类型。

缓存的目的是：解析只做一次，以后每次调用都复用。早期版本里这个步骤叫 `cachedMapperMethod`，较新的版本改成 `cachedInvoker`，思路一样。

### 第三步：调用 execute
`MapperMethod.execute(sqlSession, args)` 根据命令类型走不同分支：

- **INSERT、UPDATE、DELETE**：先把方法参数转换成传给 SQL 的参数对象。再调用 `sqlSession.insert`、`update` 或 `delete`。最后把返回的影响行数转换成方法声明的返回类型。
- **SELECT**：按方法的返回类型决定调用 `selectList`、`selectOne`、`selectMap` 或 `selectCursor`。
- **FLUSH**：调用 `flushStatements`。

### 第四步：交给 SqlSession 和 Executor
`SqlSession` 再根据 SQL 的 ID 取出 `MappedStatement`，调用 `Executor`。后面就是 `StatementHandler` 预编译、`ParameterHandler` 设置参数、执行、`ResultSetHandler` 封装结果。

### 完整链路
```text
Mapper 方法 → MapperProxy.invoke → MapperMethod.execute
→ SqlSession.selectOne / insert ... → Executor → StatementHandler → 数据库
```

### 进阶：为什么要缓存 MapperMethod（基础薄弱可先跳过）
创建 `MapperMethod` 要反射分析方法的返回类型、参数名等，开销不小。每个 Mapper 方法只创建一次，之后通过 `ConcurrentHashMap` 取用，也是线程安全的。

## 示例
```java
// 接口方法
User findById(Long id);

// 调用时发生的事（示意）
// 1. userMapper.findById(1L) 进入 MapperProxy.invoke
// 2. 取到或创建该方法的 MapperMethod
// 3. MapperMethod.execute 发现命令类型是 SELECT，返回类型是单个对象
// 4. 转换参数后调用 sqlSession.selectOne("com.example.UserMapper.findById", 1L)
```

## 易错点
- 以为每次调用都会重新解析一遍方法签名；实际有缓存
- 以为 Mapper 的 toString、hashCode 也会去执行 SQL；实际在代理里直接处理
- 以为 MapperProxy 自己执行 SQL；实际它只转交，执行在 SqlSession 和 Executor 里

## 追问
### [f1] 多个参数是怎么传给 SQL 的？
`MapperMethod` 会用参数名解析器把多个参数整理成一个 Map，用 `@Param` 指定的名字或 `param1`、`param2` 这样的默认名作为 key。单个简单参数则直接传。

### [f2] 为什么 SELECT 要看返回类型？
因为同样是查询，返回列表、单个对象、Map、游标时，需要调用 `SqlSession` 不同的方法，结果的封装方式也不一样。
