---
id: q_01M6XCBTAZXEBK2S8JSVVGBDNY
title: 跨 namespace 共享缓存怎么做（cache-ref）？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [mybatis-cache]
prerequisites: [q_01M6XCBSNWRWKD6XSZ1X4ZS2CS]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
二级缓存默认按 namespace 隔离，想让两个 Mapper 共用同一块缓存，就在其中一个映射文件里写 `<cache-ref namespace="..."/>` 引用另一个。

## 要点
- [kp1|3] `<cache-ref namespace="...">` 让当前 Mapper 引用别的 namespace 的缓存
- [kp2|3] 两个 Mapper 共用同一块缓存，数据互通
- [kp3|2] 任何一方执行增删改，这块共享缓存都会被清空
- [kp4] 引用方不用再写自己的 `<cache>`

## 详解
### 先搞懂：为什么需要共享
订单和订单明细是两个 Mapper，查订单时会联表查出明细。你更新了明细，却只清了明细 Mapper 的缓存，订单 Mapper 缓存里存的联表结果还是旧的。

可以把它想成两个部门各有一块公告栏：明细部门改了通知，订单部门的公告栏没撤，别人还看着旧信息。让两个部门共用同一块公告栏，改一次，全都更新。

后文用到的术语：
- **cache-ref**：缓存引用，指向另一个 namespace 的缓存。

### 怎么写
在订单的映射文件里：

```xml
<mapper namespace="com.demo.mapper.OrderMapper">
  <cache-ref namespace="com.demo.mapper.OrderItemMapper"/>
</mapper>
```

这样 `OrderMapper` 里的查询，缓存放在 `OrderItemMapper` 的那块缓存里。被引用的一方要有自己的 `<cache>` 配置。

### 效果
- 两个 Mapper 的查询结果共享同一块缓存。
- 任意一方的增删改，清空的是这块共享缓存，所以两边都不会读到旧数据。
- 缓存的容量、回收策略等，沿用被引用方的配置。

### 注意取舍
共享后，缓存的范围变大，一次更新清掉的内容更多，命中率会下降。所以只在确有关联查询的 Mapper 之间使用，不要所有 Mapper 都共享。

## 易错点
- 只在引用方写了 `cache-ref`，被引用方却没有 `<cache>`；没有可共享的缓存
- 以为共享是双向的；`cache-ref` 是单向引用，另一方没写时，它自己的缓存不受影响
- 滥用共享；一个 Mapper 更新会清掉所有人的缓存

## 追问
### [f1] 联表查询为什么容易出现缓存不一致？
联表结果缓存在发起查询的 Mapper 下，但更新某张被联的表时，清的是另一个 Mapper 的缓存。用 `cache-ref` 把它们放进同一块缓存可以缓解。
