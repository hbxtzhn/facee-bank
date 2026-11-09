---
id: q_01M6WWFQGCW213KFGECZSSDZ72
title: this 关键字有哪些用法？
type: concept
difficulty: easy
importance: 1
category: java
tags: [oop]
prerequisites: [q_01M6WWFPRQKH1D80GGF3825A2M, q_01M6WWFQ0MG7G3WH2MBSST69SW]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
this 有三种常见用法：直接引用本对象的成员，区分与形参同名的成员变量，以及在构造方法里用 this(...) 调用本类的其他构造方法。

## 要点
- [kp1|3] 区分成员变量和同名形参：`this.name = name`
- [kp2|3] 在构造方法里用 `this(...)` 调用本类另一个构造方法，且必须放在第一行
- [kp3|2] 直接引用本对象的成员：`this.method()`、`this.field`，通常可省略 this
- [kp4] 也可以把 `this` 当参数传出去，把当前对象交给别人

## 详解
### 先搞懂：this 就是「我自己」
`this` 表示当前对象，相当于对象说「我自己」。有了这个「我」，对象就能在内部指代自己。

后文要用的词：
- **成员变量**：定义在类里的属性。
- **形参**：方法声明里的参数变量。
- **构造方法**：与类同名、用来初始化对象的特殊方法。

### 用法一：普通的直接引用
在实例方法中，`this.field` 访问自己的属性，`this.method()` 调用自己的方法。大多数时候 `this.` 可以省略，编译器自动补上。
```java
void show() { this.print(); }   // 等同于 print();
```

### 用法二：形参与成员变量重名
构造方法或 setter 里，常把形参起得和成员变量一样。这时直接写 `name` 指的是形参（就近原则），要访问成员变量必须写 `this.name`。
```java
User(String name) { this.name = name; }
```

### 用法三：引用本类构造方法
一个类有多个构造方法时，可以让参数少的那个调用参数多的那个，避免重复写初始化逻辑：
```java
User() { this("匿名"); }              // 调用下面那个构造方法
User(String name) { this.name = name; }
```
`this(...)` 只能出现在构造方法里，并且必须是第一条语句。

### 附：把 this 传出去
有时需要把当前对象交给别的方法或注册到别处，直接传 `this` 即可。

## 易错点
- 形参和成员变量同名却不写 this，结果是形参赋给自己，属性没被设置
- `this(...)` 没放在第一行，编译报错
- 两个构造方法用 `this(...)` 互相调用，会形成递归，编译报错
- static 方法里没有 this，不能使用

## 追问
### [f1] this(...) 和 super(...) 能同时出现在一个构造方法里吗？
不能，两者都要求放在第一行，只能写一个。

### [f2] 为什么 this 不能在 static 方法里用？
static 方法属于类，不是某个对象的，调用时没有「当前对象」。
