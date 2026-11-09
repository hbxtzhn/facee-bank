---
id: q_01M6XBH7KJJCH34YCJTAS4MCP2
title: Spring Bean 的默认作用域是什么？
type: concept
difficulty: easy
importance: 3
category: spring
tags: [bean-lifecycle]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Spring Bean 默认是 singleton（单例）：容器里这个 Bean 只有一个实例，所有用到它的地方共享；如果改成 prototype，则每次获取都会新建一个实例。

## 要点
- [kp1|3] 默认作用域是 singleton，一个容器中每个 Bean 定义只有一个实例
- [kp2|3] prototype 作用域每次获取都会创建新实例
- [kp3|2] 单例被多个线程共享，有可变成员变量时要注意线程安全
- [kp4] Web 应用里还有 request、session 等作用域，分别对应一次请求和一个会话
- [kp5] 用 @Scope 注解修改作用域

## 详解
### 先搞懂：全公司共用一台打印机，还是每人一台
- **singleton（单例）**：全公司共用一台打印机，大家用的是同一个。省资源，但要注意别互相干扰。
- **prototype（原型）**：每个人领一台新打印机，互不影响，但数量会很多。

Spring 默认采用第一种：容器启动时创建好一个对象，之后谁来要都给同一个。

后文用到的词：
- **作用域（scope）**：Bean 的实例在什么范围内共享、存活多久。
- **单例**：容器里只有一个实例。
- **成员变量**：类里定义的字段，属于对象本身。

### singleton：默认，只有一个
- 同一个容器里，同一个 Bean 定义只创建一个实例；
- 多个类注入同一个 Bean，它们拿到的是同一个对象；
- 默认在容器启动时就创建好，之后一直存在，直到容器关闭。

项目里的 Controller、Service、Dao 通常都是单例，所以它们一般是无状态的，也就是没有会变化的成员变量。

### prototype：每次获取都新建
把作用域改成 prototype 后，每次从容器取（或注入）都会得到一个新对象。适合有状态、不能共享的对象。需要注意：容器只负责创建，不负责管理它之后的销毁。

### 其他作用域
在 Web 应用里还有：

- `request`：每个 HTTP 请求一个实例；
- `session`：每个用户会话一个实例。

### 怎么设置
用 `@Scope` 注解标注在类或 `@Bean` 方法上；XML 里用 `scope` 属性。

## 示例
```java
@Component
@Scope("prototype") // 不写时默认就是 singleton
public class ShoppingCart {
    // 每次获取都是一个新的购物车对象
}
```

## 易错点
- 以为每次注入都会新建对象；默认单例，注入的是同一个
- 在单例 Bean 里放可变的成员变量（如用户信息），多个请求会互相覆盖
- 单例里注入 prototype Bean，以为每次调用都是新的；注入只发生一次，拿到的始终是同一个新对象
- 以为单例就是线程安全的；单例只是实例唯一，线程安全要看有没有可变状态

## 追问
### [f1] Spring 的单例和设计模式里的单例有什么区别？
Spring 的单例是针对一个容器里每个 Bean 定义只有一个实例；而设计模式的单例是整个 JVM 里这个类只有一个实例。

### [f2] 单例 Bean 里需要每次拿到新的 prototype 对象怎么办？
可以注入 `ObjectProvider` 在需要时再获取，或者使用方法注入，每次从容器里重新取。
