---
id: q_01M6XBH6THZ2XDH676RFKJVH0E
title: 什么是 setter 注入（属性注入）？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [ioc-di]
prerequisites: [q_01M6XBH69B62C0G3H54M5E4X7D]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
setter 注入是 Spring 先用无参构造方法创建对象，再调用它的 setter 方法，把依赖一个个设置进去。

## 要点
- [kp1|3] 先通过无参构造器创建对象，再调用 setter 方法设置依赖
- [kp2|3] 类需要提供无参构造方法和对应的 setter 方法
- [kp3|2] 适合可选依赖，依赖也可以在对象创建后再变化
- [kp4] 缺点是对象创建后到注入完成之间，依赖可能还是空的，字段也不能是 final

## 详解
### 先搞懂：先入职，再慢慢配设备
员工先入职（对象创建），行政随后再给他分配电脑、工位卡、账号（setter 注入）。设备可以陆续发，有的还可以不发，也能换新的。

后文用到的词：
- **setter 方法**：给字段赋值的方法，如 `setUserDao(...)`。
- **无参构造**：不需要任何参数就能创建对象的构造方法。
- **可选依赖**：没有它也能基本工作的依赖。

### 机制：先创建，后设置
1. Spring 调用类的无参构造方法，创建出对象；
2. 根据配置找到需要注入的 Bean；
3. 调用 setter 方法，把依赖传进去；
4. 依赖设置完成后，对象才进入后续的初始化和使用。

在 XML 里通常用 `<property>` 标签，在注解方式里则是把 `@Autowired` 标注在 setter 方法上（标注在字段上是属性注入的另一种写法）。

### 优点和缺点
优点：

- 写法灵活，适合可选依赖；
- 依赖可以在运行中重新设置（需要自己保证线程安全）。

缺点：

- 字段不能声明为 final，对象创建后依赖可以被改动；
- 对象刚创建出来时依赖还没设置，如果有人在注入前就使用，会出现空指针；
- 依赖多了之后，不容易看出这个类到底需要哪些依赖。

### 和构造器注入怎么选
必需依赖优先用构造器注入；只有可选依赖，或者需要在对象创建后调整依赖时，才用 setter 注入。

## 示例
```java
@Service
public class OrderService {
    private UserDao userDao;

    @Autowired // 标注在 setter 上，由容器调用并传入依赖
    public void setUserDao(UserDao userDao) {
        this.userDao = userDao;
    }
}
```

## 易错点
- 类里没有无参构造器，或者没有对应的 setter 方法，注入就无法完成
- 以为 setter 注入和字段注入是一回事；字段注入是直接给字段赋值，不经过 setter
- 在依赖还没注入时就调用依赖，造成空指针

## 追问
### [f1] setter 注入能解决循环依赖吗？
对单例 Bean，Spring 可以通过提前暴露还没填充完的对象来解决 setter 注入的循环依赖，而构造器注入的循环依赖解决不了。

### [f2] 为什么推荐优先构造器注入？
构造器注入创建出的对象依赖完整，字段可以是 final，也更容易暴露设计问题。setter 注入更适合可选依赖。
