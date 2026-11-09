---
id: q_01M6XCBK2B3MZCHD8CR72SGV1H
title: 什么是 TypeHandler（类型处理器）？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
TypeHandler 是 MyBatis 里的类型转换器，负责 Java 类型和数据库 JDBC 类型之间的互相转换，常见类型已内置，也可以自定义。

## 要点
- [kp1|3] TypeHandler 负责 Java 类型与 JDBC 类型的双向转换
- [kp2|3] 写入时把 Java 值转成数据库参数，读取时反过来转回
- [kp3|2] MyBatis 已内置字符串、整数、日期等常见类型的处理器
- [kp4] 枚举、JSON 等特殊类型可自定义 TypeHandler

## 详解
### 先搞懂：数据库和 Java 说的不是同一种话
你的 `User` 类里有个 `status` 属性，类型是枚举 `ENABLED`。数据库里这一列存的是数字 `1`。存的时候要把枚举变成 1，读的时候要把 1 变回枚举。

这就像一个翻译：中文到英文、英文到中文，两个方向都要会。TypeHandler 就是这位翻译。

术语说明：

- **JDBC 类型**：数据库驱动那一侧的类型，如 `VARCHAR`、`INTEGER`；
- **Java 类型**：你代码里的类型，如 `String`、枚举、`Date`；
- **TypeHandler**：规定这两边怎么互相转换的组件。

### TypeHandler：两个方向各做一件事
- **写入方向**：执行 SQL 前，把 Java 参数设置到预编译语句里，也就是 Java 到 JDBC；
- **读取方向**：拿到结果集后，把列的值取出来转成 Java 对象的属性，也就是 JDBC 到 Java。

平时你没感觉到它，是因为 `String`、`Integer`、`Date` 这些常见类型，MyBatis 都内置了处理器，会自动选用。

### 什么时候需要自定义
- 枚举要按自己的规则存，比如存编号而不是名字；
- 把一个对象以 JSON 字符串的形式存进一列；
- 数据库有特殊类型，要特殊的读写方式。

自定义时，继承 `BaseTypeHandler`，实现几个方法，然后在配置里注册，或者在字段上指定使用。

## 示例
```java
public class StatusHandler extends BaseTypeHandler<Status> {
    @Override
    public void setNonNullParameter(PreparedStatement ps, int i,
                                    Status p, JdbcType t) throws SQLException {
        ps.setInt(i, p.getCode());
    }

    @Override
    public Status getNullableResult(ResultSet rs, String col) throws SQLException {
        return Status.of(rs.getInt(col));
    }
    // 其余按列序号、存储过程取值的方法略
}
```

## 易错点
- 以为 TypeHandler 只管读，其实写入参数时也要用它
- 自定义后忘了注册或在映射里指定，MyBatis 不会自动选用它
- 以为枚举必须自己写，MyBatis 默认就有按名字处理枚举的内置方式

## 追问
### [f1] 枚举默认怎么存？
默认按枚举名字符串存取。如果想存编号，可以换用 MyBatis 自带的按序号处理器，或者自己写 TypeHandler 按业务编码转换。
