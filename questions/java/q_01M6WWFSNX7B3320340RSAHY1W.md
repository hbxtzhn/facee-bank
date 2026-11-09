---
id: q_01M6WWFSNX7B3320340RSAHY1W
title: 什么是接口？
type: concept
difficulty: easy
importance: 2
category: java
tags: [oop]
prerequisites: [q_01M6WWFMMAVFDAFR8718MYN95W]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
接口是一组方法的约定，只规定「能做什么」，由类用 implements 去实现，一个类可以同时实现多个接口。

## 要点
- [kp1|3] 接口定义一组方法的约定，类用 implements 实现它
- [kp2|3] 一个类可以实现多个接口，弥补了类只能单继承的限制
- [kp3|2] 接口不能直接 new，需要实现类提供方法的具体实现
- [kp4] 接口类型的引用可以指向实现类对象，是多态的常用方式

## 详解
### 先搞懂：插座和插头
手机充电器和插座之间有一个约定：插头的形状。只要符合约定，不管哪个品牌的充电器都能插上。接口就是这样一份「约定」：规定要有哪些方法，不管谁来实现。

做项目时，你写 `List<String> list = new ArrayList<>()`，`List` 是接口，`ArrayList` 是实现类，换成 `LinkedList` 也行，使用者的代码不用变。

后文要用的词：
- **实现类**：用 `implements` 去实现接口的类。
- **抽象方法**：只有声明、没有方法体的方法。

### 怎么写
```java
interface Payment {
    void pay(int amount);        // 默认就是 public abstract
}
class WechatPay implements Payment {
    public void pay(int amount) { System.out.println("微信支付 " + amount); }
}
```
实现类必须实现接口里所有抽象方法，并且实现时要写成 `public`。

### 接口的特点
- 不能直接实例化。
- 接口里的方法默认是 `public abstract`；Java 8 起，接口还可以有 `default` 方法和 `static` 方法（带方法体）。
- 接口里的变量默认是 `public static final`，即常量。
- 一个接口可以继承多个接口：`interface C extends A, B`。

### 多实现：弥补单继承
Java 类只能继承一个父类，但可以实现多个接口。一个类可以同时是「可序列化的」「可比较的」，就靠同时实现多个接口。

### 为什么要用接口
调用方依赖接口而不依赖具体实现，换实现时调用代码不用改，也便于测试时用假的实现替代。

## 易错点
- 以为实现类可以只实现一部分抽象方法；除非它自己是抽象类，否则必须全部实现
- 实现接口方法时漏写 public，编译报错，因为权限不能比接口小
- 以为接口里的变量可以修改；它们是常量

## 追问
### [f1] 接口可以继承接口吗？
可以，用 extends，而且可以同时继承多个。

### [f2] 接口里能写方法体吗？
Java 8 起，可以用 `default` 或 `static` 修饰，写带方法体的方法；Java 9 起还可以写 `private` 方法。
