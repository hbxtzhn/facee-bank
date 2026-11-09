---
id: q_01M6XCC0W5DCXH3780S1M7T5SD
title: MyBatis 怎么调用存储过程？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
在 `<select>` 或 `<update>` 标签上设置 `statementType="CALLABLE"`，用 `{call 存储过程名(...)}` 调用，参数用 `mode` 标明是 IN 还是 OUT。

## 要点
- [kp1|3] 标签上写 `statementType="CALLABLE"`，MyBatis 才会按存储过程方式执行
- [kp2|3] SQL 写成 `{call 过程名(参数...)}` 的形式
- [kp3|2] 参数用 `mode=IN`、`OUT`、`INOUT` 区分输入和输出
- [kp4] OUT 参数的值会被写回传入的参数对象或 Map

## 详解
### 先搞懂：存储过程是什么
**存储过程**是提前写好、存在数据库里的一段 SQL 程序。比如数据库里有个过程叫 `count_user`，你给它一个状态，它算出用户数再还给你。

调用它就像打电话给数据库里的一个“函数”：有的值你传进去，有的值它传回来。

- **IN**：只从 Java 传给数据库的参数。
- **OUT**：由存储过程算出来、传回 Java 的参数。
- **INOUT**：既传进去，又被改写后传回来。

### 调用方式：CALLABLE 加 call 语法
普通语句 MyBatis 用 `PreparedStatement` 执行。调用存储过程要换成 `CallableStatement`，所以要在标签上写 `statementType="CALLABLE"`。

SQL 部分用 JDBC 的标准写法：`{call 过程名(?, ?)}`，在 MyBatis 里把 `?` 换成 `#{}` 即可。

### 参数：用 mode 说明方向
每个 `#{}` 里可以写 `mode`，不写默认是 IN。OUT 和 INOUT 参数建议同时写 `jdbcType`，因为数据库要知道返回值是什么类型。

调用结束后，OUT 参数的值会写回你传入的对象。传入的如果是 `Map`，就从 Map 里按名字取；如果是 Java 对象，就从对应属性取。

如果存储过程本身还返回了结果集，仍然按 `resultType` 或 `resultMap` 映射。

## 示例
```xml
<select id="countUser" statementType="CALLABLE" parameterType="map">
    {call count_user(
        #{status, mode=IN,  jdbcType=INTEGER},
        #{total,  mode=OUT, jdbcType=INTEGER})}
</select>
```

```java
Map<String, Object> param = new HashMap<>();
param.put("status", 1);
userMapper.countUser(param);
Integer total = (Integer) param.get("total"); // OUT 参数被写回 Map
```

## 易错点
- 忘了写 `statementType="CALLABLE"`，会按普通语句执行，调用会失败
- 以为 OUT 参数会作为方法返回值；实际是写回参数对象，要从参数里取
- OUT 参数不写 `jdbcType`，部分数据库会报类型错误

## 追问
### [f1] 存储过程在项目里好用吗？
它能减少网络往返，但逻辑藏在数据库里，不方便版本管理和调试，迁移数据库也麻烦。多数互联网项目把逻辑放在 Java 代码里，只在历史系统或批量计算时才用存储过程。
