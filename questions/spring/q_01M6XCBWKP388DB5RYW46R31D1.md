---
id: q_01M6XCBWKP388DB5RYW46R31D1
title: 怎么用插件记录 SQL 和参数用于审计？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [interceptor]
prerequisites: [q_01M6XCBVV81R8AQS2VMXFM4JS6]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 3 手册：Configuration（Plugins、settings）", url: "https://mybatis.org/mybatis-3/configuration.html" }
estimatedMinutes: 3
---

## 一句话
在插件里通过 MappedStatement 和 BoundSql 取出 SQL 与参数，把它们连同方法 ID、耗时一起记录下来，就能用于调试和审计。

## 要点
- [kp1|3] 拦截 `Executor` 的 `query` 和 `update`，覆盖所有 SQL
- [kp2|3] `BoundSql.getSql()` 得到带问号的 SQL，参数值要另外取
- [kp3|2] 参数值从 `parameterObject` 和 `parameterMappings` 里按名字取
- [kp4|2] 敏感字段如密码、手机号要脱敏，不能原样落库
- [kp5] 日志写入尽量异步，不拖慢业务 SQL

## 详解
### 先搞懂：SQL 带问号，参数是分开放的
你在日志里看到的 SQL 往往长这样：`select * from user where id = ?`。问号对应的真实值，MyBatis 是分开保存的。

这像是快递单：地址模板是“收件人 ____”，具体名字写在另一张纸上。要还原完整信息，两张纸都要拿。

后文用到的词：

- **MappedStatement**：对应一个 Mapper 方法，里面有完整 ID，比如 `UserMapper.findById`。
- **BoundSql**：这次执行的 SQL 文本，加上参数的定义。
- **parameterObject**：调用 Mapper 方法时传进来的参数对象。

### 怎么取出 SQL 和参数
在 `intercept` 里，参数数组的第 0 个是 `MappedStatement`，第 1 个是参数对象。

1. 调用 `ms.getBoundSql(参数对象)` 得到 `BoundSql`。
2. `getSql()` 拿到带问号的 SQL。
3. `getParameterMappings()` 是一个列表，告诉你每个问号对应的属性名。
4. 参数对象是单个值时，直接用它；是实体或 Map 时，按属性名取值。

按属性名取值可以用 `Configuration.newMetaObject(参数对象)` 再调用 `getValue`，它能处理 Map 和 JavaBean 两种情况。

### 记录什么、怎么记
审计关心的是“谁、什么时候、对哪条数据做了什么”。一条记录通常包括：

- Mapper 方法 ID 和 SQL 类型（查询、修改等）
- SQL 文本和参数值
- 耗时和执行结果（行数或异常）
- 当前用户、请求 ID 等业务信息，可以从 `ThreadLocal` 取

### 落库时要注意的事
- **别影响业务**：写审计日志放进异步队列，不要在拦截器里同步写另一张表。同步写可能让业务事务一起变慢，甚至因为审计失败而回滚。
- **别再被自己拦住**：审计表的写入如果也走 MyBatis，会再次触发插件，造成无限循环。要排除审计表的方法 ID。
- **脱敏**：密码、证件号、手机号等敏感字段不能明文保存。
- **只审计需要的**：大量查询都记录会很多，通常只记增删改，或者只记指定表。

## 示例
```java
@Intercepts({
    @Signature(type = Executor.class, method = "update",
        args = {MappedStatement.class, Object.class})
})
public class AuditInterceptor implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        MappedStatement ms = (MappedStatement) invocation.getArgs()[0];
        Object param = invocation.getArgs()[1];
        BoundSql boundSql = ms.getBoundSql(param);
        MetaObject meta = ms.getConfiguration().newMetaObject(param);

        List<Object> values = new ArrayList<>();
        for (ParameterMapping pm : boundSql.getParameterMappings()) {
            values.add(meta.getValue(pm.getProperty()));
        }
        long start = System.currentTimeMillis();
        try {
            return invocation.proceed();
        } finally {
            long cost = System.currentTimeMillis() - start;
            AuditQueue.offer(ms.getId(), boundSql.getSql(), values, cost); // 异步写入
        }
    }
}
```

## 易错点
- 只记下带问号的 SQL，参数值没取，审计时无法还原
- 审计表写入也走 MyBatis 又触发了插件，造成循环
- 密码等敏感字段原样写进日志

## 追问
### [f1] 参数是单个基本类型时怎么取值？
单个简单类型参数时，参数对象本身就是值，用 `MetaObject` 取属性会出错。可以先判断参数对象是不是简单类型，再决定直接用还是按名字取。

### [f2] 只是想看 SQL，有没有不写插件的办法？
有。MyBatis 可以通过日志框架把 Mapper 所在包的日志级别调成 debug，直接打印 SQL 和参数，适合开发环境调试。
