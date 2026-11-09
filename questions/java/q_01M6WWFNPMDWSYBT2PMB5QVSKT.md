---
id: q_01M6WWFNPMDWSYBT2PMB5QVSKT
title: 什么是封装？
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
封装就是把对象的属性设为 private，不让外部直接改，只通过 getter、setter 等公开方法访问，把内部实现藏起来。

## 要点
- [kp1|3] 属性用 private 修饰，外部不能直接读写
- [kp2|3] 通过 public 的 getter、setter 等方法对外提供访问
- [kp3|2] 在 setter 里可以加校验，防止对象被设成非法状态
- [kp4] 内部实现可以随意修改，只要对外方法不变，调用方不受影响

## 详解
### 先搞懂：自动取款机
你用 ATM 取钱，只能插卡、输入密码、按按钮，不能伸手进去直接拿钞票。机器内部怎么存钱、怎么记账，你看不见，也改不了。这就是封装：对外只开放有限的操作，内部细节藏起来。

做项目时的场景：用户年龄不该是负数。如果 `age` 是公开的，谁都能写 `user.age = -5`；如果是 private，只能通过 `setAge` 改，就可以在里面检查。

后文要用的词：
- **访问修饰符**：控制谁能访问，如 `private` 只有本类能访问，`public` 谁都能访问。
- **getter / setter**：读取、修改属性的公开方法，一般命名为 `getXxx`、`setXxx`。

### 做法：属性私有，方法公开
1. 把属性声明为 `private`；
2. 提供 `public` 的 getter 读取；
3. 需要修改时提供 setter，并在其中做校验。

### 好处
- **保护数据**：改值必须经过方法，可以校验，不会被随意改成非法值。
- **隐藏实现**：内部想换种存法（比如把生日改成直接存年龄），只改类内部，调用方不受影响。
- **控制权限**：只提供 getter 不提供 setter，就是只读属性。

### 不是所有属性都必须有 getter、setter
封装的重点是「控制访问」，不是机械地给每个属性生成一对方法。如果对外不需要，就不要开放。

## 示例
```java
public class User {
    private int age;

    public int getAge() { return age; }

    public void setAge(int age) {
        if (age < 0) {
            throw new IllegalArgumentException("年龄不能为负");
        }
        this.age = age;
    }
}
```

## 易错点
- 给每个私有属性都生成 getter 和 setter，却没有任何校验，等于把属性公开，没有真正封装
- 以为封装只是写 private；关键是通过方法控制访问
- getter 直接返回内部的可变对象（如 List），外部仍能改内部数据

## 追问
### [f1] 封装和继承、多态是什么关系？
封装管「藏起来」，继承管「复用」，多态管「同一调用不同表现」。三者都是为了让代码更容易维护和扩展。

### [f2] 为什么 getter 返回集合要小心？
直接返回内部集合，外部拿到的是同一个对象，可以随意增删。可以返回只读视图或副本。
