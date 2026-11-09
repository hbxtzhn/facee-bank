---
id: q_01M6XBP8FXX5QCW38DR3A5M45A
title: Spring 框架由哪些核心模块组成？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [ioc-di]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
Spring 由核心容器、AOP、数据访问、Web、测试等模块组成，其中核心容器负责创建和管理对象，是其他模块的基础。

## 要点
- [kp1|3] 核心容器包括 core、beans、context、expression，负责 IoC 和依赖注入
- [kp2|3] AOP 模块支持面向切面编程，如事务、日志这类横切功能
- [kp3|2] 数据访问模块包括 JDBC、事务、ORM 等，简化数据库操作
- [kp4|2] Web 模块包括 Spring MVC 和响应式的 WebFlux，用来开发 Web 应用
- [kp5] 测试模块（spring-test）支持在测试中加载容器

## 详解
### 先搞懂：Spring 像一个工具箱
做项目时，我们用 Spring 管理对象、连数据库、开接口、做事务。这些功能不是一整块，而是按职责拆成了多个模块，用哪个引入哪个。

可以把 Spring 想成一个工具箱：最底层有一个放所有工具的「基座」（核心容器），上面分格子放着各类专用工具（AOP、数据访问、Web 等）。

后文用到的词：
- **IoC 容器**：负责创建对象、管理对象之间依赖关系的东西。
- **Bean**：被 Spring 容器管理的对象。
- **模块**：Spring 按功能拆分出的独立 jar 包。

### 核心容器：所有功能的基座
- **spring-core**：基础工具类，是其他模块的底层依赖；
- **spring-beans**：Bean 的定义、创建和装配，提供 IoC 容器的基础实现（BeanFactory）；
- **spring-context**：在前两者基础上提供应用上下文 ApplicationContext，加上国际化、事件发布、资源加载等企业级功能，是我们平时使用 Spring 的入口；
- **spring-expression**：Spring 表达式语言（SpEL），可以在运行时读取和操作对象属性。

### AOP：把横切逻辑抽出来
- **spring-aop**：提供面向切面编程，把日志、权限、事务这类与业务无关、又散落在各处的功能统一处理；
- **spring-aspects**：和 AspectJ 集成。

### 数据访问：简化和数据库打交道
- **spring-jdbc**：封装 JDBC，减少模板代码；
- **spring-tx**：事务管理，支持声明式事务；
- **spring-orm**：整合 Hibernate、JPA 等 ORM 框架。

### Web：开发接口和网站
- **spring-web**：Web 应用的基础支持；
- **spring-webmvc**：Spring MVC，基于 Servlet 的传统 Web 框架；
- **spring-webflux**：响应式 Web 框架，用于非阻塞的场景。

### 测试
- **spring-test**：支持在单元测试和集成测试里加载 Spring 容器、模拟请求。

## 示例
```xml
<!-- 实际项目里常通过 Spring Boot 的 starter 一次引入所需模块，如 Web 开发 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

## 易错点
- 以为 Spring 是一个单一的大 jar；它按模块拆分，可以按需引入
- 把 Spring MVC 当成 Spring 全部；它只是 Web 模块中的一部分
- 以为 spring-beans 就是 ApplicationContext 所在模块；ApplicationContext 在 spring-context

## 追问
### [f1] spring-context 和 spring-beans 是什么关系？
spring-beans 提供最基础的 Bean 容器（BeanFactory）；spring-context 在它上面扩展出 ApplicationContext，增加了国际化、事件、资源加载等功能。

### [f2] Spring Boot 和 Spring 是什么关系？
Spring Boot 不是替代 Spring，而是在 Spring 之上提供自动配置和 starter 依赖，让这些模块更容易组合并开箱即用。
