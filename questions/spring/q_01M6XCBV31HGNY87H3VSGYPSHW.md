---
id: q_01M6XCBV31HGNY87H3VSGYPSHW
title: 什么是 MyBatis 插件（拦截器）？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [interceptor, mybatis-internals]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
MyBatis 插件就是拦截器，可以拦截 Executor、StatementHandler、ParameterHandler、ResultSetHandler 四类对象的方法，在前后加入自己的逻辑。

## 要点
- [kp1|3] 插件是实现了 `Interceptor` 接口的类，用来拦截方法调用
- [kp2|3] 只能拦截 Executor、StatementHandler、ParameterHandler、ResultSetHandler
- [kp3|2] 用 `@Intercepts` 和 `@Signature` 声明拦截哪个类的哪个方法
- [kp4] 常见用途：分页、SQL 日志、耗时统计、数据权限

## 详解
### 先搞懂：在流水线上加一道检查站
MyBatis 执行一条查询，要经过几个步骤：创建语句、设置参数、执行、封装结果。每一步都由一个核心对象负责。

插件就像在这条流水线上设置检查站：东西经过时，你可以看一眼、改一改、记个录，再放行。

后文用到的术语：
- **拦截器**：一个在方法调用前后插入逻辑的类。
- **四大对象**：负责执行流程不同环节的核心对象。

### 四大对象各管什么
| 对象 | 负责什么 |
|---|---|
| `Executor` | 执行查询、更新、提交、回滚，管理缓存 |
| `StatementHandler` | 创建并执行 JDBC 语句 |
| `ParameterHandler` | 给语句设置参数 |
| `ResultSetHandler` | 把结果集封装成对象 |

### 怎么写一个插件
1. 写一个类，实现 `Interceptor` 接口，在 `intercept` 方法里写自己的逻辑。
2. 用 `@Intercepts` 加 `@Signature` 声明要拦截的类、方法和参数类型。
3. 在配置里注册这个插件。

```java
@Intercepts(@Signature(type = Executor.class, method = "query",
        args = {MappedStatement.class, Object.class,
                RowBounds.class, ResultHandler.class}))
public class TimeCostPlugin implements Interceptor {
    @Override
    public Object intercept(Invocation inv) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return inv.proceed();   // 放行，执行原方法
        } finally {
            System.out.println("cost=" + (System.currentTimeMillis() - start));
        }
    }
}
```

### 原理：基于动态代理
MyBatis 创建这四类对象时，会把它们交给插件处理，通过 JDK 动态代理包上一层。调用方法时先走代理，由代理决定要不要交给插件，下一题详细讲。

## 易错点
- 想拦截任意类的方法；插件只能拦截那四类对象
- 在 `intercept` 里忘记调用 `proceed()`；原方法没有执行，查询会没有结果
- 把 `@Signature` 的参数类型写错；匹配不上，插件不会生效

## 追问
### [f1] 分页插件为什么通常拦截 `StatementHandler` 或 `Executor`？
因为要在语句执行之前改写 SQL，加上分页条件。这两个对象都能拿到最终的 SQL 或执行入口，分页插件按需要选一个切入。
