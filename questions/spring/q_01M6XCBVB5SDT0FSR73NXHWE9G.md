---
id: q_01M6XCBVB5SDT0FSR73NXHWE9G
title: 插件是怎么通过动态代理拦截四大核心对象的？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [interceptor, dynamic-proxy]
prerequisites: [q_01M6XCBV31HGNY87H3VSGYPSHW]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 源码：Plugin.java", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/plugin/Plugin.java" }
  - { title: "MyBatis 源码：Configuration.java（newExecutor）", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/session/Configuration.java" }
estimatedMinutes: 3
---

## 一句话
`Plugin` 工具类在 MyBatis 创建核心对象时，为它生成 JDK 动态代理；代理的 `invoke` 发现方法签名匹配，就把调用交给插件的 `intercept` 方法。

## 要点
- [kp1|3] 创建四大对象时，`InterceptorChain` 依次让每个插件包装目标对象
- [kp2|3] `Plugin.wrap` 用 JDK 动态代理，只为声明过的接口生成代理
- [kp3|2] `Plugin` 实现 `InvocationHandler`，在 `invoke` 里判断是否匹配
- [kp4] 多个插件会一层套一层，后注册的在外层

## 详解
### 先搞懂：先包一层壳，再看要不要截
MyBatis 创建 `Executor` 等对象后，不直接用，而是先交给每个插件说：「你要不要包装一下？」插件把原对象包进一个代理里，返回代理对象，后面用的就是这个代理。

可以把它想成门卫：所有人进门都要经过门卫，门卫手里有一张名单，名单上的人才拦下来检查，其他人直接放行。

后文用到的术语：
- **JDK 动态代理**：运行时基于接口生成代理对象，调用会先进入 `InvocationHandler` 的 `invoke` 方法。
- **签名**：要拦截的类、方法名和参数类型，写在 `@Signature` 里。

### 第一步：包装
创建核心对象时，MyBatis 调用 `InterceptorChain.pluginAll(target)`，对每个插件依次调用 `plugin(target)`。默认实现是 `Plugin.wrap(target, this)`，它做这些事：

1. 读取插件类上的 `@Intercepts`，整理出「类 → 方法集合」的签名表。
2. 看目标对象实现了哪些接口，只保留签名表里有的接口。
3. 有匹配的接口，就用 JDK 动态代理创建代理，handler 是一个 `Plugin` 对象。
4. 没有匹配，直接返回原对象，不包装。

### 第二步：调用时判断
`Plugin` 实现了 `InvocationHandler`。代理对象的方法被调用时，进入 `Plugin.invoke`：

- 根据方法所属的接口，到签名表里查这个方法在不在集合里。
- 在，就把目标对象、方法、参数封成 `Invocation`，调用插件的 `intercept`。
- 不在，直接反射调用目标对象的原方法。

### 为什么只能拦这四类对象
因为 JDK 动态代理只能代理接口，而 MyBatis 只在创建这四类对象的地方调用了 `pluginAll`。别的对象没有这个钩子，插件机制就够不着。

### 多个插件时
每个插件包装一次，所以会形成代理套代理。最后注册的插件在最外层，调用时先进入它，它调用 `proceed` 才轮到里面一层。

## 易错点
- 把 `Plugin` 当成插件本身；插件是你写的 `Interceptor`，`Plugin` 是 MyBatis 的代理工具
- `@Signature` 写的类型没有对应接口；目标对象不会被包装，插件不生效
- 以为插件不用写注解也能拦截；没有 `@Intercepts` 会在包装时报错

## 追问
### [f1] 为什么用 JDK 动态代理，而不是 CGLIB？
四大对象都有接口，JDK 动态代理够用，也不需要额外依赖。拦截点由接口方法定义，所以签名里写的是接口类型。
