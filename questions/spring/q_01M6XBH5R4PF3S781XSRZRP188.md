---
id: q_01M6XBH5R4PF3S781XSRZRP188
title: 什么是 ApplicationContext（应用上下文）？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [ioc-di]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
ApplicationContext 是 Spring 的应用上下文，也就是我们平时说的 Spring 容器；它在 BeanFactory 管理 Bean 的基础上，增加了国际化、事件发布、资源加载等企业级功能。

## 要点
- [kp1|3] ApplicationContext 是 BeanFactory 的子接口，是功能更完整的容器
- [kp2|3] 它在 Bean 管理之外，还提供国际化、事件发布、资源加载等功能
- [kp3|2] 实际开发中基本都直接使用 ApplicationContext，而不是 BeanFactory
- [kp4] 常见实现有 ClassPathXmlApplicationContext、AnnotationConfigApplicationContext

## 详解
### 先搞懂：容器是负责管理对象的「管家」
做项目时，Service 里要用 Dao，Controller 里要用 Service。不用自己 `new`，而是由 Spring 创建好放进「容器」，需要时从容器里拿，这个容器就是管家。

BeanFactory 是最基础的管家，只会一件事：创建和管理 Bean。ApplicationContext 是升级版的管家，除了管 Bean，还会处理很多企业开发里常见的杂事。

后文用到的词：
- **Bean**：由 Spring 容器创建和管理的对象。
- **BeanFactory**：最基础的容器接口，只负责 Bean 的创建与获取。
- **ApplicationContext**：BeanFactory 的子接口，功能更全。

### 它比 BeanFactory 多了什么
ApplicationContext 继承了 BeanFactory 的全部能力，并额外提供：

- **国际化**：根据用户语言环境返回不同语言的文字（MessageSource）；
- **事件发布**：容器内部可以发布事件，各组件订阅并响应（ApplicationEventPublisher）；
- **资源加载**：用统一方式读取类路径、文件、网络上的资源（ResourceLoader）；
- **环境和配置**：读取配置属性、区分不同环境；
- 能自动识别并应用各类后置处理器（如 BeanPostProcessor），支持 AOP 等功能。

### 怎么选
日常开发直接用 ApplicationContext。Spring Boot 启动后得到的也是它的某个实现。

BeanFactory 只在极少数对资源极度敏感的场景里才会直接用到，一般是框架内部使用。

## 示例
```java
// 基于注解配置创建容器
ApplicationContext ctx = new AnnotationConfigApplicationContext(AppConfig.class);

// 从容器里取 Bean
UserService service = ctx.getBean(UserService.class);
service.hello();
```

## 易错点
- 以为 ApplicationContext 和 BeanFactory 是两个不相关的东西；前者是后者的子接口
- 以为只有 XML 配置才能用 ApplicationContext；注解和 Java 配置也可以
- 以为日常需要自己创建 ApplicationContext；Spring Boot 会自动创建，通常只需要注入

## 追问
### [f1] BeanFactory 和 ApplicationContext 在创建 Bean 的时机上有什么区别？
BeanFactory 通常是用到时才创建（延迟加载）；ApplicationContext 默认在启动时就把单例 Bean 创建好，启动时就能发现配置错误。

### [f2] 怎么在 Bean 里拿到 ApplicationContext？
可以直接 `@Autowired` 注入，或者实现 `ApplicationContextAware` 接口，由 Spring 在初始化时把容器传进来。
