---
id: q_01M6XBPAGES2AXHTZABY0T2HTK
title: JDK 动态代理是怎么实现的？
type: concept
difficulty: hard
importance: 2
category: spring
tags: [dynamic-proxy, reflection]
prerequisites: [q_01M6XBP9ZWJJVYTDKK8GKBAAVQ]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 5
references:
  - { title: "Java SE 21 API：java.lang.reflect.Proxy", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/reflect/Proxy.html" }
---

## 一句话
JDK 动态代理用 `Proxy.newProxyInstance` 在运行时生成一个实现目标接口的代理类，代理类的每个方法都会转给 `InvocationHandler.invoke`。

## 要点
- [kp1|3] 用 `Proxy.newProxyInstance` 传入类加载器、接口数组和处理器
- [kp2|3] 生成的代理类实现了目标的所有接口，方法调用都转给 `invoke`
- [kp3|2] 在 `invoke` 里先做增强，再用反射调用目标方法
- [kp4|2] 代理类已继承 `Proxy`，所以只能基于接口，不能基于类
- [kp5] 同样的接口组合生成的代理类会被缓存复用

## 详解
### 先搞懂：前台转接电话
公司前台接到任何来电，都先登记，再转给对应的人。前台不管来电内容是什么，统一走“登记、转接”这一套。代理类就是前台，`InvocationHandler` 就是前台里的“登记并转接”流程，目标对象是被转接的那个人。

后文术语：
- **反射**：运行时通过方法对象来调用方法，而不是直接写 `obj.foo()`。
- **InvocationHandler**：处理器接口，只有一个 `invoke` 方法，增强逻辑写在里面。
- **类加载器**：负责把类加载进 JVM，生成的代理类也需要一个。

### 使用步骤
1. 写一个类实现 `InvocationHandler`，持有目标对象。
2. 在 `invoke` 里写增强，并通过 `method.invoke(target, args)` 调用目标方法。
3. 调用 `Proxy.newProxyInstance`，得到代理对象。
4. 把代理对象转成接口类型使用。

### 运行时发生了什么
`newProxyInstance` 内部会在运行时生成一个类（名字类似 `$Proxy0`）。这个类继承 `Proxy`，并实现你传入的所有接口。接口里每个方法，在代理类里都被实现成一句：调用处理器的 `invoke`，把当前代理对象、方法对象和参数传过去。

所以调用 `proxy.save()` 的实际路径是：代理类的 `save` 方法，转到 `handler.invoke`，再由你的代码决定怎么处理。

### 为什么只能代理接口
Java 只支持单继承，而代理类已经继承了 `Proxy`，没法再继承目标类，只能靠实现接口来做到“和目标长得一样”。

### 进阶：缓存与注意点
相同类加载器和接口组合生成的代理类会被缓存，不会重复生成。`invoke` 中不要对 `proxy` 参数调用接口方法，否则会再次进入 `invoke` 造成无限递归，调用目标时应使用 `target`。

## 示例
```java
interface UserService { void save(); }

class UserServiceImpl implements UserService {
    public void save() { System.out.println("保存用户"); }
}

UserService target = new UserServiceImpl();
UserService proxy = (UserService) Proxy.newProxyInstance(
        target.getClass().getClassLoader(),
        target.getClass().getInterfaces(),
        (p, method, args) -> {
            System.out.println("前置增强");
            Object result = method.invoke(target, args);
            System.out.println("后置增强");
            return result;
        });
proxy.save();
```

## 易错点
- 把代理对象转成 `UserServiceImpl`，会抛出 `ClassCastException`
- 在 `invoke` 里用 `proxy` 调用方法，导致无限递归
- 以为必须手写代理类；代理类是运行时自动生成的

## 追问
### [f1] `invoke` 的三个参数分别是什么？
`proxy` 是代理对象本身，`method` 是被调用的方法对象，`args` 是调用时传入的参数数组。
