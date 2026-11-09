---
id: q_01M6XCC3F6EAQBBFMGVT9J2Z5T
title: lazyLoadTriggerMethods 是做什么的？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [association-mapping, configuration]
prerequisites: [q_01M6XCBQWWQPY8ASY7VYDWPJ9R]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`lazyLoadTriggerMethods` 指定调用对象的哪些方法时，会一次性触发它所有延迟加载的属性。默认是 `equals`、`clone`、`hashCode`、`toString`。

## 要点
- [kp1|3] 这个配置项配合延迟加载使用，决定哪些方法调用会触发加载
- [kp2|3] 默认值是 `equals,clone,hashCode,toString`
- [kp3|2] 调用这些方法时，对象里所有延迟属性都会被加载
- [kp4] 值是方法名列表，用逗号分隔，可以改

## 详解
### 先搞懂：延迟加载是什么
查订单时，订单里有个“用户”属性。如果每次查订单都顺便把用户查出来，就多发了一条 SQL。延迟加载的做法是：先不查用户，等到代码真的用到 `order.getUser()` 时再查。

这就像去图书馆借书，目录里有“附录”，你不翻到附录，管理员就不去取它。

- **延迟加载**：关联数据在第一次用到时才去查。
- **代理对象**：开启延迟加载后，MyBatis 返回的对象其实是个代理，拦截方法调用。

### 触发方法：哪些调用会让代理“全部加载”
正常情况下，只有你调用某个属性的 getter 时，才加载那个属性。

但 `equals`、`hashCode`、`toString` 这类方法会用到对象的所有字段，代理没法判断，所以默认约定：调用这几个方法时，把所有延迟属性都加载完。`clone` 同理，复制对象要用到全部内容。

`lazyLoadTriggerMethods` 就是这张“触发名单”，默认就是上面四个。

### 为什么要关心它
最常见的坑是打日志：你写了一句 `log.info("order={}", order)`，会调用 `toString`，结果把所有延迟加载的关联数据都查了出来，延迟加载就白费了，还多发了 SQL。

可以按需调整名单，比如去掉 `toString`。但这样一来，`toString` 输出的未加载属性可能是空的。

## 示例
```xml
<settings>
    <setting name="lazyLoadingEnabled" value="true"/>
    <setting name="lazyLoadTriggerMethods" value="equals,clone,hashCode"/>
</settings>
```

## 易错点
- 没开启延迟加载却调整这个配置，不会有任何效果
- 打日志、调试时打印对象，无意中触发了全部延迟加载
- 以为只有 getter 能触发加载；`toString` 等方法也会

## 追问
### [f1] 延迟加载在什么时候会失效？
对象代理要在会话还没关闭时才能加载。会话关闭后再访问延迟属性，会报错或取不到数据。所以事务外使用延迟属性要特别小心。
