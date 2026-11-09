---
id: q_01M6XCBSNWRWKD6XSZ1X4ZS2CS
title: 什么是 MyBatis 的二级缓存，怎么开启？
type: concept
difficulty: easy
importance: 3
category: spring
tags: [mybatis-cache]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
references:
  - { title: "MyBatis 3 文档：Mapper XML 文件（cache 元素与默认值、事务性）", url: "https://mybatis.org/mybatis-3/sqlmap-xml.html" }
  - { title: "MyBatis 3 文档：配置（settings：cacheEnabled）", url: "https://mybatis.org/mybatis-3/configuration.html" }
---

## 一句话
二级缓存作用于 Mapper 的 namespace，多个 SqlSession 可以共享；默认关闭，在映射文件里加 `<cache/>`，并让实体类实现 Serializable 才能用。

## 要点
- [kp1|3] 二级缓存按 namespace 划分，多个 Session 可以共享
- [kp2|3] 在映射文件里加 `<cache/>` 标签即可开启
- [kp3|2] 实体类要实现 `Serializable`，缓存可能需要序列化
- [kp4] 事务提交或 Session 关闭后，查询结果才真正写入二级缓存

## 详解
### 先搞懂：一级缓存是私人小本子，二级缓存是公共公告栏
一级缓存只在自己的 Session 里有用，另一个 Session 看不到。二级缓存是同一个 Mapper 的所有 Session 共用的：A 查出来放上去，B 来查时就能直接用。

后文用到的术语：
- **namespace**：映射文件的命名空间，通常对应一个 Mapper 接口。二级缓存按它来划分。
- **序列化**：把对象变成字节，方便存储或复制。

### 怎么开启
全局的 `cacheEnabled` 设置默认就是开启的，所以实际只需要两步：

1. 在 Mapper 的 XML 里加 `<cache/>`。
2. 让被缓存的实体类实现 `Serializable`。

也可以用注解方式，在 Mapper 接口上加 `@CacheNamespace`。

### 查询的顺序
执行一条查询时，MyBatis 按顺序找：先看二级缓存，再看一级缓存，最后才去数据库。

### 什么时候才写进二级缓存
查询结果不是立刻写入二级缓存，而是先放在当前 Session 的暂存区，等事务提交或 Session 关闭后，才真正进入二级缓存。所以别的 Session 在这之前读不到。

### 默认配置是什么
只写 `<cache/>` 时，使用默认值：回收策略 LRU，容量 1024 个对象，不按时间刷新，返回的对象可读写。具体含义后面的题会讲。

## 示例
```xml
<mapper namespace="com.demo.mapper.UserMapper">
  <cache/>
  <select id="selectById" resultType="User">
    select * from user where id = #{id}
  </select>
</mapper>
```

```java
public class User implements Serializable {
    private Long id;
    private String name;
}
```

## 易错点
- 开了 `<cache/>` 但实体类没实现 `Serializable`；使用默认的可读写模式时，取缓存会因为序列化出错
- 以为查完马上能被别的 Session 命中；要等提交或关闭 Session 之后
- 以为全局设置默认是关闭的；`cacheEnabled` 默认是开着，但每个 Mapper 不写 `<cache/>` 就不会缓存

## 追问
### [f1] 二级缓存的作用范围为什么是 namespace？
缓存对象归属于某个 Mapper，更新这个 Mapper 的数据时，只需要清空这一个 namespace 的缓存，范围清晰，也便于管理。
