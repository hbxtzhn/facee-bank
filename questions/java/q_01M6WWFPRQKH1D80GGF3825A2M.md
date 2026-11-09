---
id: q_01M6WWFPRQKH1D80GGF3825A2M
title: this 指的是什么？
type: concept
difficulty: easy
importance: 1
category: java
tags: [oop]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 1
---

## 一句话
this 是当前对象的引用，指向正在执行这段代码的那个对象本身。

## 要点
- [kp1|3] this 代表当前对象，哪个对象调用方法，this 就指向哪个对象
- [kp2|3] this 只能用在实例方法和构造方法里，不能用在 static 方法里
- [kp3|2] 最常见用途是区分与形参同名的成员变量
- [kp4] this 也可以把当前对象传给别的方法

## 详解
### 先搞懂：「我」是谁
你在公司说「我」，指的就是说话的那个人；换一个人说，「我」就指另一个人。`this` 就是对象代码里的「我」。

做项目时：`User a` 和 `User b` 都调用了 `getName()`，方法代码是同一份，但 a 调用时 `this` 是 a，b 调用时 `this` 是 b，所以返回各自的名字。

后文要用的词：
- **实例方法**：没有 `static` 修饰、需要通过对象调用的方法。
- **成员变量**：定义在类里、属于对象的属性。

### this 指向谁
`user.setName("张三")` 执行时，方法体里的 `this` 就是 `user` 这个对象。所以 `this.name` 访问的是 `user` 自己的 `name`。

### 为什么 static 方法里不能用
`static` 方法属于类，不依赖某个对象，调用时没有「当前对象」，自然没有 `this`。

### 平时怎么用
大多数时候，访问成员变量可以省略 `this`，编译器会自动补上。必须写 `this` 的典型场景是形参和成员变量同名。

## 示例
```java
class User {
    private String name;

    void setName(String name) {
        this.name = name;   // this.name 是成员变量，name 是形参
    }
}
```

## 易错点
- 在 static 方法里写 this，编译报错
- 以为 this 是个固定对象；它随调用对象而变
- 形参和成员变量同名时漏写 this，结果是形参自己赋给自己，成员变量没变

## 追问
### [f1] this 和 super 有什么区别？
`this` 指当前对象，`super` 用来访问父类的成员或调用父类的构造方法。
