---
id: q_01M6XCBMTP5J3M5G2A2VQVKQ1T
title: MyBatis 的全局配置 settings 有哪些常用项？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [configuration]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 3 文档：配置 - settings", url: "https://mybatis.org/mybatis-3/configuration.html" }
  - { title: "MyBatis 源码：XMLConfigBuilder.settingsAsProperties", url: "https://github.com/mybatis/mybatis-3/blob/master/src/main/java/org/apache/ibatis/builder/xml/XMLConfigBuilder.java" }
estimatedMinutes: 2
---

## 一句话
settings 是 MyBatis 的全局开关，常用的有缓存、懒加载、主键回填、驼峰映射和日志实现，改它会影响所有映射语句。

## 要点
- [kp1|3] `cacheEnabled` 控制二级缓存的全局开关，默认开启
- [kp2|3] `mapUnderscoreToCamelCase` 开启下划线转驼峰，默认关闭
- [kp3|2] `lazyLoadingEnabled` 控制关联对象是否懒加载，默认关闭
- [kp4|2] `useGeneratedKeys` 全局启用主键回填，`logImpl` 指定日志实现

## 详解
### 先搞懂：全局开关，一改全变
MyBatis 有很多行为，比如要不要缓存、字段要不要自动转驼峰。每条 SQL 都单独配太累，所以提供一个统一的 `settings` 配置，写一次，全局生效。这就像手机的系统设置：改一个选项，所有应用都受影响。

术语说明：

- **全局配置**：配置文件里的 `settings`，影响整个 MyBatis；
- **懒加载**：关联的对象先不查，等真正用到时再查。

### 常用的几项
- **`cacheEnabled`**：二级缓存的总开关，默认开启。关闭后，所有映射文件里的二级缓存配置都不起作用。
- **`lazyLoadingEnabled`**：关联对象是否懒加载，默认关闭。开启后，关联查询不会立刻执行。
- **`mapUnderscoreToCamelCase`**：把 `user_name` 这样的列自动映射到 `userName` 属性，默认关闭。
- **`useGeneratedKeys`**：全局允许 JDBC 取回自增主键，默认关闭。
- **`logImpl`**：指定日志实现，比如打印 SQL。默认不指定，由 MyBatis 自动找可用的日志框架。

### 怎么配置
在 XML 配置文件里写 `<settings>` 标签，每项是一个 `<setting name value>`。在 Spring Boot 里，则写在配置文件的 `mybatis.configuration` 前缀下。

## 示例
```xml
<settings>
  <setting name="cacheEnabled" value="true"/>
  <setting name="mapUnderscoreToCamelCase" value="true"/>
  <setting name="logImpl" value="STDOUT_LOGGING"/>
</settings>
```

```yaml
# Spring Boot 配置
mybatis:
  configuration:
    map-underscore-to-camel-case: true
```

## 易错点
- 以为 `cacheEnabled` 是一级缓存开关，其实它管二级缓存
- 以为驼峰映射默认就开，实际默认关闭，需要自己打开
- 把 setting 的名字写错，MyBatis 启动时会报错而不是忽略

## 追问
### [f1] lazyLoadingEnabled 开启后有什么要注意的？
关联对象在第一次访问时才查询，可能带来额外的查询次数。会话关闭后再访问还没加载的关联对象，会拿不到数据，要注意会话的范围。
