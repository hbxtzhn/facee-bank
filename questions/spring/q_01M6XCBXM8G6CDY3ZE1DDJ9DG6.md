---
id: q_01M6XCBXM8G6CDY3ZE1DDJ9DG6
title: PageHelper 分页插件是怎么改写 SQL 的？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [pagination, interceptor]
prerequisites: [q_01M6XCBXCBRGX36RJVRGVR98ES]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "PageHelper 源码：PageInterceptor.java", url: "https://raw.githubusercontent.com/pagehelper/Mybatis-PageHelper/master/src/main/java/com/github/pagehelper/PageInterceptor.java" }
  - { title: "PageHelper 文档：HowToUse", url: "https://github.com/pagehelper/Mybatis-PageHelper/blob/master/wikis/en/HowToUse.md" }
estimatedMinutes: 4
---

## 一句话
PageHelper 是一个拦截 Executor 的 query 方法的插件，它按数据库方言把原 SQL 包装成带 limit 的分页语句，并补上分页参数后再放行执行。

## 要点
- [kp1|3] 插件拦截 `Executor` 的 `query` 方法，在真正执行前动手
- [kp2|3] 分页参数由 `startPage` 存进 `ThreadLocal`，插件从中读取
- [kp3|2] 按方言（dialect）生成分页 SQL，例如 MySQL 加 `limit`
- [kp4|2] 先执行一条统计总数的查询，再执行分页查询
- [kp5] 执行完成后清理 `ThreadLocal`，避免影响其他查询

## 详解
### 先搞懂：快递在出库前被重新打包
你写的查询是 `select * from user`，没有分页。你只在前面调用了 `startPage`。

PageHelper 就像快递站的打包员：包裹出库前，它把原来的 SQL 取出来，按目的地的规矩（不同数据库的语法）改一改，再发走。

后文用到的词：

- **拦截器**：能在 MyBatis 内部方法前后插入逻辑的插件。
- **方言**：不同数据库的分页语法不一样，每种数据库对应一种写法。
- **ThreadLocal**：每个线程自己的一份存储，不会被别的线程看到。

### 第一步：startPage 把参数放进线程
调用 `PageHelper.startPage(页码, 每页条数)` 时，插件只是把页码和条数存进当前线程的 `ThreadLocal`，并没有马上做什么。

### 第二步：拦截 Executor 的 query
插件声明拦截 `Executor` 的 `query`。这个方法有两个重载，所以插件写了两个签名。

下一条查询执行时，请求先来到插件。插件检查线程里有没有分页参数：

- 没有，直接放行，什么也不改。
- 有，进入分页处理。

### 第三步：先查总数，再查当前页
插件会做两件事：

1. **统计总数**：根据原 SQL 生成一条统计行数的 SQL，单独执行。这条语句和原查询用同一套参数。总数是 0 时，通常就不用再查当前页了。
2. **改写成分页 SQL**：调用当前方言，把原 SQL 包装成带分页条件的语句。例如 MySQL 方言会在末尾加上 `limit` 和 `offset`。

页码和条数需要作为参数传给数据库，插件会把它们补进参数里，再执行改写后的查询。

### 第四步：清理现场
查询结束后，插件在 `finally` 里清掉线程中的分页参数。这样同一个线程下一次的查询不会被误分页。

### 为什么方言能适配不同数据库
插件会根据数据库连接的类型（或配置）选定一个方言对象。不同方言只负责一件事：把原 SQL 变成该数据库认可的分页 SQL。

所以业务代码不变，换数据库时，插件换一种写法而已。

### 进阶：只用拦截器的限制（基础薄弱可先跳过）
- 插件改写的是 SQL 字符串，原 SQL 里如果已经有复杂结构（如 `union`），改写结果要实际验证。
- 统计总数的 SQL 会尽量精简，但含 `group by` 的查询通常要多包一层。
- 同一线程里只对下一条查询生效，这是靠 `ThreadLocal` 实现的约束。

## 示例
```java
// 插件内部大致的处理逻辑（示意，不是真实源码）
Object intercept(Invocation invocation) throws Throwable {
    try {
        Page page = LOCAL_PAGE.get();           // startPage 存进去的参数
        if (page == null) {
            return invocation.proceed();       // 没有分页，直接放行
        }
        long total = executeCountQuery(invocation); // 先统计总数
        page.setTotal(total);
        String pageSql = dialect.getPageSql(originalSql, page); // 方言改写
        // 用改写后的 SQL 和补充的分页参数执行查询
        return executeWithSql(invocation, pageSql);
    } finally {
        LOCAL_PAGE.remove();                   // 清理线程中的分页参数
    }
}
```

## 易错点
- 以为插件在启动时就改写所有 SQL；实际只改写 startPage 之后的下一条查询
- 以为分页参数是传给 Mapper 的；实际是通过 ThreadLocal 传递，所以要紧挨着查询
- 以为统计总数和分页是同一条 SQL；实际是两条语句

## 追问
### [f1] 如果 startPage 后没有查询会怎样？
参数会留在线程里。线程被线程池复用时，后面不相关的查询可能被误分页。所以 startPage 要紧跟查询。

### [f2] 不想统计总数怎么办？
可以通过参数关闭总数统计，只执行分页查询，省掉一条语句。适合“加载更多”这种不需要总页数的场景。
