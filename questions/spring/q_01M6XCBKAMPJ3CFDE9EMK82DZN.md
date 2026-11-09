---
id: q_01M6XCBKAMPJ3CFDE9EMK82DZN
title: TypeHandler 的 setParameter 和 getResult 分别做什么？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [sql-mapping]
prerequisites: [q_01M6XCBK2B3MZCHD8CR72SGV1H]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 3 文档：配置 - typeHandlers（BaseTypeHandler 与自定义示例）", url: "https://mybatis.org/mybatis-3/configuration.html#typeHandlers" }
estimatedMinutes: 3
---

## 一句话
setParameter 管“存”：把 Java 值转成 JDBC 参数设进 SQL；getResult 管“取”：把结果集里的值转成 Java 类型。

## 要点
- [kp1|3] `setParameter` 在执行 SQL 前，把 Java 值设置为预编译语句的参数
- [kp2|3] `getResult` 在读取结果时，把结果集里的值转成 Java 类型
- [kp3|2] 继承 `BaseTypeHandler` 时，实际要实现 `setNonNullParameter` 和几个取值方法
- [kp4] `getResult` 有按列名、按列序号、从存储过程取值三种入口

## 详解
### 先搞懂：一次存、一次取
你的订单有个枚举 `PAID`，数据库里存的是数字 `2`。保存订单时，要把 `PAID` 变成 `2` 写进去；查订单时，要把读到的 `2` 变回 `PAID`。

这就像寄信和收信：寄信时按邮局的格式填地址，收信时按你家的习惯翻译内容。两个方向的动作不一样，所以要两个方法。

术语说明：

- **PreparedStatement**：预编译语句，SQL 里的 `?` 占位符通过它来设值；
- **ResultSet**：查询结果集，里面是数据库返回的每一行每一列；
- **TypeHandler**：规定上面两件事的接口。

### setParameter：存的时候用
MyBatis 执行 SQL 前，要把 `#{}` 对应的 Java 值放到 `PreparedStatement` 的第几个问号上。`setParameter` 就负责这一步：拿到 Java 对象，转换成 JDBC 能接受的值，调用 `setInt`、`setString` 之类的方法设进去。

比如枚举 `PAID` 转成编号 2，就调用 `ps.setInt(位置, 2)`。

### getResult：取的时候用
查询返回后，MyBatis 要把某一列的值转成属性的 Java 类型。`getResult` 就负责这一步：从 `ResultSet` 里读出原始值，再转成目标类型返回。

同一个“取”动作有几种入口：按列名取、按列序号取，以及从存储过程的输出参数取。自定义时这几个方法都要实现，通常写法一致。

### 自定义时要实现什么
继承 `BaseTypeHandler` 更省事：它帮你处理了 null 值，你只需写非空时的设值方法 `setNonNullParameter`，以及三个取值方法。直接实现 `TypeHandler` 接口也行，但 null 要自己处理。

## 示例
```java
public class PayStatusHandler extends BaseTypeHandler<PayStatus> {
    @Override
    public void setNonNullParameter(PreparedStatement ps, int i,
                                    PayStatus s, JdbcType t) throws SQLException {
        ps.setInt(i, s.getCode()); // 存：枚举转编号
    }

    @Override
    public PayStatus getNullableResult(ResultSet rs, String col) throws SQLException {
        return PayStatus.of(rs.getInt(col)); // 取：编号转枚举
    }

    @Override
    public PayStatus getNullableResult(ResultSet rs, int idx) throws SQLException {
        return PayStatus.of(rs.getInt(idx));
    }

    @Override
    public PayStatus getNullableResult(CallableStatement cs, int idx) throws SQLException {
        return PayStatus.of(cs.getInt(idx));
    }
}
```

## 易错点
- 只实现了存、没实现取，写入正常但查询出来的属性不对
- 编号不在枚举里时，`of` 方法返回 null 或抛异常，要自己处理
- 以为 null 值也会走 `setNonNullParameter`，其实基类先处理了 null

## 追问
### [f1] 为什么继承 BaseTypeHandler，而不是直接实现 TypeHandler？
`BaseTypeHandler` 已经把 null 的设值和读取处理好，子类只关心非空值，代码更少，也不容易漏掉 null 判断。
