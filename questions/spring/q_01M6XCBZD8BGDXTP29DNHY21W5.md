---
id: q_01M6XCBZD8BGDXTP29DNHY21W5
title: ResultSetHandler 在 SQL 执行中做什么？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [mybatis-internals, sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 源码：DefaultResultSetHandler.java", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/executor/resultset/DefaultResultSetHandler.java" }
  - { title: "MyBatis 3 文档：Configuration（objectFactory、plugins、jdbcTypeForNull）", url: "https://mybatis.org/mybatis-3/configuration.html" }
estimatedMinutes: 3
---

## 一句话
ResultSetHandler 负责把数据库返回的结果集逐行读出来，用 TypeHandler 转换字段类型、用 ObjectFactory 创建对象，最后包装成你要的 Java 对象返回。

## 要点
- [kp1|3] `ResultSetHandler` 把 JDBC 的 `ResultSet` 转成 Java 对象
- [kp2|3] 默认实现 `DefaultResultSetHandler`，核心方法是 `handleResultSets`
- [kp3|2] 每个字段的值由 `TypeHandler` 从结果集中读出并转换类型
- [kp4|2] 对象实例由 `ObjectFactory` 创建，再逐个字段填值
- [kp5] 查询结果统一以 List 形式返回，单个对象再取第一个

## 详解
### 先搞懂：把快递拆开，按清单摆好
数据库返回的是一张表格，每行有若干列。你的程序要的是 `User` 对象。

`ResultSetHandler` 就像拆快递的人：一行一行读表格，每读一行就新建一个 `User`，把每一列的值填到对应属性里，最后把一堆 `User` 摆成清单交给你。

后文用到的词：

- **ResultSet**：JDBC 返回的结果集，像一张可以逐行往下读的表格。
- **TypeHandler**：类型处理器，把数据库列的值转成 Java 类型。
- **ObjectFactory**：对象工厂，负责创建结果对象的实例。

### 处理流程
`StatementHandler` 执行完查询后，把 `Statement` 交给 `ResultSetHandler.handleResultSets`。接着：

1. **取出结果集**：从 `Statement` 里拿到 `ResultSet`，包装一下方便读取。
2. **找映射规则**：根据 `resultType` 或 `resultMap`，知道列和属性的对应关系。
3. **逐行处理**：对结果集里的每一行：
   - 用 `ObjectFactory` 创建目标对象，一般是调用无参构造器；
   - 对每个要映射的列，用对应的 `TypeHandler` 读出值；
   - 用反射把值设置到对象的属性上。
4. **收集结果**：把每行得到的对象放进列表。
5. **返回**：查询一个对象时，外层会取列表中的第一个；返回列表就直接给列表。

### 自动映射和手动映射
- **手动映射**：在 `resultMap` 里写清每列对应哪个属性，包括关联查询用的 `association` 和 `collection`。
- **自动映射**：没有指定时，MyBatis 按列名和属性名自动匹配。是否开启驼峰转换等，由设置项控制。

### 为什么这样设计
读取的类型转换、对象创建、结果收集各自独立：想换对象创建方式，自定义 `ObjectFactory`；想特殊处理某列，自定义 `TypeHandler`。主流程不用改。

### 还有哪些结果处理
除了普通结果集，它还处理存储过程的输出参数，以及用 `Cursor` 返回的游标式结果，一行一行读，不必一次装入内存。

## 示例
```xml
<!-- 列名和属性名不一致时，用 resultMap 指定对应关系 -->
<resultMap id="userMap" type="User">
    <id column="id" property="id"/>
    <result column="user_name" property="name"/>
</resultMap>

<select id="findAll" resultMap="userMap">
    select id, user_name from user
</select>
```

## 易错点
- 列名和属性名不一致，又没配映射，对应属性会是 null
- 以为查询单个对象就是只读一行；实际仍按列表处理，多于一行时会抛出异常
- 实体类没有无参构造器，又没有提供对应的构造方式，创建对象失败

## 追问
### [f1] 查询返回多行但方法声明返回单个对象会怎样？
MyBatis 会抛出 `TooManyResultsException`。返回单个对象要求结果最多一行。

### [f2] 想把某列特殊处理，怎么做？
自定义一个 `TypeHandler` 并在映射里指定，或注册为全局处理器。读取时就按你的规则转换。
