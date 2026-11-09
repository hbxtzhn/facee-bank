---
id: q_01M6XCBQWWQPY8ASY7VYDWPJ9R
title: 什么是延迟加载（懒加载）？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [association-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
延迟加载就是关联对象先不查，等代码真正访问它时才发 SQL 去查；MyBatis 里要把 `lazyLoadingEnabled` 设为 true 才生效。

## 要点
- [kp1|3] 延迟加载：关联对象用到时才查询，没用到就不发 SQL
- [kp2|3] 需要在 settings 里设置 `lazyLoadingEnabled` 为 true
- [kp3|2] 它只对嵌套查询（`select` 属性）生效，联表嵌套结果不能延迟
- [kp4] 默认是关闭的，也可以在单个关联上用 `fetchType` 覆盖

## 详解
### 先搞懂：先查订单，要不要顺便查用户
查一个订单列表，页面只显示订单号，用不到下单的用户信息。如果每个订单都顺带把用户也查出来，就白白多发了 SQL。

可以把它想成外卖订单：先给你订单摘要，点开详情时才去加载菜品图片。没点开就不用加载。

后文用到的术语：
- **立即加载**：查主对象时，关联对象一起查出来。
- **延迟加载**：查主对象时只查主对象，关联对象等用到再查。

### 怎么开启
全局开关写在配置文件的 settings 里：

```xml
<settings>
  <setting name="lazyLoadingEnabled" value="true"/>
</settings>
```

开启后，用 `<association>` 或 `<collection>` 配合 `select` 属性，关联对象就变成延迟加载。想让个别关联不延迟，可以在这个标签上写 `fetchType="eager"`，反过来 `fetchType="lazy"` 则让它延迟。

### 效果是什么样
- 调用 `order.getPay()` 之前，数据库里只收到查订单的那一条 SQL。
- 第一次调用 `order.getPay()` 时，才发出查支付的 SQL，结果存进对象。
- 之后再调用，直接用已经存好的值，不会再查。

### 有什么限制
- 只有嵌套查询才能延迟，因为它的关联 SQL 本来就是单独一条。联表的嵌套结果一次就查完了，没有可延迟的部分。
- 对象要在 SqlSession 还没关闭时访问，关闭后再访问关联属性，会因为没法再查而出错。

## 易错点
- 以为开了 `lazyLoadingEnabled` 所有关联都延迟；联表嵌套结果不受影响
- 在 Session 关闭之后才访问关联属性；此时已不能再发查询
- 打印或序列化对象时触发了所有关联属性的 getter；会把延迟的数据全部查出来

## 追问
### [f1] `fetchType` 和全局开关谁优先？
关联标签上写的 `fetchType` 优先于全局的 `lazyLoadingEnabled`。所以可以全局关闭、个别关联打开，也可以反过来。
