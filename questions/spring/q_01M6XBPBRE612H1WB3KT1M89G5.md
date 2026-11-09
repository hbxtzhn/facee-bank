---
id: q_01M6XBPBRE612H1WB3KT1M89G5
title: 怎么让 Spring Cloud 应用运行时刷新配置（@RefreshScope）？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [configuration, microservice]
prerequisites: [q_01M6XBHAKYTM47DX67NMKJ89WJ]
appliesTo: ["Spring Cloud"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
在读取配置的 Bean 上加 @RefreshScope，配置变更并触发刷新后，这个 Bean 会用新配置重新创建，不用重启应用。

## 要点
- [kp1|3] 在需要动态刷新的 Bean 或配置类上标注 @RefreshScope
- [kp2|3] 刷新时旧的 Bean 被丢弃，下次使用时按新配置重新创建
- [kp3|2] 刷新要触发：Config 调 refresh 端点，Nacos 可自动刷新
- [kp4] 用 @ConfigurationProperties 绑定的配置，刷新时会重新绑定

## 详解
### 先搞懂：配置改了，为什么应用不知道
一个 Bean 用 `@Value("${switch.enabled}")` 读了配置，Spring 在创建这个 Bean 时就把值填进去了。之后即使配置中心里的值变了，这个 Bean 手里的仍是旧值，因为它不会自己再去读。

可以想成抄了一份电话号码在便签上：通讯录改了，便签不会自己变。要换新号码，得重新抄一份。`@RefreshScope` 做的就是“作废旧便签，下次用时重抄”。

后文用到的术语：
- **Bean**：由 Spring 创建和管理的对象。
- **作用域（scope）**：决定 Bean 什么时候创建、活多久，比如单例、每次请求新建。
- **刷新**：让应用重新读取最新配置。

### 怎么做：加注解，再触发刷新
**第一步，给 Bean 加注解：**
```java
@RefreshScope
@RestController
public class SwitchController {
    @Value("${switch.enabled:false}")
    private boolean enabled;
}
```

**第二步，触发刷新。**
- 用 Spring Cloud Config：修改配置后，调用应用的 `/actuator/refresh` 端点（需要引入 actuator，并在配置里暴露 `refresh` 端点）。
- 用 Nacos Config：在 Nacos 页面发布新配置，客户端监听到变化后会自动刷新；Bean 仍需要 `@RefreshScope` 才会重新创建。

### 刷新时发生了什么
标了 `@RefreshScope` 的 Bean 实际是一个代理对象，调用时才找真正的 Bean。刷新时，Spring 清掉缓存的旧 Bean；下次有人调用，就会创建一个新 Bean，并用最新的配置赋值。

用 `@ConfigurationProperties` 绑定的配置类，刷新时 Spring Cloud 会重新绑定属性，一般不用额外加 `@RefreshScope`。

## 易错点
- 只改了配置中心的值，却没有触发刷新，以为应用会自动更新；Spring Cloud Config 需要主动触发
- 以为所有 Bean 都会刷新；没标 `@RefreshScope` 的单例 Bean 仍然保留旧值
- 以为刷新能改变一切；线程池、连接池这类启动时创建的对象，不会因刷新自动调整

## 追问
### [f1] @RefreshScope 的 Bean 刷新后，旧对象怎么办？
旧对象不再被使用，等待垃圾回收；新的调用会拿到按新配置创建的对象。

### [f2] 配置多个实例时，怎么一次刷新全部？
逐个实例调用 refresh 端点很麻烦。常见做法是用消息总线（如 Spring Cloud Bus）广播刷新，或用 Nacos 这类自带推送的配置中心。
