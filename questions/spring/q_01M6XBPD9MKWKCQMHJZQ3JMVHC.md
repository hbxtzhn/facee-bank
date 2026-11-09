---
id: q_01M6XBPD9MKWKCQMHJZQ3JMVHC
title: 什么是 Spring Boot Starter（起步依赖）？
type: concept
difficulty: easy
importance: 3
category: spring
tags: [configuration]
prerequisites: [q_01M6XBPD1K4DD4GVY53R1EZAA3]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Starter 把某类功能需要的依赖打包成一个起步依赖，引入后配合自动配置，基本不用写配置就能用。

## 要点
- [kp1|3] Starter 把某个功能需要的多个依赖整合在一起，只需引入一个
- [kp2|3] 依赖版本由 Spring Boot 统一管理，不用逐个对齐版本
- [kp3|2] Starter 和自动配置配合：引入依赖后，对应的默认配置自动生效
- [kp4] 官方命名 spring-boot-starter-*，第三方习惯命名 xxx-spring-boot-starter

## 详解
### 先搞懂：做个 Web 项目要引多少依赖
做 Web 项目，需要 Spring MVC、JSON 转换库、校验、日志、内嵌 Tomcat 等十几个依赖。以前要自己一个个找、一个个加，还要确认它们的版本能互相配合，一不小心就冲突。

Starter 像一份套餐：你点“Web 套餐”，里面的主食、饮料、配菜都配齐了，不用逐样点单。

后文用到的术语：
- **依赖（dependency）**：项目用到的第三方库，在 Maven 或 Gradle 里声明。
- **版本管理**：Spring Boot 提前整理好一批互相兼容的版本，你不写版本号也能用。
- **自动配置**：根据依赖自动创建需要的 Bean。

### Starter 带来了什么
1. **一个依赖顶一组**：比如 `spring-boot-starter-web` 包含 Spring MVC、内嵌 Tomcat、JSON 处理等；
2. **版本不用操心**：由 Spring Boot 的依赖管理统一指定，常见依赖不需要写版本号；
3. **配合自动配置**：引入后，Spring Boot 检测到类路径上有相关类，就自动创建默认 Bean。

### 常见的 Starter
- `spring-boot-starter-web`：开发 Web 和 REST 接口
- `spring-boot-starter-test`：测试相关库
- `spring-boot-starter-data-redis`：访问 Redis
- `spring-boot-starter-jdbc`：使用 JDBC 访问数据库

### 自己写 Starter 的思路
想把公共功能给多个项目共用，可以做成自己的 Starter。写一个自动配置类，在约定的文件里登记它。用条件注解控制何时生效，再打成依赖包。别人引入后就能直接用。

## 示例
```xml
<!-- 引入 Web 起步依赖，不用写版本号 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

## 易错点
- 以为 Starter 本身包含了所有配置逻辑；它主要是依赖的集合，真正创建 Bean 的是自动配置类
- 随意给 Starter 里的依赖指定别的版本，可能破坏 Spring Boot 的版本兼容性
- 以为所有 Starter 都由官方提供；第三方也可以提供自己的 Starter

## 追问
### [f1] Starter 和自动配置是什么关系？
Starter 负责把依赖带进来，自动配置负责根据这些依赖创建默认 Bean，两者配合才做到引入即用。

### [f2] 为什么引入 Starter 时常常不用写版本号？
项目继承了 Spring Boot 的依赖管理（如 `spring-boot-starter-parent` 或 BOM），其中已经规定了常见依赖的版本。
