---
id: q_01M6XCBF5R5MGFW3R1NRVVSPJS
title: MyBatis 是怎么把 Java 对象的属性设置到 SQL 参数中的？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [sql-mapping, reflection]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
MyBatis 解析 SQL 里的 `#{属性名}`，用反射从参数对象里取出值，再通过 TypeHandler 设置到预编译语句的占位符上。

## 要点
- [kp1|3] SQL 中用 `#{属性名}` 表示参数，会被换成 `?` 占位符
- [kp2|3] 框架通过反射按属性名从参数对象取值
- [kp3|2] 取到的值由 TypeHandler 按类型设置到 `PreparedStatement`
- [kp4] `#{}` 走预编译，能防 SQL 注入

## 详解
### 先搞懂：像填快递单
做项目时，你只在 SQL 里写 `#{name}`，并没写设置参数的代码。这像填快递单：模板上留了空格（占位符），你给出一个人的资料，工作人员按"姓名""电话"这些字段名，把资料抄到对应空格里。

后文用到的词：

- **占位符**：SQL 中的 `?`，执行前再填入具体值。
- **反射**：程序运行时按名字读取对象属性的能力。
- **TypeHandler**：类型处理器，负责 Java 类型与数据库类型之间的转换。

### 参数是怎么填进去的
1. 解析 SQL：框架把 `#{name}` 换成 `?`，并记下这个位置对应的属性名；
2. 取值：按属性名，用反射从参数对象里读出值；
3. 设置：由对应类型的 `TypeHandler` 调用 `PreparedStatement` 的设置方法，如字符串用 `setString`。

### 为什么这样设计
这样你不用自己写 `ps.setString(1, ...)` 这类重复代码，也不用关心第几个问号对应哪个属性。因为走预编译，值不会被当成 SQL 的一部分，也就避免了注入。

## 示例
```xml
<insert id="insert" parameterType="com.example.User">
    INSERT INTO user(name, age) VALUES (#{name}, #{age})
</insert>
```

## 易错点
- 以为 `#{}` 是字符串拼接；它是预编译占位符
- 属性名写错，会报找不到对应的 getter

## 追问
### [f1] `#{}` 和 `${}` 有什么区别？
`#{}` 生成占位符，参数安全；`${}` 是直接把值拼进 SQL，有注入风险，只适合表名、排序列这类无法预编译的位置，且值要自己校验。
