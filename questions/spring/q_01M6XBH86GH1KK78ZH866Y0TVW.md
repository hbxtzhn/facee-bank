---
id: q_01M6XBH86GH1KK78ZH866Y0TVW
title: 什么是 Bean 的循环依赖？
type: concept
difficulty: easy
importance: 3
category: spring
tags: [bean-lifecycle]
prerequisites: [q_01M6XBH69B62C0G3H54M5E4X7D]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
循环依赖就是 Bean 之间互相依赖形成一个圈，比如 A 依赖 B、B 又依赖 A，依赖自己也算。

## 要点
- [kp1|3] A 依赖 B 且 B 依赖 A，就是循环依赖；A 依赖 A 也是
- [kp2|3] 创建 A 要先有 B，创建 B 又要先有 A，谁都没法先完成
- [kp3|2] 链条可以更长，如 A→B→C→A
- [kp4] 单例 Bean 的部分循环依赖 Spring 能解决，prototype 的不行

## 详解
### 先搞懂：先有鸡还是先有蛋
OrderService 里要用 UserService，UserService 里又要用 OrderService。就像两个人约定“你先把钥匙给我我才给你钥匙”，谁也等不到对方。Spring 创建 Bean 时要先把它依赖的 Bean 准备好再注入，遇到这种圈，就会卡在“谁先创建”上。

后文用到的术语：
- **依赖注入**：Spring 把一个 Bean 需要的其他 Bean 自动塞进来。
- **单例**：容器里只有一个实例，是默认作用域。
- **prototype**：每次获取都新建实例的作用域。

### 常见的三种形态
- **互相依赖**：A 依赖 B，B 依赖 A。
- **自我依赖**：A 依赖 A 自己。
- **多级环**：A 依赖 B，B 依赖 C，C 又依赖 A。

### Spring 怎么对待它
对单例 Bean，如果依赖是通过 setter 或字段注入的，Spring 能靠“提前曝光半成品对象”的办法解决，这套机制叫三级缓存。但如果两边都用构造器注入，就没有办法解决，启动时会抛出 `BeanCurrentlyInCreationException`。prototype 作用域的 Bean 不缓存，出现循环依赖直接报错。

另外，较新的 Spring Boot（2.6 起）默认连能解决的循环依赖也禁止了，需要配置 `spring.main.allow-circular-references=true` 才允许。更推荐的做法是重新拆分职责，把环打断。

## 示例
```java
@Service
public class AService {
    @Autowired
    private BService b;
}

@Service
public class BService {
    @Autowired
    private AService a;
}
```

## 易错点
- 以为循环依赖只有 A 和 B 互相依赖一种；自己依赖自己、多级环也算
- 以为 Spring 能解决所有循环依赖；构造器注入的环不行
- 以为循环依赖只是 Spring 的问题；它说明类的职责划分有问题

## 追问
### [f1] 循环依赖怎么从设计上避免？
把互相依赖的公共逻辑抽到第三个类里，让 A、B 都依赖它；或者用事件、回调代替直接调用。
