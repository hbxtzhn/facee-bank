---
id: q_01M6XCBZ4XBG732PVGSXYJ72Y6
title: ParameterHandler 在 SQL 执行中做什么？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [mybatis-internals, sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 源码：DefaultParameterHandler.java", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/scripting/defaults/DefaultParameterHandler.java" }
  - { title: "MyBatis 3 文档：Configuration（objectFactory、plugins、jdbcTypeForNull）", url: "https://mybatis.org/mybatis-3/configuration.html" }
estimatedMinutes: 3
---

## 一句话
ParameterHandler 负责把你传入的参数值，一个个设置到预编译语句的问号上，转换工作由 TypeHandler 完成，把 Java 类型变成 JDBC 能识别的类型。

## 要点
- [kp1|3] `ParameterHandler` 为预编译 SQL 的每个问号设置参数值
- [kp2|3] 默认实现 `DefaultParameterHandler`，核心方法是 `setParameters`
- [kp3|2] 按 `BoundSql` 里的参数映射列表，依次取值再设置
- [kp4|2] 取到值后交给对应的 `TypeHandler` 做类型转换
- [kp5] 值为 null 时，有些数据库要指定 jdbcType

## 详解
### 先搞懂：往快递单的空格里填内容
SQL 预编译后长这样：`select * from user where name = ? and age = ?`。问号就是快递单上的空格。

`ParameterHandler` 的工作是按顺序把值填进去：第一个问号填名字，第二个问号填年龄。因为数据库不认识 Java 对象，所以填的时候还要做类型转换，比如 Java 的 `String` 变成数据库的字符串。

后文用到的词：

- **TypeHandler**：类型处理器，负责某个 Java 类型和 JDBC 类型之间的转换。
- **ParameterMapping**：描述一个问号对应哪个参数名、用哪个类型处理器。
- **parameterObject**：你调用 Mapper 方法时传的参数。

### 设置参数的过程
`DefaultParameterHandler.setParameters` 的流程：

1. 从 `BoundSql` 取出参数映射列表，每个元素对应一个问号。
2. 对每个问号，根据参数名取出值。取值的来源有几种：额外参数（比如 `foreach` 产生的临时变量）、参数对象本身（单个简单类型）、或者按属性名从对象或 Map 里取。
3. 找到这个参数对应的 `TypeHandler`。
4. 调用 `typeHandler.setParameter`，把值设置到 `PreparedStatement` 的对应位置。

### TypeHandler 做了什么
`TypeHandler` 内部其实就是调用 JDBC 的 `setString`、`setInt` 这类方法。

MyBatis 内置了常见类型的处理器。你有特殊需求，比如把枚举存成数字、把对象存成 JSON，可以自己写 `TypeHandler` 并注册。

选哪个处理器，由参数的 Java 类型和你在 `#{}` 里指定的 `typeHandler` 或 `jdbcType` 决定。

### 为什么要这样设计
参数设置交给专门的对象，和执行、结果映射分开，职责清楚。

扩展也方便：新增一种类型的转换，只要增加一个 `TypeHandler`，不用改主流程。

### 关于 null 值
参数为 null 时，部分数据库驱动不知道该设置成什么类型，会报错。这时可以在 `#{}` 里写 `jdbcType`，或在全局设置里配置 null 对应的 jdbcType。

## 示例
```xml
<!-- 参数为 null 时，指定 jdbcType 帮助驱动判断类型 -->
<insert id="insertUser">
    insert into user(name, age)
    values (#{name}, #{age, jdbcType=INTEGER})
</insert>
```

```java
// 自定义 TypeHandler 的骨架：把 Java 对象转成 JSON 字符串存库
public class JsonTypeHandler extends BaseTypeHandler<Object> {
    @Override
    public void setNonNullParameter(PreparedStatement ps, int i, Object p, JdbcType t)
            throws SQLException {
        ps.setString(i, toJson(p));
    }
    // 省略其余需要实现的读取方法
}
```

## 易错点
- 以为 ParameterHandler 负责生成 SQL；实际它只设置参数值，SQL 文本在前面已经生成
- 参数是 null 且没指定类型，部分数据库报错
- 以为 `#{}` 是字符串拼接；实际它被替换成问号，值是由这里设置的

## 追问
### [f1] `#{}` 和 `${}` 在这一步有什么区别？
`#{}` 在 SQL 里变成问号，由 `ParameterHandler` 设置值，不会注入。`${}` 在生成 SQL 时就拼成文本，根本不经过这一步。

### [f2] 多个参数时参数名是怎么对应的？
Mapper 方法里用 `@Param` 指定名字最清晰，MyBatis 会把多个参数包装成 Map，之后按名字取值。
