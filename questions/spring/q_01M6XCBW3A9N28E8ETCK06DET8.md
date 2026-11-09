---
id: q_01M6XCBW3A9N28E8ETCK06DET8
title: 怎么用插件统计 SQL 执行时间和慢查询？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [interceptor, sql-optimization]
prerequisites: [q_01M6XCBVV81R8AQS2VMXFM4JS6]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
写一个拦截 Executor 的 query 和 update 的插件，在 proceed 前后各取一次时间，差值超过阈值就把 SQL 打成慢查询日志。

## 要点
- [kp1|3] 拦截 `Executor` 的 `query` 和 `update` 方法，覆盖增删改查
- [kp2|3] 在 `proceed` 前后各记一次时间，相减得到耗时
- [kp3|2] 耗时超过阈值才输出日志，阈值通过插件属性配置
- [kp4|2] 用 `finally` 保证报错时也能记录耗时
- [kp5] 日志里带上 Mapper 方法的完整 ID，方便定位

## 详解
### 先搞懂：插件像秒表，开始按一下，结束按一下
线上接口变慢，你想知道是哪条 SQL 拖的后腿。可以在每个 Mapper 方法里手写计时，但那样每个方法都要改。

更省事的办法是在 MyBatis 的执行入口装一块秒表：SQL 开始前按一下，结束后再按一下，差值就是耗时。慢于规定时间的才记下来。

后文用到的词：

- **拦截器**：MyBatis 提供的插件机制，可以在内部方法前后插入逻辑。
- **proceed**：放行，让被拦截的原方法继续执行。
- **慢查询**：耗时超过你设定阈值的 SQL。

### 计时的位置：Executor 还是 StatementHandler
两个位置都能计时：

- 拦截 `Executor`：能拿到 `MappedStatement`，里面有 Mapper 方法的完整 ID，日志最好定位。
- 拦截 `StatementHandler`：更接近真正执行 SQL 的位置，耗时更贴近数据库。

一般选 `Executor`，签名写两个：`query` 和 `update`。`update` 同时覆盖插入、修改、删除。

### 怎么算时间并输出日志
`intercept` 里的步骤很简单：

1. 记下开始时间。
2. 调用 `invocation.proceed()` 执行原方法。
3. 在 `finally` 里算出耗时。
4. 超过阈值，就从 `MappedStatement` 取出 ID，从 `BoundSql` 取出 SQL，输出一条警告日志。

计时一定写在 `finally` 里。SQL 执行报错时，也想知道它花了多久。

拿 SQL 的方式：`MappedStatement.getBoundSql(参数对象).getSql()`。取到的是带问号的 SQL，参数值不在里面。想看参数值要额外处理，下一题会讲。

阈值不要写死，在 `setProperties` 里读配置，例如一个叫 `slowMillis` 的属性。

### 这种方式的边界
- 测到的是 MyBatis 里从调用到返回的总耗时，包含取连接的等待和结果映射，不等于数据库纯执行时间。
- 它只能发现慢，不能告诉你为什么慢；查原因还要靠 `EXPLAIN` 看执行计划。
- 数据库自己的慢查询日志是另一条线，两者可以互相印证。

## 示例
```java
@Intercepts({
    @Signature(type = Executor.class, method = "query",
        args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class}),
    @Signature(type = Executor.class, method = "update",
        args = {MappedStatement.class, Object.class})
})
public class SlowSqlInterceptor implements Interceptor {
    private long slowMillis = 1000;

    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return invocation.proceed();
        } finally {
            long cost = System.currentTimeMillis() - start;
            if (cost >= slowMillis) {
                MappedStatement ms = (MappedStatement) invocation.getArgs()[0];
                BoundSql boundSql = ms.getBoundSql(invocation.getArgs()[1]);
                System.err.println("慢SQL " + cost + "ms " + ms.getId() + " " + boundSql.getSql());
            }
        }
    }

    @Override
    public void setProperties(Properties p) {
        String v = p.getProperty("slowMillis");
        if (v != null) slowMillis = Long.parseLong(v);
    }
}
```

## 易错点
- 把计时写在 proceed 之后但没放 finally，SQL 抛异常时没有记录
- 以为测到的就是数据库执行时间；实际还含取连接和结果映射的时间
- 只拦截 query，漏掉了 update，慢的更新语句发现不了

## 追问
### [f1] 为什么不直接用数据库的慢查询日志？
两者互补。数据库日志只反映数据库侧耗时，也不知道是哪个 Mapper 方法发出的。插件能直接带上方法 ID，还能关联业务日志。

### [f2] 插件本身会拖慢系统吗？
计时只是两次取时间，开销很小。要注意日志输出：别在每次查询都打日志，也别同步做很重的操作。
