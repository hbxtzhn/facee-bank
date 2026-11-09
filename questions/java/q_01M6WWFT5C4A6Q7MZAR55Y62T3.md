---
id: q_01M6WWFT5C4A6Q7MZAR55Y62T3
title: 抽象类和接口有什么区别？
type: concept
difficulty: medium
importance: 3
category: java
tags: [oop]
prerequisites: [q_01M6WWFS81JATQ8XN7SADVDMQR, q_01M6WWFSNX7B3320340RSAHY1W]
appliesTo: ["Java >= 8"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Java 语言规范 SE 21：9.3 Field Declarations（接口字段）与 9.4 Method Declarations（default 方法）", url: "https://docs.oracle.com/javase/specs/jls/se21/html/jls-9.html" }
  - { title: "Java 语言规范 SE 21：8.1.1.1 abstract Classes", url: "https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.1.1.1" }
---

## 一句话
抽象类表示「是什么」的 is-a 关系，单继承、可以带状态和现成的方法；接口表示「能做什么」的能力约定，可以多实现。要共用代码和状态选抽象类，只定义能力选接口。

## 要点
- [kp1|3] 一个类只能继承一个抽象类，但可以实现多个接口
- [kp2|3] 抽象类可以有成员变量和普通方法；接口的变量只能是常量
- [kp3|2] 抽象类表达 is-a（是什么），接口表达能力（能做什么）
- [kp4|2] 接口自 Java 8 起可以有 default 方法，但仍不能有实例状态
- [kp5] 抽象类有构造方法，接口没有

## 详解
### 先搞懂：「身份」和「技能」
一个人的身份只能有一个主要类别，比如「程序员」，这对应抽象类：同类共享一套基础属性和做事方式。但技能可以有很多，会游泳、会开车、会弹琴，这对应接口：谁学会了谁就拥有，互不冲突。

做项目时，`Serializable`（可序列化）、`Comparable`（可比较）都是接口：任何类只需要声明「我也具备这个能力」，不用改变它是什么。

后文要用的词：
- **is-a**：「是一种」的关系，如狗是动物。
- **能力约定**：一个类承诺自己能做某些事，如能被比较。
- **default 方法**：接口里带方法体的方法，Java 8 引入。

### 对比：抽象类和接口
| 维度 | 抽象类 | 接口 |
|---|---|---|
| 继承 / 实现 | 单继承，一个类只能 extends 一个 | 多实现，一个类可以 implements 多个 |
| 成员变量 | 可以有普通成员变量 | 只能是 public static final 常量 |
| 方法实现 | 可以有抽象方法，也可以有普通方法 | 抽象方法，加 default、static 方法（Java 8+） |
| 构造方法 | 有 | 没有 |
| 设计含义 | is-a，同一类事物的共同模板 | can-do，一种能力或规范 |
| 适用场景 | 多个相关类要共享代码和状态 | 跨越不同类型的统一约定 |

结论：先想接口，因为多实现更灵活；如果几个相关类需要共用状态或大段实现代码，再用抽象类。两者也可以搭配：接口定义规范，抽象类给出默认骨架实现。

### 单继承与多实现的影响
一个类只能有一个父类，如果父类位置被抽象类占了，就不能再继承别的类。接口不占这个位置，所以能力型约定用接口更合适。

### 例子：为什么创建线程推荐 Runnable
`Thread` 是个类，继承它就占掉了唯一的父类名额；实现 `Runnable` 接口则没有这个限制。

### 进阶：default 方法和菱形问题（基础薄弱可先跳过）
Java 8 起接口可以有 default 方法，所以能提供默认实现。如果两个接口有同名 default 方法，实现类必须自己重写来消除冲突。

## 示例
```java
interface Swimmer { void swim(); }
interface Flyer   { void fly(); }

abstract class Animal {          // 共同的状态和通用方法
    protected String name;
    void eat() { System.out.println(name + " 吃东西"); }
}

class Duck extends Animal implements Swimmer, Flyer {
    public void swim() { System.out.println("游"); }
    public void fly()  { System.out.println("飞"); }
}
```

## 易错点
- 以为接口里不能有方法体；Java 8 起可以有 default 和 static 方法
- 以为抽象类必须有抽象方法；没有也可以
- 以为接口里的变量能修改；它们默认是 public static final
- 把「功能相同」当成使用抽象类的理由；只有 is-a 且需要共享代码才合适

## 追问
### [f1] 有了 default 方法，接口和抽象类还有什么区别？
接口仍然不能有实例成员变量，没有构造方法，一个类还可以实现多个。抽象类可以保存状态，单继承。

### [f2] 两个接口有同名的 default 方法，实现类怎么办？
实现类必须重写这个方法，来明确选哪个，可以用 `接口名.super.方法名()` 调用其中一个。
