---
id: q_01M6XCBVK1TTZ2C03552AC2VC8
title: 插件的方法调用流程是怎样的？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [interceptor, design-pattern]
prerequisites: [q_01M6XCBV31HGNY87H3VSGYPSHW]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
调用代理对象的方法会先进入 `invoke`：方法签名匹配就执行插件的 `intercept`，不匹配就用反射调用原方法，最后把结果返回给调用者。

## 要点
- [kp1|3] 调用代理对象的任何方法，都先进入 `Plugin.invoke`
- [kp2|3] 签名表里有这个方法，就执行插件的 `intercept`
- [kp3|2] 签名表里没有，就反射调用目标对象的原方法
- [kp4] `intercept` 里调用 `proceed()` 才会继续执行原方法

## 详解
### 先搞懂：快递路线图
你寄一个包裹，要经过中转站。中转站有一份重点名单：名单上的包裹要开箱检查，其他的直接转走。检查完了，别忘了把包裹继续送出去。

插件调用流程就是这条路线：请求先到代理，代理查名单，决定拦或放。

后文用到的术语：
- **`Invocation`**：把「目标对象、方法、参数」打包成的一个对象，传给插件。
- **`proceed()`**：`Invocation` 上的方法，作用是继续执行原来的方法。

### 一次调用的完整流程
假设你写了一个拦截 `Executor.query` 的插件，业务里调用查询：

1. 代码调用 `Executor` 的方法，这个 `Executor` 其实是代理对象。
2. 代理把调用交给 `Plugin.invoke(proxy, method, args)`。
3. `invoke` 用方法所属的接口查签名表，看这个方法是否被声明拦截。
4. 匹配：创建 `Invocation`，调用 `interceptor.intercept(invocation)`。
5. 不匹配：直接 `method.invoke(target, args)`，反射调用原方法。
6. 结果沿着调用链返回给调用方。

### intercept 里要做什么
`intercept` 里通常这样写：前置逻辑，调用 `invocation.proceed()`，后置逻辑，返回结果。

```java
@Override
public Object intercept(Invocation invocation) throws Throwable {
    // 前置：方法执行之前
    Object result = invocation.proceed();   // 继续执行原方法
    // 后置：方法执行之后
    return result;
}
```

不调用 `proceed()`，原方法就不会被执行，你可以返回自己构造的结果，达到「短路」的效果。

### 设计思路
这是责任链和代理模式的结合：每个插件是链上的一环，通过 `proceed` 把调用传给下一环，最里面才是真正的目标对象。

### 多个插件时的顺序
假设注册了插件 A 和 B，B 在外层。调用时先进入 B 的 `intercept`，B 调用 `proceed` 才进入 A，A 再调用 `proceed` 才执行原方法。返回时顺序相反。

## 易错点
- 在 `intercept` 里忘了调用 `proceed()`，却期望原方法执行；结果会缺失
- 以为所有方法都会进入 `intercept`；只有签名匹配的方法才会
- 以为多个插件是并列的；它们是层层嵌套的

## 追问
### [f1] 不匹配签名的方法，也会经过代理吗？
会经过代理的 `invoke`，但只是判断一下就直接反射调用原方法，不会进入插件逻辑，额外开销很小。
