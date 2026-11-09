---
id: q_01M6XCBSXX78M3WZPPJ1YG0VCW
title: 二级缓存怎么接入 Ehcache 等第三方存储？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [mybatis-cache, cache-pattern]
prerequisites: [q_01M6XCBSNWRWKD6XSZ1X4ZS2CS]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
`<cache>` 标签的 `type` 属性可以指定一个实现了 MyBatis `Cache` 接口的类，换成 Ehcache 等第三方缓存，缓存数据就不再只存在本机内存里。

## 要点
- [kp1|3] `<cache type="...">` 的 `type` 指定自定义的缓存实现类
- [kp2|3] 自定义缓存类必须实现 MyBatis 的 `Cache` 接口
- [kp3|2] 常见做法是引入 mybatis-ehcache 之类的适配包
- [kp4] 缓存读写模式由 MyBatis 的缓存装饰器统一处理

## 详解
### 先搞懂：默认缓存放在 JVM 内存里
MyBatis 自带的二级缓存是一个 `HashMap` 一类的内存结构，放在当前应用的进程里。应用一重启，缓存就没了。多台服务器各有各的缓存，彼此不同步。

可以把它想成每个分店各自的小黑板：想让总部统一管理，就要换成一块共享的大屏幕。接入第三方缓存，就是换大屏幕。

后文用到的术语：
- **`Cache` 接口**：MyBatis 对缓存的统一抽象，规定了放、取、删、清空等方法。
- **适配包**：第三方缓存厂商或社区写的实现类，把自己的缓存包装成 `Cache` 接口。

### 怎么接入
1. 引入第三方缓存的依赖和适配包，例如 Ehcache 的适配包。
2. 在映射文件里用 `type` 指定实现类：

```xml
<cache type="org.mybatis.caches.ehcache.EhcacheCache"/>
```

3. 按适配包的要求，配置缓存自己的参数文件，如容量和过期时间。

### 原理：为什么能换
MyBatis 只依赖 `Cache` 接口，不关心里面怎么存。`type` 里写什么类，就用什么类来存取。所以不改业务代码，只改配置，就能换存储。

### 自己写一个行不行
可以。实现 `Cache` 接口的几个方法，核心是 `putObject`、`getObject`、`removeObject`、`clear`，再用 `type` 指向它。比如存到 Redis 里，让多台服务器共享。

### 进阶：读写和并发（基础薄弱可先跳过）
MyBatis 会在你的实现外面包上若干装饰器，用来处理事务暂存、序列化、日志等，自定义实现只需要关注存取本身。需要的话，实现类还可以接收 `<property>` 配置的参数。

## 易错点
- 只加了 `type`，却没引入对应的依赖；启动时找不到类
- 以为换了第三方缓存就自动解决了多服务器一致性；是否一致取决于这个缓存本身是否集中存储
- 以为一级缓存也能这样换；`type` 只作用于二级缓存

## 追问
### [f1] 第三方缓存和二级缓存的默认实现，对业务代码有影响吗？
基本没有影响，业务代码只调 Mapper 方法。差别主要在存储位置、容量、过期方式和多服务器是否共享，这些都由缓存本身决定。
