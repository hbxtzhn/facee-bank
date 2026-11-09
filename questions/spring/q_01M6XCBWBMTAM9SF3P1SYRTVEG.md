---
id: q_01M6XCBWBMTAM9SF3P1SYRTVEG
title: 怎么用插件实现数据权限过滤？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [interceptor]
prerequisites: [q_01M6XCBVV81R8AQS2VMXFM4JS6]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
在拦截 StatementHandler 的 prepare 方法时，取出原 SQL，按当前用户的权限拼上查询条件再写回去，查询结果就只包含有权限的数据。

## 要点
- [kp1|3] 拦截 `StatementHandler` 的 `prepare`，此时 SQL 还没预编译
- [kp2|3] 取出 `BoundSql` 里的原 SQL，拼上权限条件后写回
- [kp3|2] 当前用户信息通常放在 `ThreadLocal` 里，插件从中读取
- [kp4|2] 用注解标记哪些方法需要过滤，避免所有 SQL 都被改
- [kp5] 改写 SQL 要谨慎处理拼接，防止注入和语法错误

## 详解
### 先搞懂：同一条查询，不同的人看到不同的数据
业务里常见这样的需求：销售只能看自己名下的客户，部门经理能看本部门的，管理员看全部。

最笨的办法是在每个查询里手写“再加个 `owner_id = 当前用户`”，几十个查询都要改，还容易漏。

更好的办法：让 MyBatis 在 SQL 发给数据库之前，统一给它加一道条件。就像快递出库前，仓库统一贴一张“只送这个区域”的标签。

后文用到的词：

- **数据权限**：同一张表里，不同用户能看到的行不一样。
- **StatementHandler**：负责准备和执行 SQL 语句的内部对象。
- **BoundSql**：保存最终 SQL 文本和参数信息的对象。

### 改写的位置：prepare 之前
插件拦截 `StatementHandler` 的 `prepare` 方法，参数是 `Connection` 和超时时间。

这个时刻 SQL 文本已经生成，但还没交给数据库预编译。这是最后一个能改 SQL 的机会。

### 改写的步骤
1. 在 `intercept` 里拿到 `StatementHandler`，从中取出 `BoundSql`。
2. 判断这次调用要不要过滤。常见做法是自定义一个注解，贴在 Mapper 方法上，插件根据方法 ID 找到注解。
3. 从 `ThreadLocal` 取出当前用户的权限范围，比如可见的部门 ID 列表。
4. 把原 SQL 包一层，在外面加条件，再把新 SQL 写回 `BoundSql`。

`BoundSql` 里的 SQL 字段没有公开的 set 方法，一般用 MyBatis 自带的 `SystemMetaObject` 或反射去改。

包一层的写法，例如把原 SQL 变成：`select * from (原SQL) t where t.dept_id in (...)`。这样不用去解析原 SQL 的结构，但要确保原 SQL 查出的结果里有权限字段。

复杂场景也可以用 SQL 解析库来改写，更精确，但实现更重。

### 要注意的几个问题
- **防注入**：权限值来自服务端用户信息，不是用户输入。尽管如此，拼数字或做过校验的值，不要拼任意字符串。
- **只对查询生效**：增删改一般不走这个逻辑，需要的话单独处理。
- **和分页插件配合**：改写发生在什么顺序，会影响总数查询是否带上权限条件，要实际验证。
- **线程池场景**：`ThreadLocal` 里的用户信息，在异步线程里取不到，要显式传递。

## 示例
```java
@Intercepts({
    @Signature(type = StatementHandler.class, method = "prepare",
        args = {Connection.class, Integer.class})
})
public class DataScopeInterceptor implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        StatementHandler handler = (StatementHandler) invocation.getTarget();
        BoundSql boundSql = handler.getBoundSql();
        String sql = boundSql.getSql();

        Long deptId = UserContext.currentDeptId(); // 从 ThreadLocal 取
        if (deptId != null && sql.trim().toLowerCase().startsWith("select")) {
            String newSql = "select * from (" + sql + ") t where t.dept_id = " + deptId;
            MetaObject meta = SystemMetaObject.forObject(boundSql);
            meta.setValue("sql", newSql); // 写回新 SQL
        }
        return invocation.proceed();
    }
}
```

## 易错点
- 所有查询都改写，连不需要权限的字典表查询也被加上条件
- 在异步线程里执行查询，取不到 ThreadLocal 中的用户，导致条件为空或报错
- 字符串直接拼用户可控的值，留下 SQL 注入风险

## 追问
### [f1] 除了插件，还有别的做法吗？
可以在 Service 层手动传权限参数，写进每个查询的 where 里。更直观但重复多。数据库层面也可用视图或行级策略，但各数据库支持不同。

### [f2] 为什么选 StatementHandler 而不是 Executor？
`Executor` 的 query 拿到的是 `MappedStatement`，改 SQL 要重新构造对象，比较绕。`StatementHandler` 直接拿到 `BoundSql`，改写更方便。
