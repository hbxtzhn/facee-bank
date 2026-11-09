---
id: q_01M6WWFPGSBAEEXYJG2HV848TE
title: 多态解决了什么问题？
type: concept
difficulty: easy
importance: 2
category: java
tags: [oop]
prerequisites: [q_01M6ZYJ2EYQH3AQMDQH8A8EPG1]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
多态让调用代码只依赖父类或接口、不依赖具体子类，新增一种子类时只要扩展、不用改调用处，从而提高灵活性和可扩展性。

## 要点
- [kp1|3] 调用方只依赖父类或接口，不关心具体是哪个子类
- [kp2|3] 新增子类只需新写一个类，调用处不用改，符合对扩展开放、对修改关闭
- [kp3|2] 可以消除一长串 if-else 或 switch 类型判断
- [kp4] 具体调用哪个子类的方法，运行时才确定

## 详解
### 先搞懂：支付方式越来越多
假设你做电商，一开始只有微信支付，后来加了支付宝，再后来加了银行卡。如果每加一种，都要去改下单的代码，加一个 `if`，就会很快变成一团乱麻，改一处还容易改坏别处。

类比：公司前台只管叫「下一位」，不管来的是谁。来了新同事，前台的工作方式不用变。

后文要用的词：
- **父类 / 接口**：统一的调用入口，如 `Payment`。
- **扩展**：增加新的子类或实现类。

### 没有多态时的写法
```java
if (type.equals("wechat")) { ... }
else if (type.equals("alipay")) { ... }
```
每增加一种支付方式，都要回来改这段代码。判断越多，越容易漏改、改错。

### 有多态时的写法
先定义统一的 `Payment` 接口，每种支付方式是一个实现类。下单代码只写 `payment.pay(amount)`。新增银行卡支付，只要新写一个 `BankPayment` 类，下单代码一行不用改。

### 好处总结
- **灵活**：调用方可以在运行时换用不同的实现。
- **易扩展**：新增类型不改旧代码，出错面小。
- **易维护**：每种实现的逻辑独立在自己的类里，职责清楚。

### 代价
多态依赖良好的抽象。接口设计得不好，新增实现时可能还是得改接口，所以要先想清楚哪些行为是共性。

## 示例
```java
interface Payment { void pay(int amount); }
class WechatPay implements Payment { public void pay(int a) { /* ... */ } }
class AliPay implements Payment { public void pay(int a) { /* ... */ } }

void checkout(Payment payment, int amount) {
    payment.pay(amount);   // 不关心具体是哪种支付
}
```

## 易错点
- 以为多态是为了少写代码；主要价值是让新增需求时不用改旧代码
- 抽象不当，每新增一个子类就要给接口加方法，多态的好处就没了
- 滥用继承层级，层次太深反而难读

## 追问
### [f1] 多态和开闭原则有什么关系？
开闭原则要求对扩展开放、对修改关闭。多态是实现它的常见手段：靠新增子类扩展，调用代码不用动。

### [f2] 策略模式用到了多态吗？
用到了。把不同算法封装成实现同一接口的类，调用方通过接口调用，运行时换用不同的实现。
