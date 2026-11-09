---
id: q_01M6XCC6DPABMYNAKR0E1ANEVQ
title: Spring Boot 怎么读取配置文件（application.yml）和 @Value？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [configuration]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
把配置项写在 `application.yml` 里，Spring Boot 启动时自动加载；在 Bean 字段上用 `@Value("${key}")` 就能把对应的值注入进来。

## 要点
- [kp1|3] `application.yml` 放在 `resources` 目录下，Boot 启动时自动读取
- [kp2|3] `@Value("${a.b}")` 按占位符取配置值，注入到字段或参数
- [kp3|2] 可以写默认值：`${a.b:默认值}`，配置缺失时不会启动报错
- [kp4] 配置项较多时，可改用 `@ConfigurationProperties` 批量绑定成对象

## 详解
### 先搞懂：数据库地址、开关不要写死在代码里
项目里的数据库地址、端口、功能开关，如果写死在代码中，换一个环境就得改代码重新打包。

可以把它想成一张贴在墙上的配置清单：代码需要什么，就去清单上查。清单换了一张，代码不用动。`application.yml` 就是这张清单，`@Value` 就是代码去查清单的动作。

后文用到的术语：

- **配置项**：yml 里的一个键值对；
- **占位符**：写成 `${...}` 的形式，表示这里的值要去配置里查。

### application.yml：层级写法的配置文件
yml 用缩进表示层级。下面的配置，对应的键就是 `app.name` 和 `app.max-size`：

```yaml
app:
  name: demo
  max-size: 100
```

Spring Boot 启动时会自动读取 `resources` 目录下的 `application.yml`。

### @Value：按键取值
在字段上写 `@Value("${app.name}")`，Spring 创建这个 Bean 时，会把配置里 `app.name` 对应的值填进去。

- 类必须是 Spring 管理的 Bean，如加了 `@Component`，否则不会注入；
- 配置里找不到这个键，启动会报错；想容错就写默认值，如 `${app.name:unknown}`；
- 值会自动转成字段的类型，如 `int`、`boolean`。

## 示例
```java
@Component
public class AppInfo {

    @Value("${app.name}")
    private String name;

    @Value("${app.max-size:50}")
    private int maxSize;
}
```

## 易错点
- 用 `new AppInfo()` 创建对象，字段不会被注入，必须由 Spring 创建
- 把 `@Value` 写在 `static` 字段上，注入不会生效
- 键名拼错或层级不对，启动时报找不到占位符
- 以为 `@Value` 能随时刷新；配置改了通常要重启，除非用了配置中心的动态刷新

## 追问
### [f1] @Value 和 @ConfigurationProperties 怎么选？
只取一两个值，用 `@Value` 最简单。同一前缀下有多项配置，用 `@ConfigurationProperties` 绑定到一个类里，更清晰，也方便做校验。

### [f2] 不同环境的配置怎么区分？
可以写多个文件，如 `application-dev.yml`、`application-prod.yml`，再用 `spring.profiles.active` 指定启用哪一个。
