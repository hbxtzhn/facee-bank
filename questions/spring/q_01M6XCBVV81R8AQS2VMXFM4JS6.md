---
id: q_01M6XCBVV81R8AQS2VMXFM4JS6
title: 怎么编写一个 MyBatis 插件？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [interceptor]
prerequisites: [q_01M6XCBV31HGNY87H3VSGYPSHW]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
写一个类实现 Interceptor 接口，用 @Intercepts 和 @Signature 声明拦截哪个对象的哪个方法，在 intercept 里调用 proceed 放行，最后在配置里注册。

## 要点
- [kp1|3] 插件类实现 `Interceptor` 接口，核心方法是 `intercept`
- [kp2|3] `@Intercepts` 加 `@Signature`，用 type、method、args 指定拦截点
- [kp3|2] 只能拦截 Executor、StatementHandler、ParameterHandler、ResultSetHandler
- [kp4|2] `intercept` 里调用 `invocation.proceed()` 才会继续执行原方法
- [kp5] 用 `<plugin>` 标签或 Spring Boot 的 Bean 注册

## 详解
### 先搞懂：插件就是给 MyBatis 内部流程装“门卫”
你在项目里写 Mapper 方法，MyBatis 会在内部一步步执行：生成 SQL、设置参数、执行、封装结果。

插件相当于在其中几个步骤门口放一个门卫。请求经过时先找门卫，门卫可以看一眼、记个账、改点东西，再放行。

后文会用到几个词：

- **拦截器**：就是这个“门卫”，也就是插件本身。
- **Invocation**：被拦下来的这次调用，里面有目标对象、方法和参数。
- **proceed**：放行，让原来的方法继续执行。

### 第一步：实现 Interceptor 接口
接口有三个方法：

- `intercept(Invocation)`：真正的拦截逻辑写在这里。
- `plugin(Object)`：决定要不要给目标对象套上代理。默认实现已经够用。
- `setProperties(Properties)`：接收配置里传进来的参数。

最关键的是 `intercept`。你在这里做自己的事，然后调用 `invocation.proceed()` 放行，并把结果返回。忘了调用 proceed，原来的查询就不会执行。

### 第二步：用 @Intercepts 声明拦截点
在类上加 `@Intercepts`，里面放一个或多个 `@Signature`。每个 `@Signature` 要写三样东西：

- `type`：拦截哪种对象。
- `method`：拦截它的哪个方法名。
- `args`：这个方法的参数类型，用来区分重载方法。

MyBatis 只允许拦截四类对象：`Executor`、`StatementHandler`、`ParameterHandler`、`ResultSetHandler`。想改 SQL 多选 `StatementHandler`，想统一处理查询和更新多选 `Executor`。

`args` 写错，MyBatis 会找不到方法而报错。`Executor` 的 `query` 有两个重载，要对应写对。

### 第三步：注册插件
在 `mybatis-config.xml` 里用 `<plugins>` 和 `<plugin>` 标签写上插件的全类名，需要参数就放在里面的 `<property>` 里。

用 Spring Boot 时，通常把插件声明成一个 Spring Bean，starter 会自动把它加进配置。

多个插件会层层嵌套代理，先注册的在里层，后注册的在外层。

## 示例
```java
@Intercepts({
    @Signature(type = Executor.class, method = "query",
        args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class})
})
public class DemoInterceptor implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        System.out.println("查询前");
        Object result = invocation.proceed(); // 放行，执行原来的查询
        System.out.println("查询后");
        return result;
    }
}
```

```xml
<plugins>
    <plugin interceptor="com.example.DemoInterceptor"/>
</plugins>
```

## 易错点
- 在 intercept 里忘了调用 proceed，结果原方法根本没执行
- 以为能拦截任意类的方法；实际只能拦截四类内部对象
- `@Signature` 的 args 和真实方法参数不一致，启动或运行时报找不到方法

## 追问
### [f1] 插件是怎么生效的？
MyBatis 创建 Executor 等对象时，会把它们交给插件的 `plugin` 方法，用 JDK 动态代理包一层。调用方法时先进代理，再进你的 `intercept`。

### [f2] 想拦截更新操作该怎么写？
拦截 `Executor` 的 `update` 方法，参数是 `MappedStatement` 和 `Object`。插入、修改、删除都会走这个方法。
