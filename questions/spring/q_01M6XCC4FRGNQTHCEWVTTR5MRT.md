---
id: q_01M6XCC4FRGNQTHCEWVTTR5MRT
title: MyBatis 怎么注册 Mapper 映射文件（resource、class、package）？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [configuration, mybatis-internals]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
在 `mybatis-config.xml` 的 `<mappers>` 里注册 Mapper，有三种写法：`resource` 指定 XML 路径，`class` 指定接口，`package` 扫描整个包。

## 要点
- [kp1|3] `resource`：写 XML 映射文件在类路径下的位置
- [kp2|3] `class`：写 Mapper 接口的全限定名
- [kp3|2] `package`：写包名，扫描包下所有 Mapper 接口
- [kp4|2] `class` 和 `package` 要求 XML 与接口同名、同包路径
- [kp5] 还有 `url` 方式，用完整路径引用文件，较少使用

## 详解
### 先搞懂：为什么要注册
你写了 Mapper 接口和 XML，但 MyBatis 启动时并不会自己去找它们。必须告诉它“这些文件在哪”，它才会解析里面的 SQL。

这就像开会要发通知：不发通知，人不知道要来。

- **映射文件**：写 SQL 的 XML。
- **注册**：让 MyBatis 知道有哪些映射需要加载。

### 三种写法
- **resource**：直接指向 XML 文件。不要求有接口，适合只用 XML 的老写法。
- **class**：指向接口。MyBatis 会找与接口同名、同路径的 XML；如果没有 XML，就读接口上的注解 SQL。
- **package**：指向一个包，包里所有接口都会被注册，最省事，新增 Mapper 不用再改配置。

### 怎么选
Mapper 多时用 `package`，新增接口不用改配置。需要精确控制或单个文件时用 `resource` 或 `class`。

### 和 Spring 整合后
Spring 项目里，一般不在这里注册。接口靠 `@MapperScan` 扫描，XML 靠 `mapperLocations` 指定。

## 示例
```xml
<mappers>
    <mapper resource="mapper/UserMapper.xml"/>
    <mapper class="com.example.mapper.OrderMapper"/>
    <package name="com.example.mapper"/>
</mappers>
```

## 易错点
- 用 `class` 或 `package` 时，XML 与接口不同名或不在对应路径，XML 没被加载
- 同一个 Mapper 用两种方式重复注册，可能报重复定义的错误
- Spring 整合后还在这里配置，却没有扫描接口，注入时找不到 Bean

## 追问
### [f1] 构建后 XML 找不到怎么办？
Maven 默认只把 `resources` 目录里的文件打进类路径。XML 放在 `src/main/java` 下，需要在构建配置里额外声明包含，否则运行时找不到。
