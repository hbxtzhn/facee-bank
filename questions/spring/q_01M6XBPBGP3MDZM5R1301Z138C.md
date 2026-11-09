---
id: q_01M6XBPBGP3MDZM5R1301Z138C
title: Spring Cloud 是做什么的？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [microservice]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Spring Cloud 是基于 Spring Boot 的微服务工具集，整合了注册发现、配置中心、网关、远程调用等常用组件。

## 要点
- [kp1|3] Spring Cloud 基于 Spring Boot，解决微服务拆分后出现的公共问题
- [kp2|3] 服务找得到：注册中心（如 Nacos、Eureka）负责服务注册与发现
- [kp3|2] 配置统一管：配置中心（如 Nacos Config）集中管理配置
- [kp4|2] 请求进得来、调得通：网关（Spring Cloud Gateway）管入口，OpenFeign 做远程调用

## 详解
### 先搞懂：微服务拆开后，多出来哪些活
把一个应用拆成十几个服务后，会冒出很多原来没有的问题：服务地址怎么找、配置怎么统一改、外部请求从哪进、服务之间怎么调用、调用失败怎么办。

每个项目自己造轮子太累。Spring Cloud 就像一套装修工具箱：水电、门窗、锁具都配好了，按需取用，并且和 Spring Boot 的写法风格一致。

后文用到的术语：
- **注册中心**：记录各服务实例地址的“通讯录”。
- **负载均衡**：同一服务有多个实例时，决定这次请求发给谁。
- **熔断、限流**：下游出问题或流量过大时，保护自己不被拖垮。

### 方案对比：常见组件和分工
| 要解决的问题 | 常见组件 |
|---|---|
| 服务注册与发现 | Nacos、Eureka |
| 配置集中管理 | Nacos Config、Spring Cloud Config |
| 统一入口 | Spring Cloud Gateway |
| 服务间调用 | OpenFeign（声明式 HTTP 客户端） |
| 客户端负载均衡 | Spring Cloud LoadBalancer |
| 限流、熔断、降级 | Sentinel、Resilience4j |

结论：具体选哪个实现按团队技术栈来；国内项目常搭配 Spring Cloud Alibaba，使用 Nacos 和 Sentinel。

### 它不是什么
Spring Cloud 不是单个框架，而是多个子项目的统称；它也不会替你决定怎么拆服务。组件各自有版本，使用时要选和 Spring Boot 版本匹配的 Spring Cloud 版本，否则可能启动报错。

## 易错点
- 以为 Spring Cloud 就是 Eureka 加 Feign；它是一整套可替换的组件集合
- 随意搭配 Spring Boot 和 Spring Cloud 版本；两者有对应关系，不匹配会出现兼容问题

## 追问
### [f1] Spring Cloud 和 Spring Cloud Alibaba 是什么关系？
Spring Cloud Alibaba 是一个独立项目，按 Spring Cloud 的标准接口接入 Nacos、Sentinel 等阿里系组件。

### [f2] 不用 Spring Cloud 能做微服务吗？
可以。比如用 Dubbo 加 Nacos，或其他语言的方案。Spring Cloud 只是 Java 生态里常见的一种选择。
