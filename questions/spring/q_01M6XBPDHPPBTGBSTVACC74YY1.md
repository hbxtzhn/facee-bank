---
id: q_01M6XBPDHPPBTGBSTVACC74YY1
title: "@SpringBootApplication 注解是做什么的？"
type: concept
difficulty: easy
importance: 3
category: spring
tags: [configuration, ioc-di]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`@SpringBootApplication` 是启动类上的组合注解，一个注解就同时打开配置类、自动配置和组件扫描三个功能。

## 要点
- [kp1|3] 它是组合注解，包含三个注解：配置类、自动配置、组件扫描
- [kp2|3] `@EnableAutoConfiguration` 负责按依赖自动装配 Bean
- [kp3|2] `@ComponentScan` 默认扫描启动类所在包及其子包
- [kp4] `@SpringBootConfiguration` 表明启动类本身是一个配置类

## 详解
### 先搞懂：为什么启动类上只写一个注解就能跑
做项目时，你只在启动类上写了一个注解，Controller、Service 就都能用，数据库连接也自动配好了。这像租房时选了"精装修全包套餐"：套餐里包含了家具、网络、水电开通，你不用一样一样买。

后文用到的词：

- **配置类**：专门用来声明 Bean（由 Spring 管理的对象）的类。
- **组件扫描**：Spring 去指定的包里找带 `@Component`、`@Service` 等注解的类，把它们注册成 Bean。
- **自动配置**：Spring Boot 根据你引入的依赖，自动把常用 Bean 配好。

### 三个注解各管一件事
`@SpringBootApplication` 把下面三个注解合在了一起：

1. `@SpringBootConfiguration`：本质是 `@Configuration`，说明启动类自己就是一个配置类，里面可以直接写 `@Bean` 方法。
2. `@EnableAutoConfiguration`：开启自动配置，是 Spring Boot "约定大于配置"的核心。
3. `@ComponentScan`：开启组件扫描。默认从启动类所在的包开始，往下扫描所有子包。

### 一个常见后果：启动类的位置
组件扫描默认从启动类所在包往下扫，所以启动类要放在项目的根包下。如果 Controller 放在启动类的包之外，就扫不到，接口会 404。

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
- 以为自动配置靠 `@ComponentScan` 实现；实际由 `@EnableAutoConfiguration` 负责
- 把启动类放进子包，导致上层包里的 Bean 扫描不到

## 追问
### [f1] 如果 Controller 不在启动类所在的包下怎么办？
可以把启动类移到根包，或者在 `@SpringBootApplication` 里用 `scanBasePackages` 指定要扫描的包。
