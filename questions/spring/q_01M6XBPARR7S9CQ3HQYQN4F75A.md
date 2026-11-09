---
id: q_01M6XBPARR7S9CQ3HQYQN4F75A
title: CGLIB 代理是怎么实现的？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [dynamic-proxy, bytecode-execution]
prerequisites: [q_01M6XBP9ZWJJVYTDKK8GKBAAVQ]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Spring Framework 参考文档：Proxying Mechanisms（CGLIB 限制、Objenesis）", url: "https://docs.spring.io/spring-framework/reference/core/aop/proxying.html" }
  - { title: "Spring Framework API：cglib Enhancer", url: "https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/cglib/proxy/Enhancer.html" }
  - { title: "Spring Framework API：cglib MethodProxy.invokeSuper", url: "https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/cglib/proxy/MethodProxy.html" }
estimatedMinutes: 3
---

## 一句话
CGLIB 在运行时用字节码技术生成目标类的子类，覆盖其中非 final 的方法，在覆盖的方法里先做增强再调用父类方法，所以不需要接口。

## 要点
- [kp1|3] CGLIB 通过继承目标类生成子类作为代理
- [kp2|3] 子类覆盖非 final 方法，把调用交给 `MethodInterceptor`
- [kp3|2] 底层操作字节码，在运行时生成子类的 class
- [kp4|2] final 类和 final、private 方法无法被增强
- [kp5] 在 `intercept` 里用 `invokeSuper` 调用原方法

## 详解
### 先搞懂：找个“亲戚”顶班
目标类是一位老师，CGLIB 找来一位“亲戚”，长得一样（继承了所有方法），上课前先点名、下课后记录，中间的讲课内容照搬老师。调用方请的是“亲戚”，却以为是老师本人。

后文术语：
- **子类**：继承目标类，拥有同样的方法，可以覆盖。
- **字节码**：JVM 执行的 class 文件内容，可以在运行时生成。

### 使用步骤
1. 创建 `Enhancer`，设置父类为目标类。
2. 设置回调，写一个 `MethodInterceptor`，增强逻辑放在 `intercept` 方法里。
3. 调用 `create()`，得到代理对象，它实际是目标类的子类实例。

### 运行时发生了什么
`Enhancer` 在运行时生成一个子类，里面对每个可以覆盖的方法都做了重写：重写的方法不直接执行原逻辑，而是调用拦截器的 `intercept`。你在拦截器里决定先做什么，再通过 `MethodProxy.invokeSuper` 调用父类（也就是原目标）的方法。

### 为什么不能代理 final
CGLIB 靠覆盖方法来拦截。final 类不能被继承，final 方法不能被覆盖，private 方法子类看不到，所以这些都拦截不了。

### 进阶：Spring 里的 CGLIB
Spring 把 CGLIB 重新打包进自己的包（`org.springframework.cglib`），项目里不用额外引入依赖。`invokeSuper` 走的是 CGLIB 生成的快速调用类，不是普通反射；是否更快这里不下结论。

## 示例
```java
Enhancer enhancer = new Enhancer();
enhancer.setSuperclass(UserService.class);
enhancer.setCallback((MethodInterceptor) (obj, method, args, proxy) -> {
    System.out.println("前置增强");
    Object result = proxy.invokeSuper(obj, args);
    System.out.println("后置增强");
    return result;
});
UserService service = (UserService) enhancer.create();
service.save();
```

## 易错点
- 在 `intercept` 里用 `method.invoke(obj, args)` 调用原方法，会再次被拦截而无限递归
- 给目标类的方法加了 final，增强悄悄失效
- 以为 CGLIB 一定需要目标类有无参构造；新版 Spring 借助 Objenesis 已不强制

## 追问
### [f1] CGLIB 和 JDK 代理的核心区别是什么？
JDK 代理实现接口，CGLIB 继承目标类。因此 CGLIB 不需要接口，但受 final 限制。
