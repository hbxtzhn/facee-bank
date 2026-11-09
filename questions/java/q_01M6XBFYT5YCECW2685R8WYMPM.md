---
id: q_01M6XBFYT5YCECW2685R8WYMPM
title: Object 的 clone() 方法怎么用？
type: concept
difficulty: easy
importance: 1
category: java
tags: [object-methods]
prerequisites: [q_01M6XBFY9M3D7DGAV9KPZSNV2P]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
让类实现 Cloneable 接口，再重写 clone() 并调用 super.clone()，就能得到一个浅拷贝的副本；要深拷贝，引用成员得自己再复制。

## 要点
- [kp1|3] 类必须实现 Cloneable，否则 super.clone() 抛 CloneNotSupportedException
- [kp2|3] Object.clone() 是浅拷贝，引用成员仍然共用
- [kp3|2] Object 的 clone() 是 protected，要在子类里重写后才能对外调用
- [kp4|2] 要深拷贝，在 clone() 里对每个引用成员也调用复制
- [kp5] 数组的 clone() 只复制一层元素

## 详解
### 先搞懂：clone() 是 Object 自带的“复印机”
做项目时想复制一个订单对象，最直接的办法是自己 new 一个，再一个字段一个字段地赋值，字段多了很烦。Java 在所有对象的祖先类 `Object` 里提供了 `clone()` 方法，相当于一台现成的复印机：一调用，就按原对象的样子生出一个新对象。

不过这台复印机有两个规矩：

- 谁想用，得先登记，登记的方式就是实现 `Cloneable` 接口；
- 它默认只复印一层，也就是浅拷贝。

后文用到的词：

- **Cloneable**：一个没有任何方法的接口，只是一个“允许被复制”的标记。
- **浅拷贝**：基本类型复制值，引用类型只复制地址，副本和原对象共用内部对象。

### 怎么用：三步
1. 类实现 `Cloneable`；
2. 重写 `clone()`，在里面调用 `super.clone()`，并把返回值强制转换成自己的类型；
3. 外部调用 `obj.clone()` 拿到副本。

为什么要重写？因为 `Object.clone()` 是 `protected` 的，在类外部不能直接调用。重写时通常把它改成 `public`。

如果没有实现 `Cloneable` 就调用 `super.clone()`，会抛出 `CloneNotSupportedException`，这是编译时异常，所以方法要声明抛出或捕获它。

### 默认是浅拷贝，深拷贝要自己动手
`super.clone()` 把基本类型的值复制过去，引用成员的地址也原样复制，所以副本和原对象的引用成员指向同一个对象。

要变成深拷贝，在重写的 `clone()` 里，拿到 `super.clone()` 的结果后，再把每个引用成员也复制一份（比如调用它自己的 `clone()`），然后赋给副本。

### 数组也有 clone()
数组可以直接调用 `clone()`，不需要实现 `Cloneable`。基本类型数组复制出来互不影响；对象数组只复制元素的地址，元素对象仍是同一批。

## 示例
```java
class Address implements Cloneable {
    String city;
    @Override
    public Address clone() throws CloneNotSupportedException {
        return (Address) super.clone();
    }
}
class Order implements Cloneable {
    int amount;
    Address address;
    @Override
    public Order clone() throws CloneNotSupportedException {
        Order copy = (Order) super.clone();  // 浅拷贝
        copy.address = address.clone();      // 补一步，变成深拷贝
        return copy;
    }
}
```

## 易错点
- 以为 Cloneable 里有 clone() 方法；它是空接口，clone() 定义在 Object 里
- 以为调用 clone() 就是深拷贝；默认只复制一层
- 重写 clone() 时不调用 super.clone() 而是自己 new，在有子类时容易得到类型不对的副本
- 引用成员本身的类没有实现 Cloneable，却想在 clone() 里调用它的 clone()，这是编译不过的

## 追问
### [f1] 除了 clone()，还有什么办法复制对象？
可以写拷贝构造器，把另一个同类对象传进去逐字段复制，或者用序列化再反序列化。这两种方式不依赖 Cloneable，行为更直观，很多团队更倾向它们。
