---
id: q_01M6XBPD1K4DD4GVY53R1EZAA3
title: Spring Boot 是做什么的？
type: concept
difficulty: easy
importance: 3
category: spring
tags: [configuration]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Spring Boot 是 Spring 之上的快速开发框架：靠默认配置和自动配置省掉大量手工配置，内嵌 Tomcat 等服务器，打成 jar 就能直接运行。

## 要点
- [kp1|3] 约定优于配置：提供合理默认值，需要时再覆盖
- [kp2|3] 自动配置：根据引入的依赖和条件，自动把常用 Bean 配好
- [kp3|2] 内嵌 Tomcat、Jetty、Undertow 等服务器，直接运行 jar，不用部署 WAR
- [kp4] 起步依赖（starter）把一类功能需要的依赖打成一个包

## 详解
### 先搞懂：以前搭一个 Web 项目有多麻烦
早期用 Spring 开发 Web 项目，要写大量 XML 配置，要自己对齐各种依赖的版本。还要打成 WAR 包，部署到另一台装好的 Tomcat 里。光搭环境就很花时间，还容易因版本冲突出错。

Spring Boot 好比精装修的房子：水电、厨卫都配好了，拎包入住；想改再动手改，不想改就直接用。

后文用到的术语：
- **约定优于配置**：框架先按常见做法设好默认值，你只配置和默认不同的地方。
- **自动配置**：Spring Boot 根据项目里有什么依赖，自动创建需要的 Bean。
- **内嵌服务器**：Tomcat 等服务器作为库被打进应用里，随应用一起启动。

### 它主要解决了什么
1. **快速创建项目**：用 Spring Initializr 或 IDE 勾选依赖，就能生成可运行的项目骨架。
2. **自动配置**：引入 `spring-boot-starter-web`，Spring MVC、内嵌 Tomcat、JSON 转换等就自动配好；引入数据库相关依赖，数据源也会按配置自动创建。
3. **内嵌服务器**：应用打成可执行 jar，一条 `java -jar` 命令就能启动。
4. **统一的外部配置**：用 `application.yml` 或 `application.properties` 管理配置，也支持环境变量、命令行参数等多种来源。
5. **生产特性**：提供 Actuator，可以查看健康状态、指标等运维信息。

### 自动配置的大致原理
启动类上的 `@SpringBootApplication` 组合了三个注解：`@SpringBootConfiguration`（标明是配置类）、`@EnableAutoConfiguration`（开启自动配置）、`@ComponentScan`（扫描组件）。其中 `@EnableAutoConfiguration` 会读取各个依赖里登记的自动配置类，并根据条件注解（如“类路径下有某个类才生效”“你没有自己定义这个 Bean 才生效”）决定是否创建对应的 Bean。

## 示例
```java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

## 易错点
- 以为 Spring Boot 是替代 Spring 的新框架；它建立在 Spring 之上，简化配置，底层仍是 Spring
- 以为“自动配置”就是不用配置了；它只是提供默认值，业务相关的配置仍要自己写
- 以为 Spring Boot 一定要用内嵌 Tomcat；也可以换成 Jetty、Undertow，或打成 WAR 部署到外部容器

## 追问
### [f1] @SpringBootApplication 是由哪几个注解组成的？
`@SpringBootConfiguration`、`@EnableAutoConfiguration` 和 `@ComponentScan`。

### [f2] 自动配置的类从哪里来？
各个依赖（starter）里登记了自己的自动配置类，Spring Boot 启动时读取这些登记信息，再用条件注解判断是否生效。
