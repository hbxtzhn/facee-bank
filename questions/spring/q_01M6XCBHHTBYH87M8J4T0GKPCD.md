---
id: q_01M6XCBHHTBYH87M8J4T0GKPCD
title: SqlSessionFactoryBuilder 是做什么的？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [mybatis-internals, design-pattern]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`SqlSessionFactoryBuilder` 只负责读取配置、构建 `SqlSessionFactory`，建完就没用了，是方法级的临时对象。

## 要点
- [kp1|3] 作用是读取配置并构建 `SqlSessionFactory`
- [kp2|3] 生命周期是方法级，用完即可丢弃
- [kp3|2] 它是建造者模式的应用
- [kp4] 应用启动时用一次，之后只用工厂

## 详解
### 先搞懂：像一次性的装修队
做项目时，装修队按图纸把房子盖好就走人，之后住的是房子。`SqlSessionFactoryBuilder` 就是装修队，按配置把 `SqlSessionFactory` 建好，任务就结束了。

后文用到的词：

- **建造者模式**：把复杂对象的创建过程单独交给一个对象负责。
- **生命周期**：对象从创建到可以丢弃的时间范围。

### 它做什么
调用 `build(inputStream)`，读取配置文件，创建并返回 `SqlSessionFactory`。

### 为什么是方法级
配置读取一次就够，工厂建好后 Builder 不再被需要。保留它没有价值，所以通常写在一个方法里，用完就让它被回收。

## 示例
```java
InputStream in = Resources.getResourceAsStream("mybatis-config.xml");
SqlSessionFactory factory = new SqlSessionFactoryBuilder().build(in);
```

## 易错点
- 把它当成单例长期保存；其实没有必要
- 把它和 `SqlSessionFactory` 的生命周期混为一谈

## 追问
### [f1] 为什么要把构建过程单独拆出来？
配置解析复杂，拆给 Builder 后，工厂可以专心管理会话，两者职责清晰。
