---
id: q_01M6XBPDSXNCW68HXAN8KRD74B
title: Spring Boot 的自动配置是怎么加载配置类的？
type: concept
difficulty: hard
importance: 3
category: spring
tags: [configuration, bean-lifecycle]
prerequisites: [q_01M6XBPD1K4DD4GVY53R1EZAA3, q_01M6XBPD9MKWKCQMHJZQ3JMVHC, q_01M6XBPDHPPBTGBSTVACC74YY1]
appliesTo: ["Spring Boot >= 2.7"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 5
---

## 一句话
`@EnableAutoConfiguration` 通过 `@Import` 引入选择器，选择器从约定的清单文件里读出自动配置类，再按条件注解过滤后注册。

## 要点
- [kp1|3] `@EnableAutoConfiguration` 用 `@Import` 导入 `AutoConfigurationImportSelector`
- [kp2|3] 选择器从各 jar 的清单文件读取候选自动配置类全名
- [kp3|2] 候选类再经 `@Conditional` 系列条件过滤，满足才生效
- [kp4|2] 2.7 起清单在 `AutoConfiguration.imports` 文件，旧版在 `spring.factories`
- [kp5] 用户自己定义的 Bean 优先，自动配置用 `@ConditionalOnMissingBean` 让位

## 详解
### 先搞懂：自动配置像"按需上菜"
做项目时，你加了 Redis 的依赖，没写任何配置，就能直接注入 `RedisTemplate`。这像自助餐厅：后厨准备了几十道菜（所有可能的配置类），但只有你"点"的才会端上桌。你点菜的方式，就是在项目里引入了哪些依赖。

后文用到的词：

- **自动配置类**：Spring Boot 各模块自带的配置类，里面声明了常用 Bean。
- **清单文件**：放在 jar 里的一份文本，列出该 jar 提供的自动配置类全名。
- **条件注解**：形如 `@ConditionalOnClass` 的注解，条件满足这个配置才生效。

### 第一步：@Import 把选择器请进来
`@SpringBootApplication` 里包含 `@EnableAutoConfiguration`。后者本身带着一个 `@Import(AutoConfigurationImportSelector.class)`。

`@Import` 的作用是让 Spring 在解析配置类时，额外导入指定的类。这里导入的是一个选择器：它不是 Bean，而是"返回一批类名，让 Spring 把它们当配置类"的工具。

### 第二步：读取候选清单
选择器启动后，会去 classpath（类路径）上所有 jar 里找清单文件，把里面列出的自动配置类全名都读出来，作为候选。

清单的位置随版本变化：

| 版本 | 清单位置 |
|---|---|
| Spring Boot 2.7 之前 | `META-INF/spring.factories` 中的 `EnableAutoConfiguration` 项 |
| Spring Boot 2.7 起 | `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` |
| Spring Boot 3.0 起 | 只读 `.imports` 文件，不再读 `spring.factories` 里的这一项 |

### 第三步：按条件过滤再注册
候选类有几百个，不会全部生效。每个自动配置类上都有条件注解，常见的有：

- `@ConditionalOnClass`：classpath 里有某个类才生效，比如有 Redis 客户端才配 Redis；
- `@ConditionalOnMissingBean`：你没自己定义同类型 Bean 才生效，也就是用户配置优先；
- `@ConditionalOnProperty`：配置文件里开了某个开关才生效。

条件不满足的类会被丢掉，满足的才被注册进容器。另外，用户可以通过 `exclude` 手动排除某个自动配置类。

### 进阶：延迟导入（基础薄弱可先跳过）
`AutoConfigurationImportSelector` 实现的是 `DeferredImportSelector`，意思是它的导入会推迟到用户自己的配置类都处理完之后。这样 `@ConditionalOnMissingBean` 才能先看到用户定义的 Bean，再决定自己要不要生效。

## 示例
```java
@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

## 易错点
- 以为所有自动配置类都会生效；实际大多数会被条件注解过滤掉
- 以为自动配置会覆盖自己写的 Bean；实际通常用 `@ConditionalOnMissingBean` 主动让位
- 照旧教程把自动配置写进 `spring.factories`，新版本里不再读取

## 追问
### [f1] 怎么自己写一个自动配置？
写一个带 `@AutoConfiguration` 的配置类，里面用条件注解声明 Bean，再把类全名写进 `.imports` 清单文件。这样别的项目引入你的 jar 就能自动生效。

### [f2] 怎么知道哪些自动配置生效了？
启动时加上 `--debug` 参数，会输出自动配置报告，列出哪些匹配、哪些不匹配以及原因。
